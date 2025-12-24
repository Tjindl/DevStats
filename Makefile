.PHONY: help up down logs install migrate run setup activate

# Variables
# Detect OS and set VENV_BIN
ifeq ($(OS),Windows_NT)
VENV_BIN := .venv/Scripts
else
VENV_BIN := .venv/bin
endif

PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
ALEMBIC := $(VENV_BIN)/alembic
UVICORN := $(VENV_BIN)/uvicorn
DOCKER_COMPOSE := docker compose

help:
	@echo "Available commands:"
	@echo "  make up       - Start Docker services (Postgres)"
	@echo "  make down     - Stop Docker services"
	@echo "  make logs     - View Docker logs"
	@echo "  make install  - Install Python dependencies"
	@echo "  make migrate  - Run database migrations"
	@echo "  make run      - Start the backend server"
	@echo "  make setup    - Full setup (install deps, start DB, migrate)"
	@echo "  make activate - Show command to activate venv"

activate:
	@echo "source $(VENV_BIN)/activate"

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

install:
	$(PIP) install -r requirements.txt

migrate:
	$(ALEMBIC) -c backend/alembic.ini upgrade head

run:
	$(PYTHON) -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

setup: install up migrate
