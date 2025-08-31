# Use an official Python runtime as a parent image
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# NEU: Der direkte Befehl ohne extra Skript.
# Führt zuerst migrate aus UND DANN startet es den Server.
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000