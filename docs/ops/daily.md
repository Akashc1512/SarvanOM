# Daily Operations Runbook

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Operations Team  

## Overview

This document provides comprehensive daily operations procedures for SarvanOM v2, including system monitoring, health checks, maintenance tasks, and incident response. It serves as the primary reference for operations team members to ensure system reliability and performance.

## Daily Operations Checklist

### 1. Morning Health Check (08:00 UTC)

#### 1.1 System Health Verification
```bash
# Check overall system health
kubectl get pods -n sarvanom-production
kubectl get services -n sarvanom-production
kubectl get ingress -n sarvanom-production

# Verify all services are running
kubectl get pods -n sarvanom-production | grep -v Running
kubectl get pods -n sarvanom-production | grep -v Ready
```

#### 1.2 Database Health Check
```bash
# PostgreSQL health check
kubectl exec -it postgres-0 -n sarvanom-production -- psql -U sarvanom -d sarvanom_production -c "SELECT 1;"

# Redis health check
kubectl exec -it redis-0 -n sarvanom-production -- redis-cli ping

# Qdrant health check
kubectl exec -it qdrant-0 -n sarvanom-production -- curl -f http://localhost:6333/health

# ArangoDB health check
kubectl exec -it arangodb-0 -n sarvanom-production -- curl -f http://localhost:8529/_api/version

# Meilisearch health check
kubectl exec -it meilisearch-0 -n sarvanom-production -- curl -f http://localhost:7700/health
```

#### 1.3 External Service Connectivity
```bash
# Check external API connectivity
curl -f https://api.openai.com/v1/models
curl -f https://api.anthropic.com/v1/models
curl -f https://api-inference.huggingface.co/models

# Check Ollama connectivity
curl -f http://ollama-production:11434/api/tags
```

#### 1.4 Performance Metrics Review
```bash
# Check system resource usage
kubectl top pods -n sarvanom-production
kubectl top nodes

# Check disk usage
kubectl exec -it postgres-0 -n sarvanom-production -- df -h
kubectl exec -it qdrant-0 -n sarvanom-production -- df -h
```

### 2. Performance Monitoring (Every 2 Hours)

#### 2.1 Response Time Monitoring
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://api.sarvanom.com/health"

# Check query processing times
curl -w "@curl-format.txt" -o /dev/null -s "https://api.sarvanom.com/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "user_id": "test_user"}'
```

#### 2.2 Error Rate Monitoring
```bash
# Check error rates from logs
kubectl logs -n sarvanom-production deployment/gateway --since=2h | grep -i error | wc -l
kubectl logs -n sarvanom-production deployment/retrieval --since=2h | grep -i error | wc -l
kubectl logs -n sarvanom-production deployment/synthesis --since=2h | grep -i error | wc -l
```

#### 2.3 Resource Utilization
```bash
# Check CPU and memory usage
kubectl top pods -n sarvanom-production --sort-by=cpu
kubectl top pods -n sarvanom-production --sort-by=memory

# Check disk usage
kubectl exec -it postgres-0 -n sarvanom-production -- df -h /var/lib/postgresql/data
kubectl exec -it qdrant-0 -n sarvanom-production -- df -h /qdrant/storage
```

### 3. Log Analysis (Every 4 Hours)

#### 3.1 Error Log Analysis
```bash
# Analyze error patterns
kubectl logs -n sarvanom-production deployment/gateway --since=4h | grep -i error | sort | uniq -c | sort -nr
kubectl logs -n sarvanom-production deployment/retrieval --since=4h | grep -i error | sort | uniq -c | sort -nr
kubectl logs -n sarvanom-production deployment/synthesis --since=4h | grep -i error | sort | uniq -c | sort -nr
```

#### 3.2 Performance Log Analysis
```bash
# Analyze slow queries
kubectl logs -n sarvanom-production deployment/gateway --since=4h | grep "slow query" | sort | uniq -c | sort -nr

# Analyze timeout issues
kubectl logs -n sarvanom-production deployment/gateway --since=4h | grep "timeout" | sort | uniq -c | sort -nr
```

#### 3.3 Security Log Analysis
```bash
# Check for security events
kubectl logs -n sarvanom-production deployment/gateway --since=4h | grep -i "security\|auth\|unauthorized" | sort | uniq -c | sort -nr

# Check for suspicious activity
kubectl logs -n sarvanom-production deployment/gateway --since=4h | grep -i "suspicious\|anomaly\|attack" | sort | uniq -c | sort -nr
```

### 4. Database Maintenance (Daily at 02:00 UTC)

#### 4.1 PostgreSQL Maintenance
```bash
# Run VACUUM and ANALYZE
kubectl exec -it postgres-0 -n sarvanom-production -- psql -U sarvanom -d sarvanom_production -c "VACUUM ANALYZE;"

