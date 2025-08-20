# =============================================================================
# SarvanOM Docker Compose Management
# Optimized for Windows 11 Docker Desktop (WSL2 backend)
# =============================================================================

.PHONY: help up down build logs clean restart health-check test-docker-health doctor

# Default target
help:
	@echo "SarvanOM Docker Compose Management"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo "  up          - Start all services with .env.docker"
	@echo "  down         - Stop all services"
	@echo "  build        - Build all services"
	@echo "  logs         - Show logs for all services"
	@echo "  clean        - Remove all containers, networks, and volumes"
	@echo "  restart      - Restart all services"
	@echo "  health-check - Check health of all services"
	@echo "  test-docker-health - Run comprehensive Docker health tests"
	@echo "  doctor       - Check development environment setup"
	@echo ""

# Start all services with .env.docker
up:
	@echo "Starting SarvanOM services with .env.docker..."
	docker compose --env-file .env.docker up --build -d
	@echo "Services started. Check logs with 'make logs'"

# Stop all services
down:
	@echo "Stopping SarvanOM services..."
	docker compose down
	@echo "Services stopped."

# Build all services
build:
	@echo "Building SarvanOM services..."
	docker compose --env-file .env.docker build
	@echo "Build completed."

# Show logs for all services
logs:
	@echo "Showing logs for all services..."
	docker compose logs -f

# Clean up everything
clean:
	@echo "Cleaning up Docker resources..."
	docker compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup completed."

# Restart all services
restart:
	@echo "Restarting all services..."
	docker compose restart
	@echo "Services restarted."

# Health check for all services
health-check:
	@echo "Checking health of all services..."
	@echo "Backend:"
	@curl -f http://localhost:8000/health/basic || echo "Backend not healthy"
	@echo "Frontend:"
	@curl -f http://localhost:3000 || echo "Frontend not healthy"
	@echo "Ollama:"
	@curl -f http://localhost:11434/api/tags || echo "Ollama not healthy"
	@echo "Meilisearch:"
	@curl -f http://localhost:7700/version || echo "Meilisearch not healthy"
	@echo "ArangoDB:"
	@curl -f http://localhost:8529/_api/version || echo "ArangoDB not healthy"
	@echo "Qdrant:"
	@curl -f http://localhost:6333/health || echo "Qdrant not healthy"
	@echo "PostgreSQL:"
	@docker exec sarvanom-postgres pg_isready -U postgres -d sarvanom_db || echo "PostgreSQL not healthy"
	@echo "Redis:"
	@docker exec sarvanom-redis redis-cli ping || echo "Redis not healthy"

# Test Docker health with Python script
test-docker-health:
	@echo "Running comprehensive Docker health tests..."
	python test_docker_health.py

# Check development environment setup
doctor:
	@echo "Checking development environment setup..."
	python scripts/dev_check.py

# Windows-specific commands
windows-up:
	@echo "Starting services for Windows 11..."
	docker compose --env-file .env.docker up --build -d
	@echo "Services started. Access at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Ollama:   http://localhost:11434"

windows-down:
	@echo "Stopping services for Windows 11..."
	docker compose down
	@echo "Services stopped."

# Development commands
dev-up:
	@echo "Starting development environment..."
	docker compose --env-file .env.docker up --build -d
	@echo "Development environment started."

dev-logs:
	@echo "Showing development logs..."
	docker compose logs -f sarvanom_backend frontend

# Production commands
prod-up:
	@echo "Starting production environment..."
	docker compose --env-file .env.docker -f docker-compose.yml up --build -d
	@echo "Production environment started."

# Utility commands
status:
	@echo "Service Status:"
	docker compose ps

volumes:
	@echo "Docker Volumes:"
	docker volume ls

networks:
	@echo "Docker Networks:"
	docker network ls

# Data directory setup
setup-data-dirs:
	@echo "Setting up data directories..."
	mkdir -p data/postgres data/redis data/meilisearch data/arangodb data/arangodb-apps data/qdrant data/ollama
	@echo "Data directories created."

# Pre-flight checks
preflight:
	@echo "Running pre-flight checks..."
	@echo "Checking Docker Desktop..."
	docker version || (echo "Docker Desktop not running. Please start Docker Desktop." && exit 1)
	@echo "Checking .env.docker file..."
	test -f .env.docker || (echo ".env.docker file not found. Please create it from env.docker.template." && exit 1)
	@echo "Checking data directories..."
	make setup-data-dirs
	@echo "Pre-flight checks completed."

# Quick start
quick-start: preflight up
	@echo "SarvanOM is starting up..."
	@echo "This may take a few minutes for all services to be healthy."
	@echo "Run 'make health-check' to verify all services are running."
	@echo "Run 'make logs' to view service logs."

# =============================================================================
# Code Garden - Code Cleanup and Refactoring Tools
# =============================================================================

.PHONY: cg-audit cg-plan cg-apply cg-preview cg-split cg-restore cg-syntax

cg-audit:
	@if [ "$(OS)" = "Windows_NT" ]; then \
		powershell -ExecutionPolicy Bypass -File scripts/code_garden/run_audit.ps1; \
	else \
		bash scripts/code_garden/run_audit.sh; \
	fi

cg-plan:
	@python scripts/code_garden/parse_reports.py

cg-apply:
	@python scripts/code_garden/apply_plan.py

cg-preview:
	@CG_SPLIT_LINES=500 python scripts/code_garden/split_large_modules.py

cg-split:
	@python scripts/code_garden/apply_refactor.py

cg-restore:
	@echo "Restore by copying files from latest archive/cg_* back to their original paths"
	@ls -1d archive/cg_* | tail -n 1 || true

cg-syntax:
	@python scripts/code_garden/check_syntax.py 