from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Der Pfad zur Startseite (home.html)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # Diese Zeile bindet ALLE URLs aus der games-App unter dem Präfix /games/ ein
    path('games/', include('games.urls')),
]