# Check database size
kubectl exec -it postgres-0 -n sarvanom-production -- psql -U sarvanom -d sarvanom_production -c "SELECT pg_size_pretty(pg_database_size('sarvanom_production'));"

# Check for long-running queries
kubectl exec -it postgres-0 -n sarvanom-production -- psql -U sarvanom -d sarvanom_production -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

#### 4.2 Redis Maintenance
```bash
# Check Redis memory usage
kubectl exec -it redis-0 -n sarvanom-production -- redis-cli info memory

# Check Redis key count
kubectl exec -it redis-0 -n sarvanom-production -- redis-cli dbsize

# Run Redis memory optimization
kubectl exec -it redis-0 -n sarvanom-production -- redis-cli memory purge
```

#### 4.3 Qdrant Maintenance
```bash
# Check Qdrant collection status
kubectl exec -it qdrant-0 -n sarvanom-production -- curl -s http://localhost:6333/collections | jq

# Check Qdrant storage usage
kubectl exec -it qdrant-0 -n sarvanom-production -- df -h /qdrant/storage

# Optimize Qdrant collections
kubectl exec -it qdrant-0 -n sarvanom-production -- curl -X POST http://localhost:6333/collections/documents/optimize
```

#### 4.4 ArangoDB Maintenance
```bash
# Check ArangoDB database status
kubectl exec -it arangodb-0 -n sarvanom-production -- curl -s http://localhost:8529/_api/database | jq

# Check ArangoDB storage usage
kubectl exec -it arangodb-0 -n sarvanom-production -- df -h /var/lib/arangodb3

# Run ArangoDB maintenance
kubectl exec -it arangodb-0 -n sarvanom-production -- curl -X POST http://localhost:8529/_api/admin/execute
```

#### 4.5 Meilisearch Maintenance
```bash
# Check Meilisearch index status
kubectl exec -it meilisearch-0 -n sarvanom-production -- curl -s http://localhost:7700/indexes | jq

# Check Meilisearch storage usage
kubectl exec -it meilisearch-0 -n sarvanom-production -- df -h /meili_data

# Optimize Meilisearch indexes
kubectl exec -it meilisearch-0 -n sarvanom-production -- curl -X POST http://localhost:7700/indexes/documents/settings
```

### 5. Backup Verification (Daily at 03:00 UTC)

#### 5.1 Database Backup Verification
```bash
# Verify PostgreSQL backup
aws s3 ls s3://sarvanom-backups/postgres/$(date +%Y/%m/%d)/

# Verify Redis backup
aws s3 ls s3://sarvanom-backups/redis/$(date +%Y/%m/%d)/

# Verify Qdrant backup
aws s3 ls s3://sarvanom-backups/qdrant/$(date +%Y/%m/%d)/

# Verify ArangoDB backup
aws s3 ls s3://sarvanom-backups/arangodb/$(date +%Y/%m/%d)/

# Verify Meilisearch backup
aws s3 ls s3://sarvanom-backups/meilisearch/$(date +%Y/%m/%d)/
```

#### 5.2 Application Backup Verification
```bash
# Verify configuration backup
aws s3 ls s3://sarvanom-backups/config/$(date +%Y/%m/%d)/

# Verify secrets backup
aws s3 ls s3://sarvanom-backups/secrets/$(date +%Y/%m/%d)/

# Verify logs backup
aws s3 ls s3://sarvanom-backups/logs/$(date +%Y/%m/%d)/
```

### 6. Security Monitoring (Every 6 Hours)

#### 6.1 Security Event Analysis
```bash
# Check for failed login attempts
kubectl logs -n sarvanom-production deployment/gateway --since=6h | grep "failed login" | wc -l

# Check for suspicious API usage
kubectl logs -n sarvanom-production deployment/gateway --since=6h | grep "suspicious" | wc -l

# Check for privilege escalation attempts
kubectl logs -n sarvanom-production deployment/gateway --since=6h | grep "privilege" | wc -l
```

#### 6.2 Access Control Verification
```bash
# Check user access patterns
kubectl logs -n sarvanom-production deployment/gateway --since=6h | grep "access granted" | wc -l
kubectl logs -n sarvanom-production deployment/gateway --since=6h | grep "access denied" | wc -l

# Check API key usage
kubectl logs -n sarvanom-production deployment/gateway --since=6h | grep "api key" | wc -l
```

### 7. Capacity Planning (Daily at 16:00 UTC)

