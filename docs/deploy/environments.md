# Deployment Environments

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: DevOps Team  

## Overview

This document defines the deployment environments for SarvanOM v2, including development, staging, and production environments. Each environment is configured with appropriate resources, security measures, and monitoring to support the application lifecycle.

## Environment Architecture

### 1. Environment Overview

#### 1.1 Environment Types
- **Development**: Local development and testing
- **Staging**: Pre-production validation and testing
- **Production**: Live production environment

#### 1.2 Environment Characteristics
- **Isolation**: Each environment is completely isolated
- **Scalability**: Environments scale based on demand
- **Security**: Appropriate security measures for each environment
- **Monitoring**: Comprehensive monitoring and alerting

### 2. Development Environment

#### 2.1 Purpose
- **Local Development**: Developer workstation setup
- **Feature Testing**: Individual feature development and testing
- **Integration Testing**: Service integration testing
- **Debugging**: Development debugging and troubleshooting

#### 2.2 Infrastructure
- **Compute**: Local Docker containers
- **Storage**: Local volumes and bind mounts
- **Networking**: Local Docker network
- **Databases**: Local containerized databases

#### 2.3 Configuration
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  gateway:
    build: .
    ports:
      - "8004:8004"
    environment:
      - ENV=development
      - DEBUG=true
      - LOG_LEVEL=debug
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - postgres
      - redis
      - qdrant
      - arangodb
      - meilisearch

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=sarvanom_dev
      - POSTGRES_USER=sarvanom
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  arangodb:
    image: arangodb:3.11
    environment:
      - ARANGO_ROOT_PASSWORD=dev_password
    ports:
      - "8529:8529"
    volumes:
      - arangodb_data:/var/lib/arangodb3

  meilisearch:
    image: getmeili/meilisearch:latest
    environment:
      - MEILI_MASTER_KEY=dev_master_key
    ports:
      - "7700:7700"
    volumes:
      - meilisearch_data:/meili_data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  arangodb_data:
  meilisearch_data:
  ollama_data:
```

#### 2.4 Access Control
- **Authentication**: Local development accounts
- **Authorization**: Full access for developers
- **Network**: Local network access only
- **Data**: Non-sensitive test data

### 3. Staging Environment

#### 3.1 Purpose
- **Pre-production Testing**: Full system testing
- **Performance Testing**: Load and stress testing
- **Security Testing**: Security validation
- **User Acceptance Testing**: Stakeholder validation

#### 3.2 Infrastructure
- **Compute**: Kubernetes cluster (3 nodes)
- **Storage**: Persistent volumes
- **Networking**: Load balancer and ingress
- **Databases**: Managed database services

#### 3.3 Configuration
```yaml
# k8s/staging/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sarvanom-staging
  labels:
    environment: staging
    app: sarvanom

---
# k8s/staging/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sarvanom-config
  namespace: sarvanom-staging
data:
  ENV: staging
  DEBUG: "false"
  LOG_LEVEL: info
  DATABASE_URL: postgresql://sarvanom:staging_password@postgres-staging:5432/sarvanom_staging
  REDIS_URL: redis://redis-staging:6379
  QDRANT_URL: http://qdrant-staging:6333
  ARANGODB_URL: http://arangodb-staging:8529
  MEILISEARCH_URL: http://meilisearch-staging:7700
  OLLAMA_URL: http://ollama-staging:11434

---
# k8s/staging/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: sarvanom-secrets
  namespace: sarvanom-staging
type: Opaque
data:
  POSTGRES_PASSWORD: c3RhZ2luZ19wYXNzd29yZA==
  REDIS_PASSWORD: c3RhZ2luZ19yZWRpc19wYXNzd29yZA==
  ARANGO_ROOT_PASSWORD: c3RhZ2luZ19hcmFuZ29fcGFzc3dvcmQ=
  MEILI_MASTER_KEY: c3RhZ2luZ19tZWlsaV9tYXN0ZXJfa2V5
  OPENAI_API_KEY: c3RhZ2luZ19vcGVuYWlfYXBpX2tleQ==
  ANTHROPIC_API_KEY: c3RhZ2luZ19hbnRocm9waWNfYXBpX2tleQ==
  HUGGINGFACE_API_KEY: c3RhZ2luZ19odWdnaW5nZmFjZV9hcGlfa2V5
