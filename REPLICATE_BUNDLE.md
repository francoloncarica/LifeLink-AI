# 🚑 LifeLink AI — Prompt de recreación completa


## Misión

Sos un agente de codificación experto. Recreá **exactamente** la app **LifeLink AI** en una
carpeta nueva `LifeLink-AI/`. Creá **cada archivo** en la ruta indicada, con el contenido
**EXACTO** que está entre las marcas `<!-- BEGIN FILE: ruta -->` y `<!-- END FILE: ruta -->`
(todo lo que está dentro del bloque de código, sin las marcas ni el cerco de backticks).

Reglas estrictas:
- Copiá el contenido **literal**. No edites, no "mejores", no agregues comentarios.
- Las rutas usan `/`. En Windows convertí a `\` automáticamente.
- No crees archivos que no estén listados. No toques nada fuera de `LifeLink-AI/`.
- Cuando termines de crear todos los archivos, seguí los **pasos de setup**.

## Qué es LifeLink AI

Plataforma **local** (MVP) de **orquestación de emergencias médicas**. Tres pilares:
- **Preparar**: perfil del paciente (condiciones, alergias, medicación, contactos, cobertura) + planes de viaje preventivos.
- **Detectar**: activación por botón SOS, caída (wearable), choque, biométrico o voz.
- **Orquestar**: el *Emergency Orchestrator* hace triage, puntúa los prestadores con una rúbrica
  ponderada y explicable (cercanía/ETA, especialidad, cobertura, calidad, disponibilidad, trauma,
  idioma) y dispara un timeline automático de acciones.

**Stack**: Django 5.2 + SQLite + Leaflet (mapas vía CDN, sin API key). UI estilo Apple.
Instalable como **PWA** (se agrega al inicio del iPhone y abre a pantalla completa).

## Pasos de setup (después de crear TODOS los archivos)

Windows (PowerShell):

```powershell
cd LifeLink-AI
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt Pillow
.\.venv\Scripts\python.exe gen_icons.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

macOS / Linux:

```bash
cd LifeLink-AI
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt Pillow
python gen_icons.py
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000
```

Abrí http://127.0.0.1:8000/ en la compu. Admin opcional: `python manage.py createsuperuser`.

## Mostrarlo en un iPhone (misma red Wi-Fi)

1. Averiguá la IP local de la PC: `ipconfig` (Windows) o `ifconfig` / `ip a` (mac/Linux). Ej: `192.168.0.20`.
2. Corré el server permitiendo esa IP:
   - Windows: `$env:LIFELINK_DEMO_HOST="192.168.0.20"; .\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000`
   - mac/Linux: `LIFELINK_DEMO_HOST=192.168.0.20 python manage.py runserver 0.0.0.0:8000`
   (Podés usar `*` en vez de la IP para permitir cualquier host.)
3. En el iPhone (mismo Wi-Fi) abrí `http://192.168.0.20:8000/` en **Safari**.
4. **Compartir → Agregar a inicio** → se instala como app a pantalla completa. 🎉
   El botón SOS y los mapas funcionan (el CSRF ya contempla la IP local).

> Para un link público (mostrar desde cualquier lado) ya están `render.yaml` + `build.sh`:
> subí el repo a GitHub y deploya en render.com con *New → Blueprint*.

## Probar el demo

- En el **Dashboard**, panel *Simular emergencia*: elegí tipo (ej. Paro cardíaco), detección y
  ubicación (chips o click en el mapa) → **Activar SOS** → mirá el *Emergency Journey* y el
  desglose "Por qué este prestador". Probá el escenario **Miami** para ver la traducción médica.
- *Planes de viaje*: generá un plan para Madrid, São Paulo, etc.

> Nota: los datos clínicos del paciente demo (Martín Gómez) son **ficticios**.


## Mapa de archivos (37 archivos)

- `requirements.txt`
- `manage.py`
- `gen_icons.py`
- `build.sh`
- `render.yaml`
- `.gitignore`
- `README.md`
- `lifelink/__init__.py`
- `lifelink/settings.py`
- `lifelink/urls.py`
- `lifelink/asgi.py`
- `lifelink/wsgi.py`
- `core/__init__.py`
- `core/apps.py`
- `core/models.py`
- `core/geo.py`
- `core/triage.py`
- `core/orchestrator.py`
- `core/travel.py`
- `core/admin.py`
- `core/context_processors.py`
- `core/urls.py`
- `core/views.py`
- `core/migrations/__init__.py`
- `core/migrations/0001_initial.py`
- `core/management/__init__.py`
- `core/management/commands/__init__.py`
- `core/management/commands/seed_demo.py`
- `core/templates/core/base.html`
- `core/templates/core/dashboard.html`
- `core/templates/core/emergency_detail.html`
- `core/templates/core/emergencies.html`
- `core/templates/core/patient.html`
- `core/templates/core/providers.html`
- `core/templates/core/travel.html`
- `core/templates/core/travel_detail.html`
- `core/static/core/manifest.webmanifest`

---


<!-- BEGIN FILE: requirements.txt -->
```text
Django>=5.0,<6.0
gunicorn>=21.0
whitenoise>=6.0
```
<!-- END FILE: requirements.txt -->


<!-- BEGIN FILE: manage.py -->
```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```
<!-- END FILE: manage.py -->


<!-- BEGIN FILE: gen_icons.py -->
```python
"""Generate LifeLink AI PWA icons (run once after setup). Requires Pillow.

    python gen_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / 'core' / 'static' / 'core'
OUT.mkdir(parents=True, exist_ok=True)

TEAL = (10, 185, 194)
BLUE = (10, 132, 255)
# Heartbeat pulse in a 24x24 viewBox (same path as the in-app logo).
PULSE = [(3, 12), (7, 12), (9, 17), (13, 4), (15, 12), (21, 12)]


def render(size):
    img = Image.new('RGB', (size, size), BLUE)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        row = (
            int(TEAL[0] + (BLUE[0] - TEAL[0]) * t),
            int(TEAL[1] + (BLUE[1] - TEAL[1]) * t),
            int(TEAL[2] + (BLUE[2] - TEAL[2]) * t),
        )
        for x in range(size):
            px[x, y] = row

    d = ImageDraw.Draw(img)
    pad = size * 0.20
    scale = (size - 2 * pad) / 24.0
    pts = [(pad + x * scale, pad + y * scale) for x, y in PULSE]
    w = max(2, int(size * 0.055))
    d.line(pts, fill=(255, 255, 255), width=w, joint='curve')
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=(255, 255, 255))
    return img


base = render(512)
base.save(OUT / 'icon-512.png')
base.resize((192, 192), Image.LANCZOS).save(OUT / 'icon-192.png')
base.resize((180, 180), Image.LANCZOS).save(OUT / 'apple-touch-icon.png')
print('PWA icons generated in', OUT)
```
<!-- END FILE: gen_icons.py -->


<!-- BEGIN FILE: build.sh -->
```bash
#!/usr/bin/env bash
# Render build script for LifeLink AI.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_demo
```
<!-- END FILE: build.sh -->


<!-- BEGIN FILE: render.yaml -->
```yaml
# Render.com blueprint for LifeLink AI.
# Deploy: push to GitHub → Render → New → Blueprint → pick this repo.
services:
  - type: web
    name: lifelink-ai
    runtime: python
    plan: free
    buildCommand: "bash ./build.sh"
    startCommand: "gunicorn lifelink.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: "3.12.7"
      - key: DEBUG
        value: "False"
      - key: SECRET_KEY
        generateValue: true
```
<!-- END FILE: render.yaml -->


<!-- BEGIN FILE: .gitignore -->
```text
# Byte-compiled / optimized / virtualenv
__pycache__/
*.py[cod]
.venv/
venv/

# Django
db.sqlite3
db.sqlite3-journal
staticfiles/
*.log

# Local / editor
.DS_Store
_smoke.py
.vscode/
```
<!-- END FILE: .gitignore -->


<!-- BEGIN FILE: README.md -->
````markdown
# 🚑 LifeLink AI

> **Every patient. Everywhere. Instantly.** — The Intelligent Emergency Response Network.

Prototipo local (MVP) de la plataforma **LifeLink AI**: una capa de inteligencia que
**orquesta automáticamente** la respuesta ante una emergencia médica, desde el primer
segundo del evento hasta el ingreso al prestador de salud óptimo.

Construido con **Django + SQLite + Leaflet**, corre 100 % local y sin claves de API.

---

## Los 3 pilares

| Pilar | Qué hace | Dónde está |
|-------|----------|-----------|
| 🟢 **Preparar** | Perfil "Always Ready" del paciente (condiciones, alergias, medicación, contactos, cobertura) + planes de viaje preventivos. | `Paciente`, `Planes de viaje` |
| 🟡 **Detectar** | Activación por botón SOS, caída (wearable), choque vehicular, biométrico o voz. | Panel **SOS** del Dashboard |
| 🔴 **Orquestar** | El **Emergency Orchestrator**: triage, scoring de prestadores y journey automático en segundos. | `core/orchestrator.py` |

---

## El corazón: el Emergency Orchestrator

Ante un evento (paciente + tipo + ubicación GPS) el motor:

1. **Triage** (`core/triage.py`): determina urgencia (escala tipo ESI 1–5) y la especialidad
   requerida, ajustando por antecedentes del paciente.
2. **Scoring transparente** (`core/orchestrator.py`): puntúa cada prestador con una rúbrica
   ponderada y **explicable** (se ve el desglose en la UI):

   | Dimensión | Peso | Criterio |
   |-----------|-----:|----------|
   | Cercanía | 34 | distancia de ruta → ETA de ambulancia |
   | Especialidad | 22 | ¿tiene la especialidad que el evento requiere? |
   | Cobertura | 18 | ¿el prestador acepta la obra social del paciente? |
   | Calidad clínica | 12 | rating 0–5 |
   | Disponibilidad | 9 | guardia abierta + camas libres |
   | Trauma | 5 | nivel de centro de trauma (si aplica) |
   | Idioma | +3 | bonus situacional (relevante en el exterior) |

3. **Journey automático**: genera el timeline de acciones (geolocalización ✓, triage ✓,
   cobertura ✓, prestador ✓, ambulancia 🚑, historia clínica 📋, familia 👨‍👩‍👧,
   aseguradora 📞, traducción 🌐, monitoreo 📡).

Es **determinístico y local** — modela exactamente cómo decidiría la capa de IA en producción,
pero sin depender de servicios externos.

---

## Setup

```powershell
# 1. Entorno + dependencias
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Base de datos + datos demo
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo

# 3. Server
.\.venv\Scripts\python.exe manage.py runserver
```

