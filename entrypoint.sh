#!/bin/sh

# Führt die Datenbank-Migrationen aus (Möbel aufstellen)
python manage.py migrate

# Startet den Webserver (Lichter anmachen)
python manage.py runserver 0.0.0.0:8000