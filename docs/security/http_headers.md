# HTTP Headers - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Create HTTP headers spec for CSP, HSTS, referrer, frame, and permissions

---

## 🎯 **HTTP Headers Overview**

SarvanOM v2 implements comprehensive HTTP security headers to protect against common web vulnerabilities and ensure secure communication between clients and servers.

### **Core Principles**
1. **Defense in Depth**: Multiple layers of security headers
2. **Zero Trust**: Assume all requests are potentially malicious
3. **Content Security**: Prevent XSS and injection attacks
4. **Transport Security**: Ensure secure communication
5. **Privacy Protection**: Minimize information leakage

---

## 🔒 **Security Headers**

### **Content Security Policy (CSP)**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **Content-Security-Policy** | `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.sarvanom.com; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self';` | Prevent XSS attacks | All responses |

### **CSP Implementation**
```python
# Example CSP implementation
class ContentSecurityPolicy:
    def __init__(self):
        self.csp_directives = {
            "default-src": ["'self'"],
            "script-src": [
                "'self'",
                "'unsafe-inline'",
                "'unsafe-eval'",
                "https://cdn.jsdelivr.net"
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
                "https://fonts.googleapis.com"
            ],
            "font-src": [
                "'self'",
                "https://fonts.gstatic.com"
            ],
            "img-src": [
                "'self'",
                "data:",
                "https:"
            ],
            "connect-src": [
                "'self'",
                "https://api.sarvanom.com"
            ],
            "frame-src": ["'none'"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"]
        }
    
    def generate_csp_header(self) -> str:
        """Generate CSP header value"""
        csp_parts = []
        
        for directive, sources in self.csp_directives.items():
            csp_parts.append(f"{directive} {' '.join(sources)}")
        
        return "; ".join(csp_parts)
    
    def apply_csp_header(self, response):
        """Apply CSP header to response"""
        csp_value = self.generate_csp_header()
        response.headers["Content-Security-Policy"] = csp_value
        return response
```

### **HTTP Strict Transport Security (HSTS)**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **Strict-Transport-Security** | `max-age=31536000; includeSubDomains; preload` | Force HTTPS | All HTTPS responses |

### **HSTS Implementation**
```python
# Example HSTS implementation
class HTTPStrictTransportSecurity:
    def __init__(self):
        self.max_age = 31536000  # 1 year
        self.include_subdomains = True
        self.preload = True
    
    def generate_hsts_header(self) -> str:
        """Generate HSTS header value"""
        hsts_parts = [f"max-age={self.max_age}"]
        
        if self.include_subdomains:
            hsts_parts.append("includeSubDomains")
        
        if self.preload:
            hsts_parts.append("preload")
        
        return "; ".join(hsts_parts)
    
    def apply_hsts_header(self, response):
        """Apply HSTS header to response"""
        hsts_value = self.generate_hsts_header()
        response.headers["Strict-Transport-Security"] = hsts_value
        return response
```

### **X-Frame-Options**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **X-Frame-Options** | `DENY` | Prevent clickjacking | All responses |

### **X-Frame-Options Implementation**
```python
# Example X-Frame-Options implementation
class XFrameOptions:
    def __init__(self):
        self.frame_options = "DENY"
    
    def apply_frame_options_header(self, response):
        """Apply X-Frame-Options header to response"""
        response.headers["X-Frame-Options"] = self.frame_options
        return response
```

### **X-Content-Type-Options**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **X-Content-Type-Options** | `nosniff` | Prevent MIME sniffing | All responses |

### **X-Content-Type-Options Implementation**
```python
# Example X-Content-Type-Options implementation
class XContentTypeOptions:
    def __init__(self):
        self.content_type_options = "nosniff"
    
    def apply_content_type_options_header(self, response):
        """Apply X-Content-Type-Options header to response"""
        response.headers["X-Content-Type-Options"] = self.content_type_options
        return response
```

### **Referrer Policy**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **Referrer-Policy** | `strict-origin-when-cross-origin` | Control referrer information | All responses |

### **Referrer Policy Implementation**
```python
# Example Referrer Policy implementation
class ReferrerPolicy:
    def __init__(self):
        self.referrer_policy = "strict-origin-when-cross-origin"
    
    def apply_referrer_policy_header(self, response):
        """Apply Referrer-Policy header to response"""
        response.headers["Referrer-Policy"] = self.referrer_policy
        return response
```

### **Permissions Policy**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **Permissions-Policy** | `geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), ambient-light-sensor=(), autoplay=(), encrypted-media=(), fullscreen=(self), picture-in-picture=()` | Control browser features | All responses |