#### 7.1 Resource Usage Analysis
```bash
# Analyze CPU usage trends
kubectl top pods -n sarvanom-production --sort-by=cpu | head -10

# Analyze memory usage trends
kubectl top pods -n sarvanom-production --sort-by=memory | head -10

# Analyze storage usage trends
kubectl exec -it postgres-0 -n sarvanom-production -- df -h /var/lib/postgresql/data
kubectl exec -it qdrant-0 -n sarvanom-production -- df -h /qdrant/storage
```

#### 7.2 Growth Projection
```bash
# Calculate daily growth rates
./scripts/calculate_growth_rates.sh

# Project future resource needs
./scripts/project_resource_needs.sh

# Generate capacity planning report
./scripts/generate_capacity_report.sh
```

### 8. End-of-Day Summary (Daily at 23:00 UTC)

#### 8.1 Daily Metrics Summary
```bash
# Generate daily metrics report
./scripts/generate_daily_metrics.sh

# Generate performance summary
./scripts/generate_performance_summary.sh

# Generate security summary
./scripts/generate_security_summary.sh
```

#### 8.2 Issue Tracking
```bash
# Check for unresolved issues
kubectl get events -n sarvanom-production --sort-by='.lastTimestamp' | grep -v Normal

# Check for pending alerts
kubectl get alerts -n sarvanom-production

# Update issue tracking system
./scripts/update_issue_tracking.sh
```

## Automated Monitoring Scripts

### 1. Health Check Script
```bash
#!/bin/bash
# health_check.sh

set -e

NAMESPACE="sarvanom-production"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/var/log/sarvanom/health_check_${TIMESTAMP}.log"

echo "Starting health check at $(date)" | tee -a $LOG_FILE

# Check pod status
echo "Checking pod status..." | tee -a $LOG_FILE
kubectl get pods -n $NAMESPACE | tee -a $LOG_FILE

# Check service status
echo "Checking service status..." | tee -a $LOG_FILE
kubectl get services -n $NAMESPACE | tee -a $LOG_FILE

# Check ingress status
echo "Checking ingress status..." | tee -a $LOG_FILE
kubectl get ingress -n $NAMESPACE | tee -a $LOG_FILE

# Check database connectivity
echo "Checking database connectivity..." | tee -a $LOG_FILE
kubectl exec -it postgres-0 -n $NAMESPACE -- psql -U sarvanom -d sarvanom_production -c "SELECT 1;" | tee -a $LOG_FILE

# Check external API connectivity
echo "Checking external API connectivity..." | tee -a $LOG_FILE
curl -f https://api.openai.com/v1/models | tee -a $LOG_FILE

echo "Health check completed at $(date)" | tee -a $LOG_FILE
```

### 2. Performance Monitoring Script
```bash
#!/bin/bash
# performance_monitor.sh

set -e

NAMESPACE="sarvanom-production"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/var/log/sarvanom/performance_${TIMESTAMP}.log"

echo "Starting performance monitoring at $(date)" | tee -a $LOG_FILE

# Check resource usage
echo "Checking resource usage..." | tee -a $LOG_FILE
kubectl top pods -n $NAMESPACE | tee -a $LOG_FILE

# Check response times
echo "Checking response times..." | tee -a $LOG_FILE
curl -w "@curl-format.txt" -o /dev/null -s "https://api.sarvanom.com/health" | tee -a $LOG_FILE

# Check error rates
echo "Checking error rates..." | tee -a $LOG_FILE
kubectl logs -n $NAMESPACE deployment/gateway --since=1h | grep -i error | wc -l | tee -a $LOG_FILE

echo "Performance monitoring completed at $(date)" | tee -a $LOG_FILE
```

### 3. Log Analysis Script
```bash
#!/bin/bash
# log_analysis.sh

set -e

NAMESPACE="sarvanom-production"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/var/log/sarvanom/log_analysis_${TIMESTAMP}.log"

echo "Starting log analysis at $(date)" | tee -a $LOG_FILE

# Analyze error patterns
echo "Analyzing error patterns..." | tee -a $LOG_FILE
kubectl logs -n $NAMESPACE deployment/gateway --since=4h | grep -i error | sort | uniq -c | sort -nr | tee -a $LOG_FILE

# Analyze performance issues
echo "Analyzing performance issues..." | tee -a $LOG_FILE
kubectl logs -n $NAMESPACE deployment/gateway --since=4h | grep "slow query" | sort | uniq -c | sort -nr | tee -a $LOG_FILE

# Analyze security events
echo "Analyzing security events..." | tee -a $LOG_FILE
kubectl logs -n $NAMESPACE deployment/gateway --since=4h | grep -i "security\|auth\|unauthorized" | sort | uniq -c | sort -nr | tee -a $LOG_FILE

echo "Log analysis completed at $(date)" | tee -a $LOG_FILE
```

