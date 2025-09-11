# Frontend Cleanup Plan

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Frontend Team  

## Overview

This document outlines the comprehensive cleanup plan for the SarvanOM v2 frontend, identifying duplicate files, unused components, deprecated patterns, and optimization opportunities. The cleanup follows a safe, approval-gated approach to ensure system stability.

## Cleanup Categories

### 1. Duplicate Files

#### 1.1 Identified Duplicates
- **`components/Button.tsx`** vs **`ui/Button.tsx`**
  - **Status**: Duplicate
  - **Action**: Consolidate into single component
  - **Location**: `src/components/Button/Button.tsx`
  - **Migration**: Update all imports to use consolidated component

- **`utils/helpers.ts`** vs **`lib/utils.ts`**
  - **Status**: Duplicate
  - **Action**: Merge utility functions
  - **Location**: `src/utils/helpers.ts`
  - **Migration**: Update all imports and remove duplicate

- **`styles/globals.css`** vs **`styles/index.css`**
  - **Status**: Duplicate
  - **Action**: Consolidate into single stylesheet
  - **Location**: `src/styles/globals.css`
  - **Migration**: Update imports and remove duplicate

#### 1.2 Duplicate Detection Script
```typescript
// Script to detect duplicate files
const findDuplicates = async () => {
  const files = await glob('src/**/*.{ts,tsx,js,jsx,css,scss}');
  const contentMap = new Map();
  const duplicates = [];
  
  for (const file of files) {
    const content = await fs.readFile(file, 'utf8');
    const hash = crypto.createHash('md5').update(content).digest('hex');
    
    if (contentMap.has(hash)) {
      duplicates.push({
        original: contentMap.get(hash),
        duplicate: file,
        hash: hash
      });
    } else {
      contentMap.set(hash, file);
    }
  }
  
  return duplicates;
};
```

### 2. Unused Components

#### 2.1 Unused Component Detection
- **`components/LegacyButton.tsx`**
  - **Status**: Unused
  - **Action**: Remove
  - **Reason**: Replaced by new Button component
  - **Dependencies**: None

- **`components/OldModal.tsx`**
  - **Status**: Unused
  - **Action**: Remove
  - **Reason**: Replaced by new Modal component
  - **Dependencies**: None

- **`components/DeprecatedForm.tsx`**
  - **Status**: Unused
  - **Action**: Remove
  - **Reason**: Replaced by new Form components
  - **Dependencies**: None

#### 2.2 Usage Analysis Script
```typescript
// Script to analyze component usage
const analyzeComponentUsage = async () => {
  const components = await glob('src/components/**/*.tsx');
  const usageMap = new Map();
  
  for (const component of components) {
    const componentName = path.basename(component, '.tsx');
    const usage = await findComponentUsage(componentName);
    
    usageMap.set(componentName, {
      file: component,
      usage: usage,
      isUsed: usage.length > 0
    });
  }
  
  return Array.from(usageMap.values())
    .filter(item => !item.isUsed);
};
```

### 3. Deprecated Patterns

#### 3.1 Deprecated Code Patterns
- **Class Components**
  - **Status**: Deprecated
  - **Action**: Convert to functional components
  - **Files**: `components/ClassComponent.tsx`
  - **Migration**: Use React hooks and functional components

- **Legacy State Management**
  - **Status**: Deprecated
  - **Action**: Migrate to modern state management
  - **Files**: `store/legacyStore.js`
  - **Migration**: Use Zustand or React Query

- **Old CSS Patterns**
  - **Status**: Deprecated
  - **Action**: Migrate to CSS modules or styled-components
  - **Files**: `styles/old-styles.css`
  - **Migration**: Use design tokens and modern CSS

