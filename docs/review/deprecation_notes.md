# Deprecation Notes & Migration Guide

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Engineering Team  

## Overview

This document outlines the deprecation strategy for SarvanOM v2, including files and components that will be moved to the `/deprecated/` directory with a grace period for migration. This approach ensures system stability while allowing for gradual cleanup.

## Deprecation Strategy

### 1. Grace Period Policy

#### 1.1 Deprecation Timeline
- **Phase 1**: Mark as deprecated (Week 1)
- **Phase 2**: Move to `/deprecated/` (Week 2)
- **Phase 3**: Grace period (Weeks 3-8)
- **Phase 4**: Final removal (Week 9)

#### 1.2 Notification Process
- **Internal**: Team notification via Slack
- **Documentation**: Update all relevant documentation
- **Code**: Add deprecation warnings in code
- **Migration**: Provide migration guides and examples

### 2. Deprecation Categories

#### 2.1 High Priority Deprecations
- **Duplicate Configuration Files**
- **Outdated Documentation**
- **Legacy Test Results**
- **Unused Dependencies**

#### 2.2 Medium Priority Deprecations
- **Duplicate Documentation**
- **Old Report Files**
- **Legacy Scripts**
- **Unused Components**

#### 2.3 Low Priority Deprecations
- **Cache Files**
- **Temporary Files**
- **Old Test Results**
- **Backup Files**

## Deprecation List

### 1. Configuration Files

#### 1.1 ESLint Configuration
- **File**: `frontend/eslint.config.js`
- **Status**: Deprecated
- **Reason**: Duplicate of `eslint.config.mjs`
- **Migration**: Use `eslint.config.mjs`
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/frontend/eslint.config.js`

#### 1.2 Jest Configuration
- **File**: `frontend/jest.config.js`
- **Status**: Deprecated
- **Reason**: Standardize on single Jest configuration
- **Migration**: Use standardized Jest configuration
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/frontend/jest.config.js`

#### 1.3 YAML Configuration Files
- **Files**: 
  - `config/development.yaml`
  - `config/production.yaml`
  - `config/staging.yaml`
  - `config/testing.yaml`
- **Status**: Deprecated
- **Reason**: Consolidate configuration approach
- **Migration**: Use unified configuration system
- **Grace Period**: 6 weeks
- **Action**: Move to `/deprecated/config/`

### 2. Documentation Files

#### 2.1 Mock Scan Reports
- **Files**:
  - `COMPREHENSIVE_MOCK_SCAN_FINAL_REPORT.md`
  - `COMPREHENSIVE_MOCK_SCAN_REPORT.md`
- **Status**: Deprecated
- **Reason**: Outdated reports, superseded by new documentation
- **Migration**: Refer to current documentation
- **Grace Period**: 2 weeks
- **Action**: Move to `/deprecated/reports/`

#### 2.2 Testing Documentation
- **Files**:
  - `COMPREHENSIVE_TESTING_GUIDE.md`
  - `COMPREHENSIVE_TESTING_SUMMARY.md`
