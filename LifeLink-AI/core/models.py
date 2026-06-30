"""
LifeLink AI — data model.

Three pillars of the platform map to these models:
  · PREPARE   -> PatientProfile (+ conditions, allergies, meds, contacts, policies), TravelPlan
  · DETECT    -> EmergencyEvent (trigger_type, event_type, severity)
  · ORCHESTRATE -> EmergencyAction (the automated journey timeline) +
                   ProviderCandidate (transparent provider scoring) + Provider network
"""
from datetime import date

from django.db import models


# ============================================================
#  CATALOGS
# ============================================================
class Specialty(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    # Emoji/icon shown in the UI
    icon = models.CharField(max_length=8, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'specialties'

    def __str__(self):
        return self.name


class InsuranceNetwork(models.Model):
    name = models.CharField(max_length=80, unique=True)
    country = models.CharField(max_length=60, default='Argentina')
    international = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ============================================================
#  PATIENT  (PREPARE — "Always Ready")
# ============================================================
class PatientProfile(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ('?', 'Desconocido'),
    ]

    full_name = models.CharField(max_length=120)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, default='?')
    phone = models.CharField(max_length=40, blank=True)
    languages = models.CharField(
        max_length=120, default='Español',
        help_text='Idiomas separados por coma',
    )

    home_address = models.CharField(max_length=200, blank=True)
    home_city = models.CharField(max_length=80, blank=True)
    home_country = models.CharField(max_length=80, default='Argentina')
    home_lat = models.FloatField(default=-34.6037)
    home_lng = models.FloatField(default=-58.3816)

    notes = models.TextField(blank=True)
    is_primary = models.BooleanField(
        default=False, help_text='Perfil principal mostrado por defecto',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'full_name']

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def language_list(self):
        return [s.strip() for s in self.languages.split(',') if s.strip()]

    @property
    def primary_contact(self):
        return self.contacts.filter(is_primary=True).first() or self.contacts.first()

    @property
    def active_policy(self):
        return self.policies.filter(active=True).first()

    @property
    def readiness_score(self):
        """0–100 — how "emergency ready" this profile is (completeness)."""
        checks = [
            bool(self.date_of_birth),
            self.blood_type != '?',
            bool(self.phone),
            self.home_lat is not None and self.home_lng is not None,
            self.conditions.exists() or bool(self.notes),
            self.allergies.exists(),
            self.medications.exists(),
            self.contacts.exists(),
            self.policies.filter(active=True).exists(),
        ]
        return round(sum(checks) / len(checks) * 100)


class MedicalCondition(models.Model):
    SEVERITY = [('low', 'Leve'), ('medium', 'Moderada'),
                ('high', 'Alta'), ('critical', 'Crítica')]
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='conditions')
    name = models.CharField(max_length=120)
    severity = models.CharField(max_length=10, choices=SEVERITY, default='medium')
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.name} ({self.get_severity_display()})'


class Allergy(models.Model):
    SEVERITY = [('low', 'Leve'), ('medium', 'Moderada'),
                ('high', 'Alta'), ('anaphylaxis', 'Anafilaxia')]
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='allergies')
    substance = models.CharField(max_length=120)
    reaction = models.CharField(max_length=200, blank=True)
    severity = models.CharField(max_length=12, choices=SEVERITY, default='medium')

    class Meta:
        verbose_name_plural = 'allergies'

    def __str__(self):
        return self.substance


class Medication(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=120)
    dose = models.CharField(max_length=80, blank=True)
    frequency = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.name


class EmergencyContact(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=120)
    relationship = models.CharField(max_length=60, blank=True)
    phone = models.CharField(max_length=40)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f'{self.name} ({self.relationship})'


class InsurancePolicy(models.Model):
    COVERAGE = [('basic', 'Básica'), ('full', 'Completa'), ('premium', 'Premium')]
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='policies')
    network = models.ForeignKey(InsuranceNetwork, on_delete=models.PROTECT, related_name='policies')
    plan = models.CharField(max_length=80, blank=True)
    member_id = models.CharField(max_length=80, blank=True)
    coverage_level = models.CharField(max_length=10, choices=COVERAGE, default='full')
    valid_until = models.DateField(null=True, blank=True)
    international = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-active', 'network__name']

    def __str__(self):
        return f'{self.network.name} · {self.plan or self.get_coverage_level_display()}'


