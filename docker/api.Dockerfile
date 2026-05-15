# ===========================================================================
# AgileIQ — docker/api.Dockerfile
#
# Image de l'API Flask. Build MULTI-STAGE :
#   - stage "builder" : compile et installe les dépendances Python
#   - stage "runtime" : image finale, minimale, SANS outils de compilation
#
# Avantages : image finale légère, surface d'attaque réduite, build cacheable.
#
# Build :   docker build -f docker/api.Dockerfile -t agileiq-api .
# Contexte : la racine du projet (.)
# ===========================================================================

# ---------------------------------------------------------------------------
# ARGs globaux (modifiables au build : --build-arg ENV=production)
# ---------------------------------------------------------------------------
ARG PYTHON_VERSION=3.11
ARG ENV=development

# ===========================================================================
# STAGE 1 — builder : installe les dépendances dans un virtualenv isolé
# ===========================================================================
FROM python:${PYTHON_VERSION}-slim AS builder

# Réinjecte l'ARG (les ARG ne traversent pas les stages automatiquement)
ARG ENV

# Variables d'environnement de build
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# Dépendances système nécessaires UNIQUEMENT à la compilation
# (psycopg, etc.). Elles ne seront PAS dans l'image finale.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crée un virtualenv isolé : on le copiera tel quel dans l'image finale
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# On copie d'ABORD les requirements seuls : tant qu'ils ne changent pas,
# Docker réutilise le cache de cette couche (builds ultra-rapides).
COPY requirements/ ./requirements/

# Installe dev.txt en développement, prod.txt sinon
RUN if [ "$ENV" = "development" ]; then \
        pip install -r requirements/dev.txt ; \
    else \
        pip install -r requirements/prod.txt ; \
    fi

# ===========================================================================
# STAGE 2 — runtime : image finale exécutée en production
# ===========================================================================
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG ENV

# Variables d'environnement runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=${ENV}

# Dépendances système runtime UNIQUEMENT (libpq pour psycopg, pas le -dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# SÉCURITÉ : on ne tourne JAMAIS en root. Création d'un utilisateur dédié.
RUN groupadd --system agileiq && \
    useradd --system --gid agileiq --create-home --home-dir /home/agileiq agileiq

# Récupère le virtualenv déjà construit dans le stage builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Copie du code applicatif (le .dockerignore exclut .venv, .git, etc.)
COPY --chown=agileiq:agileiq . .

# Bascule sur l'utilisateur non privilégié
USER agileiq

# Port exposé par Gunicorn / le serveur de dev
EXPOSE 8000

# HEALTHCHECK : Docker saura si le conteneur est réellement "sain"
# (l'endpoint /health sera créé dans la sous-étape 0.4)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Commande par défaut : Gunicorn (production-ready).
# En développement, docker-compose surchargera cette commande par le
# serveur Flask avec rechargement à chaud.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.wsgi:app"]
