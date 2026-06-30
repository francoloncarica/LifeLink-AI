"""ASGI config for LifeLink AI."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifelink.settings')

application = get_asgi_application()