Abrí **http://127.0.0.1:8000/**

> Admin opcional: `python manage.py createsuperuser` → http://127.0.0.1:8000/admin/

---

## Cómo probarlo (demo flow)

1. **Dashboard** → panel **Simular emergencia**: elegí tipo (ej. *Paro cardíaco*), la
   detección (*botón SOS*) y la ubicación (chips `🏠 En casa`, `🏙️ Microcentro`,
   `🛣️ Autopista`, `✈️ Miami`, o click en el mapa).
2. **🚨 Activar SOS** → el orquestador elige el prestador óptimo y abrís el **Emergency Journey**.
3. Mirá el **timeline** de acciones automáticas y la sección **"Por qué este prestador"**
   con el desglose del puntaje contra los demás candidatos.
4. Probá el escenario **✈️ Miami** para ver la **traducción médica** activarse en el exterior.
5. **Planes de viaje** → generá un Emergency Readiness Plan para *Madrid*, *São Paulo*, etc.

---

## Estructura

```
LifeLink-AI/
├─ manage.py
├─ requirements.txt
├─ lifelink/            # configuración del proyecto
│  ├─ settings.py
│  └─ urls.py
└─ core/                # app principal
   ├─ models.py         # paciente, prestadores, emergencias, viajes
   ├─ triage.py         # reglas de urgencia por tipo de evento
   ├─ geo.py            # distancia haversine + ETA
   ├─ orchestrator.py   # 🧠 motor de decisión + timeline
   ├─ travel.py         # generador de Smart Travel Plans
   ├─ views.py / urls.py
   ├─ admin.py          # edición completa de datos
   ├─ templates/core/   # UI estilo Apple + mapas Leaflet
   └─ management/commands/seed_demo.py
```

---

## Roadmap (del business plan)

- [x] **Fase 1 (MVP)** — orquestación con geolocalización, triage y scoring explicable + viajero internacional.
- [ ] **Fase 2** — integración real con aseguradoras, hospitales y ambulancias (APIs).
- [ ] **Fase 3** — wearables / sensores biométricos para activación automática real.
- [ ] **Fase 4** — plataforma abierta (aerolíneas, hoteles, gobiernos) vía API.
- [ ] **Fase 5** — capacidades predictivas (detectar el evento antes de que ocurra).

---

## Notas

- **Datos clínicos = ficticios**, solo para demo. Editá el paciente en el admin con datos reales.
- **Seguridad**: prototipo local (`DEBUG=True`, sin auth). Antes de exponerlo a una red:
  `DEBUG=False`, restringir `ALLOWED_HOSTS`, rotar `SECRET_KEY` y agregar autenticación.
- Re-correr `seed_demo` **borra** pacientes/prestadores/eventos/planes y los recrea.
````
<!-- END FILE: README.md -->


<!-- BEGIN FILE: lifelink/__init__.py -->
```python

```
<!-- END FILE: lifelink/__init__.py -->


<!-- BEGIN FILE: lifelink/settings.py -->
```python
"""
Django settings for LifeLink AI.

Local prototype — single process, SQLite. NOT hardened for network deployment.
(If this ever goes online: restrict ALLOWED_HOSTS, set DEBUG=False, rotate SECRET_KEY,
 add real authentication — see README security note.)
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Local-only prototype key. Override with the SECRET_KEY env var in production.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-lifelink-local-dev-only-do-not-deploy-1a2b3c4d5e',
)

# DEBUG defaults to True for local dev; set DEBUG=False via env var in production.
DEBUG = os.environ.get('DEBUG', 'True').lower() not in ('false', '0', 'no')

# Local prototype: localhost + common demo tunnels (VS Code dev tunnels, ngrok,
# cloudflared). For a same-Wi-Fi demo, export LIFELINK_DEMO_HOST=<laptop-LAN-IP>.
ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '[::1]',
    '.ngrok-free.app', '.ngrok.io', '.devtunnels.ms', '.trycloudflare.com',
    '.onrender.com',
]

# Django requires the HTTPS origin to be trusted for cross-origin POST (the SOS
# and travel forms POST), so tunnels / cloud hosts work out of the box.
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app', 'https://*.ngrok.io',
    'https://*.devtunnels.ms', 'https://*.trycloudflare.com',
    'https://*.onrender.com',
]

_demo_host = os.environ.get('LIFELINK_DEMO_HOST')  # e.g. 192.168.1.50 for LAN demos
if _demo_host:
    ALLOWED_HOSTS.append(_demo_host)
    CSRF_TRUSTED_ORIGINS += [f'http://{_demo_host}:8000', f'https://{_demo_host}']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lifelink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'lifelink.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise serves static files in production. CompressedStaticFilesStorage
# (no manifest hashing) keeps original filenames so the PWA manifest's hardcoded
# /static/core/icon-*.png paths keep working.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/logout redirect (admin reuse only for this prototype)
LOGIN_REDIRECT_URL = '/'
```
<!-- END FILE: lifelink/settings.py -->


<!-- BEGIN FILE: lifelink/urls.py -->
```python
"""URL configuration for LifeLink AI."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```
<!-- END FILE: lifelink/urls.py -->


<!-- BEGIN FILE: lifelink/asgi.py -->
```python
"""ASGI config for LifeLink AI."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')

application = get_asgi_application()
```
<!-- END FILE: lifelink/asgi.py -->


<!-- BEGIN FILE: lifelink/wsgi.py -->
```python
"""WSGI config for LifeLink AI."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')

application = get_wsgi_application()
```
<!-- END FILE: lifelink/wsgi.py -->


<!-- BEGIN FILE: core/__init__.py -->
```python

```
<!-- END FILE: core/__init__.py -->


<!-- BEGIN FILE: core/apps.py -->
```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'LifeLink AI'
```
<!-- END FILE: core/apps.py -->


<!-- BEGIN FILE: core/models.py -->
```python
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
```
<!-- END FILE: core/models.py -->


<!-- BEGIN FILE: core/geo.py -->
```python
"""Geospatial helpers — distance + travel-time estimates (no external API)."""
import math

# Average ambulance speed in dense urban traffic (km/h). Used to turn
# straight-line distance into a rough ETA. Intentionally conservative.
URBAN_AMBULANCE_KMH = 38.0
# Roads are never straight: inflate haversine distance to approximate real driving.
ROAD_FACTOR = 1.35
# Fixed dispatch + mobilization overhead (minutes) before the ambulance moves.
DISPATCH_OVERHEAD_MIN = 2.0


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2)
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def road_distance_km(lat1, lng1, lat2, lng2):
    """Approximate driving distance (haversine inflated by a road factor)."""
    return haversine_km(lat1, lng1, lat2, lng2) * ROAD_FACTOR


def eta_minutes(distance_km, kmh=URBAN_AMBULANCE_KMH):
    """Rough ambulance ETA in minutes for a given road distance."""
    if kmh <= 0:
        return None
    travel = distance_km / kmh * 60.0
    return int(round(travel + DISPATCH_OVERHEAD_MIN))
```
<!-- END FILE: core/geo.py -->


<!-- BEGIN FILE: core/triage.py -->
```python
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
```
<!-- END FILE: core/triage.py -->


<!-- BEGIN FILE: core/orchestrator.py -->
```python
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
```
<!-- END FILE: core/orchestrator.py -->


<!-- BEGIN FILE: core/travel.py -->
```python
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
```
<!-- END FILE: core/travel.py -->


<!-- BEGIN FILE: core/admin.py -->
```python
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
```
<!-- END FILE: core/admin.py -->


<!-- BEGIN FILE: core/context_processors.py -->
```python
from .models import PatientProfile


def nav(request):
    """Globals available to every template (brand + active patient)."""
    return {
        'app_name': 'LifeLink AI',
        'app_tagline': 'Every patient. Everywhere. Instantly.',
        'app_version': '0.1',
        'has_patient': PatientProfile.objects.exists(),
    }
```
<!-- END FILE: core/context_processors.py -->


<!-- BEGIN FILE: core/urls.py -->
```python
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Emergency / orchestration
    path('sos/', views.sos_trigger, name='sos'),
    path('emergencies/', views.emergencies_list, name='emergencies'),
    path('emergency/<int:pk>/', views.emergency_detail, name='emergency_detail'),
    path('emergency/<int:pk>/resolve/', views.emergency_resolve, name='emergency_resolve'),

    # Patient
    path('patient/', views.patient_detail, name='patient'),
    path('patient/<int:pk>/', views.patient_detail, name='patient_detail'),

    # Providers
    path('providers/', views.providers_list, name='providers'),

    # Travel plans
    path('travel/', views.travel_list, name='travel'),
    path('travel/create/', views.travel_create, name='travel_create'),
    path('travel/<int:pk>/', views.travel_detail, name='travel_detail'),
]
```
<!-- END FILE: core/urls.py -->


<!-- BEGIN FILE: core/views.py -->
```python
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
```
<!-- END FILE: core/views.py -->


<!-- BEGIN FILE: core/migrations/__init__.py -->
```python

```
<!-- END FILE: core/migrations/__init__.py -->


