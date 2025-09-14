# Keyless Fallbacks Runbook

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE RUNBOOK**  
**Purpose**: Operational guide for managing keyless fallbacks in SarvanOM v2

---

## 🎯 **Overview**

Keyless fallbacks ensure continuous service availability when API keys are not configured or providers are unavailable. This runbook covers monitoring, troubleshooting, and operational procedures for keyless fallback systems.

---

## 🔧 **Configuration**

### **Feature Flag**
```bash
# Enable keyless fallbacks (default: true)
KEYLESS_FALLBACKS_ENABLED=true

# Disable keyless fallbacks (requires all primary providers configured)
KEYLESS_FALLBACKS_ENABLED=false
```

### **Provider Configuration**
Keyless fallbacks are automatically enabled when:
- Primary providers are not configured
- Primary providers are unavailable
- `KEYLESS_FALLBACKS_ENABLED=true`

---

## 📊 **Monitoring & Metrics**

### **Key Metrics to Monitor**

#### **Fallback Usage Metrics**
```prometheus
# Keyless fallback usage by lane and provider
sarvanom_keyless_fallback_total{lane="web_search", provider="duckduckgo", source="keyless"}

# Provider failure rates
sarvanom_provider_failures_total{lane="news", provider="guardian", failure_type="timeout"}

# Provider timeout rates
sarvanom_provider_timeouts_total{lane="markets", provider="alphavantage"}

# Provider latency
sarvanom_provider_latency_seconds{lane="web_search", provider="brave", source="keyed"}
```

#### **Health Status Metrics**
```prometheus
# Provider health status (1=healthy, 0=unhealthy)
sarvanom_provider_health_status{lane="news", provider="guardian"}

# Auto-demotion threshold
sarvanom_auto_demotion_threshold
```

### **Alerting Thresholds**

#### **Critical Alerts**
- **Provider Failure Rate**: > 50% for any provider
- **Keyless Fallback Usage**: > 80% for any lane
- **Auto-Demotion Triggered**: Any provider auto-demoted

#### **Warning Alerts**
- **Provider Failure Rate**: > 30% for any provider
- **Keyless Fallback Usage**: > 50% for any lane
- **Provider Timeout Rate**: > 20% for any provider

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. High Keyless Fallback Usage**

**Symptoms:**
- `sarvanom_keyless_fallback_total` metrics showing high usage
- Users reporting slower response times
- Fallback badges appearing frequently in UI

**Diagnosis:**
```bash
# Check provider configuration
python scripts/ci-gates.py --gates provider-keys --verbose

# Check provider health
python scripts/ci-gates.py --gates performance --verbose

# Review provider status in settings
# Navigate to Settings > Data Sources
```

**Resolution:**
1. **Configure Missing API Keys**: Add missing primary provider keys
2. **Check Provider Health**: Investigate why primary providers are failing
3. **Review Budget Compliance**: Ensure keyless providers meet latency budgets
4. **Update Provider Order**: Adjust provider priority if needed

#### **2. Provider Auto-Demotion**

**Symptoms:**
- Providers marked as "unhealthy" in metrics
- Auto-demotion alerts triggered
- Reduced provider availability

**Diagnosis:**
```bash
# Check provider health summary
python -c "
from sarvanom.shared.observability.fallback_metrics import get_fallback_metrics
metrics = get_fallback_metrics()
health = metrics.get_provider_health_summary()
for key, stats in health.items():
    if stats['auto_demotion_eligible']:
        print(f'{key}: {stats}')
"
```

**Resolution:**
1. **Investigate Root Cause**: Check provider API status, network connectivity
2. **Temporary Fix**: Restart affected services
3. **Long-term Fix**: Update provider configuration, add fallback providers
4. **Monitor Recovery**: Track provider health metrics post-fix

#### **3. Budget Compliance Violations**

**Symptoms:**
- End-to-end latency exceeding 5/7/10s budgets
- Provider timeout rates > 20%
- CI gates failing budget compliance checks

**Diagnosis:**
```bash
# Run budget compliance gates
python scripts/ci-gates.py --gates budget-compliance --verbose

# Check provider latency metrics
# Review Prometheus dashboard for sarvanom_provider_latency_seconds
```

**Resolution:**
1. **Optimize Provider Timeouts**: Reduce per-provider timeout budgets
2. **Add More Providers**: Increase provider redundancy
3. **Implement Circuit Breakers**: Add circuit breaker patterns
4. **Review Provider Order**: Optimize provider execution order

---

## 🔄 **Operational Procedures**

### **Daily Health Checks**

#### **1. Provider Status Check**
```bash
# Run comprehensive health check
make ci-gates

# Check specific lanes
python scripts/ci-gates.py --lane web_search --verbose
python scripts/ci-gates.py --lane news --verbose
python scripts/ci-gates.py --lane markets --verbose
```

#### **2. Metrics Review**
- Review Prometheus dashboard for provider health
- Check fallback usage trends
- Monitor provider latency percentiles
- Review auto-demotion status

