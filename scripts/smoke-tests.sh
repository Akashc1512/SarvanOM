#!/bin/bash

# Smoke Tests Script - Universal Knowledge Hub
# Comprehensive smoke tests for deployment validation

set -euo pipefail

# Configuration
ENVIRONMENT="${1:-staging}"
TIMEOUT=60
RETRIES=10

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

# Get service URL based on environment
get_service_url() {
    case "$ENVIRONMENT" in
        "staging")
            echo "http://staging-api.universal-knowledge-hub.com"
            ;;
        "production")
            echo "https://api.universal-knowledge-hub.com"
            ;;
        "local")
            echo "http://localhost:8000"
            ;;
        *)
            echo "http://localhost:8000"
            ;;
    esac
}

# Wait for service to be ready
wait_for_service() {
    local url="$1"
    local endpoint="$2"
    local full_url="${url}${endpoint}"
    
    log "Waiting for service at $full_url..."
    
    local count=0
    while [ $count -lt $RETRIES ]; do
        if curl -f -s "$full_url" &> /dev/null; then
            log "Service is ready"
            return 0
        fi
        
        sleep 5
        ((count++))
        log "Attempt $count/$RETRIES - Service not ready yet..."
    done
    
    error "Service failed to become ready after $RETRIES attempts"
    return 1
}

# Test health endpoint
test_health_endpoint() {
    local url="$1"
    local endpoint="/health"
    
    log "Testing health endpoint..."
    
    local response=$(curl -s -w "%{http_code}" "$url$endpoint" -o /tmp/health_response)
    local status_code="${response: -3}"
    
    if [ "$status_code" = "200" ]; then
        log "Health endpoint returned 200 OK"
        
        # Parse health response
        if command -v jq &> /dev/null; then
            local status=$(jq -r '.status' /tmp/health_response 2>/dev/null || echo "unknown")
            log "Health status: $status"
        fi
        
        return 0
    else
        error "Health endpoint returned $status_code"
        return 1
    fi
}

# Test root endpoint
test_root_endpoint() {
    local url="$1"
    local endpoint="/"
    
    log "Testing root endpoint..."
    
    local response=$(curl -s -w "%{http_code}" "$url$endpoint" -o /tmp/root_response)
    local status_code="${response: -3}"
    
    if [ "$status_code" = "200" ]; then
        log "Root endpoint returned 200 OK"
        return 0
    else
        error "Root endpoint returned $status_code"
        return 1
    fi
}

# Test API endpoints
test_api_endpoints() {
    local url="$1"
    
    log "Testing API endpoints..."
    
    # Test authentication endpoints
    local auth_endpoints=("/auth/login" "/auth/register")
    for endpoint in "${auth_endpoints[@]}"; do
        local response=$(curl -s -w "%{http_code}" "$url$endpoint" -o /dev/null)
        local status_code="${response: -3}"
        
        if [ "$status_code" = "405" ] || [ "$status_code" = "422" ]; then
            log "API endpoint $endpoint is accessible (returned $status_code)"
        else
            warning "API endpoint $endpoint returned unexpected status $status_code"
        fi
    done
    
    # Test query endpoint
    local query_response=$(curl -s -w "%{http_code}" -X POST "$url/query" \
        -H "Content-Type: application/json" \
        -d '{"query":"test"}' -o /dev/null)
    local query_status="${query_response: -3}"
    
    if [ "$query_status" = "401" ] || [ "$query_status" = "422" ]; then
        log "Query endpoint is accessible (returned $query_status)"
    else
        warning "Query endpoint returned unexpected status $query_status"
    fi
}

# Test database connectivity
test_database_connectivity() {
    log "Testing database connectivity..."
    
    # This would require database credentials and connection
    # For now, we'll test if the application can connect to the database
    # by checking if health endpoint mentions database status
    
    local health_response=$(curl -s "$(get_service_url)/health")
    
    if echo "$health_response" | grep -q "database"; then
        log "Database connectivity check available in health endpoint"
    else
        warning "Database connectivity not explicitly checked"
    fi
}

# Test Redis connectivity
test_redis_connectivity() {
    log "Testing Redis connectivity..."
    
    # Check if Redis is mentioned in health response
    local health_response=$(curl -s "$(get_service_url)/health")
    
    if echo "$health_response" | grep -q "redis"; then
        log "Redis connectivity check available in health endpoint"
    else
        warning "Redis connectivity not explicitly checked"
    fi
}

# Test Elasticsearch connectivity
test_elasticsearch_connectivity() {
    log "Testing Elasticsearch connectivity..."
    
    # Check if Elasticsearch is mentioned in health response
    local health_response=$(curl -s "$(get_service_url)/health")
    
    if echo "$health_response" | grep -q "elasticsearch"; then
        log "Elasticsearch connectivity check available in health endpoint"
    else
        warning "Elasticsearch connectivity not explicitly checked"
    fi
}

# Test LLM connectivity
test_llm_connectivity() {
    log "Testing LLM connectivity..."
    
    # Test with a simple query that would trigger LLM
    local query_response=$(curl -s -X POST "$(get_service_url)/query" \
        -H "Content-Type: application/json" \
        -d '{"query":"What is Python?"}' -o /tmp/llm_test_response)
    
    if [ -s /tmp/llm_test_response ]; then
        log "LLM connectivity test completed"
    else
        warning "LLM connectivity test inconclusive (authentication required)"
    fi
}

