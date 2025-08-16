#!/bin/bash

# SarvanOM Enterprise Backend Startup Script
# MAANG/OpenAI/Perplexity Standards Implementation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.enterprise.yml"
ENV_FILE="$PROJECT_ROOT/.env.docker"
LOG_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data"

# Service ports
GATEWAY_PORT=8000
AUTH_PORT=8001
SEARCH_PORT=8002
SYNTHESIS_PORT=8003
FACT_CHECK_PORT=8004
RETRIEVAL_PORT=8005
NGINX_PORT=80
REDIS_PORT=6379
POSTGRES_PORT=5432
QDRANT_PORT=6333
MEILISEARCH_PORT=7700

# Monitoring ports
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
JAEGER_PORT=16686

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$PROJECT_ROOT/nginx/ssl"
    mkdir -p "$PROJECT_ROOT/monitoring/grafana/dashboards"
    mkdir -p "$PROJECT_ROOT/monitoring/grafana/datasources"
    
    log_success "Directories created"
}

check_environment() {
    log_info "Checking environment configuration..."
    
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning "Environment file not found. Creating default .env.docker..."
        cat > "$ENV_FILE" << EOF
# SarvanOM Enterprise Environment Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_DB=sarvanom_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://redis:6379

# Vector Database Configuration
QDRANT_URL=http://qdrant:6333
MEILI_MASTER_KEY=your_master_key_here

# Monitoring Configuration
GRAFANA_PASSWORD=admin

# API Configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_here
CORS_ORIGINS=http://localhost:3000,https://sarvanom.com

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OLLAMA_BASE_URL=http://localhost:11434

# HuggingFace Configuration
HUGGINGFACE_API_KEY=your_huggingface_key_here
EOF
        log_warning "Please update $ENV_FILE with your actual configuration values"
    fi
    
    log_success "Environment configuration checked"
}

start_services() {
    log_info "Starting SarvanOM Enterprise Backend..."
    
    # Start core services
    docker-compose -f "$COMPOSE_FILE" up -d \
        redis \
        postgres \
        qdrant \
        meilisearch
    
    log_info "Waiting for infrastructure services to be ready..."
    sleep 10
    
    # Start application services
    docker-compose -f "$COMPOSE_FILE" up -d \
        auth \
        search \
        synthesis \
        fact-check \
        retrieval \
        gateway
    
    log_info "Waiting for application services to be ready..."
    sleep 15
    
    # Start load balancer
    docker-compose -f "$COMPOSE_FILE" up -d nginx
    
    log_success "All services started"
}

wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for $service_name to be ready on port $port..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "$service_name is ready"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name failed to start within expected time"
    return 1
}

health_check() {
    log_info "Performing health checks..."
    
    local services=(
        "Gateway:8000"
        "Auth:8001"
        "Search:8002"
        "Synthesis:8003"
        "Fact-Check:8004"
        "Retrieval:8005"
        "Nginx:80"
    )
    
    local failed_services=()
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if ! wait_for_service "$name" "$port"; then
            failed_services+=("$name")
        fi
    done
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services are healthy"
        return 0
    else
        log_error "The following services failed health checks: ${failed_services[*]}"
        return 1
    fi
}

start_monitoring() {
    log_info "Starting monitoring stack..."
    
    docker-compose -f "$COMPOSE_FILE" --profile monitoring up -d
    
    log_info "Waiting for monitoring services to be ready..."
    sleep 10
    
    log_success "Monitoring stack started"
    log_info "Prometheus: http://localhost:$PROMETHEUS_PORT"
    log_info "Grafana: http://localhost:$GRAFANA_PORT (admin/admin)"
    log_info "Jaeger: http://localhost:$JAEGER_PORT"
}

show_status() {
    log_info "SarvanOM Enterprise Backend Status:"
    echo
    
    # Service status
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo
    log_info "Service URLs:"
    echo "  🌐 Main API: http://localhost:$NGINX_PORT"
    echo "  🔍 API Gateway: http://localhost:$GATEWAY_PORT"
    echo "  📚 API Documentation: http://localhost:$GATEWAY_PORT/docs"
    echo "  🔐 Authentication: http://localhost:$AUTH_PORT"
    echo "  🔎 Search: http://localhost:$SEARCH_PORT"
    echo "  🧠 Synthesis: http://localhost:$SYNTHESIS_PORT"
    echo "  ✅ Fact Check: http://localhost:$FACT_CHECK_PORT"
    echo "  📖 Retrieval: http://localhost:$RETRIEVAL_PORT"
    echo
    
    log_info "Infrastructure:"
    echo "  🗄️  PostgreSQL: localhost:$POSTGRES_PORT"
    echo "  🔄 Redis: localhost:$REDIS_PORT"
    echo "  🧮 Qdrant: localhost:$QDRANT_PORT"
    echo "  🔍 Meilisearch: localhost:$MEILISEARCH_PORT"
    echo
    
    log_info "Monitoring:"
    echo "  📊 Prometheus: http://localhost:$PROMETHEUS_PORT"
    echo "  📈 Grafana: http://localhost:$GRAFANA_PORT"
    echo "  🔍 Jaeger: http://localhost:$JAEGER_PORT"
    echo
    
    log_info "Health Check:"
    echo "  curl http://localhost/health"
    echo
}

cleanup() {
    log_info "Cleaning up..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    log_success "Cleanup completed"
}

main() {
    echo "🚀 SarvanOM Enterprise Backend Startup"
    echo "======================================"
    echo
    
    # Parse command line arguments
    case "${1:-start}" in
        "start")
            check_prerequisites
            create_directories
            check_environment
            start_services
            if health_check; then
                show_status
                log_success "SarvanOM Enterprise Backend is ready!"
            else
                log_error "Some services failed to start properly"
                exit 1
            fi
            ;;
        "monitoring")
            start_monitoring
            ;;
        "health")
            health_check
            ;;
        "status")
            show_status
            ;;
        "stop")
            cleanup
            ;;
        "restart")
            cleanup
            sleep 2
            main start
            ;;
        *)
            echo "Usage: $0 {start|monitoring|health|status|stop|restart}"
            echo
            echo "Commands:"
            echo "  start      - Start all services"
            echo "  monitoring - Start monitoring stack"
            echo "  health     - Perform health checks"
            echo "  status     - Show service status"
            echo "  stop       - Stop all services"
            echo "  restart    - Restart all services"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'log_error "Script interrupted"; cleanup; exit 1' INT TERM

# Run main function
main "$@"
