# Startet mit einem schlanken Python-Image
FROM python:3.9-slim

# Setzt das Arbeitsverzeichnis im Container
WORKDIR /code

# Kopiert die Anforderungs-Datei und installiert die Pakete
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Kopiert den restlichen Code der App
COPY . /code/

# Der Befehl, um die App beim Start des Containers auszuführen
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]