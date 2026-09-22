# Multi-stage Dockerfile pour EVO-LOG Backend (Racine)

# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Installer les dépendances système de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier le contexte pour trouver requirements.txt quel que soit le dossier racine configuré
COPY . .
RUN if [ -f requirements.txt ]; then pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt; elif [ -f EVO-LOG-backend/requirements.txt ]; then pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r EVO-LOG-backend/requirements.txt; fi

# Stage 2: Production Runtime
FROM python:3.12-slim

WORKDIR /app

# Création d'un utilisateur non-root pour des raisons de sécurité
RUN groupadd -r EVO-LOG && useradd -m -r -g EVO-LOG EVO-LOG

# Installer les dépendances système requises au runtime (WeasyPrint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdEVO-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copier les wheels et installer
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copier le code source
COPY --chown=EVO-LOG:EVO-LOG . .

# Si le contexte de build Docker est la racine du repo, rapatrier les fichiers de EVO-LOG-backend au premier niveau /app
RUN if [ -d "/app/EVO-LOG-backend" ]; then cp -rn /app/EVO-LOG-backend/* /app/ && rm -rf /app/EVO-LOG-backend; fi

RUN chmod +x start.sh

# Passer à l'utilisateur non-root
USER EVO-LOG
ENV XDG_CACHE_HOME=/home/EVO-LOG/.cache

EXPOSE 8000

# Commande de démarrage
CMD ["./start.sh"]
