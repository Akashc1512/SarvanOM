# Frontend Component Deduplication Plan

**Version**: 1.0  
**Date**: September 14, 2025  
**Branch**: chore/dedupe-components  
**Status**: Planning Phase  

## Overview

This document outlines the comprehensive plan for deduplicating frontend components in SarvanOM v2, based on the authoritative documentation sources:

- docs/frontend/components.md - Component inventory and specifications
- docs/frontend/design_tokens.md - Design system tokens and naming conventions  
- docs/frontend/pages/* - Page specifications and component requirements
- docs/contracts/naming_map.md - Canonical naming conventions
- docs/review/dup_candidates.csv - Identified duplicate components

## Deduplication Strategy: "Detect → Select Canonical → Migrate Imports → Quarantine → Verify → Safe Delete"

### Phase 1: Detection & Analysis

#### 1.1 Component Inventory Analysis
- **Source of Truth**: docs/frontend/components.md defines 8 categories with 50+ components
- **Current State**: Scan existing frontend codebase for component implementations
- **Detection Method**: 
  - AST-based analysis for component definitions
  - Import/export pattern analysis
  - File naming convention analysis
  - Functional similarity detection

#### 1.2 Duplicate Identification
- **High Priority**: Components with identical/similar functionality
- **Medium Priority**: Components with overlapping props interfaces
- **Low Priority**: Components with similar styling but different purposes
- **Categories to Focus**:
  - Layout components (AppLayout, DashboardLayout, AuthLayout)
  - Form components (Input, Textarea, Select variations)
  - Button components (Button, IconButton, ButtonGroup)
  - Modal components (Modal, Dialog, GuidedPromptModal)
  - Data display components (Table, List, Card variations)

#### 1.3 Impact Assessment
- **Usage Analysis**: Count imports and usage across codebase
- **Dependency Mapping**: Identify components that depend on duplicates
- **Breaking Change Risk**: Assess potential breaking changes
- **Test Coverage**: Identify test files that need updates

### Phase 2: Canonical Selection

#### 2.1 Selection Criteria
- **Design System Compliance**: Must follow Cosmic Pro design system
- **Accessibility**: Must meet WCAG 2.1 AA requirements
- **Performance**: Must meet performance requirements (< 1s load, 60fps)
- **TypeScript**: Must have proper TypeScript definitions
- **Testing**: Must have comprehensive test coverage
- **Documentation**: Must have proper JSDoc and Storybook stories

#### 2.2 Canonical Component Mapping
Based on docs/frontend/components.md:

| Category | Canonical Component | Duplicate Candidates |
|----------|-------------------|---------------------|
| Layout | AppLayout | MainLayout, PageLayout |
| Layout | DashboardLayout | DashboardWrapper, DashboardContainer |
| Layout | AuthLayout | LoginLayout, AuthWrapper |
| Forms | Input | TextInput, FormInput, TextField |
| Forms | Button | PrimaryButton, ActionButton, SubmitButton |
| Forms | Select | Dropdown, SelectField, ChoiceField |
| Data | Table | DataTable, ResultsTable, GridTable |
| Data | Card | ContentCard, InfoCard, DisplayCard |
| Interactive | Modal | Dialog, Popup, Overlay |
| Interactive | GuidedPromptModal | QueryModal, RefinementModal |

#### 2.3 Naming Convention Alignment
- **File Naming**: Use PascalCase for component files (Button.tsx)
- **Component Naming**: Use PascalCase for component names (Button)
- **Props Naming**: Follow naming_map.md conventions
- **CSS Classes**: Use BEM methodology (.button, .button--primary)

### Phase 3: Migration Strategy

#### 3.1 Import Migration
- **Create Alias Exports**: Temporary aliases for duplicate components
- **Update Import Statements**: Replace duplicate imports with canonical
- **Gradual Migration**: Migrate one component category at a time
- **Backward Compatibility**: Maintain temporary compatibility layer

#### 3.2 Props Interface Alignment
- **Interface Consolidation**: Merge compatible props interfaces
- **Breaking Changes**: Document and communicate breaking changes
- **Migration Guide**: Provide step-by-step migration instructions
- **Type Safety**: Ensure TypeScript compatibility throughout

#### 3.3 Styling Consolidation
- **Design Token Usage**: Ensure all components use design tokens
- **CSS-in-JS Migration**: Consolidate styling approaches
- **Theme Support**: Ensure consistent theme support
- **Responsive Design**: Maintain responsive behavior

### Phase 4: Quarantine Process

#### 4.1 Quarantine Directory
- **Location**: rontend/src/components/_quarantine/
- **Structure**: Mirror original directory structure
- **Naming**: Add _deprecated suffix to component names
- **Documentation**: Add deprecation warnings and migration notes

#### 4.2 Quarantine Rules
- **No New Imports**: Prevent new imports of quarantined components
- **Deprecation Warnings**: Add console warnings for existing imports
- **Migration Tracking**: Track migration progress
- **Rollback Plan**: Maintain ability to rollback if needed

#### 4.3 Quarantine Timeline
- **Week 1**: Quarantine high-priority duplicates
- **Week 2**: Quarantine medium-priority duplicates  
- **Week 3**: Quarantine low-priority duplicates
- **Week 4**: Final cleanup and verification

### Phase 5: Verification & Testing

#### 5.1 Automated Testing
- **Unit Tests**: Ensure all canonical components have tests
- **Integration Tests**: Test component interactions
- **Visual Regression Tests**: Ensure UI consistency
- **Accessibility Tests**: Verify accessibility compliance

#### 5.2 Manual Testing
- **Cross-browser Testing**: Test on major browsers
- **Mobile Testing**: Test on mobile devices
- **Screen Reader Testing**: Test with screen readers
- **Performance Testing**: Verify performance requirements

#### 5.3 User Acceptance Testing
- **Feature Testing**: Test all features using canonical components
- **Regression Testing**: Ensure no functionality is lost
- **Performance Testing**: Verify performance improvements
- **Accessibility Testing**: Verify accessibility compliance

### Phase 6: Safe Deletion

#### 6.1 Deletion Criteria
- **Zero Usage**: No remaining imports or references
- **Test Coverage**: All functionality covered by canonical components
- **Performance**: No performance regressions
- **Accessibility**: No accessibility regressions

#### 6.2 Deletion Process
- **Gradual Deletion**: Delete one component at a time
- **Verification**: Verify no breaking changes after each deletion
- **Rollback**: Maintain ability to restore if issues arise
- **Documentation**: Update documentation to reflect changes

#### 6.3 Post-Deletion Verification
- **Build Verification**: Ensure clean builds
- **Test Verification**: Ensure all tests pass
- **Performance Verification**: Ensure performance targets met
- **Accessibility Verification**: Ensure accessibility compliance

## Implementation Timeline

### Week 1: Detection & Analysis
- [ ] Complete component inventory analysis
- [ ] Identify all duplicate components
- [ ] Assess impact and breaking change risk
- [ ] Create detailed migration plan

### Week 2: Canonical Selection & Migration Setup
- [ ] Select canonical components for each category
- [ ] Create migration aliases and compatibility layer
- [ ] Set up quarantine directory structure
- [ ] Begin high-priority component migration

### Week 3: Migration & Quarantine
- [ ] Complete high-priority component migration
- [ ] Quarantine duplicate components
- [ ] Update import statements across codebase
- [ ] Begin medium-priority component migration

### Week 4: Verification & Cleanup
- [ ] Complete all component migrations
- [ ] Verify functionality and performance
- [ ] Complete testing and validation
- [ ] Begin safe deletion of quarantined components

### Week 5: Final Cleanup
- [ ] Complete safe deletion of all duplicate components
- [ ] Update documentation and examples
- [ ] Performance optimization and final testing
- [ ] Release and deployment

## Risk Mitigation

### 1. Breaking Changes
- **Mitigation**: Maintain backward compatibility during migration
- **Rollback Plan**: Keep quarantined components until verification complete
- **Communication**: Clear communication of breaking changes

### 2. Performance Regression
- **Mitigation**: Performance testing at each phase
- **Monitoring**: Continuous performance monitoring
- **Optimization**: Performance optimization as needed

### 3. Accessibility Regression
- **Mitigation**: Accessibility testing at each phase
- **Validation**: Screen reader and keyboard navigation testing
- **Compliance**: WCAG 2.1 AA compliance verification

### 4. Test Coverage Gaps
- **Mitigation**: Comprehensive test coverage for canonical components
- **Validation**: Test coverage analysis and gap identification
- **Remediation**: Additional tests for uncovered functionality

## Success Metrics

### 1. Code Quality
- **Component Count**: Reduce duplicate components by 80%
- **Bundle Size**: Reduce bundle size by 15-20%
- **Code Coverage**: Maintain 90%+ test coverage
- **TypeScript Coverage**: 100% TypeScript coverage

### 2. Performance
- **Load Time**: Maintain < 1s component load time
- **Runtime Performance**: Maintain 60fps UI performance
- **Bundle Size**: Reduce JavaScript bundle size
- **Memory Usage**: Reduce memory footprint

### 3. Maintainability
- **Code Duplication**: Reduce code duplication by 70%
- **Documentation**: 100% component documentation coverage
- **Consistency**: 100% design system compliance
- **Accessibility**: 100% WCAG 2.1 AA compliance

### 4. Developer Experience
- **Build Time**: Maintain or improve build times
- **Development Experience**: Improved component discovery
- **Documentation**: Comprehensive component documentation
- **Testing**: Improved test coverage and reliability

## Tools and Automation

### 1. Detection Tools
- **AST Analysis**: Custom scripts for component analysis
- **Import Analysis**: Tools for import/export analysis
- **Similarity Detection**: Tools for functional similarity analysis
- **Usage Tracking**: Tools for usage pattern analysis

### 2. Migration Tools
- **Import Replacement**: Automated import statement updates
- **Props Migration**: Automated props interface updates
- **Styling Migration**: Automated styling consolidation
- **Test Migration**: Automated test file updates

### 3. Verification Tools
- **Automated Testing**: Comprehensive test suite
- **Performance Testing**: Performance monitoring tools
- **Accessibility Testing**: Accessibility validation tools
- **Visual Regression**: Visual regression testing tools

## Documentation Updates

### 1. Component Documentation
- **Storybook**: Update all component stories
- **JSDoc**: Update all component documentation
- **Examples**: Update usage examples
- **Migration Guides**: Create migration guides for each component

### 2. Design System Documentation
- **Component Library**: Update component library documentation
- **Design Tokens**: Update design token usage
- **Accessibility**: Update accessibility guidelines
- **Performance**: Update performance guidelines

### 3. Developer Documentation
- **Getting Started**: Update getting started guides
- **Best Practices**: Update best practices documentation
- **Troubleshooting**: Update troubleshooting guides
- **API Reference**: Update API reference documentation

## Conclusion

This deduplication plan provides a comprehensive, risk-mitigated approach to consolidating frontend components in SarvanOM v2. By following the "Detect → Select Canonical → Migrate Imports → Quarantine → Verify → Safe Delete" strategy, we can achieve significant improvements in code quality, performance, and maintainability while minimizing risk and ensuring a smooth transition.

The plan is designed to be executed incrementally, with clear success metrics and rollback capabilities at each phase. This approach ensures that the deduplication process enhances rather than disrupts the development experience and user experience.

---

**Next Steps**: 
1. Begin Phase 1: Detection & Analysis
2. Set up automated detection tools
3. Create detailed component inventory
4. Begin canonical component selection process