- **Status**: Deprecated
- **Reason**: Consolidated into new testing documentation
- **Migration**: Use `docs/tests/` documentation
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/docs/`

#### 2.3 Integration Reports
- **Files**:
  - `FINAL_FRONTEND_BACKEND_INTEGRATION_REPORT.md`
  - `FINAL_INTEGRATION_STATUS_REPORT.md`
  - `FINAL_ISSUE_RESOLUTION_REPORT.md`
  - `FINAL_MOCK_REMOVAL_REPORT.md`
  - `INTEGRATION_TEST_REPORT.md`
  - `MOCK_REMOVAL_SUMMARY.md`
- **Status**: Deprecated
- **Reason**: Historical reports, no longer relevant
- **Migration**: Refer to current status in implementation tracker
- **Grace Period**: 2 weeks
- **Action**: Move to `/deprecated/reports/`

### 3. Test Results

#### 3.1 Demo Test Results
- **Files**:
  - `test_results/demo_test_report_20250908_172349.txt`
  - `test_results/demo_test_report_20250908_172957.txt`
  - `test_results/demo_test_results_20250908_172349.json`
  - `test_results/demo_test_results_20250908_172957.json`
  - `test_results/demo_test_summary_20250908_172349.json`
  - `test_results/demo_test_summary_20250908_172957.json`
- **Status**: Deprecated
- **Reason**: Old test results, no longer relevant
- **Migration**: Use current test results
- **Grace Period**: 1 week
- **Action**: Move to `/deprecated/test_results/`

#### 3.2 Comprehensive Test Results
- **Files**:
  - `test_results/comprehensive_demo_results_20250908_173440.json`
  - `test_results/comprehensive_demo_results_20250908_173454.json`
  - `test_results/comprehensive_demo_results_20250908_173508.json`
- **Status**: Deprecated
- **Reason**: Old test results, no longer relevant
- **Migration**: Use current test results
- **Grace Period**: 1 week
- **Action**: Move to `/deprecated/test_results/`

### 4. Scan Results

#### 4.1 Mock Scan Results
- **Files**:
  - `mock_scan_results.json`
  - `targeted_mock_scan_results.txt`
- **Status**: Deprecated
- **Reason**: Old scan results, no longer relevant
- **Migration**: Use current scan results
- **Grace Period**: 1 week
- **Action**: Move to `/deprecated/scan_results/`

### 5. Frontend Documentation

#### 5.1 Frontend Restructure Documentation
- **File**: `frontend/restructure_frontend.md`
- **Status**: Deprecated
- **Reason**: Superseded by new frontend documentation
- **Migration**: Use `docs/frontend/` documentation
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/frontend/`

#### 5.2 Design Specifications
- **Files**:
  - `frontend/COSMIC_PRO_DESIGN_SPEC.md`
  - `frontend/VISUAL_REFERENCE_GUIDE.md`
- **Status**: Deprecated
- **Reason**: Consolidated into new design documentation
- **Migration**: Use `docs/frontend/design_tokens.md`
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/frontend/`

### 6. Configuration Documentation

#### 6.1 Credential Documentation
- **File**: `config/default_credentials.md`
- **Status**: Deprecated
- **Reason**: Security risk, superseded by secure configuration
- **Migration**: Use secure configuration management
- **Grace Period**: 2 weeks
- **Action**: Move to `/deprecated/config/`

#### 6.2 Production Configuration
- **File**: `config/production-config.md`
- **Status**: Deprecated
- **Reason**: Superseded by new configuration documentation
- **Migration**: Use `docs/contracts/env_matrix.md`
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/config/`

### 7. Cache Files

#### 7.1 Python Cache Files
- **Files**:
  - `scripts/__pycache__/`
  - `services/__pycache__/`
  - `shared/__pycache__/`
  - `config/__pycache__/`
  - `config/production/__pycache__/`
- **Status**: Deprecated
- **Reason**: Generated files, should not be in version control
- **Migration**: Add to `.gitignore`
- **Grace Period**: 1 week
- **Action**: Remove from repository

### 8. Docker Configuration

#### 8.1 Test Docker Configuration
- **File**: `Dockerfile.test`
- **Status**: Deprecated
- **Reason**: Consolidate Docker configurations
- **Migration**: Use unified Docker configuration
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/docker/`

#### 8.2 Frontend Docker Configuration
- **File**: `frontend/Dockerfile`
- **Status**: Deprecated
- **Reason**: Consolidate Docker configurations
- **Migration**: Use unified Docker configuration
- **Grace Period**: 4 weeks
- **Action**: Move to `/deprecated/docker/`

## Migration Guide

### 1. Configuration Migration

#### 1.1 ESLint Configuration
```bash
# Before (deprecated)
# frontend/eslint.config.js

# After (current)
# frontend/eslint.config.mjs
```

#### 1.2 Jest Configuration
```bash
# Before (deprecated)
# frontend/jest.config.js

