"""
Seed LifeLink AI with realistic demo data:
  · specialties + insurance networks
  · a provider network (Buenos Aires + a few international hospitals)
  · a primary demo patient with clinical profile, contacts and coverage

All clinical data is FICTIONAL and only meant to demo the orchestration.
Re-running wipes patients / providers / events / travel plans and recreates them.

    python manage.py seed_demo
"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Specialty, InsuranceNetwork, PatientProfile, MedicalCondition, Allergy,
    Medication, EmergencyContact, InsurancePolicy, Provider, EmergencyEvent,
    EmergencyAction, ProviderCandidate, TravelPlan,
)

SPECIALTIES = [
    ('cardiology', 'Cardiología', '❤️'),
    ('neurology', 'Neurología / ACV', '🧠'),
    ('trauma', 'Trauma y cirugía', '🦴'),
    ('emergency', 'Guardia general', '🚑'),
    ('respiratory', 'Neumonología', '🫁'),
    ('pediatrics', 'Pediatría', '🧒'),
    ('allergy', 'Alergología', '🤧'),
]

NETWORKS = [
    ('OSDE', 'Argentina', True),
    ('Swiss Medical', 'Argentina', False),
    ('Galeno', 'Argentina', False),
    ('Medifé', 'Argentina', False),
    ('IOMA', 'Argentina', False),
    ('Assist Card', 'Internacional', True),
]

# name, kind, address, city, country, lat, lng, phone, quality, trauma, er_open,
# total_beds, available_beds, [specialties], [networks], languages
PROVIDERS = [
    ('Hospital Italiano de Buenos Aires', 'hospital', 'Tte. Gral. Perón 4190', 'Buenos Aires', 'Argentina',
     -34.6082, -58.4214, '+54 11 4959-0200', 4.8, 2, True, 200, 8,
     ['emergency', 'cardiology', 'neurology', 'trauma', 'respiratory'],
     ['OSDE', 'Swiss Medical', 'Galeno', 'Medifé'], 'Español, Inglés, Italiano'),
    ('Sanatorio Mater Dei', 'hospital', 'Av. Callao 1100', 'Buenos Aires', 'Argentina',
     -34.5980, -58.3920, '+54 11 4824-7000', 4.7, 2, True, 180, 7,
     ['emergency', 'cardiology', 'trauma'], ['OSDE', 'Swiss Medical'], 'Español, Inglés'),
    ('Hospital Británico', 'hospital', 'Perdriel 74', 'Buenos Aires', 'Argentina',
     -34.6286, -58.3838, '+54 11 4309-6400', 4.5, 1, True, 130, 2,
     ['emergency', 'trauma', 'respiratory'], ['Swiss Medical', 'Galeno', 'Medifé'], 'Español, Inglés'),
    ('Hospital Alemán', 'hospital', 'Av. Pueyrredón 1640', 'Buenos Aires', 'Argentina',
     -34.5896, -58.4022, '+54 11 4827-7000', 4.7, 1, True, 150, 4,
     ['emergency', 'cardiology', 'trauma', 'respiratory'],
     ['OSDE', 'Swiss Medical', 'Medifé'], 'Español, Alemán, Inglés'),
    ('Sanatorio Güemes', 'hospital', 'Av. Córdoba 3933', 'Buenos Aires', 'Argentina',
     -34.5996, -58.4112, '+54 11 4865-6000', 4.4, 2, True, 160, 7,
     ['emergency', 'cardiology', 'trauma'], ['OSDE', 'Galeno', 'IOMA'], 'Español'),
    ('Hospital de Niños Ricardo Gutiérrez', 'pediatric', 'Sánchez de Bustamante 1399', 'Buenos Aires', 'Argentina',
     -34.6020, -58.4108, '+54 11 4962-9247', 4.3, 1, True, 100, 5,
     ['pediatrics', 'emergency'], ['IOMA', 'Medifé'], 'Español'),
    ('Hospital El Cruce', 'trauma', 'Av. Calchaquí 5401', 'Florencio Varela', 'Argentina',
     -34.8065, -58.2546, '+54 11 4210-9000', 4.2, 3, True, 180, 9,
     ['trauma', 'emergency', 'cardiology'], ['IOMA'], 'Español'),
    ('Hospital Fernández', 'hospital', 'Av. Cerviño 3356', 'Buenos Aires', 'Argentina',
     -34.5836, -58.4106, '+54 11 4808-2600', 4.0, 2, True, 170, 1,
     ['emergency', 'trauma', 'respiratory'], ['IOMA'], 'Español'),
    ('Clínica Bazterrica', 'clinic', 'Juncal 3002', 'Buenos Aires', 'Argentina',
     -34.5958, -58.4014, '+54 11 4827-7800', 4.3, 0, True, 70, 3,
     ['emergency', 'cardiology'], ['OSDE', 'Swiss Medical'], 'Español, Inglés'),
    ('Hospital Privado de Rosario', 'hospital', 'Bv. Oroño 1250', 'Rosario', 'Argentina',
     -32.9580, -60.6610, '+54 341 480-3000', 4.4, 1, True, 140, 6,
     ['emergency', 'cardiology', 'trauma'], ['OSDE', 'Galeno'], 'Español'),
    ('Clínica Mayo Córdoba', 'clinic', 'Av. Colón 700', 'Córdoba', 'Argentina',
     -31.4201, -64.1888, '+54 351 468-5000', 4.2, 0, True, 90, 4,
     ['emergency', 'cardiology'], ['OSDE', 'Swiss Medical'], 'Español'),
    ('Hospital Regional de Mar del Plata', 'hospital', 'Av. Colón 2600', 'Mar del Plata', 'Argentina',
     -38.0025, -57.5424, '+54 223 472-1000', 4.1, 1, True, 110, 5,
     ['emergency', 'trauma', 'respiratory'], ['OSDE', 'IOMA'], 'Español'),
    ('Clínica del Sol Mendoza', 'clinic', 'Av. San Martín 1250', 'Mendoza', 'Argentina',
     -32.8895, -68.8458, '+54 261 428-9000', 4.3, 0, True, 80, 3,
     ['emergency', 'cardiology'], ['OSDE'], 'Español, Inglés'),
    ('Hospital Escuela Paraná', 'hospital', 'Av. Pellegrini 2200', 'Paraná', 'Argentina',
     -31.7448, -60.5170, '+54 343 423-1000', 4.0, 1, True, 95, 2,
     ['emergency', 'trauma'], ['IOMA'], 'Español'),
    ('Fundación Favaloro', 'cardiac', 'Av. Belgrano 1746', 'Buenos Aires', 'Argentina',
     -34.6113, -58.3920, '+54 11 4378-1200', 4.9, 0, True, 90, 6,
     ['cardiology', 'emergency'], ['OSDE', 'Swiss Medical'], 'Español, Inglés'),
    ('FLENI', 'stroke', 'Montañeses 2325', 'Buenos Aires', 'Argentina',
     -34.5547, -58.4560, '+54 11 5777-3200', 4.9, 0, True, 80, 5,
     ['neurology', 'emergency'], ['OSDE', 'Swiss Medical', 'Galeno'], 'Español, Inglés'),
    # --- International (for travel scenarios) ---
    ('Jackson Memorial Hospital', 'hospital', '1611 NW 12th Ave', 'Miami', 'Estados Unidos',
     25.7907, -80.2127, '+1 305-585-1111', 4.6, 3, True, 400, 12,
     ['emergency', 'trauma', 'cardiology', 'neurology'], ['Assist Card', 'OSDE'], 'Inglés, Español'),
    ('Mount Sinai Medical Center', 'hospital', '4300 Alton Rd', 'Miami Beach', 'Estados Unidos',
     25.8170, -80.1410, '+1 305-674-2121', 4.5, 1, True, 220, 6,
     ['emergency', 'cardiology'], ['Assist Card', 'OSDE'], 'Inglés, Español'),
    ('Hospital Universitario La Paz', 'hospital', 'Paseo de la Castellana 261', 'Madrid', 'España',
     40.4795, -3.6870, '+34 917 27 70 00', 4.6, 2, True, 300, 10,
     ['emergency', 'trauma', 'neurology'], ['Assist Card'], 'Español, Inglés'),
    ('Hospital das Clínicas', 'hospital', 'Av. Dr. Enéas C. Aguiar 255', 'São Paulo', 'Brasil',
     -23.5580, -46.6700, '+55 11 2661-0000', 4.4, 2, True, 350, 8,
     ['emergency', 'trauma', 'cardiology'], ['Assist Card'], 'Portugués, Español'),
    ('Sanatorio Cantegril', 'clinic', 'Av. Roosevelt y Parada 5', 'Punta del Este', 'Uruguay',
     -34.9430, -54.9330, '+598 4222 1234', 4.1, 0, True, 60, 4,
     ['emergency'], ['Assist Card'], 'Español'),
]


class Command(BaseCommand):
    help = 'Carga datos demo de LifeLink AI (paciente, prestadores, obras sociales).'

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write('Limpiando datos previos…')
        TravelPlan.objects.all().delete()
        EmergencyEvent.objects.all().delete()
        Provider.objects.all().delete()
        PatientProfile.objects.all().delete()
        # Catalogs (idempotent)
        spec = {}
        for code, name, icon in SPECIALTIES:
            obj, _ = Specialty.objects.get_or_create(code=code, defaults={'name': name, 'icon': icon})
            spec[code] = obj

        nets = {}
        for name, country, intl in NETWORKS:
            obj, _ = InsuranceNetwork.objects.get_or_create(
                name=name, defaults={'country': country, 'international': intl})
            nets[name] = obj

        # Providers
        for row in PROVIDERS:
            (name, kind, address, city, country, lat, lng, phone, quality, trauma,
             er_open, total_beds, beds, sp_codes, net_names, langs) = row
            p = Provider.objects.create(
                name=name, kind=kind, address=address, city=city, country=country,
                lat=lat, lng=lng, phone=phone, quality_rating=quality, trauma_level=trauma,
                er_open=er_open, total_beds=total_beds, available_beds=beds, languages=langs,
            )
            p.specialties.set([spec[c] for c in sp_codes])
            p.accepted_networks.set([nets[n] for n in net_names])

        # Demo patient (fictional clinical data)
        patient = PatientProfile.objects.create(
            full_name='Martín Gómez', date_of_birth=date(1984, 7, 12), blood_type='O+',
            phone='+54 9 11 5555-1234', languages='Español, Inglés',
            home_address='Av. Santa Fe 3200', home_city='Buenos Aires', home_country='Argentina',
            home_lat=-34.5885, home_lng=-58.4108, is_primary=True,
            notes='Paciente demo de LifeLink AI. Datos clínicos ficticios.',
        )
        MedicalCondition.objects.bulk_create([
            MedicalCondition(patient=patient, name='Hipertensión arterial', severity='high'),
            MedicalCondition(patient=patient, name='Asma', severity='medium'),
        ])
        Allergy.objects.bulk_create([
            Allergy(patient=patient, substance='Penicilina', reaction='Urticaria / rash', severity='high'),
            Allergy(patient=patient, substance='Polen', reaction='Rinitis', severity='low'),
        ])
        Medication.objects.bulk_create([
            Medication(patient=patient, name='Enalapril', dose='10 mg', frequency='1 vez/día'),
            Medication(patient=patient, name='Salbutamol', dose='Inhalador', frequency='A demanda'),
        ])
        EmergencyContact.objects.bulk_create([
            EmergencyContact(patient=patient, name='Laura Gómez', relationship='Esposa',
                             phone='+54 9 11 5555-9876', is_primary=True),
            EmergencyContact(patient=patient, name='Dr. Pérez', relationship='Médico de cabecera',
                             phone='+54 11 4444-1212'),
        ])
        InsurancePolicy.objects.create(
            patient=patient, network=nets['OSDE'], plan='Plan 410', member_id='OSDE-410-88123',
            coverage_level='premium', valid_until=date(2027, 12, 31), international=True, active=True,
        )

        event = EmergencyEvent.objects.create(
            patient=patient,
            event_type='cardiac',
            trigger_type='sos_button',
            severity=2,
            lat=patient.home_lat,
            lng=patient.home_lng,
            location_desc='Av. Santa Fe y Pueyrredón',
            city='Buenos Aires',
            country='Argentina',
            required_specialty=spec['cardiology'],
            selected_provider=Provider.objects.get(name='Hospital Italiano de Buenos Aires'),
            provider_distance_km=3.2,
            ambulance_eta_min=8,
            decision_score=92.4,
            status='active',
            notes='Ejemplo de orquestación con alta prioridad y cobertura de red.',
        )
        event.actions.bulk_create([
            EmergencyAction(event=event, step='dispatch', icon='🚑', title='Ambulancia despachada', detail='Unidad de alta complejidad asignada', status='done', order=1),
            EmergencyAction(event=event, step='notify', icon='📱', title='Contactos notificados', detail='Se avisó al contacto principal y al médico', status='done', order=2),
            EmergencyAction(event=event, step='hospital', icon='🏥', title='Ingreso en hospital', detail='Se priorizó ingreso en unidad de cardiología', status='active', order=3),
        ])
        event.candidates.bulk_create([
            ProviderCandidate(event=event, provider=Provider.objects.get(name='Hospital Italiano de Buenos Aires'), distance_km=3.2, eta_min=8, score=94.2, selected=True, breakdown_json='{"capacidad": 95, "cobertura": 90, "distancia": 92}'),
            ProviderCandidate(event=event, provider=Provider.objects.get(name='Fundación Favaloro'), distance_km=4.1, eta_min=10, score=91.0, breakdown_json='{"capacidad": 88, "cobertura": 90, "distancia": 85}'),
            ProviderCandidate(event=event, provider=Provider.objects.get(name='Hospital Alemán'), distance_km=5.7, eta_min=12, score=87.6, breakdown_json='{"capacidad": 82, "cobertura": 87, "distancia": 78}'),
        ])

        resolved_event = EmergencyEvent.objects.create(
            patient=patient,
            event_type='trauma',
            trigger_type='fall_detection',
            severity=3,
            lat=-34.5926,
            lng=-58.3992,
            location_desc='Calle Lavalle 1200',
            city='Buenos Aires',
            country='Argentina',
            required_specialty=spec['trauma'],
            selected_provider=Provider.objects.get(name='Hospital El Cruce'),
            provider_distance_km=28.0,
            ambulance_eta_min=24,
            decision_score=84.1,
            status='resolved',
            resolved_at=timezone.now(),
            notes='Caso de ejemplo ya resuelto con seguimiento.',
        )
        resolved_event.actions.create(step='resolve', icon='✅', title='Caso cerrado', detail='Paciente estabilizado', status='done', order=1)

        TravelPlan.objects.create(
            patient=patient,
            destination_city='Miami',
            destination_country='Estados Unidos',
            destination_lat=25.7617,
            destination_lng=-80.1918,
            start_date=date(2026, 8, 5),
            end_date=date(2026, 8, 10),
            risk_level='Alto',
            summary='Viaje internacional con cobertura de asistencia y acceso a centros de alta complejidad.',
            data_json='{"providers": [{"name": "Jackson Memorial Hospital", "lat": 25.7907, "lng": -80.2127, "quality": 4.6, "kind": "Hospital"}, {"name": "Mount Sinai Medical Center", "lat": 25.8170, "lng": -80.1410, "quality": 4.5, "kind": "Hospital"}]}',
        )
        TravelPlan.objects.create(
            patient=patient,
            destination_city='Madrid',
            destination_country='España',
            destination_lat=40.4168,
            destination_lng=-3.7038,
            start_date=date(2026, 10, 2),
            end_date=date(2026, 10, 7),
            risk_level='Moderado',
            summary='Viaje europeo con red de asistencia internacional y centros de emergencia.',
            data_json='{"providers": [{"name": "Hospital Universitario La Paz", "lat": 40.4795, "lng": -3.6870, "quality": 4.6, "kind": "Hospital"}]}',
        )

        self.stdout.write(self.style.SUCCESS(
            f'OK · {Provider.objects.count()} prestadores, '
            f'{Specialty.objects.count()} especialidades, '
            f'{InsuranceNetwork.objects.count()} obras sociales, paciente "{patient.full_name}".'
        ))
        self.stdout.write('Listo. Iniciá el server con: python manage.py runserver')
