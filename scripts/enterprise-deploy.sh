#!/bin/bash

# Enterprise Deployment Script - Universal Knowledge Hub
# Enterprise-grade deployment with security and monitoring

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-staging}"
NAMESPACE="knowledge-hub"
TIMEOUT=300
BACKUP_DIR="/tmp/backup-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Security checks
security_checks() {
    log "Running security checks..."
    
    # Check for hardcoded secrets
    if grep -r "sk-[a-zA-Z0-9]{20,}" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv; then
        error "Found hardcoded API keys"
        exit 1
    fi
    
    # Check for exposed credentials
    if grep -r "password.*=" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv; then
        error "Found hardcoded passwords"
        exit 1
    fi
    
    # Check for database URLs
    if grep -r "postgresql://.*:.*@" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv; then
        error "Found hardcoded database URLs"
        exit 1
    fi
    
    # Check file permissions
    find . -type f -name "*.sh" -exec chmod 755 {} \;
    find . -type f -name "*.py" -exec chmod 644 {} \;
    
    # Check for sensitive files
    if [ -f ".env" ]; then
        error ".env file should not be committed"
        exit 1
    fi
    
    log "Security checks passed"
}

# Pre-deployment validation
validate_deployment() {
    log "Validating deployment configuration..."
    
    # Check required environment variables
    required_vars=("KUBECONFIG" "DOCKER_REGISTRY" "IMAGE_TAG")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Validate Kubernetes context
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        error "Namespace $NAMESPACE does not exist"
        exit 1
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
        exit 1
    fi
    
    log "Deployment validation passed"
}

# Backup current deployment
backup_deployment() {
    log "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup Kubernetes resources
    kubectl get deployment -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/deployment.yaml" 2>/dev/null || true
    kubectl get service -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/service.yaml" 2>/dev/null || true
    kubectl get ingress -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/ingress.yaml" 2>/dev/null || true
    kubectl get configmap -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/configmap.yaml" 2>/dev/null || true
    kubectl get secret -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/secret.yaml" 2>/dev/null || true
    
    log "Backup created in $BACKUP_DIR"
}

# Deploy with rollback capability
deploy_with_rollback() {
    log "Starting deployment..."
    
    # Apply new deployment
    kubectl apply -f k8s/deployment.yaml -n "$NAMESPACE"
    
    # Wait for rollout
    if ! kubectl rollout status deployment/universal-knowledge-hub -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
        error "Deployment failed, rolling back..."
        kubectl rollout undo deployment/universal-knowledge-hub -n "$NAMESPACE"
        exit 1
    fi
    
    log "Deployment completed successfully"
}

# Health checks
health_checks() {
    log "Running health checks..."
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app=universal-knowledge-hub -n "$NAMESPACE" --timeout="${TIMEOUT}s"
    
    # Check service endpoints
    if ! kubectl get endpoints -n "$NAMESPACE" universal-knowledge-hub | grep -q "Addresses:"; then
        error "Service has no endpoints"
        exit 1
    fi
    
    # Test API health
    local retries=30
    local count=0
    while [ $count -lt $retries ]; do
        if curl -f "http://localhost:8000/health" &> /dev/null; then
            log "API health check passed"
            break
        fi
        sleep 10
        ((count++))
    done
    
    if [ $count -eq $retries ]; then
        error "API health check failed after $retries attempts"
        exit 1
    fi
    
    log "Health checks passed"
}

# Performance monitoring
performance_monitoring() {
    log "Starting performance monitoring..."
    
    # Monitor resource usage
    kubectl top pods -n "$NAMESPACE" --containers
    
    # Check for resource limits
    local cpu_usage=$(kubectl top pods -n "$NAMESPACE" --no-headers | awk '{sum+=$2} END {print sum}')
    local memory_usage=$(kubectl top pods -n "$NAMESPACE" --no-headers | awk '{sum+=$3} END {print sum}')
    
    if [ "$cpu_usage" -gt 1000 ]; then
        warning "High CPU usage: ${cpu_usage}m"
    fi
    
    if [ "$memory_usage" -gt 2048 ]; then
        warning "High memory usage: ${memory_usage}Mi"
    fi
    
    log "Performance monitoring completed"
}

