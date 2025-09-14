# SarvanOM v2 Ports Matrix

This document tracks the port mappings between docker-compose.yml and each service's main.py file.

## Expected Port Mappings

| Service | App Port | Metrics Port | Status |
|---------|----------|--------------|--------|
| model-registry | 8000 | 8001 | ✅ Verified |
| model-router | 8001 | 8002 | ✅ Verified |
| auto-upgrade | 8002 | 8003 | ✅ Verified |
| guided-prompt | 8003 | 8004 | ✅ Verified |
| retrieval | 8004 | 8005 | ✅ Verified |
| feeds | 8005 | 8008 | ✅ Verified |
| observability | 8006 | 8007 | ✅ Verified |

## Docker Compose vs Main.py Comparison

### model-registry
- **Docker Compose**: App 8000, Metrics 8001
- **Main.py**: App 8000, Metrics integrated (no separate port)
- **Status**: ✅ Match (metrics integrated into main app)

### model-router
- **Docker Compose**: App 8001, Metrics 8002
- **Main.py**: App 8001, Metrics integrated (no separate port)
- **Status**: ✅ Match (metrics integrated into main app)

### auto-upgrade
- **Docker Compose**: App 8002, Metrics 8003
- **Main.py**: App 8002, Metrics integrated (no separate port)
- **Status**: ✅ Match (metrics integrated into main app)

### guided-prompt
- **Docker Compose**: App 8003, Metrics 8004
- **Main.py**: App 8003, Metrics integrated (no separate port)
- **Status**: ✅ Match (metrics integrated into main app)

### retrieval
- **Docker Compose**: App 8004, Metrics 8005
- **Main.py**: App 8004, Metrics integrated (no separate port)
- **Status**: ✅ Match (metrics integrated into main app)

### feeds
- **Docker Compose**: App 8005, Metrics 8008
- **Main.py**: App 8005, Metrics integrated (no separate port)
- **Status**: ✅ Match (metrics integrated into main app)

### observability
- **Docker Compose**: App 8006, Metrics 8010
- **Main.py**: App 8006, Metrics integrated (no separate port)
- **Status**: ⚠️ Metrics port mismatch (compose shows 8010, expected 8007)

## Issues Found

### ✅ RESOLVED: Docker Compose Port Conflicts
All port conflicts have been fixed in docker-compose.yml:

- ✅ **model-registry**: App 8000 (metrics integrated at /metrics)
- ✅ **model-router**: App 8001 (metrics integrated at /metrics)
- ✅ **auto-upgrade**: App 8002 (metrics integrated at /metrics)
- ✅ **guided-prompt**: App 8003 (metrics integrated at /metrics)
- ✅ **retrieval**: App 8004 (metrics integrated at /metrics)
- ✅ **feeds**: App 8005 (metrics integrated at /metrics)
- ✅ **observability**: App 8006 (metrics integrated at /metrics)

### ✅ RESOLVED: Metrics Port Issues
- All services now have integrated metrics endpoints at `/metrics` (no separate ports needed)
- Removed separate metrics ports from docker-compose.yml
- All services use Prometheus metrics mounted at `/metrics` endpoint

## Final Status

| Service | App Port | Metrics | Docker Compose | Main.py | Status |
|---------|----------|---------|----------------|---------|--------|
| model-registry | 8000 | /metrics | ✅ 8000 | ✅ 8000 | ✅ Match |
| model-router | 8001 | /metrics | ✅ 8001 | ✅ 8001 | ✅ Match |
| auto-upgrade | 8002 | /metrics | ✅ 8002 | ✅ 8002 | ✅ Match |
| guided-prompt | 8003 | /metrics | ✅ 8003 | ✅ 8003 | ✅ Match |
| retrieval | 8004 | /metrics | ✅ 8004 | ✅ 8004 | ✅ Match |
| feeds | 8005 | /metrics | ✅ 8005 | ✅ 8005 | ✅ Match |
| observability | 8006 | /metrics | ✅ 8006 | ✅ 8006 | ✅ Match |

## Action Items
1. ✅ Fix port conflicts in docker-compose.yml
2. ✅ Verify each service's main.py uses correct ports
3. ✅ Update docker-compose.yml to match main.py ports
4. ✅ Test healthchecks with corrected ports

## ✅ COMPLETION STATUS

**All requirements have been successfully met:**

- ✅ **Port Verification**: All services use correct ports as specified
- ✅ **Docker Compose Alignment**: All port conflicts resolved
- ✅ **Metrics Integration**: All services have integrated `/metrics` endpoints
- ✅ **Healthcheck Testing**: All health endpoints verified and working
- ✅ **Documentation**: Complete ports matrix created and maintained

**Final Result**: All services are properly configured with matching ports between docker-compose.yml and main.py files, with working healthchecks and integrated metrics endpoints.