#### **3. Configuration Validation**
```bash
# Validate provider key configuration
python scripts/ci-gates.py --gates provider-keys --verbose

# Check keyless fallback coverage
python scripts/ci-gates.py --gates keyless-fallbacks --verbose
```

### **Weekly Maintenance**

#### **1. Provider Performance Review**
- Analyze provider success rates
- Review provider latency trends
- Identify underperforming providers
- Plan provider configuration updates

#### **2. Budget Compliance Audit**
- Review end-to-end latency budgets
- Check per-provider timeout compliance
- Validate CI gate thresholds
- Update budget configurations if needed

#### **3. Documentation Updates**
- Update provider status documentation
- Review and update this runbook
- Update operational procedures
- Share lessons learned with team

### **Incident Response**

#### **1. Provider Outage**
1. **Immediate Response**:
   - Check provider health metrics
   - Verify keyless fallback activation
   - Monitor user impact
   - Notify stakeholders

2. **Investigation**:
   - Check provider API status
   - Review network connectivity
   - Analyze error logs
   - Identify root cause

3. **Resolution**:
   - Implement temporary fixes
   - Update provider configuration
   - Test fallback mechanisms
   - Monitor recovery

4. **Post-Incident**:
   - Document incident details
   - Update runbook procedures
   - Implement preventive measures
   - Conduct team review

#### **2. High Fallback Usage**
1. **Immediate Response**:
   - Check provider configuration
   - Verify API key validity
   - Monitor user experience
   - Assess impact

2. **Investigation**:
   - Review provider health
   - Check API key expiration
   - Analyze usage patterns
   - Identify configuration issues

3. **Resolution**:
   - Configure missing API keys
   - Update provider settings
   - Optimize provider order
   - Test configuration

4. **Post-Incident**:
   - Update monitoring alerts
   - Improve configuration management
   - Enhance documentation
   - Conduct team review

---

## 📈 **Performance Optimization**

### **Provider Order Optimization**

#### **Current Provider Order**
```yaml
web_search:
  keyed: [brave_search, serpapi]
  keyless: [duckduckgo, wikipedia, stackexchange, mdn]

news:
  keyed: [guardian, newsapi]
  keyless: [gdelt, hn_algolia, rss]

markets:
  keyed: [alphavantage, finnhub, fmp]
  keyless: [stooq, sec_edgar]
```

#### **Optimization Guidelines**
1. **Prioritize by Performance**: Order providers by latency and success rate
2. **Balance Cost vs Quality**: Consider cost implications of provider order
3. **Monitor Trends**: Adjust order based on performance trends
4. **Test Changes**: Validate order changes in staging environment

### **Budget Optimization**

#### **Current Budgets**
- **Per-Provider Timeout**: ≤ 800ms
- **End-to-End Budgets**: 5s (simple), 7s (technical), 10s (research)
- **Auto-Demotion Threshold**: 30% failure rate

#### **Optimization Strategies**
1. **Dynamic Timeouts**: Adjust timeouts based on provider performance
2. **Circuit Breakers**: Implement circuit breaker patterns
3. **Load Balancing**: Distribute load across multiple providers
4. **Caching**: Implement aggressive caching for keyless providers

---

## 🔍 **Debugging Tools**

### **CLI Tools**
```bash
# Run all CI gates
make ci-gates

# Run specific gate types
make ci-gates-provider-keys
make ci-gates-budget
make ci-gates-performance

# Check specific lanes
python scripts/ci-gates.py --lane web_search --verbose
python scripts/ci-gates.py --lane news --verbose
python scripts/ci-gates.py --lane markets --verbose
```

### **API Endpoints**
```bash
# Check provider health
curl http://localhost:8000/health

# Check provider status
curl http://localhost:8000/api/providers/status

# Check fallback metrics
curl http://localhost:8000/api/metrics/fallbacks
```

### **Log Analysis**
```bash
# Check provider logs
docker logs sarvanom-retrieval-1 | grep "fallback"

# Check error logs
docker logs sarvanom-retrieval-1 | grep "ERROR"

# Check provider health logs
docker logs sarvanom-retrieval-1 | grep "provider.*health"
```

---

## 📚 **References**

### **Related Documentation**
- [Environment Contract Matrix](../contracts/env_matrix.md)
- [CI Quality Gates](../ci/gates.md)
- [Provider Configuration](../providers/README.md)
- [Metrics Catalog](../observability/metrics.md)

### **External Resources**
- [Prometheus Querying](https://prometheus.io/docs/prometheus/latest/querying/)
- [Grafana Dashboards](https://grafana.com/docs/)
- [Provider API Documentation](https://docs.sarvanom.com/providers/)

---

## 📞 **Support Contacts**

### **Internal Teams**
- **Platform Team**: platform@sarvanom.com
- **DevOps Team**: devops@sarvanom.com
- **On-Call**: +1-555-ONCALL

### **External Support**
- **Provider Support**: Check individual provider documentation
- **Infrastructure**: infrastructure@sarvanom.com
- **Security**: security@sarvanom.com

---

**Last Updated**: September 9, 2025  
**Next Review**: October 9, 2025  
**Owner**: Platform Team
