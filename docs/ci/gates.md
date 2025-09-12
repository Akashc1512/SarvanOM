# CI/CD Quality Gates

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Engineering Team  

## Overview

This document defines the quality gates and merge blockers that enforce code quality, security, and performance standards across the SarvanOM v2 codebase. All changes must pass these gates before being merged to any release branch.

## Merge Blockers

### 1. Code Quality Gates

#### 1.1 Linting & Formatting
- **Python**: `ruff check` and `ruff format` must pass
- **TypeScript/JavaScript**: `eslint` and `prettier` must pass
- **Configuration**: All config files must be valid YAML/JSON

#### 1.2 Type Checking
- **Python**: `mypy` with strict mode enabled
- **TypeScript**: `tsc --noEmit` must pass
- **Coverage**: Minimum 80% test coverage for new code

#### 1.3 Security Scanning
- **Dependencies**: `safety` for Python, `npm audit` for Node.js
- **Secrets**: No hardcoded secrets or API keys
- **SAST**: Static analysis security testing via GitHub Actions

### 2. Performance Gates

#### 2.1 Backend Performance
- **API Response Time**: < 5s for simple queries, < 7s for technical, < 10s for research
- **Memory Usage**: < 2GB per service instance
- **Database Queries**: < 100ms for simple queries, < 500ms for complex

#### 2.2 Frontend Performance
- **Lighthouse Score**: > 90 for Performance, Accessibility, Best Practices
- **Bundle Size**: < 1MB for main bundle
- **First Contentful Paint**: < 2s

### 3. Guided Prompt Confirmation Gates

#### 3.1 Refinement Performance Gates
- **Refinement Latency**: p95 ≤ 800ms, p99 ≤ 1000ms
- **Refinement Accept Rate**: ≥ 30% on staging for 48h
- **Refinement Quality**: No degradation in downstream query quality
- **Refinement Error Rate**: < 5% for refinement failures

#### 3.2 Guided Prompt Accessibility Gates
- **Keyboard Navigation**: All refinement UI elements must be keyboard accessible
- **Screen Reader Support**: ARIA labels and roles must be properly implemented
- **Color Contrast**: WCAG AA compliance for all refinement UI elements
- **Focus Management**: Proper focus handling in refinement modal

#### 3.3 Guided Prompt Security Gates
- **PII Redaction**: All PII must be redacted from refinement data
- **Data Storage**: No raw user queries stored without explicit consent
- **Consent Management**: Proper consent tracking and management
- **Privacy Compliance**: GDPR/CCPA compliance for refinement data

### 4. Provider Key Validation Gates

#### 4.1 Required Key Validation
- **Web Search Lane**: Must have BRAVE_SEARCH_API_KEY OR SERPAPI_KEY (both missing = CI failure)
- **News Lane**: Must have GUARDIAN_OPEN_PLATFORM_KEY OR NEWSAPI_KEY (both missing = CI failure)
- **Markets Lane**: Must have ALPHAVANTAGE_KEY (FINNHUB_KEY and FMP_API_KEY are optional)
- **LLM Providers**: Must have OPENAI_API_KEY OR ANTHROPIC_API_KEY (both missing = CI failure)
- **LMM Providers**: GEMINI_API_KEY is optional for vision features

#### 4.2 Keyless Fallback Validation
- **Budget Compliance**: Keyless-only lanes must still meet 5/7/10s end-to-end budgets
- **Provider Timeout**: Each keyless provider must respect ≤800ms per-provider timeout
- **Graceful Degradation**: System must handle missing keys without crashes

### 5. Integration Gates

#### 5.1 Service Integration
- **Health Checks**: All services must respond to `/health` endpoint
- **Database Connectivity**: All database connections must be verified
- **External APIs**: All external service integrations must be tested

#### 4.2 End-to-End Testing
- **Critical Paths**: User registration, query processing, result display
- **Cross-Service**: Gateway → Services → Database → Response flow
- **Error Handling**: Graceful degradation and error recovery

## Release Channels

### 1. Development Channel (`dev`)
- **Branch**: `develop`
- **Gates**: Code quality, basic integration tests
- **Deployment**: Automatic to dev environment
- **Purpose**: Feature development and integration