<!-- BEGIN FILE: core/migrations/0001_initial.py -->
```python
# Generated by Django 5.2.15 on 2026-06-29 19:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('triggered_at', models.DateTimeField(auto_now_add=True)),
                ('trigger_type', models.CharField(choices=[('sos_button', 'Botón SOS (app)'), ('fall_detection', 'Detección de caída (wearable)'), ('crash_detection', 'Detección de choque (vehículo)'), ('biometric', 'Sensores biométricos'), ('voice', 'Asistente de voz'), ('manual', 'Carga manual')], default='sos_button', max_length=20)),
                ('event_type', models.CharField(choices=[('cardiac', 'Paro / dolor cardíaco'), ('stroke', 'ACV / sospecha de ACV'), ('trauma', 'Trauma grave'), ('vehicle', 'Accidente vehicular'), ('fall', 'Caída'), ('unconscious', 'Pérdida de conciencia'), ('respiratory', 'Dificultad respiratoria'), ('allergic', 'Reacción alérgica'), ('other', 'Otro')], default='other', max_length=14)),
                ('severity', models.IntegerField(default=3, help_text='1 = crítico … 5 = leve (escala tipo ESI)')),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('location_desc', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(blank=True, max_length=80)),
                ('country', models.CharField(default='Argentina', max_length=80)),
                ('provider_distance_km', models.FloatField(blank=True, null=True)),
                ('ambulance_eta_min', models.IntegerField(blank=True, null=True)),
                ('decision_score', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Orquestando'), ('en_route', 'Ambulancia en camino'), ('arrived', 'Paciente ingresado'), ('resolved', 'Resuelto'), ('cancelled', 'Cancelado')], default='active', max_length=10)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-triggered_at'],
            },
        ),
        migrations.CreateModel(
            name='InsuranceNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
                ('country', models.CharField(default='Argentina', max_length=60)),
                ('international', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=120)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('blood_type', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'), ('?', 'Desconocido')], default='?', max_length=3)),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('languages', models.CharField(default='Español', help_text='Idiomas separados por coma', max_length=120)),
                ('home_address', models.CharField(blank=True, max_length=200)),
                ('home_city', models.CharField(blank=True, max_length=80)),
                ('home_country', models.CharField(default='Argentina', max_length=80)),
                ('home_lat', models.FloatField(default=-34.6037)),
                ('home_lng', models.FloatField(default=-58.3816)),
                ('notes', models.TextField(blank=True)),
                ('is_primary', models.BooleanField(default=False, help_text='Perfil principal mostrado por defecto')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-is_primary', 'full_name'],
            },
        ),
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=40, unique=True)),
                ('name', models.CharField(max_length=80)),
                ('icon', models.CharField(blank=True, max_length=8)),
            ],
            options={
                'verbose_name_plural': 'specialties',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmergencyAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.CharField(max_length=24)),
                ('icon', models.CharField(blank=True, max_length=8)),
                ('title', models.CharField(max_length=120)),
                ('detail', models.CharField(blank=True, max_length=300)),
                ('status', models.CharField(choices=[('done', 'Completado'), ('active', 'En curso'), ('pending', 'Pendiente')], default='done', max_length=8)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='core.emergencyevent')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('dose', models.CharField(blank=True, max_length=80)),
                ('frequency', models.CharField(blank=True, max_length=80)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='core.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='MedicalCondition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('severity', models.CharField(choices=[('low', 'Leve'), ('medium', 'Moderada'), ('high', 'Alta'), ('critical', 'Crítica')], default='medium', max_length=10)),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='core.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='InsurancePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan', models.CharField(blank=True, max_length=80)),
                ('member_id', models.CharField(blank=True, max_length=80)),
                ('coverage_level', models.CharField(choices=[('basic', 'Básica'), ('full', 'Completa'), ('premium', 'Premium')], default='full', max_length=10)),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('international', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='policies', to='core.insurancenetwork')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='policies', to='core.patientprofile')),
            ],
            options={
                'ordering': ['-active', 'network__name'],
            },
        ),
        migrations.AddField(
            model_name='emergencyevent',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.patientprofile'),
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('relationship', models.CharField(blank=True, max_length=60)),
                ('phone', models.CharField(max_length=40)),
                ('is_primary', models.BooleanField(default=False)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='core.patientprofile')),
            ],
            options={
                'ordering': ['-is_primary', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Allergy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('substance', models.CharField(max_length=120)),
                ('reaction', models.CharField(blank=True, max_length=200)),
                ('severity', models.CharField(choices=[('low', 'Leve'), ('medium', 'Moderada'), ('high', 'Alta'), ('anaphylaxis', 'Anafilaxia')], default='medium', max_length=12)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allergies', to='core.patientprofile')),
            ],
            options={
                'verbose_name_plural': 'allergies',
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140)),
                ('kind', models.CharField(choices=[('hospital', 'Hospital general'), ('clinic', 'Clínica'), ('trauma', 'Centro de trauma'), ('cardiac', 'Centro cardiovascular'), ('stroke', 'Centro de ACV'), ('pediatric', 'Hospital pediátrico')], default='hospital', max_length=12)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(blank=True, max_length=80)),
                ('country', models.CharField(default='Argentina', max_length=80)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('languages', models.CharField(default='Español', max_length=160)),
                ('quality_rating', models.FloatField(default=4.0, help_text='0–5')),
                ('trauma_level', models.IntegerField(default=0, help_text='0 = ninguno, 1–3 = nivel de trauma')),
                ('er_open', models.BooleanField(default=True, help_text='Guardia activa 24/7')),
                ('total_beds', models.IntegerField(default=20)),
                ('available_beds', models.IntegerField(default=5)),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('accepted_networks', models.ManyToManyField(blank=True, related_name='providers', to='core.insurancenetwork')),
                ('specialties', models.ManyToManyField(blank=True, related_name='providers', to='core.specialty')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='emergencyevent',
            name='selected_provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='core.provider'),
        ),
        migrations.CreateModel(
            name='ProviderCandidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance_km', models.FloatField(default=0)),
                ('eta_min', models.IntegerField(default=0)),
                ('score', models.FloatField(default=0)),
                ('breakdown_json', models.TextField(blank=True, help_text='JSON con el desglose del puntaje')),
                ('selected', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='core.emergencyevent')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidacies', to='core.provider')),
            ],
            options={
                'ordering': ['-score'],
            },
        ),
        migrations.AddField(
            model_name='emergencyevent',
            name='required_specialty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='core.specialty'),
        ),
        migrations.CreateModel(
            name='TravelPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination_city', models.CharField(max_length=80)),
                ('destination_country', models.CharField(max_length=80)),
                ('destination_lat', models.FloatField()),
                ('destination_lng', models.FloatField()),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ready', 'Listo'), ('draft', 'Borrador')], default='ready', max_length=8)),
                ('risk_level', models.CharField(default='Moderado', max_length=20)),
                ('summary', models.TextField(blank=True)),
                ('data_json', models.TextField(blank=True, help_text='JSON: riesgos, prestadores, idioma, etc.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travel_plans', to='core.patientprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
```
<!-- END FILE: core/migrations/0001_initial.py -->


<!-- BEGIN FILE: core/management/__init__.py -->
```python

```
<!-- END FILE: core/management/__init__.py -->


<!-- BEGIN FILE: core/management/commands/__init__.py -->
```python

```
<!-- END FILE: core/management/commands/__init__.py -->


<!-- BEGIN FILE: core/management/commands/seed_demo.py -->
```python
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

from core.models import (
    Specialty, InsuranceNetwork, PatientProfile, MedicalCondition, Allergy,
    Medication, EmergencyContact, InsurancePolicy, Provider, EmergencyEvent,
    TravelPlan,
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
    ('Fundación Favaloro', 'cardiac', 'Av. Belgrano 1746', 'Buenos Aires', 'Argentina',
     -34.6113, -58.3920, '+54 11 4378-1200', 4.9, 0, True, 90, 6,
     ['cardiology', 'emergency'], ['OSDE', 'Swiss Medical'], 'Español, Inglés'),
    ('FLENI', 'stroke', 'Montañeses 2325', 'Buenos Aires', 'Argentina',
     -34.5547, -58.4560, '+54 11 5777-3200', 4.9, 0, True, 80, 5,
     ['neurology', 'emergency'], ['OSDE', 'Swiss Medical', 'Galeno'], 'Español, Inglés'),
    ('Hospital Alemán', 'hospital', 'Av. Pueyrredón 1640', 'Buenos Aires', 'Argentina',
     -34.5896, -58.4022, '+54 11 4827-7000', 4.7, 1, True, 150, 4,
     ['emergency', 'cardiology', 'trauma', 'respiratory'],
     ['OSDE', 'Swiss Medical', 'Medifé'], 'Español, Alemán, Inglés'),
    ('Hospital Británico', 'hospital', 'Perdriel 74', 'Buenos Aires', 'Argentina',
     -34.6286, -58.3838, '+54 11 4309-6400', 4.5, 1, True, 130, 2,
     ['emergency', 'trauma', 'respiratory'], ['Swiss Medical', 'Galeno', 'Medifé'], 'Español, Inglés'),
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

        self.stdout.write(self.style.SUCCESS(
            f'OK · {Provider.objects.count()} prestadores, '
            f'{Specialty.objects.count()} especialidades, '
            f'{InsuranceNetwork.objects.count()} obras sociales, paciente "{patient.full_name}".'
        ))
        self.stdout.write('Listo. Iniciá el server con: python manage.py runserver')
```
<!-- END FILE: core/management/commands/seed_demo.py -->