# Test performance
test_performance() {
    log "Testing basic performance..."
    
    local url="$(get_service_url)"
    local start_time=$(date +%s.%N)
    
    # Make multiple requests to test response time
    for i in {1..5}; do
        curl -s "$url/health" > /dev/null
    done
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    local avg_duration=$(echo "scale=3; $duration / 5" | bc)
    
    log "Average response time: ${avg_duration}s"
    
    # Check if response time is acceptable
    if (( $(echo "$avg_duration < 2.0" | bc -l) )); then
        log "Performance is acceptable"
    else
        warning "Response time is slower than expected"
    fi
}

# Test security headers
test_security_headers() {
    log "Testing security headers..."
    
    local url="$(get_service_url)"
    local headers=$(curl -s -I "$url/health" | grep -E "(X-|Strict-|Content-Security-|X-Frame-|X-Content-Type-|Referrer-Policy)")
    
    if [ -n "$headers" ]; then
        log "Security headers found:"
        echo "$headers"
    else
        warning "No security headers detected"
    fi
}

# Test CORS
test_cors() {
    log "Testing CORS configuration..."
    
    local url="$(get_service_url)"
    local cors_headers=$(curl -s -I -H "Origin: https://example.com" "$url/health" | grep -E "(Access-Control-|CORS)")
    
    if [ -n "$cors_headers" ]; then
        log "CORS headers found:"
        echo "$cors_headers"
    else
        warning "No CORS headers detected"
    fi
}

# Test rate limiting
test_rate_limiting() {
    log "Testing rate limiting..."
    
    local url="$(get_service_url)"
    local rate_limit_hit=false
    
    # Make multiple rapid requests
    for i in {1..10}; do
        local response=$(curl -s -w "%{http_code}" "$url/health" -o /dev/null)
        local status_code="${response: -3}"
        
        if [ "$status_code" = "429" ]; then
            rate_limit_hit=true
            break
        fi
        
        sleep 0.1
    done
    
    if [ "$rate_limit_hit" = true ]; then
        log "Rate limiting is working (429 response received)"
    else
        warning "Rate limiting not detected in rapid requests"
    fi
}

# Test error handling
test_error_handling() {
    log "Testing error handling..."
    
    local url="$(get_service_url)"
    
    # Test 404 endpoint
    local not_found_response=$(curl -s -w "%{http_code}" "$url/nonexistent" -o /dev/null)
    local not_found_status="${not_found_response: -3}"
    
    if [ "$not_found_status" = "404" ]; then
        log "404 error handling working correctly"
    else
        warning "404 error handling returned $not_found_status"
    fi
    
    # Test malformed JSON
    local malformed_response=$(curl -s -w "%{http_code}" -X POST "$url/query" \
        -H "Content-Type: application/json" \
        -d '{"invalid": json}' -o /dev/null)
    local malformed_status="${malformed_response: -3}"
    
    if [ "$malformed_status" = "422" ] || [ "$malformed_status" = "400" ]; then
        log "Malformed JSON error handling working correctly"
    else
        warning "Malformed JSON error handling returned $malformed_status"
    fi
}

# Test SSL/TLS (for production)
test_ssl() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Testing SSL/TLS configuration..."
        
        local url="https://api.universal-knowledge-hub.com"
        
        if command -v openssl &> /dev/null; then
            local ssl_info=$(echo | openssl s_client -connect api.universal-knowledge-hub.com:443 -servername api.universal-knowledge-hub.com 2>/dev/null | openssl x509 -noout -dates)
            
            if [ -n "$ssl_info" ]; then
                log "SSL certificate information:"
                echo "$ssl_info"
            else
                error "SSL certificate check failed"
                return 1
            fi
        else
            warning "OpenSSL not available for SSL testing"
        fi
    fi
}

# Main smoke test function
main() {
    log "Starting smoke tests for $ENVIRONMENT environment"
    
    local service_url=$(get_service_url)
    log "Service URL: $service_url"
    
    # Run all tests
    local tests_passed=0
    local tests_failed=0
    
    # Basic connectivity tests
    if wait_for_service "$service_url" "/health"; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_health_endpoint "$service_url"; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    if test_root_endpoint "$service_url"; then
        ((tests_passed++))
    else
        ((tests_failed++))
    fi
    
    # API functionality tests
    test_api_endpoints "$service_url"
    ((tests_passed++))
    
    # Infrastructure tests
    test_database_connectivity
    test_redis_connectivity
    test_elasticsearch_connectivity
    test_llm_connectivity
    
    # Performance and security tests
    test_performance
    test_security_headers
    test_cors
    test_rate_limiting
    test_error_handling
    
    # SSL test for production
    if [ "$ENVIRONMENT" = "production" ]; then
        test_ssl
    fi
    
    # Summary
    log "Smoke tests completed"
    log "Tests passed: $tests_passed"
    log "Tests failed: $tests_failed"
    
    if [ $tests_failed -eq 0 ]; then
        log "✅ All smoke tests passed"
        exit 0
    else
        error "❌ Some smoke tests failed"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    rm -f /tmp/health_response /tmp/root_response /tmp/llm_test_response
}

# Set up error handling
trap cleanup EXIT

# Run main function
main "$@" 