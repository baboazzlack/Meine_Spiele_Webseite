# RetroArcadeHub/asgi.py

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from RetroArcadeHub.api import api as fastapi_app # Importiere unsere API

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RetroArcadeHub.settings')

django_app = get_asgi_application()

# Erstelle die Haupt-App und "montiere" die Django-App und die FastAPI-App
app = FastAPI()
app.mount("/api", fastapi_app)
app.mount("/", django_app)