# After (current)
# Use standardized Jest configuration in package.json
```

#### 1.3 YAML Configuration
```bash
# Before (deprecated)
# config/development.yaml
# config/production.yaml
# config/staging.yaml
# config/testing.yaml

# After (current)
# Use unified configuration system
# Environment-specific configuration via .env files
```

### 2. Documentation Migration

#### 2.1 Testing Documentation
```bash
# Before (deprecated)
# COMPREHENSIVE_TESTING_GUIDE.md
# COMPREHENSIVE_TESTING_SUMMARY.md

# After (current)
# docs/tests/matrix.md
# docs/tests/suites.md
# docs/tests/sla_playbook.md
```

#### 2.2 Frontend Documentation
```bash
# Before (deprecated)
# frontend/restructure_frontend.md
# frontend/COSMIC_PRO_DESIGN_SPEC.md
# frontend/VISUAL_REFERENCE_GUIDE.md

# After (current)
# docs/frontend/routes.md
# docs/frontend/components.md
# docs/frontend/design_tokens.md
```

### 3. Test Results Migration

#### 3.1 Test Results
```bash
# Before (deprecated)
# test_results/demo_test_*.json
# test_results/comprehensive_demo_results_*.json

# After (current)
# Use current test results from test runs
# Archive old results in /deprecated/test_results/
```

### 4. Scan Results Migration

#### 4.1 Mock Scan Results
```bash
# Before (deprecated)
# mock_scan_results.json
# targeted_mock_scan_results.txt