```

#### 3.4 Access Control
- **Authentication**: Staging user accounts
- **Authorization**: Limited access for testing
- **Network**: VPN access required
- **Data**: Anonymized production-like data

### 4. Production Environment

#### 4.1 Purpose
- **Live Production**: Production traffic and users
- **High Availability**: 99.9% uptime requirement
- **Performance**: Sub-10 second response times
- **Security**: Enterprise-grade security

#### 4.2 Infrastructure
- **Compute**: Kubernetes cluster (5+ nodes)
- **Storage**: High-performance persistent volumes
- **Networking**: Load balancer, CDN, and ingress
- **Databases**: Managed database services with replication

#### 4.3 Configuration
```yaml
# k8s/production/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sarvanom-production
  labels:
    environment: production
    app: sarvanom

---
# k8s/production/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sarvanom-config
  namespace: sarvanom-production
data:
  ENV: production
  DEBUG: "false"
  LOG_LEVEL: warning
  DATABASE_URL: postgresql://sarvanom:${POSTGRES_PASSWORD}@postgres-production:5432/sarvanom_production
  REDIS_URL: redis://redis-production:6379
  QDRANT_URL: http://qdrant-production:6333
  ARANGODB_URL: http://arangodb-production:8529
  MEILISEARCH_URL: http://meilisearch-production:7700
  OLLAMA_URL: http://ollama-production:11434

---
# k8s/production/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: sarvanom-secrets
  namespace: sarvanom-production
type: Opaque
data:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD_B64}
  REDIS_PASSWORD: ${REDIS_PASSWORD_B64}
  ARANGO_ROOT_PASSWORD: ${ARANGO_ROOT_PASSWORD_B64}
  MEILI_MASTER_KEY: ${MEILI_MASTER_KEY_B64}
  OPENAI_API_KEY: ${OPENAI_API_KEY_B64}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY_B64}
  HUGGINGFACE_API_KEY: ${HUGGINGFACE_API_KEY_B64}