<!-- BEGIN FILE: core/templates/core/base.html -->
```html
{% load humanize static %}<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>{% block title %}{{ app_name }}{% endblock %}</title>

  <!-- PWA / installable on iOS & Android -->
  <link rel="manifest" href="{% static 'core/manifest.webmanifest' %}">
  <meta name="theme-color" content="#0a84ff">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="LifeLink AI">
  <link rel="apple-touch-icon" href="{% static 'core/apple-touch-icon.png' %}">
  <link rel="icon" type="image/png" sizes="192x192" href="{% static 'core/icon-192.png' %}">

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    :root{
      --bg:#fafafa; --sidebar:#ffffff; --surface:#ffffff; --surface-2:#f5f5f7; --surface-hover:#efeff1;
      --border:#ececee; --border-strong:#dcdce0; --divider:#f1f1f3;
      --text:#0a0a0a; --text-2:#3a3a3c; --muted:#7e7e82; --muted-2:#a8a8ad;
      --accent:#0a84ff; --accent-soft:rgba(10,132,255,.10); --accent-hover:rgba(10,132,255,.06);
      --good:#30d158; --bad:#ff453a; --warn:#ff9f0a; --emergency:#ff3b30; --teal:#0ab9c2;
      --radius-xl:18px; --radius:12px; --radius-sm:8px;
      --shadow-xs:0 1px 2px rgba(0,0,0,.02);
      --shadow-sm:0 1px 2px rgba(0,0,0,.025), 0 0 0 1px rgba(0,0,0,.02);
      --shadow:0 2px 8px rgba(0,0,0,.04);
      --sb-w:236px; --pad-x:40px;
    }
    *{box-sizing:border-box;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
    html,body{margin:0;padding:0;background:var(--bg);color:var(--text);
      font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Inter","Helvetica Neue",Helvetica,Arial,sans-serif;
      font-size:14.5px;line-height:1.55;letter-spacing:-0.011em}
    a{color:var(--accent);text-decoration:none;transition:opacity .15s}
    a:hover{opacity:.75}

    .app{display:flex;min-height:100vh}

    /* SIDEBAR */
    .sb{width:var(--sb-w);flex-shrink:0;background:var(--sidebar);border-right:1px solid var(--border);
      position:sticky;top:0;height:100vh;display:flex;flex-direction:column;padding:20px 12px;z-index:30}
    .sb-brand{display:flex;align-items:center;gap:11px;padding:8px 12px 18px}
    .sb-brand-logo{width:30px;height:30px;border-radius:9px;
      background:linear-gradient(135deg,var(--teal),var(--accent));
      display:flex;align-items:center;justify-content:center;color:#fff;
      box-shadow:0 4px 12px rgba(10,132,255,.28)}
    .sb-brand-logo svg{width:18px;height:18px;stroke:#fff;stroke-width:2.4;fill:none;stroke-linecap:round;stroke-linejoin:round}
    .sb-brand-name{font-weight:600;font-size:15px;letter-spacing:-0.02em}
    .sb-brand-name small{display:block;font-size:10px;color:var(--muted-2);font-weight:500;letter-spacing:0}
    .sb-section{font-size:11px;color:var(--muted-2);font-weight:600;text-transform:uppercase;letter-spacing:.08em;padding:14px 12px 6px}
    .sb-nav{display:flex;flex-direction:column;gap:1px}
    .sb-nav a{display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:8px;
      color:var(--text-2);font-size:13.5px;font-weight:500;transition:background .12s,color .12s}
    .sb-nav a svg{width:16px;height:16px;flex-shrink:0;stroke:currentColor;stroke-width:1.8;fill:none;stroke-linecap:round;stroke-linejoin:round;opacity:.7}
    .sb-nav a:hover{background:var(--surface-2);color:var(--text)}
    .sb-nav a.active{background:var(--text);color:#fff}
    .sb-nav a.active svg{opacity:1}
    .sb-sos{margin:10px 12px 0}
    .sb-sos a{display:flex;align-items:center;justify-content:center;gap:8px;
      background:linear-gradient(135deg,#ff3b30,#ff375f);color:#fff;font-weight:600;font-size:13.5px;
      padding:11px;border-radius:12px;box-shadow:0 6px 16px rgba(255,59,48,.32)}
    .sb-sos a:hover{opacity:.92}
    .sb-foot{margin-top:auto;padding:10px 12px;border-top:1px solid var(--border);
      font-size:11.5px;color:var(--muted-2);display:flex;justify-content:space-between;align-items:center}
    .sb-foot a{color:var(--muted);font-size:11.5px;font-weight:500}

    /* MAIN */
    .content{flex:1;min-width:0;padding:32px var(--pad-x) 80px}
    h1.page-title{font-size:38px;font-weight:600;letter-spacing:-0.03em;margin:0 0 8px;line-height:1.05}
    .page-sub{color:var(--muted);font-size:16px;font-weight:400;margin:0 0 36px;max-width:780px;line-height:1.5}
    .page-head{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;flex-wrap:wrap;margin-bottom:36px}
    .page-head .page-sub{margin-bottom:0}
    .page-actions{display:flex;gap:8px;align-items:center;flex-shrink:0;padding-top:6px}
    section{margin-bottom:48px}
    section>h2{font-size:21px;font-weight:600;letter-spacing:-0.022em;margin:0 0 6px}
    section>.sec-sub{color:var(--muted);font-size:14px;margin:0 0 22px;max-width:780px}

    /* KPIs */
    .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;
      background:var(--surface);border-radius:var(--radius-xl);padding:6px;box-shadow:var(--shadow-sm)}
    .kpi{padding:20px 22px;border-radius:var(--radius);transition:background .15s;position:relative}
    .kpi+.kpi::before{content:"";position:absolute;left:0;top:20%;bottom:20%;width:1px;background:var(--divider)}
    .kpi:hover{background:var(--surface-2)}
    .kpi .label{font-size:12px;color:var(--muted);font-weight:500}
    .kpi .val{font-size:27px;font-weight:600;letter-spacing:-0.028em;margin-top:6px;font-variant-numeric:tabular-nums;line-height:1.1}
    .kpi .sub{font-size:11.5px;color:var(--muted-2);margin-top:4px}
    .kpi.pos .val{color:var(--good)} .kpi.neg .val{color:var(--bad)} .kpi.warn .val{color:var(--warn)}

    /* CARDS */
    .card,.card-flat{background:var(--surface);border-radius:var(--radius-xl);padding:24px;box-shadow:var(--shadow-sm)}
    .card-flat{box-shadow:none;background:var(--surface-2)}
    .grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:16px}
    .grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}

    /* MAP */
    .map{height:340px;border-radius:var(--radius-xl);overflow:hidden;box-shadow:var(--shadow-sm);z-index:1}
    .map.tall{height:460px}
    .leaflet-container{font-family:inherit}

    /* BADGES / PILLS */
    .pill{display:inline-block;padding:2px 10px;border-radius:999px;background:var(--surface-2);font-size:11.5px;color:var(--text-2);font-weight:500}
    .badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:999px;font-size:11.5px;font-weight:600}
    .badge-good{background:rgba(48,209,88,.14);color:#1d8a3a}
    .badge-bad{background:rgba(255,59,48,.14);color:#c4291f}
    .badge-warn{background:rgba(255,159,10,.16);color:#9a6200}
    .badge-info{background:var(--accent-soft);color:var(--accent)}
    .sev{display:inline-flex;align-items:center;gap:6px;padding:3px 11px;border-radius:999px;font-size:11.5px;font-weight:600}
    .sev::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
    .sev-1{background:rgba(255,59,48,.14);color:#d32117}
    .sev-2{background:rgba(255,99,10,.15);color:#c4490a}
    .sev-3{background:rgba(255,159,10,.16);color:#9a6200}
    .sev-4{background:rgba(10,132,255,.12);color:#0a6fd6}
    .sev-5{background:var(--surface-2);color:var(--muted)}

    /* BUTTONS */
    button,.btn{background:var(--text);color:#fff;border:none;border-radius:999px;padding:8px 17px;font-size:13px;
      font-weight:500;cursor:pointer;font-family:inherit;transition:opacity .15s,transform .1s;display:inline-flex;align-items:center;gap:7px}
    button:hover,.btn:hover{opacity:.85;color:#fff}
    button:active,.btn:active{transform:scale(.97)}
    .btn-secondary{background:var(--surface-2);color:var(--text)}
    .btn-secondary:hover{background:var(--surface-hover);color:var(--text);opacity:1}
    .btn-emergency{background:linear-gradient(135deg,#ff3b30,#ff375f);box-shadow:0 6px 16px rgba(255,59,48,.3)}
    .btn-emergency:hover{opacity:.92}

    /* FORMS */
    select,input[type=text],input[type=search],input[type=number],input[type=date]{
      appearance:none;-webkit-appearance:none;background:var(--surface-2);color:var(--text);border:none;outline:none;
      border-radius:var(--radius-sm);padding:9px 13px;font-size:13.5px;font-weight:500;font-family:inherit;transition:background .15s}
    select{padding-right:28px;cursor:pointer;
      background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 12 12'><path fill='%237e7e82' d='M6 8L2 4h8z'/></svg>");
      background-repeat:no-repeat;background-position:right 10px center}
    select:hover,input:hover{background:var(--surface-hover)}
    select:focus,input:focus{background:#fff;box-shadow:0 0 0 2px var(--accent-soft)}
    .filters{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:24px}
    .field label{display:block;font-size:11.5px;color:var(--muted);font-weight:500;margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em}

    /* TABLES */
    table{width:100%;border-collapse:collapse;font-size:13px}
    thead th{position:sticky;top:0;background:var(--surface);color:var(--muted);font-weight:500;font-size:11px;
      text-transform:uppercase;letter-spacing:.05em;padding:12px 16px;text-align:left;border-bottom:1px solid var(--divider)}
    tbody td{padding:12px 16px;border-bottom:1px solid var(--divider)}
    tbody tr{transition:background .12s} tbody tr:hover td{background:var(--surface-2)}
    tbody tr:last-child td{border-bottom:none}
    .num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
    .muted{color:var(--muted)} .pos{color:var(--good)} .neg{color:var(--bad)}
    .table-scroll{overflow:auto;max-height:78vh;border-radius:var(--radius-xl);background:var(--surface);box-shadow:var(--shadow-sm)}

    /* TIMELINE */
    .timeline{position:relative;padding-left:6px}
    .tl-item{display:flex;gap:16px;position:relative;padding-bottom:22px}
    .tl-item::before{content:"";position:absolute;left:17px;top:36px;bottom:-4px;width:2px;background:var(--divider)}
    .tl-item:last-child::before{display:none}
    .tl-dot{width:36px;height:36px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;
      font-size:16px;background:var(--surface-2);z-index:1}
    .tl-item.done .tl-dot{background:rgba(48,209,88,.15)}
    .tl-item.active .tl-dot{background:rgba(10,132,255,.14);box-shadow:0 0 0 4px rgba(10,132,255,.10);animation:pulse 1.8s infinite}
    .tl-item.pending .tl-dot{background:var(--surface-2);opacity:.6}
    @keyframes pulse{0%{box-shadow:0 0 0 0 rgba(10,132,255,.18)}70%{box-shadow:0 0 0 8px rgba(10,132,255,0)}100%{box-shadow:0 0 0 0 rgba(10,132,255,0)}}
    .tl-body{padding-top:2px}
    .tl-title{font-weight:600;font-size:14px}
    .tl-detail{color:var(--muted);font-size:12.5px;margin-top:1px}
    .tl-status{font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin-left:8px}
    .tl-item.done .tl-status{color:var(--good)} .tl-item.active .tl-status{color:var(--accent)}

    /* MSGS */
    .msgs{margin-bottom:22px;display:flex;flex-direction:column;gap:8px}
    .msg{padding:12px 18px;border-radius:var(--radius);font-size:13.5px;font-weight:500}
    .msg-success{background:rgba(48,209,88,.12);color:#0c7d3a}
    .msg-error{background:rgba(255,59,48,.12);color:#a8211a}
    .msg-info{background:var(--surface-2);color:var(--text)}

    /* MOBILE */
    .sb-toggle{display:none;position:fixed;top:14px;left:14px;z-index:60;width:38px;height:38px;border-radius:10px;
      background:var(--surface);border:1px solid var(--border);box-shadow:var(--shadow-sm);align-items:center;justify-content:center;padding:0}
    .sb-toggle svg{width:18px;height:18px;stroke:var(--text);stroke-width:2;fill:none;stroke-linecap:round}
    @media (max-width:900px){
      :root{--pad-x:20px}
      .sb-toggle{display:flex}
      .sb{position:fixed;left:0;top:0;transform:translateX(-100%);transition:transform .2s ease;box-shadow:var(--shadow)}
      .sb.open{transform:translateX(0)}
      .sb-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.3);z-index:25;display:none}
      .sb-backdrop.open{display:block}
      .content{padding-top:64px}
      h1.page-title{font-size:29px}
      .kpis{grid-template-columns:1fr 1fr}.kpi+.kpi::before{display:none}
      .grid-2,.grid-3{grid-template-columns:1fr}
    }
    ::-webkit-scrollbar{width:10px;height:10px}
    ::-webkit-scrollbar-track{background:transparent}
    ::-webkit-scrollbar-thumb{background:var(--border-strong);border-radius:999px;border:2px solid var(--bg)}
  </style>
</head>
<body>
  <button class="sb-toggle" id="sbToggle" aria-label="Menú"><svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
  <div class="sb-backdrop" id="sbBackdrop"></div>

  <div class="app">
    <aside class="sb" id="sb">
      <div class="sb-brand">
        <div class="sb-brand-logo">
          <svg viewBox="0 0 24 24"><path d="M3 12h4l2 5 4-13 2 8h6"/></svg>
        </div>
        <div class="sb-brand-name">LifeLink AI<small>{{ app_tagline }}</small></div>
      </div>

      <div class="sb-sos">
        <a href="{% url 'core:dashboard' %}#sos">🚨 Simular emergencia</a>
      </div>

      <div class="sb-section">General</div>
      <nav class="sb-nav">
        <a href="{% url 'core:dashboard' %}" data-path="/" data-exact="1">
          <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
          Dashboard
        </a>
        <a href="{% url 'core:emergencies' %}" data-path="/emerg">
          <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M12 8v4l3 2"/></svg>
          Emergencias
        </a>
      </nav>

      <div class="sb-section">Preparación</div>
      <nav class="sb-nav">
        <a href="{% url 'core:patient' %}" data-path="/patient">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0 1 14 0v1"/></svg>
          Paciente
        </a>
        <a href="{% url 'core:travel' %}" data-path="/travel">
          <svg viewBox="0 0 24 24"><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20z"/></svg>
          Planes de viaje
        </a>
      </nav>

      <div class="sb-section">Red</div>
      <nav class="sb-nav">
        <a href="{% url 'core:providers' %}" data-path="/provider">
          <svg viewBox="0 0 24 24"><path d="M3 21V8l9-5 9 5v13"/><path d="M9 21v-6h6v6"/><path d="M12 9v4M10 11h4"/></svg>
          Red de prestadores
        </a>
      </nav>

      <div class="sb-foot">
        <span>v{{ app_version }}</span>
        <a href="/admin/" target="_blank">Admin ↗</a>
      </div>
    </aside>

    <main class="content">
      {% if messages %}
        <div class="msgs">
          {% for m in messages %}<div class="msg msg-{{ m.tags|default:'info' }}">{{ m }}</div>{% endfor %}
        </div>
      {% endif %}
      {% block content %}{% endblock %}
    </main>
  </div>

  <script>
    (function(){
      const path = window.location.pathname;
      document.querySelectorAll('.sb-nav a[data-path]').forEach(a=>{
        const p=a.dataset.path, exact=a.dataset.exact==='1';
        if(exact?path===p:path.startsWith(p)) a.classList.add('active');
      });
      const sb=document.getElementById('sb'),bd=document.getElementById('sbBackdrop'),tg=document.getElementById('sbToggle');
      function toggle(){sb.classList.toggle('open');bd.classList.toggle('open');}
      tg.addEventListener('click',toggle); bd.addEventListener('click',toggle);
    })();

    // Shared Leaflet helpers
    const LL = {
      tiles(){ return L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        {attribution:'&copy; OpenStreetMap &copy; CARTO', maxZoom:19}); },
      icon(color){ return L.divIcon({className:'',html:
        `<div style="width:18px;height:18px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);
         background:${color};box-shadow:0 2px 6px rgba(0,0,0,.3);border:2px solid #fff"></div>`,
        iconSize:[18,18],iconAnchor:[9,18]}); },
    };
  </script>
  {% block scripts %}{% endblock %}
