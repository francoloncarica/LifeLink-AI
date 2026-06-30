import json

from django.contrib import messages
from django.db.models import Avg, Sum, Count, Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    PatientProfile, Provider, Specialty, EmergencyEvent, TravelPlan,
)
from .orchestrator import orchestrate
from .travel import generate_travel_plan, DESTINATIONS


# ------------------------------------------------------------------
#  Helpers
# ------------------------------------------------------------------
def _primary_patient():
    return (PatientProfile.objects.filter(is_primary=True).first()
            or PatientProfile.objects.first())


def _providers_geojson(providers):
    return [{
        'id': p.id,
        'name': p.name,
        'kind': p.get_kind_display(),
        'lat': p.lat,
        'lng': p.lng,
        'quality': p.quality_rating,
        'beds': p.available_beds,
        'status': p.availability_label,
        'er_open': p.er_open,
    } for p in providers]


def _float(val, default=None):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


# ------------------------------------------------------------------
#  DASHBOARD
# ------------------------------------------------------------------
def dashboard(request):
    patient = _primary_patient()
    providers = list(Provider.objects.all())

    open_events = EmergencyEvent.objects.filter(status__in=['active', 'en_route'])
    recent = list(EmergencyEvent.objects.select_related('patient', 'selected_provider')[:8])

    avg_eta = EmergencyEvent.objects.filter(
        ambulance_eta_min__isnull=False
    ).aggregate(a=Avg('ambulance_eta_min'))['a']

    beds_free = Provider.objects.aggregate(s=Sum('available_beds'))['s'] or 0

    # SOS scenario presets (only meaningful with a patient)
    scenarios = []
    if patient:
        scenarios = [
            {'key': 'home', 'label': 'En casa', 'icon': '🏠',
             'lat': patient.home_lat, 'lng': patient.home_lng,
             'desc': patient.home_address or 'Domicilio', 'country': patient.home_country},
            {'key': 'downtown', 'label': 'Microcentro CABA', 'icon': '🏙️',
             'lat': -34.6037, 'lng': -58.3816,
             'desc': 'Av. Corrientes, CABA', 'country': 'Argentina'},
            {'key': 'highway', 'label': 'Autopista Panamericana', 'icon': '🛣️',
             'lat': -34.4710, 'lng': -58.5230,
             'desc': 'Acceso Norte, km 30', 'country': 'Argentina'},
            {'key': 'abroad', 'label': 'Viajando en Miami', 'icon': '✈️',
             'lat': 25.7617, 'lng': -80.1918,
             'desc': 'Downtown Miami, EE.UU.', 'country': 'Estados Unidos'},
        ]

    ctx = {
        'patient': patient,
        'kpi_open': open_events.count(),
        'kpi_providers': len(providers),
        'kpi_beds': beds_free,
        'kpi_avg_eta': round(avg_eta) if avg_eta else None,
        'kpi_readiness': patient.readiness_score if patient else 0,
        'recent': recent,
        'open_events': list(open_events.select_related('selected_provider')[:5]),
        'event_types': EmergencyEvent.EVENT_TYPES,
        'triggers': EmergencyEvent.TRIGGERS,
        'scenarios': scenarios,
        'map_center': [patient.home_lat, patient.home_lng] if patient else [-34.6037, -58.3816],
        'providers_json': json.dumps(_providers_geojson(providers)),
        'scenarios_json': json.dumps(scenarios),
    }
    return render(request, 'core/dashboard.html', ctx)


# ------------------------------------------------------------------
#  SOS  (trigger orchestration)
# ------------------------------------------------------------------
def sos_trigger(request):
    if request.method != 'POST':
        return redirect('core:dashboard')

    patient = _primary_patient()
    if not patient:
        messages.error(request, 'No hay un paciente cargado. Corré el seed o creá uno en el admin.')
        return redirect('core:dashboard')

    event_type = request.POST.get('event_type', 'other')
    trigger_type = request.POST.get('trigger_type', 'sos_button')
    lat = _float(request.POST.get('lat'), patient.home_lat)
    lng = _float(request.POST.get('lng'), patient.home_lng)
    location_desc = request.POST.get('location_desc', '').strip()
    city = request.POST.get('city', '').strip()
    country = request.POST.get('country', '').strip() or patient.home_country

    event = orchestrate(
        patient, event_type, trigger_type=trigger_type,
        lat=lat, lng=lng, location_desc=location_desc, city=city, country=country,
    )
    messages.success(
        request,
        f'🚨 Emergencia orquestada en segundos · {event.get_event_type_display()}'
        + (f' → {event.selected_provider.name}' if event.selected_provider else ''),
    )
    return redirect('core:emergency_detail', pk=event.pk)


# ------------------------------------------------------------------
#  EMERGENCIES
# ------------------------------------------------------------------
def emergencies_list(request):
    status = request.GET.get('status', '')
    qs = EmergencyEvent.objects.select_related('patient', 'selected_provider')
    if status:
        qs = qs.filter(status=status)

    counts = {
        'all': EmergencyEvent.objects.count(),
        'open': EmergencyEvent.objects.filter(status__in=['active', 'en_route']).count(),
        'resolved': EmergencyEvent.objects.filter(status='resolved').count(),
    }
    return render(request, 'core/emergencies.html', {
        'events': list(qs[:200]),
        'status': status,
        'counts': counts,
        'statuses': EmergencyEvent.STATUS,
    })