```

#### 4.4 Access Control
- **Authentication**: Production user accounts
- **Authorization**: Role-based access control
- **Network**: Secure network access
- **Data**: Production data with encryption

## Environment Deployment

### 1. Deployment Pipeline

#### 1.1 Development Deployment
```bash
# Local development setup
git clone https://github.com/sarvanom/sarvanom-v2.git
cd sarvanom-v2
cp .env.example .env
docker-compose -f docker-compose.dev.yml up -d
```

#### 1.2 Staging Deployment
```bash
# Staging deployment
kubectl apply -f k8s/staging/
kubectl rollout status deployment/gateway -n sarvanom-staging
kubectl rollout status deployment/retrieval -n sarvanom-staging
kubectl rollout status deployment/synthesis -n sarvanom-staging
```

#### 1.3 Production Deployment
```bash
# Production deployment
kubectl apply -f k8s/production/
kubectl rollout status deployment/gateway -n sarvanom-production
kubectl rollout status deployment/retrieval -n sarvanom-production
kubectl rollout status deployment/synthesis -n sarvanom-production
```

### 2. Environment Promotion

#### 2.1 Promotion Process
- **Development → Staging**: Automated on merge to staging branch
- **Staging → Production**: Manual approval required
- **Rollback**: Automated rollback on failure

#### 2.2 Promotion Criteria
- **Tests**: All tests must pass
- **Performance**: Performance benchmarks met
- **Security**: Security scans passed
- **Approval**: Stakeholder approval required

### 3. Environment Monitoring

#### 3.1 Health Checks
- **Service Health**: All services responding
- **Database Health**: Database connectivity
- **External Services**: External API connectivity
- **Performance**: Response time monitoring

#### 3.2 Alerting
- **Critical Alerts**: Immediate notification
- **Warning Alerts**: Escalated notification
- **Info Alerts**: Logged for review
- **Recovery Alerts**: System recovery notifications

## Environment Security

### 1. Network Security

#### 1.1 Network Isolation
- **VPC**: Virtual private cloud isolation
- **Subnets**: Private and public subnet separation
- **Security Groups**: Firewall rules and access control
- **NACLs**: Network access control lists

#### 1.2 Network Monitoring
- **Traffic Analysis**: Network traffic monitoring
- **Intrusion Detection**: Security threat detection
- **DDoS Protection**: Distributed denial of service protection
- **VPN Access**: Secure remote access

### 2. Data Security

#### 2.1 Data Encryption
- **At Rest**: Database and storage encryption
- **In Transit**: TLS/SSL encryption
- **Key Management**: Secure key management
- **Backup Encryption**: Encrypted backups

#### 2.2 Access Control
- **Authentication**: Multi-factor authentication
- **Authorization**: Role-based access control
- **Audit Logging**: Comprehensive audit trails
- **Session Management**: Secure session handling

### 3. Application Security

#### 3.1 Security Headers
- **CORS**: Cross-origin resource sharing
- **CSP**: Content security policy
- **HSTS**: HTTP strict transport security
- **X-Frame-Options**: Clickjacking protection

#### 3.2 Input Validation
- **Sanitization**: Input sanitization
- **Validation**: Input validation
- **Rate Limiting**: API rate limiting
- **SQL Injection**: SQL injection prevention

## Environment Scaling

### 1. Horizontal Scaling

#### 1.1 Auto-scaling
- **CPU-based**: Scale based on CPU usage
- **Memory-based**: Scale based on memory usage
- **Custom Metrics**: Scale based on custom metrics
- **Scheduled Scaling**: Scale based on schedule

#### 1.2 Load Balancing
- **Application Load Balancer**: Layer 7 load balancing
- **Network Load Balancer**: Layer 4 load balancing
- **Health Checks**: Load balancer health checks
- **Sticky Sessions**: Session affinity

### 2. Vertical Scaling

#### 2.1 Resource Allocation
- **CPU**: CPU resource allocation
- **Memory**: Memory resource allocation
- **Storage**: Storage resource allocation
- **Network**: Network resource allocation

#### 2.2 Performance Tuning
- **Database Tuning**: Database performance optimization
- **Cache Tuning**: Cache performance optimization
- **Application Tuning**: Application performance optimization
- **Network Tuning**: Network performance optimization

## Environment Backup

### 1. Backup Strategy

#### 1.1 Database Backups
- **Automated Backups**: Daily automated backups
- **Point-in-time Recovery**: Point-in-time recovery
- **Cross-region Backups**: Cross-region backup replication
- **Backup Encryption**: Encrypted backups

#### 1.2 Application Backups
- **Configuration Backups**: Configuration backup
- **Code Backups**: Source code backup
- **Data Backups**: Application data backup
- **Metadata Backups**: Metadata backup

### 2. Disaster Recovery

#### 2.1 Recovery Procedures
- **RTO**: Recovery time objective
- **RPO**: Recovery point objective
- **Failover**: Automated failover
- **Failback**: Automated failback

#### 2.2 Testing
- **DR Testing**: Disaster recovery testing
- **Backup Testing**: Backup restoration testing
- **Failover Testing**: Failover testing
- **Recovery Testing**: Recovery testing

## Environment Maintenance

### 1. Regular Maintenance

#### 1.1 Updates
- **Security Updates**: Security patch updates
- **Feature Updates**: Feature updates
- **Bug Fixes**: Bug fix updates
- **Performance Updates**: Performance updates

#### 1.2 Monitoring
- **Health Monitoring**: System health monitoring
- **Performance Monitoring**: Performance monitoring
- **Security Monitoring**: Security monitoring
- **Capacity Monitoring**: Capacity monitoring

### 2. Maintenance Windows

#### 2.1 Scheduled Maintenance
- **Weekly**: Weekly maintenance windows
- **Monthly**: Monthly maintenance windows
- **Quarterly**: Quarterly maintenance windows
- **Annual**: Annual maintenance windows

#### 2.2 Emergency Maintenance
- **Critical Issues**: Immediate maintenance
- **Security Issues**: Security-related maintenance
- **Performance Issues**: Performance-related maintenance
- **Availability Issues**: Availability-related maintenance

---

## Appendix

### A. Environment Configuration Files
- `docker-compose.dev.yml` - Development environment
- `k8s/staging/` - Staging environment configuration
- `k8s/production/` - Production environment configuration
- `.env.example` - Environment variable template

### B. Deployment Scripts
- `scripts/deploy-dev.sh` - Development deployment script
- `scripts/deploy-staging.sh` - Staging deployment script
- `scripts/deploy-production.sh` - Production deployment script
- `scripts/rollback.sh` - Rollback script

### C. Monitoring Configuration
- `monitoring/prometheus.yml` - Prometheus configuration
- `monitoring/grafana/` - Grafana dashboards
- `monitoring/alertmanager.yml` - Alert manager configuration
- `monitoring/blackbox.yml` - Blackbox exporter configuration
