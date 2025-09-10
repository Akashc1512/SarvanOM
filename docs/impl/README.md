# SarvanOM v2 Implementation Guide

## 🎯 **Implementation Requirements**

This directory contains implementation guidelines for SarvanOM v2. All implementation must strictly follow the v2 documentation specifications.

### **Mandatory Requirements**

#### **Performance Budgets**
- **Simple Queries**: 5 seconds maximum
- **Technical Queries**: 7 seconds maximum  
- **Research/Multimedia Queries**: 10 seconds maximum
- **Guided Prompt Refinement**: ≤500ms median, p95 ≤800ms
- **Auto-skip**: If budget exceeded or <25% global budget remaining

#### **Technology Constraints**
- **Vector Database**: Qdrant is the ONLY vector DB for dev & prod
- **Environment Keys**: Do NOT rename existing .env keys
- **New Keys**: Document in `docs/contracts/env_matrix.md` with safe defaults

#### **Guided Prompt Confirmation**
- **Default**: ON for all users
- **Privacy**: No raw draft storage by default
- **Accessibility**: WCAG AA compliant, keyboard/screen reader ready
- **Latency**: Strict budget enforcement with auto-skip rules

### **Implementation Standards**

#### **Code Quality**
- Follow naming conventions in `docs/contracts/naming_map.md`
- Adhere to lint rules in `docs/contracts/lint_rules.md`
- Maintain environment contracts in `docs/contracts/env_matrix.md`

#### **Documentation**
- All features must be documented per v2 specifications
- Update relevant docs when implementing new features
- Maintain consistency with existing documentation

#### **Testing**
- Implement comprehensive test matrix per `docs/tests/matrix.md`
- Follow SLA validation procedures in `docs/tests/sla_playbook.md`
- Include Guided Prompt test scenarios

#### **Security & Privacy**
- Enforce security headers per `docs/security/http_headers.md`
- Implement data handling per `docs/security/data_handling.md`
- Follow rate limiting per `docs/security/rate_limit_and_abuse.md`

### **PR Requirements**

Each PR must include:
- **Acceptance Checklist** in PR description
- **Documentation Updates** for any new features
- **Test Coverage** for implemented functionality
- **Performance Validation** against budget requirements

### **File Management**

- **Never delete files** during cleanup
- **Move to `/deprecated/`** with 30-day grace period
- **Reference replacements** in deprecation notes
- **Follow cleanup plan** in `docs/frontend/cleanup_plan.md`

---

*Implementation must strictly follow v2 documentation. Budgets are mandatory, not suggestions.*