# Security monitoring
security_monitoring() {
    log "Running security monitoring..."
    
    # Check for security events
    local security_events=$(kubectl get events -n "$NAMESPACE" --field-selector type=Warning | grep -i security | wc -l)
    
    if [ "$security_events" -gt 0 ]; then
        warning "Found $security_events security events"
        kubectl get events -n "$NAMESPACE" --field-selector type=Warning | grep -i security
    fi
    
    # Check network policies
    if ! kubectl get networkpolicies -n "$NAMESPACE" &> /dev/null; then
        warning "No network policies configured"
    fi
    
    log "Security monitoring completed"
}

# Database health check
database_health_check() {
    log "Checking database health..."
    
    # Get database pod
    local db_pod=$(kubectl get pods -n "$NAMESPACE" -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$db_pod" ]; then
        # Check if database is ready
        if kubectl exec "$db_pod" -n "$NAMESPACE" -- pg_isready -U postgres &> /dev/null; then
            log "Database is healthy"
        else
            error "Database is not healthy"
            exit 1
        fi
    else
        warning "Database pod not found"
    fi
}

# Redis health check
redis_health_check() {
    log "Checking Redis health..."
    
    # Get Redis pod
    local redis_pod=$(kubectl get pods -n "$NAMESPACE" -l app=redis -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$redis_pod" ]; then
        # Check if Redis is ready
        if kubectl exec "$redis_pod" -n "$NAMESPACE" -- redis-cli ping &> /dev/null; then
            log "Redis is healthy"
        else
            error "Redis is not healthy"
            exit 1
        fi
    else
        warning "Redis pod not found"
    fi
}

# Elasticsearch health check
elasticsearch_health_check() {
    log "Checking Elasticsearch health..."
    
    # Get Elasticsearch service
    local es_service=$(kubectl get svc -n "$NAMESPACE" -l app=elasticsearch -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$es_service" ]; then
        # Check Elasticsearch health
        if kubectl exec -n "$NAMESPACE" deployment/elasticsearch-master -- curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green"' 2>/dev/null; then
            log "Elasticsearch is healthy"
        else
            error "Elasticsearch is not healthy"
            exit 1
        fi
    else
        warning "Elasticsearch service not found"
    fi
}

# Smoke tests
smoke_tests() {
    log "Running smoke tests..."
    
    # Test basic functionality
    if ! curl -f "http://localhost:8000/health" &> /dev/null; then
        error "Health endpoint failed"
        exit 1
    fi
    
    # Test API endpoints
    if ! curl -f "http://localhost:8000/" &> /dev/null; then
        error "Root endpoint failed"
        exit 1
    fi
    
    log "Smoke tests passed"
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$BACKUP_DIR"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    if [ -f "$BACKUP_DIR/deployment.yaml" ]; then
        kubectl apply -f "$BACKUP_DIR/deployment.yaml" -n "$NAMESPACE"
        kubectl rollout status deployment/universal-knowledge-hub -n "$NAMESPACE" --timeout="${TIMEOUT}s"
        log "Rollback completed"
    else
        error "No backup found for rollback"
        exit 1
    fi
}

# Main deployment function
main() {
    log "Starting enterprise deployment to $ENVIRONMENT"
    
    # Set up error handling
    trap 'error "Deployment failed"; cleanup; exit 1' ERR
    trap cleanup EXIT
    
    # Run deployment steps
    security_checks
    validate_deployment
    backup_deployment
    deploy_with_rollback
    health_checks
    database_health_check
    redis_health_check
    elasticsearch_health_check
    smoke_tests
    performance_monitoring
    security_monitoring
    
    log "Deployment completed successfully"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_checks
        database_health_check
        redis_health_check
        elasticsearch_health_check
        ;;
    "security")
        security_checks
        security_monitoring
        ;;
    "performance")
        performance_monitoring
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|security|performance}"
        echo "  deploy     - Deploy application"
        echo "  rollback   - Rollback to previous version"
        echo "  health     - Run health checks"
        echo "  security   - Run security checks"
        echo "  performance- Run performance monitoring"
        exit 1
        ;;
esac 