</body>
</html>
```
<!-- END FILE: core/templates/core/base.html -->


<!-- BEGIN FILE: core/templates/core/dashboard.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}Dashboard · LifeLink AI{% endblock %}
{% block content %}

<div class="page-head">
  <div>
    <h1 class="page-title">Dashboard</h1>
    <p class="page-sub">
      {% if patient %}Centro de comando de emergencias para <strong>{{ patient.full_name }}</strong>.{% else %}Plataforma de orquestación de emergencias médicas.{% endif %}
      Preparar · Detectar · Orquestar.
    </p>
  </div>
  <div class="page-actions">
    <a class="btn btn-secondary" href="{% url 'core:emergencies' %}">Ver emergencias</a>
    <a class="btn" href="#sos">🚨 Simular emergencia</a>
  </div>
</div>

{% if not patient %}
<div class="card" style="text-align:center;padding:48px">
  <h2 style="margin:0 0 8px">No hay datos cargados</h2>
  <p class="muted" style="margin:0 0 18px">Corré el seed para cargar paciente demo, prestadores y obras sociales.</p>
  <code style="background:var(--surface-2);padding:8px 14px;border-radius:8px">python manage.py seed_demo</code>
</div>
{% else %}

<!-- KPIs -->
<section>
  <div class="kpis">
    <div class="kpi {% if kpi_open %}neg{% endif %}">
      <div class="label">Emergencias activas</div>
      <div class="val">{{ kpi_open }}</div>
      <div class="sub">en orquestación</div>
    </div>
    <div class="kpi">
      <div class="label">Prestadores en red</div>
      <div class="val">{{ kpi_providers }}</div>
      <div class="sub">hospitales y clínicas</div>
    </div>
    <div class="kpi">
      <div class="label">Camas disponibles</div>
      <div class="val">{{ kpi_beds }}</div>
      <div class="sub">guardias activas</div>
    </div>
    <div class="kpi">
      <div class="label">ETA promedio</div>
      <div class="val">{% if kpi_avg_eta %}{{ kpi_avg_eta }}′{% else %}—{% endif %}</div>
      <div class="sub">ambulancia</div>
    </div>
    <div class="kpi {% if kpi_readiness >= 70 %}pos{% elif kpi_readiness < 40 %}neg{% else %}warn{% endif %}">
      <div class="label">Readiness</div>
      <div class="val">{{ kpi_readiness }}%</div>
      <div class="sub">perfil del paciente</div>
    </div>
  </div>
</section>

<!-- SOS PANEL -->
<section id="sos">
  <h2>Simular una emergencia</h2>
  <p class="sec-sub">Elegí tipo de evento, cómo se detecta y dónde ocurre. El <strong>Emergency Orchestrator</strong> hará el triage, puntuará los prestadores y disparará el journey automático en segundos.</p>

  <form method="post" action="{% url 'core:sos' %}" class="grid-2" style="align-items:start">
    {% csrf_token %}
    <div class="card">
      <div class="field" style="margin-bottom:16px">
        <label>Tipo de evento</label>
        <select name="event_type" style="width:100%">
          {% for val, label in event_types %}<option value="{{ val }}" {% if val == 'cardiac' %}selected{% endif %}>{{ label }}</option>{% endfor %}
        </select>
      </div>
      <div class="field" style="margin-bottom:16px">
        <label>Detección / activación</label>
        <select name="trigger_type" style="width:100%">
          {% for val, label in triggers %}<option value="{{ val }}">{{ label }}</option>{% endfor %}
        </select>
      </div>

      <div class="field" style="margin-bottom:10px"><label>Ubicación del evento</label></div>
      <div id="scenarioChips" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px">
        {% for s in scenarios %}
        <button type="button" class="chip" data-key="{{ s.key }}" data-lat="{{ s.lat }}" data-lng="{{ s.lng }}"
                data-desc="{{ s.desc }}" data-country="{{ s.country }}">{{ s.icon }} {{ s.label }}</button>
        {% endfor %}
      </div>
      <p class="muted" style="font-size:12px;margin:0 0 16px">📍 <span id="locLabel">Domicilio</span> — o hacé click en el mapa para elegir otro punto.</p>

      <input type="hidden" name="lat" id="f_lat" value="{{ patient.home_lat }}">
      <input type="hidden" name="lng" id="f_lng" value="{{ patient.home_lng }}">
      <input type="hidden" name="location_desc" id="f_desc" value="Domicilio">
      <input type="hidden" name="country" id="f_country" value="{{ patient.home_country }}">

      <button type="submit" class="btn btn-emergency" style="width:100%;justify-content:center;padding:13px;font-size:15px">
        🚨 Activar SOS y orquestar
      </button>
    </div>

    <div>
      <div class="map" id="sosMap"></div>
      <p class="muted" style="font-size:12px;margin-top:10px">Marcadores azules = prestadores de la red · marcador rojo = ubicación del evento.</p>
    </div>
  </form>
</section>

<!-- OPEN EMERGENCIES -->
{% if open_events %}
<section>
  <h2>En curso</h2>
  <div class="grid-3">
    {% for e in open_events %}
    <a class="card" href="{% url 'core:emergency_detail' e.pk %}" style="display:block">
      <span class="sev sev-{{ e.severity }}">{{ e.severity_label }}</span>
      <div style="font-weight:600;font-size:15px;margin:10px 0 2px">{{ e.get_event_type_display }}</div>
      <div class="muted" style="font-size:12.5px">{{ e.triggered_at|date:"d/m H:i" }} · {{ e.get_trigger_type_display }}</div>
      {% if e.selected_provider %}<div style="margin-top:10px;font-size:13px">🏥 {{ e.selected_provider.name }}</div>
      <div class="muted" style="font-size:12px">🚑 ETA {{ e.ambulance_eta_min }}′ · {{ e.provider_distance_km }} km</div>{% endif %}
    </a>
    {% endfor %}
  </div>
</section>
{% endif %}

<!-- RECENT -->
<section>
  <div class="page-head" style="margin-bottom:18px">
    <h2 style="margin:0">Actividad reciente</h2>
    <a class="btn btn-secondary" href="{% url 'core:emergencies' %}">Ver todo</a>
  </div>
  {% if recent %}
  <div class="table-scroll">
    <table>
      <thead><tr><th>Fecha</th><th>Evento</th><th>Severidad</th><th>Activación</th><th>Prestador</th><th class="num">ETA</th><th>Estado</th></tr></thead>
      <tbody>
        {% for e in recent %}
        <tr style="cursor:pointer" onclick="location.href='{% url 'core:emergency_detail' e.pk %}'">
          <td>{{ e.triggered_at|date:"d/m H:i" }}</td>
          <td><strong>{{ e.get_event_type_display }}</strong></td>
          <td><span class="sev sev-{{ e.severity }}">{{ e.severity_label }}</span></td>
          <td class="muted">{{ e.get_trigger_type_display }}</td>
          <td>{% if e.selected_provider %}{{ e.selected_provider.name }}{% else %}<span class="muted">—</span>{% endif %}</td>
          <td class="num">{% if e.ambulance_eta_min %}{{ e.ambulance_eta_min }}′{% else %}—{% endif %}</td>
          <td>
            {% if e.status == 'resolved' %}<span class="badge badge-good">Resuelto</span>
            {% elif e.is_open %}<span class="badge badge-info">{{ e.get_status_display }}</span>
            {% else %}<span class="pill">{{ e.get_status_display }}</span>{% endif %}
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="card-flat muted" style="text-align:center;padding:32px">Todavía no hay emergencias. Probá el panel SOS de arriba ☝️</div>
  {% endif %}
</section>
{% endif %}

<style>
  .chip{background:var(--surface-2);color:var(--text);border:1.5px solid transparent;border-radius:999px;
    padding:7px 13px;font-size:12.5px;font-weight:500;cursor:pointer}
  .chip:hover{background:var(--surface-hover);opacity:1}
  .chip.on{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
</style>
{% endblock %}

{% block scripts %}
{% if patient %}
<script>
const PROVIDERS = {{ providers_json|safe }};
const SCENARIOS = {{ scenarios_json|safe }};
const CENTER = {{ map_center }};

const map = L.map('sosMap', {scrollWheelZoom:false}).setView(CENTER, 12);
LL.tiles().addTo(map);

PROVIDERS.forEach(p=>{
  L.marker([p.lat,p.lng],{icon:LL.icon('#0a84ff')}).addTo(map)
   .bindPopup(`<b>${p.name}</b><br>${p.kind}<br>⭐ ${p.quality} · 🛏️ ${p.beds} · ${p.status}`);
});

let evtMarker = L.marker(CENTER,{icon:LL.icon('#ff3b30'),draggable:true}).addTo(map);
function setLoc(lat,lng,desc,country){
  document.getElementById('f_lat').value=lat;
  document.getElementById('f_lng').value=lng;
  document.getElementById('f_desc').value=desc||'';
  if(country) document.getElementById('f_country').value=country;
  document.getElementById('locLabel').textContent=desc||`${(+lat).toFixed(4)}, ${(+lng).toFixed(4)}`;
  evtMarker.setLatLng([lat,lng]); map.panTo([lat,lng]);
}
evtMarker.on('dragend', e=>{const ll=e.target.getLatLng(); setLoc(ll.lat,ll.lng,'Punto en el mapa');
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));});
map.on('click', e=>{setLoc(e.latlng.lat,e.latlng.lng,'Punto en el mapa');
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));});

document.querySelectorAll('.chip').forEach(chip=>{
  chip.addEventListener('click',()=>{
    document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));
    chip.classList.add('on');
    setLoc(+chip.dataset.lat,+chip.dataset.lng,chip.dataset.desc,chip.dataset.country);
  });
});
// default select first scenario (home)
const first=document.querySelector('.chip'); if(first) first.classList.add('on');
</script>
{% endif %}
{% endblock %}
```
<!-- END FILE: core/templates/core/dashboard.html -->


