# Vollständiger Inhalt für: RetroArcadeHub/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# NEU: Importiere die neuen Views aus der games-App
from games import views as game_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('games/', include('games.urls')),

    # NEU: URLs für die Frontend-Seiten
    path('register/', game_views.register_page, name='register_page'),
    path('login/', game_views.login_page, name='login_page'),

    # API-Pfade (bleiben unverändert)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),
]