FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# NEU: Dieser Befehl sammelt alle statischen Dateien und kopiert sie in STATIC_ROOT
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uvicorn", "RetroArcadeHub.asgi:app", "--host", "0.0.0.0", "--port", "8000"]