<!-- BEGIN FILE: core/templates/core/emergency_detail.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}Emergencia · LifeLink AI{% endblock %}
{% block content %}

<div class="page-head">
  <div>
    <h1 class="page-title" style="display:flex;align-items:center;gap:14px">
      {{ event.get_event_type_display }}
      <span class="sev sev-{{ event.severity }}" style="font-size:13px">{{ event.severity_label }}</span>
    </h1>
    <p class="page-sub" style="margin-bottom:0">
      {{ event.patient.full_name }} · {{ event.triggered_at|date:"d/m/Y H:i" }} ·
      activado por {{ event.get_trigger_type_display }}
      {% if event.country %} · {{ event.location_desc|default:event.country }}{% endif %}
    </p>
  </div>
  <div class="page-actions">
    {% if event.is_open %}
    <form method="post" action="{% url 'core:emergency_resolve' event.pk %}">{% csrf_token %}
      <button type="submit" class="btn">✓ Marcar resuelto</button>
    </form>
    {% else %}<span class="badge badge-good" style="padding:8px 14px">✓ {{ event.get_status_display }}</span>{% endif %}
    <a class="btn btn-secondary" href="{% url 'core:emergencies' %}">← Volver</a>
  </div>
</div>

<!-- Decision summary strip -->
<section>
  <div class="kpis">
    <div class="kpi">
      <div class="label">Prestador seleccionado</div>
      <div class="val" style="font-size:19px">{% if event.selected_provider %}{{ event.selected_provider.name }}{% else %}—{% endif %}</div>
      <div class="sub">{% if event.required_specialty %}requiere {{ event.required_specialty.name }}{% endif %}</div>
    </div>
    <div class="kpi"><div class="label">Distancia</div><div class="val">{% if event.provider_distance_km %}{{ event.provider_distance_km }} km{% else %}—{% endif %}</div><div class="sub">ruta estimada</div></div>
    <div class="kpi pos"><div class="label">ETA ambulancia</div><div class="val">{% if event.ambulance_eta_min %}{{ event.ambulance_eta_min }}′{% else %}—{% endif %}</div><div class="sub">despacho incluido</div></div>
    <div class="kpi"><div class="label">Score de decisión</div><div class="val">{% if event.decision_score %}{{ event.decision_score|floatformat:0 }}<span style="font-size:15px;color:var(--muted)">/100</span>{% else %}—{% endif %}</div><div class="sub">vs {{ candidates|length }} candidatos</div></div>
  </div>
</section>

<div class="grid-2" style="align-items:start">
  <!-- TIMELINE -->
  <section style="margin-bottom:0">
    <h2>Emergency Journey</h2>
    <p class="sec-sub">Acciones automáticas ejecutadas por el orquestador, sin intervención del paciente.</p>
    <div class="card">
      <div class="timeline">
        {% for a in actions %}
        <div class="tl-item {{ a.status }}">
          <div class="tl-dot">{{ a.icon }}</div>
          <div class="tl-body">
            <div class="tl-title">{{ a.title }}
              <span class="tl-status">{% if a.status == 'active' %}● en curso{% elif a.status == 'done' %}✓{% endif %}</span>
            </div>
            <div class="tl-detail">{{ a.detail }}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </section>

  <!-- MAP -->
  <section style="margin-bottom:0">
    <h2>Ubicación y derivación</h2>
    <p class="sec-sub">Evento y prestadores evaluados. El verde es el seleccionado.</p>
    <div class="map tall" id="evtMap"></div>
  </section>
</div>

<!-- WHY THIS PROVIDER -->
<section style="margin-top:48px">
  <h2>Por qué este prestador</h2>
  <p class="sec-sub">Desglose transparente del puntaje de cada candidato evaluado por el orquestador.</p>

  <div class="grid-2" style="align-items:start">
    {% for c in candidates %}
    <div class="card" style="{% if c.obj.selected %}box-shadow:0 0 0 2px var(--good), var(--shadow-sm){% endif %}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:14px">
        <div>
          <div style="font-weight:600;font-size:15.5px">
            {{ c.obj.provider.name }}
            {% if c.obj.selected %}<span class="badge badge-good" style="margin-left:6px">Seleccionado</span>{% endif %}
          </div>
          <div class="muted" style="font-size:12.5px">{{ c.obj.provider.get_kind_display }} · {{ c.obj.distance_km }} km · ETA {{ c.obj.eta_min }}′</div>
        </div>
        <div style="text-align:right">
          <div style="font-size:24px;font-weight:600;font-variant-numeric:tabular-nums">{{ c.obj.score|floatformat:0 }}</div>
          <div class="muted" style="font-size:11px">/ 100</div>
        </div>
      </div>
      {% for comp in c.breakdown.components %}
      <div style="margin-bottom:9px">
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
          <span>{{ comp.label }} <span class="muted">· {{ comp.detail }}</span></span>
          <span class="muted" style="font-variant-numeric:tabular-nums">{{ comp.points }}/{{ comp.max }}</span>
        </div>
        <div style="height:6px;background:var(--surface-2);border-radius:999px;overflow:hidden">
          <div style="height:100%;border-radius:999px;background:{% if c.obj.selected %}var(--good){% else %}var(--accent){% endif %};width:{% widthratio comp.points comp.max 100 %}%"></div>
        </div>
      </div>
      {% endfor %}
    </div>
    {% endfor %}
  </div>
</section>

{% endblock %}

{% block scripts %}
<script>
const EVT = {{ event_point|safe }};
const POINTS = {{ map_points|safe }};
const CENTER = {{ map_center|safe }};

const map = L.map('evtMap',{scrollWheelZoom:false}).setView(CENTER, 12);
LL.tiles().addTo(map);

L.marker([EVT.lat,EVT.lng],{icon:LL.icon('#ff3b30')}).addTo(map)
 .bindPopup(`<b>📍 Evento</b><br>${EVT.desc||''}`).openPopup();

const group=[[EVT.lat,EVT.lng]];
POINTS.forEach(p=>{
  const color = p.selected ? '#30d158' : '#0a84ff';
  L.marker([p.lat,p.lng],{icon:LL.icon(color)}).addTo(map)
   .bindPopup(`<b>${p.name}</b><br>Score ${Math.round(p.score)} · ETA ${p.eta}′${p.selected?'<br>✓ <b>Seleccionado</b>':''}`);
  group.push([p.lat,p.lng]);
});
if(group.length>1){ try{ map.fitBounds(group,{padding:[40,40],maxZoom:14}); }catch(e){} }
</script>
{% endblock %}
```
<!-- END FILE: core/templates/core/emergency_detail.html -->


<!-- BEGIN FILE: core/templates/core/emergencies.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}Emergencias · LifeLink AI{% endblock %}
{% block content %}

<div class="page-head">
  <div>
    <h1 class="page-title">Emergencias</h1>
    <p class="page-sub" style="margin-bottom:0">Historial completo de eventos orquestados.</p>
  </div>
  <div class="page-actions"><a class="btn" href="{% url 'core:dashboard' %}#sos">🚨 Nueva simulación</a></div>
</div>

<div class="filters">
  <a class="chip {% if not status %}on{% endif %}" href="{% url 'core:emergencies' %}">Todas ({{ counts.all }})</a>
  <a class="chip {% if status == 'active' or status == 'en_route' %}on{% endif %}" href="?status=en_route">En curso ({{ counts.open }})</a>
  <a class="chip {% if status == 'resolved' %}on{% endif %}" href="?status=resolved">Resueltas ({{ counts.resolved }})</a>
</div>

{% if events %}
<div class="table-scroll">
  <table>
    <thead><tr><th>Fecha</th><th>Paciente</th><th>Evento</th><th>Severidad</th><th>Activación</th><th>Prestador</th><th class="num">Dist.</th><th class="num">ETA</th><th class="num">Score</th><th>Estado</th></tr></thead>
    <tbody>
      {% for e in events %}
      <tr style="cursor:pointer" onclick="location.href='{% url 'core:emergency_detail' e.pk %}'">
        <td>{{ e.triggered_at|date:"d/m/y H:i" }}</td>
        <td>{{ e.patient.full_name }}</td>
        <td><strong>{{ e.get_event_type_display }}</strong></td>
        <td><span class="sev sev-{{ e.severity }}">{{ e.severity_label }}</span></td>
        <td class="muted">{{ e.get_trigger_type_display }}</td>
        <td>{% if e.selected_provider %}{{ e.selected_provider.name }}{% else %}<span class="muted">—</span>{% endif %}</td>
        <td class="num muted">{% if e.provider_distance_km %}{{ e.provider_distance_km }} km{% else %}—{% endif %}</td>
        <td class="num">{% if e.ambulance_eta_min %}{{ e.ambulance_eta_min }}′{% else %}—{% endif %}</td>
        <td class="num">{% if e.decision_score %}{{ e.decision_score|floatformat:0 }}{% else %}—{% endif %}</td>
        <td>
          {% if e.status == 'resolved' %}<span class="badge badge-good">Resuelto</span>
          {% elif e.is_open %}<span class="badge badge-info">{{ e.get_status_display }}</span>
          {% else %}<span class="pill">{{ e.get_status_display }}</span>{% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="card-flat muted" style="text-align:center;padding:40px">Sin emergencias para este filtro.</div>
{% endif %}

<style>.filters .chip{text-decoration:none}.filters .chip.on{background:var(--accent-soft);color:var(--accent)}
  .chip{background:var(--surface-2);color:var(--text);border-radius:999px;padding:7px 14px;font-size:12.5px;font-weight:500}</style>
{% endblock %}
```
<!-- END FILE: core/templates/core/emergencies.html -->


