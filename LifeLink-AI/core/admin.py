from django.contrib import admin

from .models import (
    Specialty, InsuranceNetwork, PatientProfile, MedicalCondition, Allergy,
    Medication, EmergencyContact, InsurancePolicy, Provider, EmergencyEvent,
    EmergencyAction, ProviderCandidate, TravelPlan,
)


class ConditionInline(admin.TabularInline):
    model = MedicalCondition
    extra = 0


class AllergyInline(admin.TabularInline):
    model = Allergy
    extra = 0


class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 0


class ContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0


class PolicyInline(admin.TabularInline):
    model = InsurancePolicy
    extra = 0


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'blood_type', 'home_city', 'is_primary', 'readiness_score')
    list_filter = ('is_primary', 'blood_type', 'home_city')
    search_fields = ('full_name', 'phone')
    inlines = [ConditionInline, AllergyInline, MedicationInline, ContactInline, PolicyInline]


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'city', 'quality_rating', 'trauma_level',
                    'er_open', 'available_beds')
    list_filter = ('kind', 'city', 'er_open', 'trauma_level')
    search_fields = ('name', 'city')
    filter_horizontal = ('specialties', 'accepted_networks')


class ActionInline(admin.TabularInline):
    model = EmergencyAction
    extra = 0


class CandidateInline(admin.TabularInline):
    model = ProviderCandidate
    extra = 0


@admin.register(EmergencyEvent)
class EmergencyEventAdmin(admin.ModelAdmin):
    list_display = ('triggered_at', 'patient', 'event_type', 'severity_label',
                    'selected_provider', 'ambulance_eta_min', 'status')
    list_filter = ('status', 'event_type', 'trigger_type')
    date_hierarchy = 'triggered_at'
    inlines = [ActionInline, CandidateInline]


@admin.register(TravelPlan)
class TravelPlanAdmin(admin.ModelAdmin):
    list_display = ('destination_city', 'destination_country', 'patient',
                    'risk_level', 'status', 'created_at')
    list_filter = ('destination_country', 'risk_level', 'status')


admin.site.register(Specialty)
admin.site.register(InsuranceNetwork)
admin.site.site_header = 'LifeLink AI · Admin'
admin.site.site_title = 'LifeLink AI'
admin.site.index_title = 'Gestión de datos'
