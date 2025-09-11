# Repository Inventory - SarvanOM v2

**Date**: September 9, 2025  
**Status**: Current state analysis for v2 implementation  
**Purpose**: Identify pages, components, services, and duplicates/unreferenced files

---

## 📁 **Directory Structure Analysis**

### **Root Level Files**
| File | Type | Status | Notes |
|------|------|--------|-------|
| `README.md` | Documentation | ✅ **KEEP** | Main project documentation |
| `LICENSE` | Legal | ✅ **KEEP** | Project license |
| `SECURITY.md` | Security | ✅ **KEEP** | Security policy |
| `Makefile` | Build | ✅ **KEEP** | Build automation |
| `requirements.txt` | Dependencies | ✅ **KEEP** | Python dependencies |
| `package.json` | Dependencies | ✅ **KEEP** | Node.js dependencies |
| `pyproject.toml` | Configuration | ✅ **KEEP** | Python project config |
| `docker-compose.yml` | Container | ✅ **KEEP** | Main Docker setup |
| `docker-compose.test.yml` | Container | ✅ **KEEP** | Test Docker setup |
| `Dockerfile.test` | Container | ✅ **KEEP** | Test container |

### **Report Files (Generated)**
| File | Type | Status | Action |
|------|------|--------|--------|
| `COMPLETE_SYSTEM_INTEGRATION_SUCCESS_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `COMPREHENSIVE_ISSUE_RESOLUTION_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `COMPREHENSIVE_MOCK_SCAN_FINAL_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `COMPREHENSIVE_MOCK_SCAN_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `COMPREHENSIVE_TESTING_GUIDE.md` | Guide | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `COMPREHENSIVE_TESTING_SUMMARY.md` | Summary | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `FINAL_FRONTEND_BACKEND_INTEGRATION_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `FINAL_INTEGRATION_STATUS_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `FINAL_ISSUE_RESOLUTION_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `FINAL_MOCK_REMOVAL_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `INTEGRATION_TEST_REPORT.md` | Report | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `MOCK_REMOVAL_SUMMARY.md` | Summary | ⚠️ **DEPRECATE** | Move to `/deprecated/` |
| `SARVANOM_V2_IMPLEMENTATION_TRACKER.md` | Tracker | ✅ **KEEP** | v2 implementation tracker |

---

## 🏗️ **Services Architecture**

### **Backend Services**
| Service | Location | Status | Purpose |
|---------|----------|--------|---------|
| **Gateway** | `services/gateway/` | ✅ **ACTIVE** | Main API gateway |
| **Analytics** | `services/analytics/` | ✅ **ACTIVE** | Analytics and metrics |
| **Auth** | `services/auth/` | ✅ **ACTIVE** | Authentication |
| **Fact Check** | `services/fact_check/` | ✅ **ACTIVE** | Fact checking |
| **Knowledge Graph** | `services/knowledge_graph/` | ✅ **ACTIVE** | Knowledge graph |
| **Monitoring** | `services/monitoring/` | ✅ **ACTIVE** | System monitoring |
| **Retrieval** | `services/retrieval/` | ✅ **ACTIVE** | Data retrieval |
| **Search** | `services/search/` | ✅ **ACTIVE** | Search functionality |
| **Synthesis** | `services/synthesis/` | ✅ **ACTIVE** | Content synthesis |
| **CRUD** | `services/crud/` | ✅ **ACTIVE** | Database operations |
| **Deployment** | `services/deployment/` | ✅ **ACTIVE** | Deployment configs |

### **Shared Components**
| Component | Location | Status | Purpose |
|-----------|----------|--------|---------|
| **Core** | `shared/core/` | ✅ **ACTIVE** | Core utilities |
| **Clients** | `shared/clients/` | ✅ **ACTIVE** | External client integrations |
| **Contracts** | `shared/contracts/` | ✅ **ACTIVE** | API contracts |
| **Embeddings** | `shared/embeddings/` | ✅ **ACTIVE** | Embedding utilities |
| **LLM** | `shared/llm/` | ✅ **ACTIVE** | LLM integrations |
| **Middleware** | `shared/middleware/` | ✅ **ACTIVE** | Middleware components |
| **Models** | `shared/models/` | ✅ **ACTIVE** | Data models |
| **Vectorstores** | `shared/vectorstores/` | ✅ **ACTIVE** | Vector database utilities |

---

## 🎨 **Frontend Architecture**

