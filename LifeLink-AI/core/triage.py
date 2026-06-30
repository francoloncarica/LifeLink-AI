"""
Triage rules — maps an emergency type to clinical urgency and the kind of
provider required. This is the deterministic "first read" the orchestrator
uses before scoring providers.

Severity scale (ESI-like): 1 = critical … 5 = non-urgent.
"""

# event_type -> triage profile
TRIAGE_RULES = {
    'cardiac': {
        'severity': 1, 'specialty': 'cardiology', 'needs_trauma': False,
        'preferred_kinds': ['cardiac', 'hospital'],
        'advice': 'Tiempo crítico: cada minuto cuenta para preservar músculo cardíaco.',
    },
    'stroke': {
        'severity': 1, 'specialty': 'neurology', 'needs_trauma': False,
        'preferred_kinds': ['stroke', 'hospital'],
        'advice': 'Ventana terapéutica corta ("time is brain"). Priorizar centro de ACV.',
    },
    'trauma': {
        'severity': 2, 'specialty': 'trauma', 'needs_trauma': True,
        'preferred_kinds': ['trauma', 'hospital'],
        'advice': 'Requiere centro de trauma con quirófano disponible.',
    },
    'vehicle': {
        'severity': 2, 'specialty': 'trauma', 'needs_trauma': True,
        'preferred_kinds': ['trauma', 'hospital'],
        'advice': 'Politraumatismo potencial. Activar centro de trauma de alta complejidad.',
    },
    'fall': {
        'severity': 3, 'specialty': 'trauma', 'needs_trauma': False,
        'preferred_kinds': ['hospital', 'trauma', 'clinic'],
        'advice': 'Evaluar fractura y traumatismo de cráneo según mecanismo.',
    },
    'unconscious': {
        'severity': 1, 'specialty': 'emergency', 'needs_trauma': False,
        'preferred_kinds': ['hospital'],
        'advice': 'Causa desconocida: guardia de alta complejidad con soporte vital.',
    },
    'respiratory': {
        'severity': 2, 'specialty': 'respiratory', 'needs_trauma': False,
        'preferred_kinds': ['hospital'],
        'advice': 'Posible compromiso de vía aérea. Requiere oxígeno y monitoreo.',
    },
    'allergic': {
        'severity': 2, 'specialty': 'emergency', 'needs_trauma': False,
        'preferred_kinds': ['hospital', 'clinic'],
        'advice': 'Riesgo de anafilaxia. Guardia con adrenalina y manejo de shock.',
    },
    'other': {
        'severity': 3, 'specialty': 'emergency', 'needs_trauma': False,
        'preferred_kinds': ['hospital', 'clinic'],
        'advice': 'Derivar a guardia general para evaluación inicial.',
    },
}

DEFAULT = TRIAGE_RULES['other']


def triage(event_type, patient=None):
    """
    Return a triage profile for the event, optionally adjusted by the patient's
    known risk factors.

    Returns a dict: severity, specialty, needs_trauma, preferred_kinds, advice.
    """
    rule = dict(TRIAGE_RULES.get(event_type, DEFAULT))

    # Risk modifier: a relevant high/critical pre-existing condition raises urgency.
    if patient is not None:
        try:
            high = patient.conditions.filter(severity__in=['high', 'critical'])
            if high.exists():
                keyword = {
                    'cardiac': ['cardi', 'coron', 'arritm', 'hipertens'],
                    'stroke': ['acv', 'cerebr', 'neuro', 'hipertens'],
                    'respiratory': ['epoc', 'asma', 'pulmon', 'respir'],
                }.get(event_type, [])
                for cond in high:
                    name = (cond.name or '').lower()
                    if any(k in name for k in keyword):
                        rule['severity'] = 1
                        rule['advice'] += ' Antecedente de riesgo del paciente eleva la prioridad.'
                        break
        except Exception:
            # patient may be unsaved / detached — triage still works without it.
            pass

    return rule
