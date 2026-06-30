from .models import PatientProfile


def nav(request):
    """Globals available to every template (brand + active patient)."""
    return {
        'app_name': 'LifeLink AI',
        'app_tagline': 'Every patient. Everywhere. Instantly.',
        'app_version': '0.1',
        'has_patient': PatientProfile.objects.exists(),
    }
