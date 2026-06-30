"""
Emergency Orchestrator — the "AI brain" of LifeLink AI.

Given a detected event (patient + type + GPS location), it:
  1. Runs triage to determine urgency and the required specialty.
  2. Scores every provider in the network on a transparent, weighted rubric
     (proximity, specialty, insurance coverage, quality, availability, trauma,
     language) so the decision is fully explainable.
  3. Selects the optimal provider and persists the event, the per-provider
     scoring breakdown, and the automated "Emergency Journey" timeline.

It's deterministic and rule-based (no external API), which keeps the prototype
fully local while modelling exactly how the production AI layer would decide.
"""
import json

from django.db import transaction
from django.utils import timezone

from . import geo
from .triage import triage
from .models import (
    Specialty, Provider, EmergencyEvent, EmergencyAction, ProviderCandidate,
)

# Weighted rubric — components sum to 100; language is a small situational bonus.
WEIGHTS = {
    'proximity': 34,
    'specialty': 22,
    'coverage': 18,
    'quality': 12,
    'availability': 9,
    'trauma': 5,
}
LANGUAGE_BONUS = 3
MAX_USEFUL_KM = 30.0  # beyond this, proximity score floors at 0


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def score_provider(provider, event_ctx):
    """
    Score a single provider for an event context. Returns (score, breakdown).
    `event_ctx` carries: lat, lng, rule (triage), patient policy networks, langs, abroad.
    """
    dist = geo.road_distance_km(event_ctx['lat'], event_ctx['lng'], provider.lat, provider.lng)
    eta = geo.eta_minutes(dist)
    rule = event_ctx['rule']
    components = []

    # --- Proximity ---
    prox = WEIGHTS['proximity'] * _clamp(1 - dist / MAX_USEFUL_KM)
    components.append({
        'label': 'Cercanía', 'points': round(prox, 1), 'max': WEIGHTS['proximity'],
        'detail': f'{dist:.1f} km · ETA {eta} min',
    })

    # --- Specialty match ---
    prov_specialty_codes = set(provider.specialties.values_list('code', flat=True))
    if rule['specialty'] in prov_specialty_codes:
        spec = WEIGHTS['specialty']
        spec_detail = f"Cuenta con {rule['specialty']}"
    elif 'emergency' in prov_specialty_codes:
        spec = WEIGHTS['specialty'] * 0.5
        spec_detail = 'Guardia general (sin la especialidad exacta)'
    else:
        spec = WEIGHTS['specialty'] * 0.2
        spec_detail = 'Estabilización inicial únicamente'
    components.append({
        'label': 'Especialidad', 'points': round(spec, 1), 'max': WEIGHTS['specialty'],
        'detail': spec_detail,
    })
    
    # --- Insurance coverage ---
    prov_networks = set(provider.accepted_networks.values_list('id', flat=True))
    patient_networks = event_ctx['policy_network_ids']
    if not patient_networks:
        cov = WEIGHTS['coverage'] * 0.5
        cov_detail = 'Sin cobertura activa registrada'
    elif prov_networks & patient_networks:
        cov = WEIGHTS['coverage']
        cov_detail = f"En red ({event_ctx['policy_label']})"
    else:
        cov = WEIGHTS['coverage'] * 0.25
        cov_detail = 'Fuera de red (posible copago)'
    components.append({
        'label': 'Cobertura', 'points': round(cov, 1), 'max': WEIGHTS['coverage'],
        'detail': cov_detail,
    })

    # --- Quality ---
    qual = WEIGHTS['quality'] * _clamp(provider.quality_rating / 5.0)
    components.append({
        'label': 'Calidad clínica', 'points': round(qual, 1), 'max': WEIGHTS['quality'],
        'detail': f'{provider.quality_rating:.1f} / 5',
    })

    # --- Availability ---
    if not provider.er_open:
        avail = 0.0
        avail_detail = 'Guardia cerrada'
    else:
        beds_factor = _clamp(provider.available_beds / 5.0)
        avail = WEIGHTS['availability'] * (0.5 + 0.5 * beds_factor)
        avail_detail = f'{provider.available_beds} camas libres'
    components.append({
        'label': 'Disponibilidad', 'points': round(avail, 1), 'max': WEIGHTS['availability'],
        'detail': avail_detail,
    })

    # --- Trauma capability (only differentiates when relevant) ---
    if rule['needs_trauma']:
        trauma = WEIGHTS['trauma'] * _clamp(provider.trauma_level / 3.0)
        trauma_detail = (f'Centro de trauma nivel {provider.trauma_level}'
                         if provider.trauma_level else 'Sin capacidad de trauma')
    else:
        trauma = WEIGHTS['trauma']  # neutral — not relevant for this event
        trauma_detail = 'No requerido'
    components.append({
        'label': 'Trauma', 'points': round(trauma, 1), 'max': WEIGHTS['trauma'],
        'detail': trauma_detail,
    })

    score = prox + spec + cov + qual + avail + trauma

    # --- Language bonus (matters mostly abroad) ---
    lang_bonus = 0.0
    prov_langs = {l.lower() for l in provider.language_list}
    if event_ctx['patient_langs'] & prov_langs:
        lang_bonus = LANGUAGE_BONUS
    if event_ctx['abroad']:
        components.append({
            'label': 'Idioma', 'points': round(lang_bonus, 1), 'max': LANGUAGE_BONUS,
            'detail': 'Atiende en idioma del paciente' if lang_bonus else 'Posible barrera idiomática',
        })
        score += lang_bonus

    breakdown = {
        'total': round(score, 1),
        'distance_km': round(dist, 2),
        'eta_min': eta,
        'components': components,
    }
    return score, breakdown, dist, eta


