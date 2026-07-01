from django.test import TestCase
from django.urls import reverse

from core.models import (
    Allergy,
    EmergencyContact,
    InsuranceNetwork,
    InsurancePolicy,
    MedicalCondition,
    Medication,
    PatientProfile,
    Provider,
    Specialty,
)


class PatientAndProviderViewsTests(TestCase):
    def setUp(self):
        self.specialty = Specialty.objects.create(code='cardiology', name='Cardiología')
        self.network = InsuranceNetwork.objects.create(name='OSDE')

        self.provider = Provider.objects.create(
            name='Hospital Test',
            city='Buenos Aires',
            lat=-34.6037,
            lng=-58.3816,
            available_beds=4,
            total_beds=10,
        )
        self.provider.specialties.add(self.specialty)
        self.provider.accepted_networks.add(self.network)

        self.patient = PatientProfile.objects.create(
            full_name='Ana Pérez',
            phone='+54 9 11 1111-2222',
            home_address='Av. Siempre Viva 123',
            home_city='Buenos Aires',
            home_country='Argentina',
            home_lat=-34.6,
            home_lng=-58.4,
            is_primary=True,
        )
        MedicalCondition.objects.create(patient=self.patient, name='Hipertensión', severity='high')
        Allergy.objects.create(patient=self.patient, substance='Penicilina', reaction='Rash', severity='high')
        Medication.objects.create(patient=self.patient, name='Enalapril', dose='10 mg', frequency='1/día')
        EmergencyContact.objects.create(patient=self.patient, name='Luis Pérez', relationship='Esposo', phone='+54 9 11 3333-4444', is_primary=True)
        InsurancePolicy.objects.create(patient=self.patient, network=self.network, plan='Plan 200', member_id='M-001', active=True)

    def test_providers_page_renders_with_filter_context(self):
        response = self.client.get(reverse('core:providers'), {'specialty': self.specialty.code, 'q': 'Hospital'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Red de prestadores')
        self.assertContains(response, 'Hospital Test')

    def test_patient_page_renders_clinical_sections(self):
        response = self.client.get(reverse('core:patient'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ficha clínica')
        self.assertContains(response, 'Cobertura')
        self.assertContains(response, 'Contactos')
        self.assertContains(response, 'Domicilio')
