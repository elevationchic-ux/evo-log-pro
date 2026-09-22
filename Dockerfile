# Multi-stage Dockerfile pour EVO-LOG Backend
# Utilise uvicorn directement en CMD pour eviter les problemes de line endings sur start.sh

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Installer les dependances systeme de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et builder les wheels
COPY evo-log-backend/requirements.txt ./requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.11-slim

WORKDIR /app

# Installer les dependances systeme requises au runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copier les wheels et installer
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copier le code source depuis evo-log-backend
COPY evo-log-backend/ .

EXPOSE 8000

# Commande de demarrage directe (pas de script shell intermediaire)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
