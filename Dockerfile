# Dockerfile

FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render.com stellt eine PORT-Variable bereit. Wir benutzen diese.
# Lokal wird standardmäßig Port 8000 verwendet.
EXPOSE 8000

# Starte die kombinierte Anwendung mit einem ASGI-Server (Uvicorn)
CMD ["uvicorn", "RetroArcadeHub.asgi:app", "--host", "0.0.0.0", "--port", "8000"]