<!-- BEGIN FILE: core/templates/core/patient.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}Paciente · LifeLink AI{% endblock %}
{% block content %}

{% if not patient %}
<div class="card" style="text-align:center;padding:48px">
  <h2>No hay paciente cargado</h2>
  <p class="muted">Corré <code>python manage.py seed_demo</code> o creá uno en el <a href="/admin/">admin</a>.</p>
</div>
{% else %}

<div class="page-head">
  <div>
    <h1 class="page-title">{{ patient.full_name }}</h1>
    <p class="page-sub" style="margin-bottom:0">
      {% if patient.age %}{{ patient.age }} años · {% endif %}Grupo {{ patient.blood_type }} ·
      {{ patient.home_city }}, {{ patient.home_country }} · {{ patient.languages }}
    </p>
  </div>
  <div class="page-actions"><a class="btn btn-secondary" href="/admin/core/patientprofile/{{ patient.pk }}/change/" target="_blank">Editar en admin ↗</a></div>
</div>

<!-- Readiness + KPIs -->
<section>
  <div class="kpis">
    <div class="kpi {% if patient.readiness_score >= 70 %}pos{% elif patient.readiness_score < 40 %}neg{% else %}warn{% endif %}">
      <div class="label">Emergency Readiness</div><div class="val">{{ patient.readiness_score }}%</div><div class="sub">perfil completo</div>
    </div>
    <div class="kpi"><div class="label">Condiciones</div><div class="val">{{ conditions|length }}</div></div>
    <div class="kpi"><div class="label">Alergias</div><div class="val">{{ allergies|length }}</div></div>
    <div class="kpi"><div class="label">Medicamentos</div><div class="val">{{ medications|length }}</div></div>
    <div class="kpi"><div class="label">Contactos</div><div class="val">{{ contacts|length }}</div></div>
  </div>
</section>

<div class="grid-2" style="align-items:start">
  <section style="margin-bottom:0">
    <h2>Ficha clínica</h2>
    <p class="sec-sub">Lo que el orquestador comparte con el equipo asistencial en segundos.</p>

    <div class="card" style="margin-bottom:16px">
      <h3 style="margin:0 0 12px;font-size:14px">🩺 Condiciones preexistentes</h3>
      {% for c in conditions %}
        <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--divider)">
          <span>{{ c.name }}</span><span class="badge {% if c.severity == 'critical' or c.severity == 'high' %}badge-bad{% else %}badge-warn{% endif %}">{{ c.get_severity_display }}</span>
        </div>
      {% empty %}<p class="muted" style="margin:0">Sin condiciones registradas.</p>{% endfor %}
    </div>

    <div class="card" style="margin-bottom:16px">
      <h3 style="margin:0 0 12px;font-size:14px">🤧 Alergias</h3>
      {% for a in allergies %}
        <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--divider)">
          <span>{{ a.substance }} <span class="muted" style="font-size:12px">{{ a.reaction }}</span></span>
          <span class="badge {% if a.severity == 'anaphylaxis' or a.severity == 'high' %}badge-bad{% else %}badge-warn{% endif %}">{{ a.get_severity_display }}</span>
        </div>
      {% empty %}<p class="muted" style="margin:0">Sin alergias registradas.</p>{% endfor %}
    </div>

    <div class="card">
      <h3 style="margin:0 0 12px;font-size:14px">💊 Medicación habitual</h3>
      {% for m in medications %}
        <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--divider)">
          <span>{{ m.name }}</span><span class="muted" style="font-size:12.5px">{{ m.dose }} · {{ m.frequency }}</span>
        </div>
      {% empty %}<p class="muted" style="margin:0">Sin medicación registrada.</p>{% endfor %}
    </div>
  </section>

  <section style="margin-bottom:0">
    <h2>Cobertura, contactos y domicilio</h2>
    <p class="sec-sub">Datos usados para validar prestadores y avisar a la familia.</p>

    <div class="card" style="margin-bottom:16px">
      <h3 style="margin:0 0 12px;font-size:14px">🛡️ Cobertura</h3>
      {% for p in policies %}
        <div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--divider)">
          <div><strong>{{ p.network.name }}</strong> <span class="muted" style="font-size:12px">{{ p.plan }}</span>
            <div class="muted" style="font-size:11.5px">{{ p.get_coverage_level_display }}{% if p.international %} · Internacional ✓{% endif %}</div>
          </div>
          {% if p.active %}<span class="badge badge-good">Activa</span>{% else %}<span class="pill">Inactiva</span>{% endif %}
        </div>
      {% empty %}<p class="muted" style="margin:0">Sin cobertura registrada.</p>{% endfor %}
    </div>

    <div class="card" style="margin-bottom:16px">
      <h3 style="margin:0 0 12px;font-size:14px">👨‍👩‍👧 Contactos de emergencia</h3>
      {% for c in contacts %}
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--divider)">
          <div><strong>{{ c.name }}</strong> <span class="muted" style="font-size:12px">{{ c.relationship }}</span></div>
          <div style="display:flex;align-items:center;gap:8px">{{ c.phone }}{% if c.is_primary %}<span class="badge badge-info">Principal</span>{% endif %}</div>
        </div>
      {% empty %}<p class="muted" style="margin:0">Sin contactos registrados.</p>{% endfor %}
    </div>

    <div class="card">
      <h3 style="margin:0 0 12px;font-size:14px">📍 Domicilio</h3>
      <div class="map" id="homeMap" style="height:240px"></div>
      <p class="muted" style="font-size:12.5px;margin:10px 0 0">{{ patient.home_address }} — {{ patient.home_city }}</p>
    </div>
  </section>
</div>

<!-- Recent events -->
{% if events %}
<section style="margin-top:48px">
  <h2>Emergencias del paciente</h2>
  <div class="table-scroll">
    <table>
      <thead><tr><th>Fecha</th><th>Evento</th><th>Severidad</th><th>Prestador</th><th>Estado</th></tr></thead>
      <tbody>
        {% for e in events %}
        <tr style="cursor:pointer" onclick="location.href='{% url 'core:emergency_detail' e.pk %}'">
          <td>{{ e.triggered_at|date:"d/m/y H:i" }}</td>
          <td><strong>{{ e.get_event_type_display }}</strong></td>
          <td><span class="sev sev-{{ e.severity }}">{{ e.severity_label }}</span></td>
          <td>{% if e.selected_provider %}{{ e.selected_provider.name }}{% else %}—{% endif %}</td>
          <td>{% if e.status == 'resolved' %}<span class="badge badge-good">Resuelto</span>{% else %}<span class="badge badge-info">{{ e.get_status_display }}</span>{% endif %}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</section>
{% endif %}
{% endif %}
{% endblock %}

