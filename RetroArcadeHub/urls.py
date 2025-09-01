# Vollständiger Inhalt für: RetroArcadeHub/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from games import views as game_views

# --- NEU: Importe für die korrekte statische Dateiauslieferung im Entwicklungsmodus ---
from django.conf import settings
from django.conf.urls.static import static
# --- Ende NEU ---

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('games/', include('games.urls')),

    # Frontend-Seiten für Login/Registrierung
    path('register/', game_views.register_page, name='register_page'),
    path('login/', game_views.login_page, name='login_page'),

    # API-Pfade
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),
]

# --- NEU: Der entscheidende Befehl für den Entwicklungs-Server ---
# Diese Logik fügt die URL für statische Dateien NUR hinzu, wenn DEBUG=True ist.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
# --- Ende NEU ---