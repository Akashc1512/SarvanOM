# Lint Rules Specification

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Enforce canonical names and import paths across the entire codebase

---

## 🎯 **Core Linting Principles**

### **Non-Negotiable Rules**
1. **Canonical Names Only**: Use only canonical parameter names from `naming_map.md`
2. **Consistent Imports**: Use standardized import paths
3. **No Forbidden Synonyms**: Block all forbidden parameter names
4. **Environment Variables**: Enforce environment variable naming conventions
5. **API Contracts**: Validate API parameter naming

---

## 🔍 **Parameter Name Validation**

### **High Priority Rules (Blocking)**
```yaml
# ESLint Rules for Frontend
rules:
  # Block forbidden parameter names
  "no-restricted-globals": [
    "error",
    {
      "name": "limit",
      "message": "Use 'top_k' instead of 'limit'"
    },
    {
      "name": "deadline", 
      "message": "Use 'deadline_ms' instead of 'deadline'"
    },
    {
      "name": "timeout",
      "message": "Use 'deadline_ms' instead of 'timeout'"
    },
    {
      "name": "budget",
      "message": "Use 'lane_budget_ms' instead of 'budget'"
    },
    {
      "name": "first_byte",
      "message": "Use 'ttft_ms' instead of 'first_byte'"
    }
  ]
```

### **Medium Priority Rules (Warning)**
```yaml
# ESLint Rules for Frontend
rules:
  "no-restricted-globals": [
    "warn",
    {
      "name": "temp",
      "message": "Use 'temperature' instead of 'temp'"
    },
    {
      "name": "max_tok",
      "message": "Use 'max_tokens' instead of 'max_tok'"
    },
    {
      "name": "model",
      "message": "Use 'model_id' instead of 'model'"
    }
  ]
```

### **Custom ESLint Rule: Parameter Validation**
```javascript
// Custom rule: enforce-canonical-params
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce canonical parameter names',
      category: 'Best Practices',
      recommended: true
    },
    schema: [
      {
        type: 'object',
        properties: {
          forbiddenParams: {
            type: 'array',
            items: { type: 'string' }
          },
          canonicalParams: {
            type: 'object',
            additionalProperties: { type: 'string' }
          }
        }
      }
    ]
  },
  create(context) {
    const forbiddenParams = context.options[0]?.forbiddenParams || [];
    const canonicalParams = context.options[0]?.canonicalParams || {};
    
    return {
      Property(node) {
        if (node.key.type === 'Identifier') {
          const paramName = node.key.name;
          if (forbiddenParams.includes(paramName)) {
            const canonical = canonicalParams[paramName];
            context.report({
              node,
              message: `Use '${canonical}' instead of '${paramName}'`
            });
          }
        }
      }
    };
  }
};
```

---

## 🐍 **Python Linting Rules**