def emergency_detail(request, pk):
    event = get_object_or_404(
        EmergencyEvent.objects.select_related('patient', 'selected_provider', 'required_specialty'),
        pk=pk,
    )
    actions = list(event.actions.all())
    candidates = []
    for c in event.candidates.select_related('provider'):
        try:
            breakdown = json.loads(c.breakdown_json) if c.breakdown_json else {}
        except json.JSONDecodeError:
            breakdown = {}
        candidates.append({'obj': c, 'breakdown': breakdown})

    # Map: event location + candidate providers
    map_points = [{
        'name': c['obj'].provider.name,
        'lat': c['obj'].provider.lat,
        'lng': c['obj'].provider.lng,
        'score': c['obj'].score,
        'eta': c['obj'].eta_min,
        'selected': c['obj'].selected,
    } for c in candidates]

    patient = event.patient
    return render(request, 'core/emergency_detail.html', {
        'event': event,
        'patient': patient,
        'actions': actions,
        'candidates': candidates,
        'event_point': json.dumps({'lat': event.lat, 'lng': event.lng,
                                    'desc': event.location_desc}),
        'map_points': json.dumps(map_points),
        'map_center': json.dumps([event.lat, event.lng]),
    })


def emergency_resolve(request, pk):
    event = get_object_or_404(EmergencyEvent, pk=pk)
    if request.method == 'POST':
        event.status = 'resolved'
        event.resolved_at = timezone.now()
        event.save(update_fields=['status', 'resolved_at'])
        event.actions.filter(status='active').update(status='done')
        messages.success(request, 'Emergencia marcada como resuelta.')
    return redirect('core:emergency_detail', pk=pk)


# ------------------------------------------------------------------
#  PATIENT
# ------------------------------------------------------------------
def patient_detail(request, pk=None):
    if pk:
        patient = get_object_or_404(PatientProfile, pk=pk)
    else:
        patient = _primary_patient()
    if not patient:
        return render(request, 'core/patient.html', {'patient': None})

    events = list(patient.events.select_related('selected_provider')[:8])
    return render(request, 'core/patient.html', {
        'patient': patient,
        'conditions': list(patient.conditions.all()),
        'allergies': list(patient.allergies.all()),
        'medications': list(patient.medications.all()),
        'contacts': list(patient.contacts.all()),
        'policies': list(patient.policies.select_related('network')),
        'events': events,
        'home_point': json.dumps({'lat': patient.home_lat, 'lng': patient.home_lng,
                                  'name': patient.full_name}),
    })


# ------------------------------------------------------------------
#  PROVIDERS
# ------------------------------------------------------------------
def providers_list(request):
    kind = request.GET.get('kind', '')
    specialty = request.GET.get('specialty', '')
    q = request.GET.get('q', '')

    qs = Provider.objects.prefetch_related('specialties', 'accepted_networks')
    if kind:
        qs = qs.filter(kind=kind)
    if specialty:
        qs = qs.filter(specialties__code=specialty)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(city__icontains=q))
    providers = list(qs.distinct())

    agg = Provider.objects.aggregate(
        n=Count('id'), beds=Sum('available_beds'), q=Avg('quality_rating'),
    )

    return render(request, 'core/providers.html', {
        'providers': providers,
        'count': agg['n'] or 0,
        'beds': agg['beds'] or 0,
        'avg_quality': round(agg['q'], 1) if agg['q'] else 0,
        'kinds': Provider.KIND,
        'specialties': list(Specialty.objects.all()),
        'f': {'kind': kind, 'specialty': specialty, 'q': q},
        'providers_json': json.dumps(_providers_geojson(providers)),
        'map_center': json.dumps([-34.6037, -58.3816]),
    })


# ------------------------------------------------------------------
#  TRAVEL PLANS
# ------------------------------------------------------------------
def travel_list(request):
    patient = _primary_patient()
    plans = list(TravelPlan.objects.select_related('patient'))
    suggestions = [
        {'key': k, 'city': v['city'], 'country': v['country'],
         'risk': v['risk_level'], 'language': v['language']}
        for k, v in DESTINATIONS.items()
    ]
    return render(request, 'core/travel.html', {
        'patient': patient,
        'plans': plans,
        'suggestions': suggestions,
    })


def travel_create(request):
    if request.method != 'POST':
        return redirect('core:travel')
    patient = _primary_patient()
    if not patient:
        messages.error(request, 'No hay un paciente cargado.')
        return redirect('core:travel')

    destination = request.POST.get('destination', '').strip()
    if not destination:
        messages.error(request, 'Indicá un destino.')
        return redirect('core:travel')

    plan = generate_travel_plan(patient, destination)
    messages.success(request, f'Plan de emergencia generado para {plan.destination_city}.')
    return redirect('core:travel_detail', pk=plan.pk)


def travel_detail(request, pk):
    plan = get_object_or_404(TravelPlan.objects.select_related('patient'), pk=pk)
    try:
        data = json.loads(plan.data_json) if plan.data_json else {}
    except json.JSONDecodeError:
        data = {}

    map_points = [{
        'name': p['name'], 'lat': p['lat'], 'lng': p['lng'],
        'quality': p.get('quality'), 'kind': p.get('kind'),
    } for p in data.get('providers', [])]

    return render(request, 'core/travel_detail.html', {
        'plan': plan,
        'data': data,
        'dest_point': json.dumps({'lat': plan.destination_lat, 'lng': plan.destination_lng,
                                  'city': plan.destination_city}),
        'map_points': json.dumps(map_points),
        'map_center': json.dumps([plan.destination_lat, plan.destination_lng]),
    })