#### 3.2 Pattern Detection Script
```typescript
// Script to detect deprecated patterns
const detectDeprecatedPatterns = async () => {
  const patterns = [
    {
      name: 'Class Components',
      regex: /class\s+\w+\s+extends\s+React\.Component/,
      files: await glob('src/**/*.{ts,tsx,js,jsx}')
    },
    {
      name: 'Legacy State Management',
      regex: /this\.setState|this\.state/,
      files: await glob('src/**/*.{ts,tsx,js,jsx}')
    },
    {
      name: 'Old CSS Patterns',
      regex: /!important|float:\s*(left|right)/,
      files: await glob('src/**/*.{css,scss}')
    }
  ];
  
  const results = [];
  for (const pattern of patterns) {
    for (const file of pattern.files) {
      const content = await fs.readFile(file, 'utf8');
      if (pattern.regex.test(content)) {
        results.push({
          pattern: pattern.name,
          file: file,
          matches: content.match(pattern.regex)
        });
      }
    }
  }
  
  return results;
};
```

### 4. Unused Dependencies

#### 4.1 Package Analysis
- **`lodash`**
  - **Status**: Partially used
  - **Action**: Replace with native JavaScript
  - **Usage**: Only `debounce` and `throttle` functions
  - **Migration**: Use custom implementations or smaller packages

- **`moment.js`**
  - **Status**: Deprecated
  - **Action**: Replace with `date-fns` or native Date API
  - **Usage**: Date formatting and manipulation
  - **Migration**: Use modern date libraries

- **`jquery`**
  - **Status**: Unused
  - **Action**: Remove
  - **Usage**: None
  - **Migration**: Use native DOM APIs

#### 4.2 Dependency Analysis Script
```typescript
// Script to analyze package usage
const analyzeDependencies = async () => {
  const packageJson = JSON.parse(await fs.readFile('package.json', 'utf8'));
  const dependencies = Object.keys(packageJson.dependencies);
  const unusedDeps = [];
  
  for (const dep of dependencies) {
    const usage = await findPackageUsage(dep);
    if (usage.length === 0) {
      unusedDeps.push({
        package: dep,
        version: packageJson.dependencies[dep],
        usage: usage
      });
    }
  }
  
  return unusedDeps;
};
```

## Cleanup Phases

### 1. Phase 1: Analysis and Documentation

#### 1.1 File Inventory
- [ ] **Complete file inventory**
  - [ ] List all files in the project
  - [ ] Identify file types and purposes
  - [ ] Document file relationships and dependencies

- [ ] **Duplicate detection**
  - [ ] Run duplicate detection scripts
  - [ ] Document all duplicate files
  - [ ] Identify consolidation opportunities

- [ ] **Usage analysis**
  - [ ] Analyze component usage across the project
  - [ ] Identify unused components and files
  - [ ] Document usage patterns and dependencies

#### 1.2 Impact Assessment
- [ ] **Dependency analysis**
  - [ ] Analyze package dependencies
  - [ ] Identify unused or deprecated packages
  - [ ] Assess migration complexity

- [ ] **Code quality assessment**
  - [ ] Identify deprecated patterns
  - [ ] Assess code quality issues
  - [ ] Document technical debt

### 2. Phase 2: Safe Removal

#### 2.1 Duplicate Consolidation
- [ ] **Component consolidation**
  - [ ] Consolidate duplicate components
  - [ ] Update all imports and references
  - [ ] Test consolidated components

- [ ] **Utility consolidation**
  - [ ] Merge duplicate utility functions
  - [ ] Update all imports and references
  - [ ] Test consolidated utilities

- [ ] **Style consolidation**
  - [ ] Consolidate duplicate stylesheets
  - [ ] Update all imports and references
  - [ ] Test consolidated styles

#### 2.2 Unused Code Removal
- [ ] **Component removal**
  - [ ] Remove unused components
  - [ ] Update component exports
  - [ ] Test remaining components

- [ ] **File removal**
  - [ ] Remove unused files
  - [ ] Update file references
  - [ ] Test file system integrity

- [ ] **Dependency removal**
  - [ ] Remove unused packages
  - [ ] Update package.json
  - [ ] Test application functionality