### **Flake8 Configuration**
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
per-file-ignores =
    __init__.py:F401
    tests/*:S101
select = C,E,F,W,B,B950
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .pytest_cache,
    build,
    dist
```

### **Custom Flake8 Plugin: Parameter Validation**
```python
# flake8_canonical_params.py
import ast
import re

class CanonicalParamsChecker:
    name = 'flake8-canonical-params'
    version = '1.0.0'
    
    # Forbidden parameter mappings
    FORBIDDEN_PARAMS = {
        'limit': 'top_k',
        'deadline': 'deadline_ms', 
        'timeout': 'deadline_ms',
        'budget': 'lane_budget_ms',
        'first_byte': 'ttft_ms',
        'temp': 'temperature',
        'max_tok': 'max_tokens',
        'model': 'model_id'
    }
    
    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        
    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_params(node)
            elif isinstance(node, ast.Call):
                self._check_call_args(node)
                
    def _check_function_params(self, node):
        for arg in node.args.args:
            if arg.arg in self.FORBIDDEN_PARAMS:
                canonical = self.FORBIDDEN_PARAMS[arg.arg]
                yield (
                    node.lineno,
                    node.col_offset,
                    f"CP001 Use '{canonical}' instead of '{arg.arg}'",
                    type(self)
                )
    
    def _check_call_args(self, node):
        for keyword in node.keywords:
            if keyword.arg in self.FORBIDDEN_PARAMS:
                canonical = self.FORBIDDEN_PARAMS[keyword.arg]
                yield (
                    node.lineno,
                    node.col_offset,
                    f"CP001 Use '{canonical}' instead of '{keyword.arg}'",
                    type(self)
                )
```

### **Pylint Configuration**
```ini
# .pylintrc
[MESSAGES CONTROL]
disable=
    missing-docstring,
    too-few-public-methods,
    too-many-arguments,
    too-many-locals,
    too-many-branches,
    too-many-statements

[FORMAT]
max-line-length=88
indent-string='    '

[VARIABLES]
good-names=i,j,k,ex,Run,_,id,db,ai,llm,api,url,uri,id,ip,os,io,ui,ux,kg,db,db_url,api_key,llm_provider,model_id,top_k,temperature,max_tokens,deadline_ms,lane_budget_ms,ttft_ms,finalize_ms,citations_count,disagreement_detected
```

---

## 🔧 **Import Path Validation**

### **Frontend Import Rules**
```javascript
// ESLint rule: enforce-import-paths
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce standardized import paths',
      category: 'Best Practices'
    }
  },
  create(context) {
    const importPathRules = {
      // UI components
      '^@/ui/(.*)$': 'Use @/ui/ for UI components',
      '^@/components/(.*)$': 'Use @/components/ for page components',
      
      // API routes
      '^@/app/api/(.*)$': 'Use @/app/api/ for API routes',
      
      // Shared utilities
      '^@/lib/(.*)$': 'Use @/lib/ for utilities',
      '^@/hooks/(.*)$': 'Use @/hooks/ for React hooks',
      
      // Types
      '^@/types/(.*)$': 'Use @/types/ for TypeScript types'
    };
    
    return {
      ImportDeclaration(node) {
        const importPath = node.source.value;
        
        for (const [pattern, message] of Object.entries(importPathRules)) {
          const regex = new RegExp(pattern);
          if (!regex.test(importPath)) {
            context.report({
              node,
              message: `${message}. Found: ${importPath}`
            });
          }
        }
      }
    };
  }
};
```

### **Backend Import Rules**
```python
# flake8_import_paths.py
import ast
import re

class ImportPathChecker:
    name = 'flake8-import-paths'
    version = '1.0.0'
    
    # Allowed import patterns
    ALLOWED_PATTERNS = [
        r'^shared\.',
        r'^services\.',
        r'^config\.',
        r'^tests\.',
        r'^scripts\.'
    ]
    
    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        
    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                self._check_import(node)
            elif isinstance(node, ast.ImportFrom):
                self._check_import_from(node)
                
    def _check_import(self, node):
        for alias in node.names:
            if not self._is_allowed_import(alias.name):
                yield (
                    node.lineno,
                    node.col_offset,
                    f"IP001 Import path '{alias.name}' not allowed",
                    type(self)
                )
    
    def _check_import_from(self, node):
        if node.module and not self._is_allowed_import(node.module):
            yield (
                node.lineno,
                node.col_offset,
                f"IP001 Import path '{node.module}' not allowed",
                type(self)
            )
    
    def _is_allowed_import(self, import_path):
        return any(re.match(pattern, import_path) for pattern in self.ALLOWED_PATTERNS)
```

---

## 🌍 **Environment Variable Validation**

### **Environment Variable Naming Rules**
```python
# env_var_validator.py
import re
import os

class EnvironmentVariableValidator:
    """Validate environment variable naming conventions"""
    
    # Canonical environment variable names
    CANONICAL_ENV_VARS = {
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'HUGGINGFACE_API_TOKEN',
        'OLLAMA_BASE_URL',
        'DATABASE_URL',
        'REDIS_URL',
        'VECTOR_DB_URL',
        'VECTOR_DB_API_KEY',
        'MEILISEARCH_URL',
        'MEILISEARCH_MASTER_KEY',
        'ARANGODB_URL',
        'ARANGODB_USERNAME',
        'ARANGODB_PASSWORD',
        'ARANGODB_DATABASE',
        'JWT_SECRET_KEY'
    }
    
    # Forbidden environment variable names
    FORBIDDEN_ENV_VARS = {
        'MEILI_MASTER_KEY': 'MEILISEARCH_MASTER_KEY',
        'QDRANT_URL': 'VECTOR_DB_URL',
        'QDRANT_API_KEY': 'VECTOR_DB_API_KEY'
    }
    
    def validate_environment_variables(self):
        """Validate all environment variables"""
        errors = []
        
        for key, value in os.environ.items():
            if key in self.FORBIDDEN_ENV_VARS:
                canonical = self.FORBIDDEN_ENV_VARS[key]
                errors.append(f"Use '{canonical}' instead of '{key}'")
        
        return errors
```

---

## 📋 **Pre-commit Hooks**

### **Pre-commit Configuration**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: canonical-params-check
        name: Check canonical parameter names
        entry: python scripts/check_canonical_params.py
        language: system
        pass_filenames: false
        
      - id: env-var-check
        name: Check environment variable names
        entry: python scripts/check_env_vars.py
        language: system
        pass_filenames: false
        
      - id: import-path-check
        name: Check import paths
        entry: python scripts/check_import_paths.py
        language: system
        pass_filenames: true

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-canonical-params]
        
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.42.0
    hooks:
      - id: eslint
        additional_dependencies:
          - eslint@8.42.0
          - eslint-plugin-canonical-params
```

---

## 🎯 **Validation Scripts**

### **Canonical Parameters Checker**
```python
# scripts/check_canonical_params.py
#!/usr/bin/env python3
"""Check for canonical parameter names across the codebase"""

import os
import re
import sys
from pathlib import Path

def check_file_for_forbidden_params(file_path):
    """Check a single file for forbidden parameter names"""
    errors = []
    
    forbidden_params = {
        'limit': 'top_k',
        'deadline': 'deadline_ms',
        'timeout': 'deadline_ms', 
        'budget': 'lane_budget_ms',
        'first_byte': 'ttft_ms',
        'temp': 'temperature',
        'max_tok': 'max_tokens',
        'model': 'model_id'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for forbidden, canonical in forbidden_params.items():
            pattern = rf'\b{forbidden}\b'
            matches = re.finditer(pattern, content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                errors.append(f"{file_path}:{line_num}: Use '{canonical}' instead of '{forbidden}'")
                
    except Exception as e:
        errors.append(f"{file_path}: Error reading file: {e}")
        
    return errors

def main():
    """Main validation function"""
    errors = []
    
    # Check Python files
    for py_file in Path('.').rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        errors.extend(check_file_for_forbidden_params(py_file))
    
    # Check TypeScript/JavaScript files
    for js_file in Path('.').rglob('*.{ts,tsx,js,jsx}'):
        if 'node_modules' in str(js_file) or '.next' in str(js_file):
            continue
        errors.extend(check_file_for_forbidden_params(js_file))
    
    if errors:
        print("❌ Canonical parameter validation failed:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ All parameter names are canonical")

if __name__ == '__main__':
    main()
```

---

## 📊 **Implementation Checklist**

### **Phase 1: Core Rules**
- [ ] Implement canonical parameter validation
- [ ] Add forbidden parameter blocking
- [ ] Create custom ESLint rules
- [ ] Create custom Flake8 plugins

### **Phase 2: Import Paths**
- [ ] Implement import path validation
- [ ] Add standardized import rules
- [ ] Create import path checkers

### **Phase 3: Environment Variables**
- [ ] Implement environment variable validation
- [ ] Add environment variable naming rules
- [ ] Create environment variable checkers

### **Phase 4: Pre-commit Hooks**
- [ ] Set up pre-commit hooks
- [ ] Add validation scripts
- [ ] Test all validation rules

---

## 🎯 **Success Criteria**

- ✅ All forbidden parameter names are blocked
- ✅ All import paths follow standardized patterns
- ✅ All environment variables use canonical names
- ✅ Pre-commit hooks prevent violations
- ✅ CI/CD pipeline enforces all rules

---

*This lint rules specification must be implemented before any code changes in Phase 1.*
