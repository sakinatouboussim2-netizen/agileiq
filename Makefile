# ==========================================================================
# AgileIQ — Makefile
# Raccourcis pour les commandes courantes. Usage : make <cible>
# ==========================================================================
DOCKER_USER := $(shell id -u):$(shell id -g)
.PHONY: help up down restart logs ps shell test test-cov lint format \
        migrate db-shell clean pre-commit

help:  ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Docker ---------------------------------------------------------------
up:  ## Démarre la stack Docker en arrière-plan
	docker compose up -d --build

down:  ## Arrête la stack (volumes conservés)
	docker compose down

restart:  ## Redémarre uniquement l'API
	docker compose restart api

logs:  ## Logs en temps réel (Ctrl+C pour sortir)
	docker compose logs -f --tail=100

ps:  ## État des services
	docker compose ps

shell:  ## Shell bash dans le conteneur API
	docker compose exec api bash

# --- Tests ----------------------------------------------------------------
test:  ## Lance la suite de tests (pytest)
	docker compose exec api pytest

test-cov:  ## Lance les tests avec rapport de couverture
	docker compose exec api pytest --cov=app --cov-report=term-missing --cov-report=html

# --- Qualité de code -----------------------------------------------------
lint:  ## Vérifie ruff + black + mypy
	docker compose exec api bash -c "ruff check app && black --check app && mypy app"

format:  ## Applique le formatage automatique
	docker compose exec api bash -c "ruff check --fix app && black app"

pre-commit:  ## Exécute tous les hooks pre-commit (depuis l'hôte)
	pre-commit run --all-files

# --- Base de données -----------------------------------------------------
migrate:  ## Applique les migrations Alembic
	docker compose exec api flask --app app.wsgi:app db upgrade

db-shell:  ## Ouvre un psql interactif
	docker compose exec postgres psql -U $${POSTGRES_USER:-agileiq} -d $${POSTGRES_DB:-agileiq}

# --- Nettoyage -----------------------------------------------------------
clean:  ## Supprime les caches Python (pas les volumes Docker)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ==============================
# Database / Alembic
# ==============================

db-migrate:
	docker compose exec -u $(DOCKER_USER) api flask db migrate -m "$(M)"

db-init:
	docker compose exec -u $(DOCKER_USER) api flask db init
db-upgrade:
	docker compose exec api flask db upgrade

db-downgrade:
	docker compose exec api flask db downgrade

db-shell:
	docker compose exec postgres psql -U agileiq -d agileiq