### **Pages & Routes**
| Page | Location | Status | Purpose |
|------|----------|--------|---------|
| **Landing** | `frontend/src/app/page.tsx` | ✅ **ACTIVE** | Home page |
| **Search** | `frontend/src/app/search/` | ✅ **ACTIVE** | Search interface |
| **Analytics** | `frontend/src/app/analytics/` | ✅ **ACTIVE** | Analytics dashboard |
| **Knowledge Graph** | `frontend/src/app/knowledge-graph/` | ✅ **ACTIVE** | KG visualization |
| **Auth** | `frontend/src/app/auth/` | ✅ **ACTIVE** | Authentication |
| **Admin** | `frontend/src/app/admin/` | ✅ **ACTIVE** | Admin panel |

### **API Routes**
| Route | Location | Status | Purpose |
|-------|----------|--------|---------|
| **Query** | `frontend/src/app/api/query/` | ✅ **ACTIVE** | Query processing |
| **Analytics** | `frontend/src/app/api/analytics/` | ✅ **ACTIVE** | Analytics API |
| **Health** | `frontend/src/app/api/health/` | ✅ **ACTIVE** | Health checks |
| **Agents** | `frontend/src/app/api/agents/` | ✅ **ACTIVE** | Agent APIs |

### **UI Components**
| Component | Location | Status | Purpose |
|-----------|----------|--------|---------|
| **Layout** | `frontend/src/components/layout/` | ✅ **ACTIVE** | Layout components |
| **UI** | `frontend/src/ui/` | ✅ **ACTIVE** | UI components |
| **Forms** | `frontend/src/components/forms/` | ✅ **ACTIVE** | Form components |

---

## 🧪 **Testing Infrastructure**

### **Test Files**
| Test Type | Location | Status | Purpose |
|-----------|----------|--------|---------|
| **Unit Tests** | `tests/` | ✅ **ACTIVE** | Unit test suite |
| **E2E Tests** | `frontend/e2e/` | ✅ **ACTIVE** | End-to-end tests |
| **Integration Tests** | Various | ✅ **ACTIVE** | Integration tests |

### **Test Configuration**
| Config | Location | Status | Purpose |
|--------|----------|--------|---------|
| **Jest** | `frontend/jest.config.js` | ✅ **ACTIVE** | Unit test config |
| **Playwright** | `frontend/playwright.config.ts` | ✅ **ACTIVE** | E2E test config |
| **Lighthouse** | `frontend/lighthouse.config.js` | ✅ **ACTIVE** | Performance testing |

---

## 📊 **Configuration Files**

### **Application Config**
| Config | Location | Status | Purpose |
|--------|----------|--------|---------|
| **Development** | `config/development.yaml` | ✅ **ACTIVE** | Dev environment |
| **Production** | `config/production.yaml` | ✅ **ACTIVE** | Prod environment |
| **Staging** | `config/staging.yaml` | ✅ **ACTIVE** | Staging environment |
| **Testing** | `config/testing.yaml` | ✅ **ACTIVE** | Test environment |

### **Frontend Config**
| Config | Location | Status | Purpose |
|--------|----------|--------|---------|
| **Next.js** | `frontend/next.config.js` | ✅ **ACTIVE** | Next.js config |
| **Tailwind** | `frontend/tailwind.config.js` | ✅ **ACTIVE** | CSS framework |
| **TypeScript** | `frontend/tsconfig.json` | ✅ **ACTIVE** | TypeScript config |
| **ESLint** | `frontend/eslint.config.js` | ✅ **ACTIVE** | Linting config |

---

## 🗂️ **Data & Storage**

### **Data Directories**
| Directory | Status | Purpose |
|-----------|--------|---------|
| `data/arangodb/` | ✅ **ACTIVE** | ArangoDB data |
| `data/meilisearch/` | ✅ **ACTIVE** | Meilisearch data |
| `data/ollama/` | ✅ **ACTIVE** | Ollama models |
| `data/postgres/` | ✅ **ACTIVE** | PostgreSQL data |
| `data/qdrant/` | ✅ **ACTIVE** | Qdrant data |
| `data/redis/` | ✅ **ACTIVE** | Redis data |

### **Test Data**
| Directory | Status | Purpose |
|-----------|--------|---------|
| `test_data/` | ✅ **ACTIVE** | Test datasets |
| `test_results/` | ⚠️ **CLEANUP** | Generated test results |

---

## 🔧 **Scripts & Automation**

