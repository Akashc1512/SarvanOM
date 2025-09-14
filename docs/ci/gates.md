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

### 4. Doc→Code Compliance Gates

#### 4.1 Environment Variable Compliance
- **Unknown Keys**: No undocumented environment variables in code
- **Synonyms**: No non-canonical environment variable names (e.g., FINNHUB_API_KEY vs ALPHAVANTAGE_KEY)
- **Canonical Names**: All environment variables must use documented canonical names from `docs/contracts/env_matrix.md`

#### 4.2 Backend Compliance
- **Budget Enforcement**: Timeouts/budgets in config match 5/7/10s and Guided Prompt ≤500ms median / p95 ≤800ms
- **Lane Order**: Provider execution order per lane (Web, News, Markets, Vector, KG, Keyword) matches documentation
- **Router Policy**: Router only mounts OpenAI/Anthropic for text and Gemini for vision when keys exist; otherwise graceful disable
- **Metrics Emission**: Required tags: `trace_id`, `lane`, `provider`, `fallback_used`, `timeout`
- **Main.py Wiring**: FastAPI app registers all routers referenced in docs, mounts `/health` & `/metrics`

#### 4.3 Frontend Compliance
- **Routes Parity**: Next.js route tree matches documented routes in `docs/frontend/routes.md`
- **Canonical Components**: Pages import canonical components (by name) and not deprecated ones
- **Guided Prompt Presence**: Every "Prompting surface" has `GuidedPromptModal` wired, default ON, Settings toggle discoverable
- **Fallback UX**: Search/Comprehensive pages show "ⓘ via fallback" badge when keyless provider is used

### 5. Provider Key Validation Gates

#### 5.1 Required Key Validation
- **Web Search Lane**: Must have BRAVE_SEARCH_API_KEY OR SERPAPI_KEY (both missing = CI failure)
- **News Lane**: Must have GUARDIAN_OPEN_PLATFORM_KEY OR NEWSAPI_KEY (both missing = CI failure)
- **Markets Lane**: Must have ALPHAVANTAGE_KEY (FINNHUB_KEY and FMP_API_KEY are optional)
- **LLM Providers**: Must have OPENAI_API_KEY OR ANTHROPIC_API_KEY (both missing = CI failure)
- **LMM Providers**: GEMINI_API_KEY is optional for vision features

#### 5.2 Keyless Fallback Validation
- **Budget Compliance**: Keyless-only lanes must still meet 5/7/10s end-to-end budgets
- **Provider Timeout**: Each keyless provider must respect ≤800ms per-provider timeout
- **Graceful Degradation**: System must handle missing keys without crashes

#### 5.3 Key Presence Check
- **Lane Validation**: If a lane has no keys and keyless is disabled, fail with actionable message
- **Actionable Messages**: Clear instructions on how to resolve key absence (add keys or enable keyless fallbacks)

### 6. Integration Gates

#### 6.1 Service Integration
- **Health Checks**: All services must respond to `/health` endpoint
- **Database Connectivity**: All database connections must be verified
- **External APIs**: All external service integrations must be tested

#### 6.2 End-to-End Testing
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

#### 1.1 Doc→Code Compliance Suite
```yaml
name: Doc→Code Compliance Suite
on: [pull_request, push]
jobs:
  doc-code-compliance:
    name: Doc→Code Compliance Suite
    runs-on: ubuntu-latest
    steps:
      - name: Run Doc→Code Compliance Suite
        run: python scripts/compliance_checker.py
      - name: Check compliance results and fail if issues found
        run: |
          # Check for unknown environment keys
          # Check for synonyms
          # Check backend compliance
          # Check frontend compliance
      - name: Upload compliance reports
        uses: actions/upload-artifact@v3
        with:
          name: compliance-reports
          path: |
            reports/compliance/
            reports/wiring/
            reports/duplications/
```

#### 1.2 Key Presence Check
```yaml
  key-presence-check:
    name: Key Presence Check
    runs-on: ubuntu-latest
    steps:
      - name: Check key presence and keyless fallback configuration
        run: |
          # Check for required keys in each lane
          # Validate keyless fallback configuration
          # Provide actionable messages for missing keys
        env:
          KEYLESS_FALLBACKS_ENABLED: true
          # API keys would be set as secrets in real CI
```

#### 1.3 PR Validation
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

#### 1.4 Release Validation
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

#### 2.1 Doc→Code Compliance Thresholds
- **Unknown Environment Keys**: 0 (any unknown key = build failure)
- **Environment Variable Synonyms**: 0 (any synonym = build failure)
- **Missing Required Endpoints**: 0 (any missing endpoint = build failure)
- **Incorrect Lane Order**: 0 (any incorrect order = build failure)
- **Per-Provider Timeouts**: ≤800ms (any timeout >800ms = build failure)
- **Missing Guided Prompt Budget**: 0 (missing budget = build failure)

#### 2.2 Code Quality Thresholds
- **Test Coverage**: ≥ 80%
- **Code Duplication**: ≤ 5%
- **Cyclomatic Complexity**: ≤ 10
- **Technical Debt Ratio**: ≤ 5%

#### 2.3 Performance Thresholds
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
- `.github/workflows/ci-gates.yml` (Main CI gates workflow)
- `.github/workflows/doc-code-compliance.yml` (Doc→Code compliance suite)
- `.github/workflows/pr-validation.yml`
- `.github/workflows/release-validation.yml`
- `pyproject.toml` (ruff, mypy config)
- `.eslintrc.js` (ESLint config)
- `jest.config.js` (test config)

### B. Compliance Suite Scripts
- `scripts/compliance_checker.py` (Doc→Code compliance checker)
- `scripts/wiring_checker.py` (Backend/frontend wiring validation)
- `scripts/duplicate_scanner.py` (Duplicate/dead code scanner)

### C. Generated Reports
- `reports/compliance/backend.md` (Backend compliance status)
- `reports/compliance/frontend.md` (Frontend compliance status)
- `reports/compliance/env_gaps.json` (Environment variable gaps)
- `reports/wiring/backend_endpoints.md` (Backend endpoint validation)
- `reports/wiring/frontend_routes.md` (Frontend route validation)
- `reports/duplications/backend.csv` (Backend duplications)
- `reports/duplications/frontend.csv` (Frontend duplications)
- `docs/review/dup_candidates.csv` (Duplication candidates)
- `docs/review/deprecation_notes.md` (Deprecation recommendations)

### D. Monitoring Tools
- **GitHub Actions**: CI/CD pipeline
- **Prometheus**: Performance metrics
- **Grafana**: Dashboards and alerting
- **Slack**: Notifications and alerts

### E. Quality Tools
- **Ruff**: Python linting and formatting
- **MyPy**: Python type checking
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **Safety**: Python security scanning
- **Bandit**: Python security analysis
