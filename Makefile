# Universal Knowledge Hub - Development Makefile
# 
# This Makefile provides comprehensive development commands for the Universal
# Knowledge Hub platform. It includes setup, development, testing, building,
# and deployment commands with proper error handling and documentation.
#
# Features:
# - One-command setup and installation
# - Development server management
# - Comprehensive testing suite
# - Code quality tools (linting, formatting)
# - Docker container management
# - Database operations
# - Security auditing
# - Monitoring and health checks
# - Production deployment
# - Documentation generation
#
# Usage:
#   make help                    # Show all available commands
#   make setup                   # Complete project setup
#   make dev                     # Start development servers
#   make test                    # Run all tests
#   make docker-up               # Start Docker services
#
# Environment Variables:
#   ENVIRONMENT: Set to 'development', 'staging', or 'production'
#   LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
#   DOCKER_COMPOSE_FILE: Custom docker-compose file path
#
# Dependencies:
#   - Node.js >= 18.0.0
#   - Python >= 3.13.5
#   - Docker and Docker Compose
#   - Git
#
# Authors: Universal Knowledge Platform Engineering Team
# Version: 1.0.0 (2024-12-28)
# License: MIT

.PHONY: help install dev build test lint format clean docker-setup docker-build docker-up docker-down logs setup

# Default target
help:
	@echo "Universal Knowledge Hub - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install     - Install all dependencies (Node.js and Python)"
	@echo "  setup       - Complete project setup with environment configuration"
	@echo ""
	@echo "Development:"
	@echo "  dev         - Start development servers (frontend + backend)"
	@echo "  dev:frontend- Start frontend development server"
	@echo "  dev:backend - Start backend development server"
	@echo ""
	@echo "Building:"
	@echo "  build       - Build all services"
	@echo "  build:frontend - Build frontend application"
	@echo "  build:backend  - Build backend services"
	@echo ""
	@echo "Testing:"
	@echo "  test        - Run all tests"
	@echo "  test:unit   - Run unit tests"
	@echo "  test:integration - Run integration tests"
	@echo "  test:e2e    - Run end-to-end tests"
	@echo "  test:performance - Run performance tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        - Run linting for all code"
	@echo "  format      - Format all code"
	@echo ""
	@echo "Docker:"
	@echo "  docker-setup - Setup Docker environment"
	@echo "  docker-build - Build all Docker images"
	@echo "  docker-up   - Start all services with Docker Compose"
	@echo "  docker-down - Stop all Docker services"
	@echo "  logs        - Show Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean all build artifacts"
	@echo "  logs        - Show application logs"

# Installation
install:
	@echo "Installing Node.js dependencies..."
	npm install
	@echo "Installing Python dependencies..."
	pip install -e .[dev,test,security]
	@echo "Installation complete!"

setup: install
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "Created .env file from template. Please configure your environment variables."; \
	else \
		echo ".env file already exists."; \
	fi
	@echo "Setup complete!"

# Development
dev:
	@echo "Starting development servers..."
	npm run dev

dev:frontend:
	@echo "Starting frontend development server..."
	npm run dev:frontend

dev:backend:
	@echo "Starting backend development server..."
	npm run dev:backend

# Building
build:
	@echo "Building all services..."
	npm run build

build:frontend:
	@echo "Building frontend..."
	npm run build:frontend

build:backend:
	@echo "Building backend services..."
	npm run build:backend

# Testing
test:
	@echo "Running all tests..."
	npm run test

test:unit:
	@echo "Running unit tests..."
	npm run test:unit

test:integration:
	@echo "Running integration tests..."
	npm run test:integration

test:e2e:
	@echo "Running end-to-end tests..."
	npm run test:e2e

test:performance:
	@echo "Running performance tests..."
	npm run test:performance

# Code Quality
lint:
	@echo "Running linting..."
	npm run lint

format:
	@echo "Formatting code..."
	npm run format

# Docker
docker-setup:
	@echo "Setting up Docker environment..."
	@if [ ! -f .env.docker ]; then \
		cp env.docker.template .env.docker; \
		echo "Created .env.docker file from template. Please configure your environment variables."; \
	else \
		echo ".env.docker file already exists."; \
	fi
	docker-compose down -v
	docker-compose build --no-cache

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose --env-file .env.docker up --build -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Docker health check
docker-health:
	@echo "Checking Docker service health..."
	python test_docker_health.py

# Docker with environment file
up:
	docker-compose --env-file .env.docker up --build -d

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose --env-file .env.docker up --build -d

# Utilities
clean:
	@echo "Cleaning build artifacts..."
	npm run clean
	@echo "Removing Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Removing test artifacts..."
	rm -rf .pytest_cache/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	@echo "Clean complete!"

# Service-specific commands
start:api-gateway:
	@echo "Starting API Gateway..."
	cd services/api-gateway && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

start:auth-service:
	@echo "Starting Auth Service..."
	cd services/auth-service && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

start:search-service:
	@echo "Starting Search Service..."
	cd services/search-service && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002

start:synthesis-service:
	@echo "Starting Synthesis Service..."
	cd services/synthesis-service && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003

start:factcheck-service:
	@echo "Starting Fact Check Service..."
	cd services/factcheck-service && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8004

start:analytics-service:
	@echo "Starting Analytics Service..."
	cd services/analytics-service && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8005

# Database commands
db:migrate:
	@echo "Running database migrations..."
	python -m alembic upgrade head

db:seed:
	@echo "Seeding database..."
	python scripts/seed_database.py

# Security
security:audit:
	@echo "Running security audit..."
	bandit -r services/ shared/
	pip-audit

# Monitoring
monitor:logs:
	@echo "Showing application logs..."
	tail -f logs/*.log

monitor:health:
	@echo "Checking service health..."
	curl -f http://localhost:8000/health || echo "API Gateway not responding"
	curl -f http://localhost:8001/health || echo "Auth Service not responding"
	curl -f http://localhost:8002/health || echo "Search Service not responding"
	curl -f http://localhost:8003/health || echo "Synthesis Service not responding"
	curl -f http://localhost:8004/health || echo "Fact Check Service not responding"
	curl -f http://localhost:8005/health || echo "Analytics Service not responding"

# Production
prod:build:
	@echo "Building for production..."
	docker-compose -f docker-compose.prod.yml build

prod:deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

# Documentation
docs:generate:
	@echo "Generating API documentation..."
	cd services/api-gateway && python -m uvicorn main:app --reload --port 8000 &
	@sleep 5
	curl http://localhost:8000/openapi.json > docs/api/openapi.json
	@echo "API documentation generated at docs/api/openapi.json"

docs:serve:
	@echo "Serving documentation..."
	python -m http.server 8080 --directory docs/ 