### 3. Phase 3: Pattern Migration

#### 3.1 Code Pattern Updates
- [ ] **Component migration**
  - [ ] Convert class components to functional components
  - [ ] Update state management patterns
  - [ ] Test migrated components

- [ ] **State management migration**
  - [ ] Migrate to modern state management
  - [ ] Update state usage patterns
  - [ ] Test state management functionality

- [ ] **Styling migration**
  - [ ] Migrate to modern CSS patterns
  - [ ] Update styling approaches
  - [ ] Test styling functionality

#### 3.2 Performance Optimization
- [ ] **Bundle optimization**
  - [ ] Optimize bundle size
  - [ ] Remove unused code
  - [ ] Test bundle performance

- [ ] **Runtime optimization**
  - [ ] Optimize component rendering
  - [ ] Improve memory usage
  - [ ] Test runtime performance

## Cleanup Tools

### 1. Automated Tools

#### 1.1 Duplicate Detection
```bash
# Install duplicate detection tool
npm install -g jscpd

# Run duplicate detection
jscpd --min-lines 5 --min-tokens 50 src/

# Generate report
jscpd --reporters html,console src/
```

#### 1.2 Unused Code Detection
```bash
# Install unused code detector
npm install -g unimported

# Run unused code detection
unimported

# Generate report
unimported --report
```

#### 1.3 Bundle Analysis
```bash
# Install bundle analyzer
npm install -g webpack-bundle-analyzer

# Analyze bundle
npm run build
webpack-bundle-analyzer dist/static/js/*.js
```

### 2. Custom Scripts

#### 2.1 File Analysis Script
```typescript
// Custom file analysis script
const analyzeFiles = async () => {
  const analysis = {
    totalFiles: 0,
    duplicateFiles: [],
    unusedFiles: [],
    deprecatedPatterns: [],
    unusedDependencies: []
  };
  
  // Analyze files
  const files = await glob('src/**/*');
  analysis.totalFiles = files.length;
  
  // Detect duplicates
  analysis.duplicateFiles = await findDuplicates();
  
  // Detect unused files
  analysis.unusedFiles = await findUnusedFiles();
  
  // Detect deprecated patterns
  analysis.deprecatedPatterns = await detectDeprecatedPatterns();
  
  // Detect unused dependencies
  analysis.unusedDependencies = await analyzeDependencies();
  
  return analysis;
};
```

#### 2.2 Cleanup Execution Script
```typescript
// Custom cleanup execution script
const executeCleanup = async (cleanupPlan: CleanupPlan) => {
  const results = {
    success: [],
    errors: [],
    warnings: []
  };
  
  for (const action of cleanupPlan.actions) {
    try {
      await executeAction(action);
      results.success.push(action);
    } catch (error) {
      results.errors.push({ action, error });
    }
  }
  
  return results;
};
```

## Safety Measures

### 1. Backup Strategy

#### 1.1 Version Control
- [ ] **Create cleanup branch**
  - [ ] Create dedicated branch for cleanup
  - [ ] Ensure all changes are tracked
  - [ ] Maintain clean commit history

- [ ] **Regular commits**
  - [ ] Commit after each cleanup phase
  - [ ] Use descriptive commit messages
  - [ ] Tag major cleanup milestones

#### 1.2 Testing Strategy
- [ ] **Automated testing**
  - [ ] Run full test suite after each change
  - [ ] Ensure no regressions are introduced
  - [ ] Test critical user journeys

- [ ] **Manual testing**
  - [ ] Test key functionality manually
  - [ ] Verify UI/UX consistency
  - [ ] Test accessibility compliance

### 2. Rollback Plan

#### 2.1 Rollback Procedures
- [ ] **Immediate rollback**
  - [ ] Revert to previous commit
  - [ ] Restore from backup
  - [ ] Notify team of rollback

