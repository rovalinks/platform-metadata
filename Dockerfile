FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY cloudrun/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY cloudrun/ ./cloudrun/
COPY registry/ ./registry/

WORKDIR /app/cloudrun

CMD exec gunicorn \
    --bind :${PORT} \
    --workers 1 \
    --threads 8 \
    app:app