# After (current)
# Use current scan results from recent scans
# Archive old results in /deprecated/scan_results/
```

## Deprecation Process

### 1. Pre-Deprecation

#### 1.1 Analysis
- [ ] Identify files for deprecation
- [ ] Assess impact and dependencies
- [ ] Plan migration strategy
- [ ] Set deprecation timeline

#### 1.2 Communication
- [ ] Notify team of deprecation plan
- [ ] Update documentation
- [ ] Create migration guides
- [ ] Set up monitoring

### 2. Deprecation

#### 2.1 Mark as Deprecated
- [ ] Add deprecation warnings
- [ ] Update documentation
- [ ] Notify users
- [ ] Set grace period

#### 2.2 Move to Deprecated
- [ ] Create `/deprecated/` directory structure
- [ ] Move files to deprecated location
- [ ] Update references
- [ ] Test system functionality

### 3. Grace Period

#### 3.1 Monitoring
- [ ] Monitor usage of deprecated files
- [ ] Track migration progress
- [ ] Provide support for migration
- [ ] Update documentation

#### 3.2 Support
- [ ] Answer migration questions
- [ ] Provide migration assistance
- [ ] Update migration guides
- [ ] Monitor system stability

### 4. Final Removal

#### 4.1 Final Cleanup
- [ ] Remove deprecated files
- [ ] Clean up references
- [ ] Update documentation
- [ ] Test system functionality

#### 4.2 Documentation
- [ ] Update migration guides
- [ ] Archive deprecation notes
- [ ] Document lessons learned
- [ ] Update best practices

## Rollback Plan

### 1. Emergency Rollback

#### 1.1 Immediate Rollback
- [ ] Restore files from `/deprecated/`
- [ ] Revert configuration changes
- [ ] Test system functionality
- [ ] Notify team of rollback

#### 1.2 Investigation
- [ ] Investigate rollback cause
- [ ] Assess impact
- [ ] Plan remediation
- [ ] Update deprecation plan

### 2. Partial Rollback

#### 2.1 Selective Rollback
- [ ] Restore specific files
- [ ] Maintain system stability
- [ ] Update migration plan
- [ ] Communicate changes

#### 2.2 Gradual Migration
- [ ] Implement gradual migration
- [ ] Monitor system stability
- [ ] Provide extended support
- [ ] Update timeline

## Success Metrics

### 1. Deprecation Metrics

#### 1.1 File Reduction
- **Target**: 30% reduction in total files
- **Current**: 1,247 files
- **Target**: 873 files
- **Measurement**: File count before/after deprecation

#### 1.2 Documentation Consolidation
- **Target**: 50% reduction in documentation files
- **Current**: 45 documentation files
- **Target**: 23 documentation files
- **Measurement**: Documentation file count

#### 1.3 Configuration Simplification
- **Target**: 40% reduction in configuration files
- **Current**: 25 configuration files
- **Target**: 15 configuration files
- **Measurement**: Configuration file count

### 2. Quality Metrics

#### 2.1 System Stability
- **No Regressions**: Zero system regressions
- **Performance**: Maintained or improved performance
- **Functionality**: All features working correctly
- **User Experience**: Consistent user experience

#### 2.2 Developer Experience
- **Build Time**: Improved build times
- **Development**: Easier development process
- **Maintenance**: Reduced maintenance overhead
- **Documentation**: Clearer documentation

## Timeline

### 1. Week 1: Analysis and Planning
- [ ] Complete file analysis
- [ ] Identify deprecation candidates
- [ ] Plan migration strategy
- [ ] Get team approval

### 2. Week 2: Deprecation
- [ ] Mark files as deprecated
- [ ] Move files to `/deprecated/`
- [ ] Update documentation
- [ ] Test system functionality

### 3. Weeks 3-8: Grace Period
- [ ] Monitor system stability
- [ ] Provide migration support
- [ ] Update documentation
- [ ] Track migration progress

### 4. Week 9: Final Cleanup
- [ ] Remove deprecated files
- [ ] Final testing and validation
- [ ] Update documentation
- [ ] Document lessons learned

---

## Appendix

### A. Deprecated File Structure
```
/deprecated/
├── config/
│   ├── development.yaml
│   ├── production.yaml
│   ├── staging.yaml
│   ├── testing.yaml
│   ├── default_credentials.md
│   └── production-config.md
├── docs/
│   ├── COMPREHENSIVE_TESTING_GUIDE.md
│   └── COMPREHENSIVE_TESTING_SUMMARY.md
├── frontend/
│   ├── eslint.config.js
│   ├── jest.config.js
│   ├── restructure_frontend.md
│   ├── COSMIC_PRO_DESIGN_SPEC.md
│   └── VISUAL_REFERENCE_GUIDE.md
├── reports/
│   ├── COMPREHENSIVE_MOCK_SCAN_FINAL_REPORT.md
│   ├── COMPREHENSIVE_MOCK_SCAN_REPORT.md
│   ├── FINAL_FRONTEND_BACKEND_INTEGRATION_REPORT.md
│   ├── FINAL_INTEGRATION_STATUS_REPORT.md
│   ├── FINAL_ISSUE_RESOLUTION_REPORT.md
│   ├── FINAL_MOCK_REMOVAL_REPORT.md
│   ├── INTEGRATION_TEST_REPORT.md
│   └── MOCK_REMOVAL_SUMMARY.md
├── test_results/
│   ├── demo_test_report_20250908_172349.txt
│   ├── demo_test_report_20250908_172957.txt
│   ├── demo_test_results_20250908_172349.json
│   ├── demo_test_results_20250908_172957.json
│   ├── demo_test_summary_20250908_172349.json
│   ├── demo_test_summary_20250908_172957.json
│   ├── comprehensive_demo_results_20250908_173440.json
│   ├── comprehensive_demo_results_20250908_173454.json
│   └── comprehensive_demo_results_20250908_173508.json
├── scan_results/
│   ├── mock_scan_results.json
│   └── targeted_mock_scan_results.txt
└── docker/
    ├── Dockerfile.test
    └── frontend/Dockerfile
```

### B. Migration Scripts
- `scripts/deprecate-files.js` - File deprecation script
- `scripts/move-to-deprecated.js` - Move files to deprecated directory
- `scripts/update-references.js` - Update file references
- `scripts/cleanup-deprecated.js` - Final cleanup script

### C. Monitoring Tools
- `scripts/monitor-deprecation.js` - Monitor deprecation progress
- `scripts/usage-analysis.js` - Analyze file usage
- `scripts/migration-tracking.js` - Track migration progress
- `scripts/rollback-script.js` - Emergency rollback script