### **Permissions Policy Implementation**
```python
# Example Permissions Policy implementation
class PermissionsPolicy:
    def __init__(self):
        self.permissions = {
            "geolocation": "()",
            "microphone": "()",
            "camera": "()",
            "payment": "()",
            "usb": "()",
            "magnetometer": "()",
            "gyroscope": "()",
            "accelerometer": "()",
            "ambient-light-sensor": "()",
            "autoplay": "()",
            "encrypted-media": "()",
            "fullscreen": "(self)",
            "picture-in-picture": "()"
        }
    
    def generate_permissions_policy_header(self) -> str:
        """Generate Permissions-Policy header value"""
        policy_parts = []
        
        for feature, allowlist in self.permissions.items():
            policy_parts.append(f"{feature}={allowlist}")
        
        return ", ".join(policy_parts)
    
    def apply_permissions_policy_header(self, response):
        """Apply Permissions-Policy header to response"""
        policy_value = self.generate_permissions_policy_header()
        response.headers["Permissions-Policy"] = policy_value
        return response
```

---

## 🛡️ **Additional Security Headers**

### **X-XSS-Protection**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **X-XSS-Protection** | `1; mode=block` | Enable XSS filtering | All responses |

### **X-XSS-Protection Implementation**
```python
# Example X-XSS-Protection implementation
class XXSSProtection:
    def __init__(self):
        self.xss_protection = "1; mode=block"
    
    def apply_xss_protection_header(self, response):
        """Apply X-XSS-Protection header to response"""
        response.headers["X-XSS-Protection"] = self.xss_protection
        return response
```

### **Cross-Origin Resource Sharing (CORS)**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **Access-Control-Allow-Origin** | `https://sarvanom.com` | Control cross-origin requests | API responses |
| **Access-Control-Allow-Methods** | `GET, POST, PUT, DELETE, OPTIONS` | Allowed HTTP methods | API responses |
| **Access-Control-Allow-Headers** | `Content-Type, Authorization, X-Requested-With` | Allowed headers | API responses |
| **Access-Control-Max-Age** | `86400` | Preflight cache time | API responses |

### **CORS Implementation**
```python
# Example CORS implementation
class CrossOriginResourceSharing:
    def __init__(self):
        self.allowed_origins = [
            "https://sarvanom.com",
            "https://www.sarvanom.com",
            "https://app.sarvanom.com"
        ]
        self.allowed_methods = [
            "GET", "POST", "PUT", "DELETE", "OPTIONS"
        ]
        self.allowed_headers = [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Trace-ID",
            "X-Span-ID"
        ]
        self.max_age = 86400  # 24 hours
    
    def apply_cors_headers(self, response, origin: str = None):
        """Apply CORS headers to response"""
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "https://sarvanom.com"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        return response
```

### **Cache Control**
| Header | Value | Purpose | Implementation |
|--------|-------|---------|----------------|
| **Cache-Control** | `no-cache, no-store, must-revalidate` | Prevent caching | Sensitive responses |
| **Pragma** | `no-cache` | HTTP/1.0 cache control | Sensitive responses |
| **Expires** | `0` | Expire immediately | Sensitive responses |

### **Cache Control Implementation**
```python
# Example Cache Control implementation
class CacheControl:
    def __init__(self):
        self.no_cache_directives = [
            "no-cache",
            "no-store",
            "must-revalidate"
        ]
        self.pragma = "no-cache"
        self.expires = "0"
    
    def apply_no_cache_headers(self, response):
        """Apply no-cache headers to response"""
        response.headers["Cache-Control"] = ", ".join(self.no_cache_directives)
        response.headers["Pragma"] = self.pragma
        response.headers["Expires"] = self.expires
        
        return response
    
    def apply_cache_headers(self, response, max_age: int = 3600):
        """Apply cache headers to response"""
        response.headers["Cache-Control"] = f"public, max-age={max_age}"
        response.headers["Expires"] = str(int(time.time()) + max_age)
        
        return response
```

---

## 🔧 **Header Implementation**

