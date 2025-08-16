# Routing Audit Report

## 🎯 **Objective**
Conduct a comprehensive routing audit to identify and resolve duplicate or shadowed endpoints across all FastAPI applications in the Sarvanom platform.

## 📊 **Current Service Architecture**

### **Active Services:**
1. **Gateway Service** (Port 8000) - Main API Gateway
2. **Auth Service** (Port 8014) - Authentication microservice
3. **Fact-Check Service** (Port 8013) - Fact-checking microservice
4. **Synthesis Service** (Port 8002) - Content synthesis microservice
5. **Search Service** (Port 8015) - Search microservice
6. **Retrieval Service** (Port 8001) - Vector retrieval microservice

## 🚨 **CRITICAL ROUTING CONFLICTS IDENTIFIED**

### **1. Health Endpoint Conflicts** ❌ **HIGH PRIORITY**

#### **Duplicate `/health` Endpoints:**
- **Gateway Service** (`services/gateway/main.py:329`) - `@app.get("/health")`
- **Gateway Routes** (`services/gateway/routes.py:148`) - `@health_router.get("/health")`
- **Auth Service** (`shared/core/app_factory.py:145`) - `@app.get("/health")`
- **Fact-Check Service** (`shared/core/app_factory.py:145`) - `@app.get("/health")`
- **Synthesis Service** (`shared/core/app_factory.py:145`) - `@app.get("/health")`
- **Search Service** (`shared/core/app_factory.py:145`) - `@app.get("/health")`
- **Retrieval Service** (`shared/core/app_factory.py:145`) - `@app.get("/health")`

#### **Issue:** All services expose `/health` endpoint, creating conflicts when running on same host

### **2. Metrics Endpoint Conflicts** ❌ **HIGH PRIORITY**

#### **Duplicate `/metrics` Endpoints:**
- **Gateway Service** (`shared/core/app_factory.py:156`) - `@app.get("/metrics")`
- **Auth Service** (`shared/core/app_factory.py:156`) - `@app.get("/metrics")`
- **Fact-Check Service** (`shared/core/app_factory.py:156`) - `@app.get("/metrics")`
- **Synthesis Service** (`shared/core/app_factory.py:156`) - `@app.get("/metrics")`
- **Search Service** (`shared/core/app_factory.py:156`) - `@app.get("/metrics")`
- **Retrieval Service** (`shared/core/app_factory.py:156`) - `@app.get("/metrics")`

#### **Issue:** All services expose `/metrics` endpoint, creating conflicts

### **3. Root Endpoint Conflicts** ❌ **MEDIUM PRIORITY**

#### **Duplicate `/` Endpoints:**
- **Gateway Service** (`shared/core/app_factory.py:162`) - `@app.get("/")`
- **Auth Service** (`shared/core/app_factory.py:162`) - `@app.get("/")`
- **Fact-Check Service** (`shared/core/app_factory.py:162`) - `@app.get("/")`
- **Synthesis Service** (`shared/core/app_factory.py:162`) - `@app.get("/")`
- **Search Service** (`shared/core/app_factory.py:162`) - `@app.get("/")`
- **Retrieval Service** (`shared/core/app_factory.py:162`) - `@app.get("/")`

#### **Issue:** All services expose root endpoint, creating conflicts

### **4. Gateway Internal Conflicts** ❌ **HIGH PRIORITY**

#### **Duplicate Health Endpoints in Gateway:**
- **Gateway Main** (`services/gateway/main.py:329`) - `@app.get("/health")`
- **Gateway Routes** (`services/gateway/routes.py:148`) - `@health_router.get("/health")`

#### **Issue:** Gateway has two different health endpoints

## 🔧 **RECOMMENDED SOLUTIONS**

### **Solution 1: Service-Specific Health Endpoints**
```python
# Each service should have unique health endpoints:
- Gateway: /health (aggregate status)
- Auth: /auth/health
- Fact-Check: /fact-check/health  
- Synthesis: /synthesis/health
- Search: /search/health
- Retrieval: /retrieval/health
```

### **Solution 2: Metrics Aggregation**
```python
# Gateway should aggregate metrics from all services:
- Gateway: /metrics (aggregate metrics)
- Individual services: /internal/metrics (internal only)
```

### **Solution 3: Service-Specific Root Endpoints**
```python
# Each service should have descriptive root endpoints:
- Gateway: / (API documentation)
- Auth: /auth/ (auth service info)
- Fact-Check: /fact-check/ (fact-check service info)
- etc.
```

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Fix Gateway Internal Conflicts**
1. Remove duplicate health endpoint from `services/gateway/main.py`
2. Keep only the health router endpoint in `services/gateway/routes.py`
3. Update gateway health to provide aggregate status

### **Phase 2: Update App Factory**
1. Modify `shared/core/app_factory.py` to use service-specific prefixes
2. Add configuration options for endpoint customization
3. Update all services to use unique endpoints

### **Phase 3: Update Service Routes**
1. Update each service to use service-specific health/metrics endpoints
2. Ensure no conflicts when running on same host
3. Update documentation and tests

## 🎯 **IMMEDIATE ACTIONS REQUIRED**

1. **Remove duplicate health endpoint from gateway main.py**
2. **Update app factory to support service-specific endpoints**
3. **Update all services to use unique endpoint prefixes**
4. **Update tests to reflect new endpoint structure**

## 📊 **IMPACT ASSESSMENT**

### **High Impact:**
- **Health endpoint conflicts** - Prevents proper health monitoring
- **Metrics endpoint conflicts** - Prevents proper metrics collection
- **Gateway internal conflicts** - Causes routing confusion

### **Medium Impact:**
- **Root endpoint conflicts** - Affects service discovery
- **Documentation updates** - Need to update API docs

### **Low Impact:**
- **Test updates** - Need to update endpoint tests

## ✅ **SUCCESS CRITERIA**

1. **No duplicate endpoints** across services
2. **Gateway provides aggregate health status** from all services
3. **Each service has unique, descriptive endpoints**
4. **All tests pass** with new endpoint structure
5. **Documentation updated** to reflect new endpoints

## 🚀 **NEXT STEPS**

1. **Immediate:** Fix gateway internal health endpoint conflict
2. **Short-term:** Update app factory for service-specific endpoints
3. **Medium-term:** Update all services to use unique endpoints
4. **Long-term:** Implement proper service discovery and health aggregation