### 2. Staging Channel (`staging`)
- **Branch**: `release/v2`
- **Gates**: All quality gates + performance benchmarks
- **Deployment**: Manual approval required
- **Purpose**: Pre-production validation

### 3. Production Channel (`prod`)
- **Branch**: `main`
- **Gates**: All gates + security audit + load testing
- **Deployment**: Canary deployment with rollback capability
- **Purpose**: Production release

## Quality Gate Configuration

### 1. GitHub Actions Workflows

#### 1.1 PR Validation
```yaml
name: PR Validation
on: [pull_request]
jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - name: Code Quality
        run: |
          ruff check
          mypy
          pytest --cov
      - name: Security Scan
        run: |
          safety check
          npm audit
      - name: Performance Test
        run: |
          pytest tests/performance/
```

#### 1.2 Release Validation
```yaml
name: Release Validation
on: [push]
jobs:
  full-validation:
    runs-on: ubuntu-latest
    steps:
      - name: Full Test Suite
        run: |
          pytest tests/
          npm test
      - name: Load Testing
        run: |
          k6 run tests/load/
      - name: Security Audit
        run: |
          bandit -r .
          npm audit --audit-level=high
```

### 2. Gate Thresholds

#### 2.1 Code Quality Thresholds
- **Test Coverage**: ≥ 80%
- **Code Duplication**: ≤ 5%
- **Cyclomatic Complexity**: ≤ 10
- **Technical Debt Ratio**: ≤ 5%

#### 2.2 Performance Thresholds
- **API Latency**: P95 < 5s, P99 < 10s
- **Throughput**: ≥ 100 requests/second
- **Error Rate**: ≤ 0.1%
- **Availability**: ≥ 99.9%

## Gate Enforcement

### 1. Automatic Enforcement
- **PR Checks**: All gates must pass before merge
- **Branch Protection**: Required status checks enabled
- **Auto-merge**: Disabled until all gates pass

### 2. Manual Override
- **Emergency Fixes**: Requires 2+ senior engineer approval
- **Documentation**: Must be documented in ADR
- **Follow-up**: Must be addressed in next sprint

### 3. Gate Failure Handling
- **Immediate**: Block merge and notify team
- **Investigation**: Root cause analysis within 24h
- **Resolution**: Fix or adjust thresholds within 48h

## Monitoring & Alerting

### 1. Gate Status Dashboard
- **Real-time**: Current gate status for all branches
- **Historical**: Gate pass/fail trends over time
- **Metrics**: Performance and quality trends

### 2. Alerts
- **Gate Failures**: Immediate Slack notification
- **Performance Degradation**: Alert if thresholds exceeded
- **Security Issues**: Immediate escalation to security team

## Gate Maintenance

### 1. Regular Review
- **Monthly**: Review gate effectiveness and thresholds
- **Quarterly**: Update gates based on new requirements
- **Annually**: Comprehensive gate strategy review

### 2. Continuous Improvement
- **Feedback Loop**: Collect developer feedback on gates
- **Optimization**: Reduce false positives and improve accuracy
- **Automation**: Increase automation where possible

## Compliance & Audit

### 1. Audit Trail
- **Gate Results**: All gate results logged and retained
- **Override History**: All manual overrides documented
- **Performance Data**: Historical performance metrics

### 2. Compliance Reporting
- **Monthly**: Gate compliance report to engineering leadership
- **Quarterly**: Quality metrics and trends analysis
- **Annual**: Comprehensive quality assessment

---

## Appendix

### A. Gate Configuration Files
- `.github/workflows/pr-validation.yml`
- `.github/workflows/release-validation.yml`
- `pyproject.toml` (ruff, mypy config)
- `.eslintrc.js` (ESLint config)
- `jest.config.js` (test config)

### B. Monitoring Tools
- **GitHub Actions**: CI/CD pipeline
- **Prometheus**: Performance metrics
- **Grafana**: Dashboards and alerting
- **Slack**: Notifications and alerts

### C. Quality Tools
- **Ruff**: Python linting and formatting
- **MyPy**: Python type checking
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **Safety**: Python security scanning
- **Bandit**: Python security analysis