### **Scripts**
| Script | Location | Status | Purpose |
|--------|----------|--------|---------|
| **CI Guardrails** | `scripts/ci_guardrails.py` | ✅ **ACTIVE** | CI/CD checks |
| **Test Runner** | `scripts/comprehensive_test_runner.py` | ✅ **ACTIVE** | Test automation |
| **Health Check** | `scripts/system-health-check.ps1` | ✅ **ACTIVE** | System monitoring |
| **Code Garden** | `scripts/code_garden/` | ✅ **ACTIVE** | Code organization |

---

## ⚠️ **Duplicates & Unreferenced Files**

### **Report Files (To Deprecate)**
- Multiple integration and testing reports
- Mock removal reports
- Issue resolution reports
- **Action**: Move to `/deprecated/` with 30-day grace period

### **Test Results (To Cleanup)**
- Generated test result files in `test_results/`
- **Action**: Clean up old test results, keep structure

### **Temporary Files**
- Various temporary analysis files
- **Action**: Review and clean up

---

## 📋 **Cleanup Plan**

### **Phase 1: Deprecation (30-day grace)**
1. Move report files to `/deprecated/`
2. Add deprecation notes
3. Update references

### **Phase 2: Cleanup (After grace period)**
1. Remove deprecated files
2. Clean up test results
3. Remove temporary files

### **Phase 3: Organization**
1. Organize documentation
2. Standardize naming
3. Update references

---

## 🎯 **Prompting Surfaces**

### **UI Surfaces That Accept Free-Text Input**
| Surface | Location | Component | Purpose | Guided Prompt Integration |
|---------|----------|-----------|---------|---------------------------|
| **Main Search Bar** | `frontend/src/app/page.tsx` | Search input | Primary query interface | ✅ **PRIMARY TARGET** |
| **Search Page** | `frontend/src/app/search/` | Search interface | Dedicated search page | ✅ **PRIMARY TARGET** |
| **Comprehensive Query** | `frontend/src/app/comprehensive-query/` | Research composer | Advanced query builder | ✅ **PRIMARY TARGET** |
| **Chat Interface** | Various chat components | Chat input | Conversational queries | ✅ **PRIMARY TARGET** |
| **Knowledge Graph Query** | `frontend/src/app/knowledge-graph/` | KG search | Graph traversal queries | ✅ **PRIMARY TARGET** |
| **Multimodal Demo** | `frontend/src/app/multimodal-demo/` | File + text input | Multimodal queries | ✅ **PRIMARY TARGET** |
| **Admin Query Interface** | `frontend/src/app/admin/` | Admin search | Administrative queries | ✅ **PRIMARY TARGET** |
| **Analytics Query** | `frontend/src/app/analytics/` | Analytics search | Data analysis queries | ✅ **PRIMARY TARGET** |

### **API Endpoints That Process Free-Text**
| Endpoint | Location | Purpose | Guided Prompt Integration |
|----------|----------|---------|---------------------------|
| **Query API** | `frontend/src/app/api/query/` | Main query processing | ✅ **PRIMARY TARGET** |
| **Comprehensive Query** | `frontend/src/app/api/query/comprehensive/` | Advanced queries | ✅ **PRIMARY TARGET** |
| **Knowledge Graph Query** | `frontend/src/app/api/knowledge-graph/query/` | KG queries | ✅ **PRIMARY TARGET** |
| **Agent Queries** | `frontend/src/app/api/agents/` | Agent-based queries | ✅ **PRIMARY TARGET** |

### **Backend Services That Process Queries**
| Service | Location | Purpose | Guided Prompt Integration |
|---------|----------|---------|---------------------------|
| **Gateway** | `services/gateway/` | Main orchestrator | ✅ **PRIMARY TARGET** |
| **Synthesis** | `services/synthesis/` | Content synthesis | ✅ **PRIMARY TARGET** |
| **Retrieval** | `services/retrieval/` | Data retrieval | ✅ **PRIMARY TARGET** |
| **Search** | `services/search/` | Search functionality | ✅ **PRIMARY TARGET** |

### **Guided Prompt Integration Points**
1. **Frontend Integration**: All free-text input components will integrate with `GuidedPromptModal`
2. **Backend Integration**: New `PromptRefinementService` will analyze queries before processing
3. **Settings Integration**: User preferences stored in user profile with local overrides
4. **Observability**: Metrics collection for refinement acceptance rates and performance

---

## 📊 **Summary**

**Total Files Analyzed**: 200+  
**Active Services**: 11  
**Active Frontend Pages**: 6+  
**Active API Routes**: 10+  
**Files to Deprecate**: 12+  
**Files to Cleanup**: 5+  

**Status**: ✅ **READY FOR v2 CLEANUP IMPLEMENTATION**

---

*This inventory will be updated as cleanup progresses.*