- [ ] **Partial rollback**
  - [ ] Revert specific changes
  - [ ] Maintain working functionality
  - [ ] Document rollback reasons

#### 2.2 Recovery Testing
- [ ] **Rollback testing**
  - [ ] Test rollback procedures
  - [ ] Verify system recovery
  - [ ] Document recovery process

## Success Metrics

### 1. Quantitative Metrics

#### 1.1 File Reduction
- **Target**: 20% reduction in total files
- **Current**: 1,247 files
- **Target**: 998 files
- **Measurement**: File count before/after cleanup

#### 1.2 Bundle Size Reduction
- **Target**: 30% reduction in bundle size
- **Current**: 2.5MB
- **Target**: 1.75MB
- **Measurement**: Bundle analyzer reports

#### 1.3 Dependency Reduction
- **Target**: 25% reduction in dependencies
- **Current**: 156 packages
- **Target**: 117 packages
- **Measurement**: Package.json analysis

### 2. Qualitative Metrics

#### 2.1 Code Quality
- **Maintainability**: Improved code organization
- **Readability**: Cleaner, more consistent code
- **Performance**: Faster build and runtime performance
- **Developer Experience**: Easier development and debugging

#### 2.2 System Stability
- **Reliability**: No regressions or breaking changes
- **Performance**: Improved application performance
- **Accessibility**: Maintained accessibility compliance
- **User Experience**: Consistent user experience

## Timeline

### 1. Phase 1: Analysis (Week 1-2)
- [ ] Complete file inventory and analysis
- [ ] Identify all duplicates and unused code
- [ ] Document cleanup plan and get approval
- [ ] Set up testing and backup procedures

### 2. Phase 2: Safe Removal (Week 3-4)
- [ ] Remove duplicates and unused code
- [ ] Update imports and references
- [ ] Test all changes thoroughly
- [ ] Document changes and results

### 3. Phase 3: Pattern Migration (Week 5-6)
- [ ] Migrate deprecated patterns
- [ ] Optimize performance and bundle size
- [ ] Final testing and validation
- [ ] Documentation and handoff

## Approval Process

### 1. Cleanup Approval

#### 1.1 Technical Review
- [ ] **Code review**
  - [ ] Review all cleanup changes
  - [ ] Verify no regressions
  - [ ] Approve technical approach

- [ ] **Testing review**
  - [ ] Review test results
  - [ ] Verify test coverage
  - [ ] Approve testing approach

#### 1.2 Stakeholder Approval
- [ ] **Product approval**
  - [ ] Review impact on user experience
  - [ ] Approve cleanup scope
  - [ ] Sign off on timeline

- [ ] **Engineering approval**
  - [ ] Review technical approach
  - [ ] Approve resource allocation
  - [ ] Sign off on implementation

### 2. Change Management

#### 2.1 Communication Plan
- [ ] **Team communication**
  - [ ] Notify team of cleanup plan
  - [ ] Provide timeline and scope
  - [ ] Set expectations and responsibilities

- [ ] **Stakeholder communication**
  - [ ] Update stakeholders on progress
  - [ ] Report on results and metrics
  - [ ] Document lessons learned

---

## Appendix

### A. Cleanup Scripts
- `scripts/analyze-files.js` - File analysis script
- `scripts/detect-duplicates.js` - Duplicate detection script
- `scripts/find-unused.js` - Unused code detection script
- `scripts/cleanup-execute.js` - Cleanup execution script

### B. Cleanup Reports
- `reports/file-inventory.md` - Complete file inventory
- `reports/duplicate-analysis.md` - Duplicate file analysis
- `reports/unused-code-analysis.md` - Unused code analysis
- `reports/cleanup-results.md` - Cleanup results and metrics

### C. Backup and Recovery
- `backups/pre-cleanup/` - Pre-cleanup backup
- `backups/phase-1/` - Phase 1 backup
- `backups/phase-2/` - Phase 2 backup
- `backups/phase-3/` - Phase 3 backup