# ============================================================
#  PROVIDER NETWORK
# ============================================================
class Provider(models.Model):
    KIND = [
        ('hospital', 'Hospital general'),
        ('clinic', 'Clínica'),
        ('trauma', 'Centro de trauma'),
        ('cardiac', 'Centro cardiovascular'),
        ('stroke', 'Centro de ACV'),
        ('pediatric', 'Hospital pediátrico'),
    ]
    name = models.CharField(max_length=140)
    kind = models.CharField(max_length=12, choices=KIND, default='hospital')
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, default='Argentina')
    lat = models.FloatField()
    lng = models.FloatField()
    phone = models.CharField(max_length=40, blank=True)

    specialties = models.ManyToManyField(Specialty, related_name='providers', blank=True)
    accepted_networks = models.ManyToManyField(InsuranceNetwork, related_name='providers', blank=True)
    languages = models.CharField(max_length=160, default='Español')

    quality_rating = models.FloatField(default=4.0, help_text='0–5')
    trauma_level = models.IntegerField(default=0, help_text='0 = ninguno, 1–3 = nivel de trauma')
    er_open = models.BooleanField(default=True, help_text='Guardia activa 24/7')
    total_beds = models.IntegerField(default=20)
    available_beds = models.IntegerField(default=5)

    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def language_list(self):
        return [s.strip() for s in self.languages.split(',') if s.strip()]

    @property
    def occupancy_pct(self):
        if not self.total_beds:
            return 0
        used = max(self.total_beds - self.available_beds, 0)
        return round(used / self.total_beds * 100)

    @property
    def availability_label(self):
        if not self.er_open:
            return 'Guardia cerrada'
        if self.available_beds <= 0:
            return 'Sin camas'
        if self.available_beds <= 2:
            return 'Saturado'
        return 'Disponible'


# ============================================================
#  EMERGENCY  (DETECT + ORCHESTRATE)
# ============================================================
class EmergencyEvent(models.Model):
    EVENT_TYPES = [
        ('cardiac', 'Paro / dolor cardíaco'),
        ('stroke', 'ACV / sospecha de ACV'),
        ('trauma', 'Trauma grave'),
        ('vehicle', 'Accidente vehicular'),
        ('fall', 'Caída'),
        ('unconscious', 'Pérdida de conciencia'),
        ('respiratory', 'Dificultad respiratoria'),
        ('allergic', 'Reacción alérgica'),
        ('other', 'Otro'),
    ]
    TRIGGERS = [
        ('sos_button', 'Botón SOS (app)'),
        ('fall_detection', 'Detección de caída (wearable)'),
        ('crash_detection', 'Detección de choque (vehículo)'),
        ('biometric', 'Sensores biométricos'),
        ('voice', 'Asistente de voz'),
        ('manual', 'Carga manual'),
    ]
    STATUS = [
        ('active', 'Orquestando'),
        ('en_route', 'Ambulancia en camino'),
        ('arrived', 'Paciente ingresado'),
        ('resolved', 'Resuelto'),
        ('cancelled', 'Cancelado'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='events')
    triggered_at = models.DateTimeField(auto_now_add=True)
    trigger_type = models.CharField(max_length=20, choices=TRIGGERS, default='sos_button')
    event_type = models.CharField(max_length=14, choices=EVENT_TYPES, default='other')
    severity = models.IntegerField(default=3, help_text='1 = crítico … 5 = leve (escala tipo ESI)')

    lat = models.FloatField()
    lng = models.FloatField()
    location_desc = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, default='Argentina')

    required_specialty = models.ForeignKey(
        Specialty, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    selected_provider = models.ForeignKey(
        Provider, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    provider_distance_km = models.FloatField(null=True, blank=True)
    ambulance_eta_min = models.IntegerField(null=True, blank=True)
    decision_score = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS, default='active')
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f'{self.get_event_type_display()} · {self.patient.full_name} · {self.triggered_at:%Y-%m-%d %H:%M}'

    SEVERITY_LABELS = {
        1: 'Crítico', 2: 'Emergencia', 3: 'Urgente', 4: 'Menor', 5: 'No urgente',
    }

    @property
    def severity_label(self):
        return self.SEVERITY_LABELS.get(self.severity, '—')

    @property
    def is_open(self):
        return self.status in ('active', 'en_route')


class EmergencyAction(models.Model):
    """One automated step of the Emergency Journey timeline."""
    STATUS = [('done', 'Completado'), ('active', 'En curso'), ('pending', 'Pendiente')]
    event = models.ForeignKey(EmergencyEvent, on_delete=models.CASCADE, related_name='actions')
    step = models.CharField(max_length=24)
    icon = models.CharField(max_length=8, blank=True)
    title = models.CharField(max_length=120)
    detail = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=8, choices=STATUS, default='done')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'


class ProviderCandidate(models.Model):
    """Transparent scoring of a provider for a given event (the "why this hospital")."""
    event = models.ForeignKey(EmergencyEvent, on_delete=models.CASCADE, related_name='candidates')
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='candidacies')
    distance_km = models.FloatField(default=0)
    eta_min = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    breakdown_json = models.TextField(blank=True, help_text='JSON con el desglose del puntaje')
    selected = models.BooleanField(default=False)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f'{self.provider.name} · {self.score:.1f}'


# ============================================================
#  TRAVEL  (PREPARE — Smart Travel Emergency Plan)
# ============================================================
class TravelPlan(models.Model):
    STATUS = [('ready', 'Listo'), ('draft', 'Borrador')]
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='travel_plans')
    destination_city = models.CharField(max_length=80)
    destination_country = models.CharField(max_length=80)
    destination_lat = models.FloatField()
    destination_lng = models.FloatField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=8, choices=STATUS, default='ready')
    risk_level = models.CharField(max_length=20, default='Moderado')
    summary = models.TextField(blank=True)
    data_json = models.TextField(blank=True, help_text='JSON: riesgos, prestadores, idioma, etc.')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.destination_city}, {self.destination_country} · {self.patient.full_name}'