## Alerting and Notifications

### 1. Alert Thresholds
```yaml
# Alert configuration
alerts:
  critical:
    - name: "Service Down"
      condition: "pod_status != 'Running'"
      severity: "critical"
      notification: ["email", "slack", "pagerduty"]
    
    - name: "High Error Rate"
      condition: "error_rate > 5%"
      severity: "critical"
      notification: ["email", "slack", "pagerduty"]
    
    - name: "High Response Time"
      condition: "response_time > 10s"
      severity: "critical"
      notification: ["email", "slack", "pagerduty"]
    
    - name: "Database Connection Failed"
      condition: "database_connection == false"
      severity: "critical"
      notification: ["email", "slack", "pagerduty"]
  
  warning:
    - name: "High CPU Usage"
      condition: "cpu_usage > 80%"
      severity: "warning"
      notification: ["email", "slack"]
    
    - name: "High Memory Usage"
      condition: "memory_usage > 80%"
      severity: "warning"
      notification: ["email", "slack"]
    
    - name: "High Disk Usage"
      condition: "disk_usage > 80%"
      severity: "warning"
      notification: ["email", "slack"]
    
    - name: "Slow Query"
      condition: "query_time > 5s"
      severity: "warning"
      notification: ["email", "slack"]
```

### 2. Notification Channels
```yaml
# Notification configuration
notifications:
  email:
    recipients: ["ops-team@sarvanom.com", "on-call@sarvanom.com"]
    template: "alert_email_template.html"
  
  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#alerts"
    template: "alert_slack_template.json"
  
  pagerduty:
    integration_key: "${PAGERDUTY_INTEGRATION_KEY}"
    escalation_policy: "sarvanom-ops"
```

## Escalation Procedures

### 1. Escalation Matrix
```yaml
# Escalation matrix
escalation:
  level_1:
    role: "Operations Engineer"
    response_time: "15 minutes"
    escalation_time: "30 minutes"
  
  level_2:
    role: "Senior Operations Engineer"
    response_time: "5 minutes"
    escalation_time: "15 minutes"
  
  level_3:
    role: "Engineering Manager"
    response_time: "5 minutes"
    escalation_time: "10 minutes"
  
  level_4:
    role: "CTO"
    response_time: "5 minutes"
    escalation_time: "5 minutes"
```

### 2. Escalation Triggers
```yaml
# Escalation triggers
triggers:
  automatic_escalation:
    - condition: "service_down > 15 minutes"
      escalate_to: "level_2"
    
    - condition: "error_rate > 10%"
      escalate_to: "level_2"
    
    - condition: "response_time > 30s"
      escalate_to: "level_2"
    
    - condition: "security_breach_detected"
      escalate_to: "level_3"
  
  manual_escalation:
    - condition: "complex_issue"
      escalate_to: "level_2"
    
    - condition: "business_impact"
      escalate_to: "level_3"
    
    - condition: "security_incident"
      escalate_to: "level_4"
```

## Documentation and Reporting

### 1. Daily Reports
- **System Health Report**: Overall system status and health metrics
- **Performance Report**: Response times, throughput, and resource usage
- **Security Report**: Security events, access patterns, and threat detection
- **Capacity Report**: Resource utilization and growth projections

### 2. Weekly Reports
- **Trend Analysis**: Performance and usage trends over the week
- **Issue Summary**: Resolved and outstanding issues
- **Capacity Planning**: Resource needs and scaling recommendations
- **Security Assessment**: Security posture and recommendations

### 3. Monthly Reports
- **SLA Compliance**: Service level agreement compliance metrics
- **Cost Analysis**: Infrastructure costs and optimization opportunities
- **Security Review**: Comprehensive security assessment
- **Performance Review**: Performance optimization recommendations

---

## Appendix

### A. Monitoring Tools
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Dashboards and visualization
- **Jaeger**: Distributed tracing
- **ELK Stack**: Log aggregation and analysis
- **PagerDuty**: Incident management and escalation

### B. Automation Scripts
- `scripts/health_check.sh` - System health check script
- `scripts/performance_monitor.sh` - Performance monitoring script
- `scripts/log_analysis.sh` - Log analysis script
- `scripts/backup_verification.sh` - Backup verification script
- `scripts/capacity_planning.sh` - Capacity planning script

### C. Configuration Files
- `monitoring/prometheus.yml` - Prometheus configuration
- `monitoring/grafana/` - Grafana dashboards
- `monitoring/alertmanager.yml` - Alert manager configuration
- `monitoring/blackbox.yml` - Blackbox exporter configuration