### **Security Headers Middleware**
```python
# Example security headers middleware implementation
class SecurityHeadersMiddleware:
    def __init__(self):
        self.csp = ContentSecurityPolicy()
        self.hsts = HTTPStrictTransportSecurity()
        self.frame_options = XFrameOptions()
        self.content_type_options = XContentTypeOptions()
        self.referrer_policy = ReferrerPolicy()
        self.permissions_policy = PermissionsPolicy()
        self.xss_protection = XXSSProtection()
        self.cors = CrossOriginResourceSharing()
        self.cache_control = CacheControl()
    
    def apply_security_headers(self, response, request=None):
        """Apply all security headers to response"""
        # Content Security Policy
        response = self.csp.apply_csp_header(response)
        
        # HTTP Strict Transport Security
        if request and request.is_secure:
            response = self.hsts.apply_hsts_header(response)
        
        # X-Frame-Options
        response = self.frame_options.apply_frame_options_header(response)
        
        # X-Content-Type-Options
        response = self.content_type_options.apply_content_type_options_header(response)
        
        # Referrer Policy
        response = self.referrer_policy.apply_referrer_policy_header(response)
        
        # Permissions Policy
        response = self.permissions_policy.apply_permissions_policy_header(response)
        
        # X-XSS-Protection
        response = self.xss_protection.apply_xss_protection_header(response)
        
        # CORS headers
        if request:
            origin = request.headers.get("Origin")
            response = self.cors.apply_cors_headers(response, origin)
        
        # Cache control for sensitive endpoints
        if self._is_sensitive_endpoint(request):
            response = self.cache_control.apply_no_cache_headers(response)
        else:
            response = self.cache_control.apply_cache_headers(response)
        
        return response
    
    def _is_sensitive_endpoint(self, request) -> bool:
        """Check if endpoint is sensitive"""
        if not request:
            return False
        
        sensitive_paths = [
            "/api/auth/",
            "/api/user/",
            "/api/admin/",
            "/api/analytics/"
        ]
        
        return any(request.path.startswith(path) for path in sensitive_paths)
```

### **FastAPI Integration**
```python
# Example FastAPI integration
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.security_headers = SecurityHeadersMiddleware()
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Apply security headers
        response = self.security_headers.apply_security_headers(response, request)
        
        return response

# Add middleware to FastAPI app
app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

### **Next.js Integration**
```javascript
// Example Next.js integration
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.sarvanom.com; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self';"
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains; preload'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), ambient-light-sensor=(), autoplay=(), encrypted-media=(), fullscreen=(self), picture-in-picture=()'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  }
];

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## 📊 **Header Validation**

### **Security Header Testing**
```python
# Example security header testing
class SecurityHeaderValidator:
    def __init__(self):
        self.required_headers = [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Referrer-Policy",
            "Permissions-Policy",
            "X-XSS-Protection"
        ]
        
        self.https_required_headers = [
            "Strict-Transport-Security"
        ]
    
    def validate_headers(self, response, is_https: bool = False) -> dict:
        """Validate security headers in response"""
        validation_result = {
            "valid": True,
            "missing_headers": [],
            "invalid_headers": [],
            "recommendations": []
        }
        
        # Check required headers
        for header in self.required_headers:
            if header not in response.headers:
                validation_result["missing_headers"].append(header)
                validation_result["valid"] = False
        
        # Check HTTPS-specific headers
        if is_https:
            for header in self.https_required_headers:
                if header not in response.headers:
                    validation_result["missing_headers"].append(header)
                    validation_result["valid"] = False
        
        # Validate header values
        self._validate_header_values(response, validation_result)
        
        # Generate recommendations
        self._generate_recommendations(validation_result)
        
        return validation_result
    
    def _validate_header_values(self, response, validation_result):
        """Validate header values"""
        # Validate CSP
        if "Content-Security-Policy" in response.headers:
            csp_value = response.headers["Content-Security-Policy"]
            if "unsafe-inline" in csp_value and "script-src" in csp_value:
                validation_result["recommendations"].append(
                    "Consider removing 'unsafe-inline' from script-src for better security"
                )
        
        # Validate HSTS
        if "Strict-Transport-Security" in response.headers:
            hsts_value = response.headers["Strict-Transport-Security"]
            if "max-age=0" in hsts_value:
                validation_result["invalid_headers"].append("Strict-Transport-Security")
                validation_result["valid"] = False
        
        # Validate X-Frame-Options
        if "X-Frame-Options" in response.headers:
            frame_options = response.headers["X-Frame-Options"]
            if frame_options not in ["DENY", "SAMEORIGIN"]:
                validation_result["invalid_headers"].append("X-Frame-Options")
                validation_result["valid"] = False
    
    def _generate_recommendations(self, validation_result):
        """Generate security recommendations"""
        if not validation_result["valid"]:
            validation_result["recommendations"].append(
                "Fix missing or invalid security headers to improve security posture"
            )
        
        if "Content-Security-Policy" in validation_result["missing_headers"]:
            validation_result["recommendations"].append(
                "Implement Content Security Policy to prevent XSS attacks"
            )
        
        if "Strict-Transport-Security" in validation_result["missing_headers"]:
            validation_result["recommendations"].append(
                "Implement HSTS to enforce HTTPS connections"
            )
```

---

## 📚 **References**

- Security & Privacy: `10_security_and_privacy.md`
- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This HTTP headers specification provides comprehensive security headers for SarvanOM v2 system protection and compliance.*