{% block scripts %}
{% if patient %}
<script>
const HOME = {{ home_point|safe }};
const map = L.map('homeMap',{scrollWheelZoom:false,zoomControl:false}).setView([HOME.lat,HOME.lng],14);
LL.tiles().addTo(map);
L.marker([HOME.lat,HOME.lng],{icon:LL.icon('#0ab9c2')}).addTo(map).bindPopup(`<b>🏠 ${HOME.name}</b>`);
</script>
{% endif %}
{% endblock %}
```
<!-- END FILE: core/templates/core/patient.html -->


<!-- BEGIN FILE: core/templates/core/providers.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}Red de prestadores · LifeLink AI{% endblock %}
{% block content %}

<div class="page-head">
  <div>
    <h1 class="page-title">Red de prestadores</h1>
    <p class="page-sub" style="margin-bottom:0">Hospitales y clínicas con geolocalización, especialidades y disponibilidad en tiempo real.</p>
  </div>
</div>

<section>
  <div class="kpis">
    <div class="kpi"><div class="label">Prestadores</div><div class="val">{{ count }}</div></div>
    <div class="kpi"><div class="label">Camas disponibles</div><div class="val">{{ beds }}</div></div>
    <div class="kpi"><div class="label">Calidad promedio</div><div class="val">{{ avg_quality }}<span style="font-size:15px;color:var(--muted)">/5</span></div></div>
  </div>
</section>

<section>
  <div class="map tall" id="provMap"></div>
</section>

<form method="get" class="filters">
  <select name="kind"><option value="">Todos los tipos</option>
    {% for val,label in kinds %}<option value="{{ val }}" {% if f.kind == val %}selected{% endif %}>{{ label }}</option>{% endfor %}
  </select>
  <select name="specialty"><option value="">Todas las especialidades</option>
    {% for s in specialties %}<option value="{{ s.code }}" {% if f.specialty == s.code %}selected{% endif %}>{{ s.name }}</option>{% endfor %}
  </select>
  <input type="search" name="q" placeholder="Buscar nombre o ciudad…" value="{{ f.q }}">
  <button type="submit">Filtrar</button>
  <a class="btn btn-secondary" href="{% url 'core:providers' %}">Limpiar</a>
</form>

<div class="table-scroll">
  <table>
    <thead><tr><th>Prestador</th><th>Tipo</th><th>Ciudad</th><th>Especialidades</th><th class="num">Calidad</th><th class="num">Camas</th><th>Estado</th></tr></thead>
    <tbody>
      {% for p in providers %}
      <tr>
        <td><strong>{{ p.name }}</strong>{% if p.trauma_level %} <span class="pill">Trauma N{{ p.trauma_level }}</span>{% endif %}</td>
        <td class="muted">{{ p.get_kind_display }}</td>
        <td>{{ p.city }}</td>
        <td style="max-width:280px">{% for s in p.specialties.all %}<span class="pill" style="margin:1px">{{ s.icon }} {{ s.name }}</span>{% endfor %}</td>
        <td class="num">{{ p.quality_rating }}</td>
        <td class="num">{{ p.available_beds }}/{{ p.total_beds }}</td>
        <td>
          {% if p.availability_label == 'Disponible' %}<span class="badge badge-good">{{ p.availability_label }}</span>
          {% elif p.availability_label == 'Saturado' %}<span class="badge badge-warn">{{ p.availability_label }}</span>
          {% else %}<span class="badge badge-bad">{{ p.availability_label }}</span>{% endif %}
        </td>
      </tr>
      {% empty %}<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--muted)">Sin prestadores para este filtro.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}

{% block scripts %}
<script>
const PROVIDERS = {{ providers_json|safe }};
const CENTER = {{ map_center|safe }};
const map = L.map('provMap',{scrollWheelZoom:false}).setView(CENTER, 11);
LL.tiles().addTo(map);
const grp=[];
PROVIDERS.forEach(p=>{
  const color = !p.er_open ? '#a8a8ad' : (p.beds<=2 ? '#ff9f0a' : '#0a84ff');
  L.marker([p.lat,p.lng],{icon:LL.icon(color)}).addTo(map)
   .bindPopup(`<b>${p.name}</b><br>${p.kind}<br>⭐ ${p.quality} · 🛏️ ${p.beds} · ${p.status}`);
  grp.push([p.lat,p.lng]);
});
if(grp.length){ try{ map.fitBounds(grp,{padding:[40,40],maxZoom:13}); }catch(e){} }
</script>
{% endblock %}
```
<!-- END FILE: core/templates/core/providers.html -->


<!-- BEGIN FILE: core/templates/core/travel.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}Planes de viaje · LifeLink AI{% endblock %}
{% block content %}

<div class="page-head">
  <div>
    <h1 class="page-title">Smart Travel Plans</h1>
    <p class="page-sub" style="margin-bottom:0">Planes de emergencia preventivos por destino — generados con el perfil del paciente.</p>
  </div>
</div>

<section>
  <h2>Generar un plan</h2>
  <p class="sec-sub">Escribí un destino o elegí uno sugerido. La IA arma el Emergency Readiness Plan en segundos.</p>
  <form method="post" action="{% url 'core:travel_create' %}" class="card">
    {% csrf_token %}
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <input type="text" name="destination" id="destInput" placeholder="Ej: Miami, Madrid, São Paulo…" style="flex:1;min-width:240px" required>
      <button type="submit" class="btn">✈️ Generar plan</button>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:14px">
      {% for s in suggestions %}
      <button type="button" class="chip" onclick="document.getElementById('destInput').value='{{ s.city }}'">
        {{ s.city }}, {{ s.country }} <span class="muted">· {{ s.risk }}</span>
      </button>
      {% endfor %}
    </div>
  </form>
</section>

<section>
  <h2>Planes generados</h2>
  {% if plans %}
  <div class="grid-3">
    {% for p in plans %}
    <a class="card" href="{% url 'core:travel_detail' p.pk %}" style="display:block">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div style="font-weight:600;font-size:16px">{{ p.destination_city }}</div>
        <span class="badge {% if p.risk_level == 'Bajo' %}badge-good{% elif p.risk_level == 'Alto' %}badge-bad{% else %}badge-warn{% endif %}">{{ p.risk_level }}</span>
      </div>
      <div class="muted" style="font-size:13px">{{ p.destination_country }}</div>
      <p class="muted" style="font-size:12.5px;margin:12px 0 0">{{ p.summary|truncatechars:110 }}</p>
      <div class="muted" style="font-size:11px;margin-top:10px">{{ p.created_at|date:"d/m/Y H:i" }}</div>
    </a>
    {% endfor %}
  </div>
  {% else %}
  <div class="card-flat muted" style="text-align:center;padding:36px">Todavía no generaste ningún plan. Probá con un destino ☝️</div>
  {% endif %}
</section>

<style>.chip{background:var(--surface-2);color:var(--text);border:none;border-radius:999px;padding:7px 13px;font-size:12.5px;font-weight:500;cursor:pointer}
  .chip:hover{background:var(--surface-hover)}</style>
{% endblock %}
```
<!-- END FILE: core/templates/core/travel.html -->


<!-- BEGIN FILE: core/templates/core/travel_detail.html -->
```html
{% extends "core/base.html" %}
{% load humanize %}
{% block title %}{{ plan.destination_city }} · Travel Plan{% endblock %}
{% block content %}

<div class="page-head">
  <div>
    <h1 class="page-title" style="display:flex;align-items:center;gap:12px">
      {{ plan.destination_city }}
      <span class="badge {% if plan.risk_level == 'Bajo' %}badge-good{% elif plan.risk_level == 'Alto' %}badge-bad{% else %}badge-warn{% endif %}" style="font-size:12px">Riesgo {{ plan.risk_level }}</span>
    </h1>
    <p class="page-sub" style="margin-bottom:0">{{ plan.destination_country }} · plan para {{ plan.patient.full_name }} · {{ plan.created_at|date:"d/m/Y" }}</p>
  </div>
  <div class="page-actions"><a class="btn btn-secondary" href="{% url 'core:travel' %}">← Volver</a></div>
</div>

<section>
  <div class="card-flat" style="font-size:14.5px">{{ plan.summary }}</div>
</section>

<!-- Coverage banner -->
<section>
  <div class="card" style="display:flex;align-items:center;gap:14px;{% if data.coverage_ok %}box-shadow:0 0 0 2px rgba(48,209,88,.3), var(--shadow-sm){% else %}box-shadow:0 0 0 2px rgba(255,159,10,.35), var(--shadow-sm){% endif %}">
    <div style="font-size:26px">{% if data.coverage_ok %}🛡️{% else %}⚠️{% endif %}</div>
    <div><div style="font-weight:600">Cobertura</div><div class="muted" style="font-size:13px">{{ data.coverage_note }}</div></div>
  </div>
</section>

<div class="grid-2" style="align-items:start">
  <section style="margin-bottom:0">
    <h2>Contexto del destino</h2>
    <div class="card" style="margin-bottom:16px">
      <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--divider)"><span>🗣️ Idioma</span><strong>{{ data.language }}</strong></div>
      <div style="display:flex;justify-content:space-between;padding:8px 0"><span>⚠️ Nivel de riesgo</span><strong>{{ data.risk_level }}</strong></div>
    </div>

    <div class="card" style="margin-bottom:16px">
      <h3 style="margin:0 0 10px;font-size:14px">🦠 Riesgos sanitarios</h3>
      {% for r in data.health_risks %}<div style="padding:5px 0;border-bottom:1px solid var(--divider)">{{ r }}</div>{% endfor %}
    </div>

    <div class="card" style="margin-bottom:16px">
      <h3 style="margin:0 0 10px;font-size:14px">💉 Vacunas</h3>
      {% for v in data.vaccines %}<span class="pill" style="margin:2px">{{ v }}</span>{% endfor %}
    </div>

    {% if data.patient_flags %}
    <div class="card">
      <h3 style="margin:0 0 10px;font-size:14px">🩺 Específico del paciente</h3>
      {% for f in data.patient_flags %}<div style="padding:6px 0;border-bottom:1px solid var(--divider)">{{ f }}</div>{% endfor %}
    </div>
    {% endif %}
  </section>

  <section style="margin-bottom:0">
    <h2>Hospitales de referencia</h2>
    <p class="sec-sub">Prestadores más adecuados cerca del destino.</p>
    <div class="map" id="travelMap" style="margin-bottom:16px"></div>

    {% for p in data.providers %}
    <div class="card" style="margin-bottom:12px;display:flex;justify-content:space-between;align-items:center">
      <div><strong>{{ p.name }}</strong><div class="muted" style="font-size:12.5px">{{ p.kind }} · {{ p.distance_km }} km · ⭐ {{ p.quality }}</div></div>
      <div class="muted" style="font-size:12.5px">{{ p.phone }}</div>
    </div>
    {% empty %}
    <div class="card-flat muted">Sin prestadores catalogados en este destino. Recomendación: contratar asistencia al viajero con red local.</div>
    {% endfor %}

    <div class="card-flat" style="margin-top:8px">
      <h3 style="margin:0 0 10px;font-size:14px">✅ Recomendaciones</h3>
      {% for r in data.recommendations %}<div style="padding:5px 0">• {{ r }}</div>{% endfor %}
    </div>
  </section>
</div>
{% endblock %}

{% block scripts %}
<script>
const DEST = {{ dest_point|safe }};
const POINTS = {{ map_points|safe }};
const CENTER = {{ map_center|safe }};
const map = L.map('travelMap',{scrollWheelZoom:false}).setView(CENTER, 11);
LL.tiles().addTo(map);
L.marker([DEST.lat,DEST.lng],{icon:LL.icon('#ff3b30')}).addTo(map).bindPopup(`<b>📍 ${DEST.city}</b>`);
const grp=[[DEST.lat,DEST.lng]];
POINTS.forEach(p=>{
  L.marker([p.lat,p.lng],{icon:LL.icon('#0a84ff')}).addTo(map).bindPopup(`<b>${p.name}</b><br>${p.kind||''} · ⭐ ${p.quality||''}`);
  grp.push([p.lat,p.lng]);
});
if(grp.length>1){ try{ map.fitBounds(grp,{padding:[50,50],maxZoom:12}); }catch(e){} }
</script>
{% endblock %}
```
<!-- END FILE: core/templates/core/travel_detail.html -->


<!-- BEGIN FILE: core/static/core/manifest.webmanifest -->
```json
{
  "name": "LifeLink AI",
  "short_name": "LifeLink",
  "description": "Every patient. Everywhere. Instantly. — Intelligent Emergency Response Network.",
  "lang": "es",
  "dir": "ltr",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#fafafa",
  "theme_color": "#0a84ff",
  "icons": [
    { "src": "/static/core/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/static/core/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ]
}
```
<!-- END FILE: core/static/core/manifest.webmanifest -->
