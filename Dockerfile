# Use an official Python runtime as a parent image
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# NEU: Kopiere unsere Checkliste in die Vitrine und mache sie "offiziell" (ausführbar)
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Der Startbefehl ist jetzt, einfach nur die Checkliste auszuführen
CMD ["/app/entrypoint.sh"]