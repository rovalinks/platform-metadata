# ==========================================
# STAGE 1: BUILDER (Heavy)
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy only requirements to cache this layer
COPY cloudrun/requirements.txt .

# Install dependencies into a dedicated prefix folder
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# STAGE 2: RUNTIME (Ultra-Light)
# ==========================================
FROM python:3.12-slim

# Standard Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app/cloudrun

WORKDIR /app

# 1. Copy ONLY the compiled python packages from Stage 1
COPY --from=builder /install /usr/local

# 2. Copy the actual application code
COPY cloudrun/ ./cloudrun/

# Note: We intentionally do NOT copy registry/ here anymore. 
# The engine pulls it dynamically from GCS, saving massive image space.

WORKDIR /app/cloudrun

# Run the API via Gunicorn
CMD exec gunicorn \
    --bind :${PORT} \
    --workers 1 \
    --threads 8 \
    app:app