import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Liest den Secret Key aus den Umgebungsvariablen von Render.
# Wenn er nicht gefunden wird (z.B. lokal), wird ein Standardwert verwendet.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-gfn-retro-hub-LOCAL-DEV-KEY')

# Der DEBUG-Modus wird auf Render automatisch deaktiviert.
# Lokal bleibt er aktiv, es sei denn, die Variable ist anders gesetzt.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Erlaubt Anfragen von deiner Render-URL und von localhost.
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
else:
    # Für die lokale Entwicklung
    ALLOWED_HOSTS.append('127.0.0.1')
    ALLOWED_HOSTS.append('localhost')


# Wichtig für die Sicherheit bei Online-Betrieb
CSRF_TRUSTED_ORIGINS = ['https://gfn-retro-hub.onrender.com']
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


# Application definition

INSTALLED_APPS = [
    'games',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Wichtig für Static Files auf Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RetroArcadeHub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RetroArcadeHub.wsgi.application'
ASGI_APPLICATION = 'RetroArcadeHub.asgi.app'

DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3' } }

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static') ]
# Wichtig für Static Files auf Render
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'