# Timeline step catalog (icon + base title)
def _build_timeline(event, patient, provider, rule, eta, ctx):
    steps = []

    steps.append(('geolocate', '📍', 'Ubicación confirmada',
                  event.location_desc or f'{event.lat:.4f}, {event.lng:.4f}', 'done'))

    steps.append(('triage', '🧠', f'Triage IA · {event.severity_label}',
                  rule['advice'], 'done'))

    if ctx['policy_label']:
        steps.append(('coverage', '🛡️', 'Cobertura verificada',
                      f"{ctx['policy_label']} validada en segundos", 'done'))
    else:
        steps.append(('coverage', '🛡️', 'Cobertura',
                      'Sin póliza activa — se deriva al prestador público más cercano', 'done'))

    if provider:
        steps.append(('provider_select', '🏥', f'Prestador óptimo: {provider.name}',
                      f'{event.provider_distance_km:.1f} km · score {event.decision_score:.0f}/100',
                      'done'))
        steps.append(('ambulance', '🚑', 'Ambulancia despachada',
                      f'ETA estimado {eta} min', 'active'))

    n_cond = patient.conditions.count()
    n_all = patient.allergies.count()
    n_med = patient.medications.count()
    steps.append(('history_share', '📋', 'Historia clínica compartida',
                  f'Grupo {patient.blood_type} · {n_cond} condiciones · {n_all} alergias · {n_med} medicamentos',
                  'done'))

    contact = patient.primary_contact
    if contact:
        steps.append(('notify_family', '👨‍👩‍👧', 'Familia notificada',
                      f'{contact.name} ({contact.relationship or "contacto"}) · {contact.phone}', 'done'))

    if ctx['policy_label']:
        steps.append(('notify_insurer', '📞', 'Aseguradora informada',
                      f"Caso abierto con {ctx['policy_network']}", 'done'))

    if ctx['abroad']:
        steps.append(('translate', '🌐', 'Traducción médica activada',
                      f'Información clínica traducida para {event.country}', 'done'))

    steps.append(('monitor', '📡', 'Monitoreo en tiempo real',
                  'Seguimiento del caso hasta el ingreso hospitalario', 'active'))

    objs = [
        EmergencyAction(event=event, step=s, icon=icon, title=title,
                        detail=detail, status=status, order=i)
        for i, (s, icon, title, detail, status) in enumerate(steps)
    ]
    EmergencyAction.objects.bulk_create(objs)


@transaction.atomic
def orchestrate(patient, event_type, *, trigger_type='sos_button',
                lat=None, lng=None, location_desc='', city='', country='Argentina'):
    """
    Run the full orchestration for a detected event and persist everything.
    Returns the created EmergencyEvent.
    """
    if lat is None:
        lat = patient.home_lat
    if lng is None:
        lng = patient.home_lng

    rule = triage(event_type, patient)
    specialty = Specialty.objects.filter(code=rule['specialty']).first()

    # Build the scoring context once.
    policy = patient.active_policy
    ctx = {
        'lat': lat, 'lng': lng, 'rule': rule,
        'policy_network_ids': {policy.network_id} if policy else set(),
        'policy_label': (f'{policy.network.name} · {policy.get_coverage_level_display()}'
                         if policy else ''),
        'policy_network': policy.network.name if policy else '',
        'patient_langs': {l.lower() for l in patient.language_list},
        'abroad': bool(country and country.strip().lower() != (patient.home_country or '').strip().lower()),
    }

    # Score all providers; prefer open ERs.
    providers = list(Provider.objects.all().prefetch_related('specialties', 'accepted_networks'))
    scored = []
    for p in providers:
        s, breakdown, dist, eta = score_provider(p, ctx)
        scored.append((s, p, breakdown, dist, eta))

    # Selection: only open ERs are eligible; fall back to all if none are open.
    eligible = [row for row in scored if row[1].er_open] or scored
    eligible.sort(key=lambda r: r[0], reverse=True)

    best = eligible[0] if eligible else None
    best_provider = best[1] if best else None
    best_dist = best[3] if best else None
    best_eta = best[4] if best else None
    best_score = best[0] if best else None

    event = EmergencyEvent.objects.create(
        patient=patient,
        trigger_type=trigger_type,
        event_type=event_type,
        severity=rule['severity'],
        lat=lat, lng=lng,
        location_desc=location_desc, city=city, country=country,
        required_specialty=specialty,
        selected_provider=best_provider,
        provider_distance_km=round(best_dist, 2) if best_dist is not None else None,
        ambulance_eta_min=best_eta,
        decision_score=round(best_score, 1) if best_score is not None else None,
        status='en_route' if best_provider else 'active',
    )

    # Persist the top candidates (limit to keep the UI focused).
    cand_objs = []
    for s, p, breakdown, dist, eta in eligible[:6]:
        cand_objs.append(ProviderCandidate(
            event=event, provider=p, distance_km=round(dist, 2), eta_min=eta,
            score=round(s, 1), breakdown_json=json.dumps(breakdown, ensure_ascii=False),
            selected=(p == best_provider),
        ))
    ProviderCandidate.objects.bulk_create(cand_objs)

    _build_timeline(event, patient, best_provider, rule, best_eta, ctx)
    return event

