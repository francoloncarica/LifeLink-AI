"""
Smart Travel Emergency Plan generator (PREPARE pillar).

Builds a personalized "Emergency Readiness Plan" for a destination, combining a
small curated destination catalog with the patient's own risk profile and
coverage, plus the nearest providers we know in that country.
"""
import json

from . import geo
from .models import Provider, TravelPlan

# Curated catalog of popular destinations (coords + health context).
DESTINATIONS = {
    'miami': {
        'city': 'Miami', 'country': 'Estados Unidos', 'lat': 25.7617, 'lng': -80.1918,
        'language': 'Inglés', 'risk_level': 'Moderado',
        'health_risks': ['Costos médicos muy altos sin seguro internacional',
                         'Temporada de huracanes (jun–nov)'],
        'vaccines': ['Ninguna obligatoria'],
        'recommendations': ['Confirmar que la póliza cubra EE.UU. (suelen excluirlo)',
                            'Llevar resumen clínico traducido al inglés'],
    },
    'madrid': {
        'city': 'Madrid', 'country': 'España', 'lat': 40.4168, 'lng': -3.7038,
        'language': 'Español', 'risk_level': 'Bajo',
        'health_risks': ['Olas de calor extremo en verano'],
        'vaccines': ['Ninguna obligatoria'],
        'recommendations': ['Tarjeta Sanitaria Europea no aplica a no residentes — usar seguro',
                            'Sistema público de alta calidad'],
    },
    'sao paulo': {
        'city': 'São Paulo', 'country': 'Brasil', 'lat': -23.5505, 'lng': -46.6333,
        'language': 'Portugués', 'risk_level': 'Moderado',
        'health_risks': ['Dengue endémico', 'Fiebre amarilla en zonas rurales'],
        'vaccines': ['Fiebre amarilla (recomendada)'],
        'recommendations': ['Repelente de mosquitos', 'Barrera idiomática: activar traducción médica'],
    },
    'punta del este': {
        'city': 'Punta del Este', 'country': 'Uruguay', 'lat': -34.9595, 'lng': -54.9510,
        'language': 'Español', 'risk_level': 'Bajo',
        'health_risks': ['Oferta hospitalaria limitada fuera de temporada'],
        'vaccines': ['Ninguna obligatoria'],
        'recommendations': ['Verificar convenio de la prepaga en Uruguay'],
    },
    'nueva york': {
        'city': 'Nueva York', 'country': 'Estados Unidos', 'lat': 40.7128, 'lng': -74.0060,
        'language': 'Inglés', 'risk_level': 'Moderado',
        'health_risks': ['Costos médicos muy altos sin seguro internacional',
                         'Inviernos extremos'],
        'vaccines': ['Ninguna obligatoria'],
        'recommendations': ['Seguro con cobertura amplia en EE.UU.',
                            'Resumen clínico en inglés'],
    },
    'santiago': {
        'city': 'Santiago', 'country': 'Chile', 'lat': -33.4489, 'lng': -70.6693,
        'language': 'Español', 'risk_level': 'Bajo',
        'health_risks': ['Altura en zonas cordilleranas', 'Smog en invierno'],
        'vaccines': ['Ninguna obligatoria'],
        'recommendations': ['Aclimatación si se viaja a la cordillera'],
    },
}

GENERIC = {
    'language': 'Local', 'risk_level': 'Moderado',
    'health_risks': ['Riesgos no catalogados — consultar fuente sanitaria oficial'],
    'vaccines': ['Verificar requisitos del destino'],
    'recommendations': ['Llevar resumen clínico', 'Confirmar cobertura internacional'],
}


def lookup_destination(query):
    """Resolve a free-text destination to a catalog entry (or None)."""
    key = (query or '').strip().lower()
    if key in DESTINATIONS:
        return DESTINATIONS[key]
    for k, v in DESTINATIONS.items():
        if key and (key in k or key in v['city'].lower() or key in v['country'].lower()):
            return v
    return None


def generate_travel_plan(patient, destination_query):
    """Create and persist a TravelPlan for the patient + destination query."""
    dest = lookup_destination(destination_query)
    if dest is None:
        dest = dict(GENERIC, city=(destination_query or 'Destino').title(),
                    country='—', lat=patient.home_lat, lng=patient.home_lng)

    policy = patient.active_policy
    coverage_ok = bool(policy and policy.international)
    coverage_note = (
        f'{policy.network.name} con cobertura internacional ✓' if coverage_ok
        else (f'{policy.network.name} SIN cobertura internacional — contratar asistencia al viajero'
              if policy else 'Sin póliza activa — contratar seguro de viaje')
    )

    # Nearest known providers in the destination country.
    providers = Provider.objects.filter(country__iexact=dest['country'])
    recommended = []
    for p in providers:
        d = geo.road_distance_km(dest['lat'], dest['lng'], p.lat, p.lng)
        recommended.append((d, p))
    recommended.sort(key=lambda r: r[0])
    recommended = recommended[:3]

    rec_data = [{
        'name': p.name,
        'kind': p.get_kind_display(),
        'distance_km': round(d, 1),
        'quality': p.quality_rating,
        'phone': p.phone,
        'lat': p.lat, 'lng': p.lng,
    } for d, p in recommended]

    # Patient-specific flags.
    patient_flags = []
    if patient.conditions.filter(severity__in=['high', 'critical']).exists():
        patient_flags.append('Antecedentes de alto riesgo: llevar epicrisis y medicación de respaldo')
    if patient.allergies.filter(severity__in=['high', 'anaphylaxis']).exists():
        patient_flags.append('Alergia grave: portar autoinyector y alerta médica')
    if patient.medications.exists():
        patient_flags.append(f'{patient.medications.count()} medicamentos crónicos: verificar disponibilidad en destino')

    data = {
        'language': dest['language'],
        'risk_level': dest['risk_level'],
        'health_risks': dest['health_risks'],
        'vaccines': dest['vaccines'],
        'recommendations': dest['recommendations'],
        'coverage_ok': coverage_ok,
        'coverage_note': coverage_note,
        'patient_flags': patient_flags,
        'providers': rec_data,
    }

    summary = (f"Plan de emergencia para {dest['city']}, {dest['country']}. "
               f"Riesgo {dest['risk_level'].lower()}. Idioma {dest['language']}. "
               f"{'Cobertura internacional confirmada.' if coverage_ok else 'Atención: revisar cobertura.'}")

    plan = TravelPlan.objects.create(
        patient=patient,
        destination_city=dest['city'],
        destination_country=dest['country'],
        destination_lat=dest['lat'],
        destination_lng=dest['lng'],
        status='ready',
        risk_level=dest['risk_level'],
        summary=summary,
        data_json=json.dumps(data, ensure_ascii=False),
    )
    return plan
