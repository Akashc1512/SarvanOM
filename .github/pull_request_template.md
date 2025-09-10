# Pull Request Template - SarvanOM v2

## 📋 **Acceptance Checklist**

**PR Number**: PR-X  
**Feature**: [Brief description]  
**Related Documentation**: [Link to relevant docs]

### **Implementation Requirements**
- [ ] Implementation follows v2 documentation specifications
- [ ] Performance budgets respected (5/7/10s, Guided Prompt ≤500ms)
- [ ] Qdrant used as only vector DB
- [ ] No existing .env keys renamed
- [ ] New optional keys documented in `docs/contracts/env_matrix.md`

### **Code Quality**
- [ ] Follows naming conventions in `docs/contracts/naming_map.md`
- [ ] Passes lint rules in `docs/contracts/lint_rules.md`
- [ ] Type checking passes (mypy/tsc)
- [ ] Test coverage ≥80% for new code

### **Guided Prompt Integration** (if applicable)
- [ ] Guided Prompt feature implemented per `docs/prompting/*`
- [ ] Privacy constraints enforced (no raw draft storage)
- [ ] Accessibility requirements met (WCAG AA)
- [ ] Latency budgets respected with auto-skip rules
- [ ] KPIs emitted per `docs/observability/metrics.md`

### **Security & Privacy**
- [ ] Security headers implemented per `docs/security/http_headers.md`
- [ ] Data handling follows `docs/security/data_handling.md`
- [ ] Rate limiting implemented per `docs/security/rate_limit_and_abuse.md`
- [ ] PII redaction working correctly

### **Testing**
- [ ] Test matrix coverage per `docs/tests/matrix.md`
- [ ] SLA validation per `docs/tests/sla_playbook.md`
- [ ] Guided Prompt test scenarios included
- [ ] Performance tests validate budget requirements

### **Documentation**
- [ ] Documentation updated for new features
- [ ] API contracts documented
- [ ] Configuration options documented
- [ ] Breaking changes documented

### **Observability**
- [ ] Metrics emitted per `docs/observability/metrics.md`
- [ ] Tracing implemented per `docs/observability/tracing.md`
- [ ] Dashboard configuration per `docs/observability/dashboards.md`
- [ ] Error handling and logging implemented

### **Deployment**
- [ ] Environment configuration documented
- [ ] Deployment procedures tested
- [ ] Rollback procedures documented
- [ ] Health checks implemented

---

## 📝 **Description**

[Describe what this PR implements]

## 🔗 **Related Issues**

[Link to related issues or documentation]

## 🧪 **Testing**

[Describe testing performed]

## 📊 **Performance Impact**

[Describe any performance implications]

## 🔒 **Security Considerations**

[Describe any security implications]

## 📚 **Documentation Updates**

[List documentation files updated]

---

**Reviewer Checklist:**
- [ ] All acceptance criteria met
- [ ] Code follows v2 specifications
- [ ] Performance budgets validated
- [ ] Security requirements satisfied
- [ ] Documentation complete
