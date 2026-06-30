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
