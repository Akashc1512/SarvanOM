# Rate Limit & Abuse Prevention - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Create rate limit and abuse spec for per-IP RPM, UA fingerprinting, and burst logic

---

## 🎯 **Rate Limiting Overview**

SarvanOM v2 implements comprehensive rate limiting and abuse prevention to protect against malicious traffic, ensure fair resource usage, and maintain system stability.

### **Core Principles**
1. **Fair Usage**: Ensure equitable access to resources
2. **Abuse Prevention**: Protect against malicious and automated attacks
3. **System Stability**: Prevent resource exhaustion
4. **User Experience**: Minimize impact on legitimate users
5. **Scalability**: Handle high-volume traffic efficiently

---

## 🚦 **Rate Limiting Strategy**

### **Rate Limit Tiers**
| Tier | Description | Limits | Use Case |
|------|-------------|--------|----------|
| **Anonymous** | Unauthenticated users | 10 RPM, 100 RPH | Public access |
| **Authenticated** | Logged-in users | 60 RPM, 1000 RPH | Regular usage |
| **Premium** | Premium subscribers | 120 RPM, 5000 RPH | Enhanced usage |
| **Enterprise** | Enterprise customers | 300 RPM, 20000 RPH | High-volume usage |
| **API** | API consumers | 1000 RPM, 50000 RPH | Programmatic access |

### **Rate Limit Implementation**
```python
# Example rate limiting implementation
class RateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.rate_limits = {
            "anonymous": {"rpm": 10, "rph": 100},
            "authenticated": {"rpm": 60, "rph": 1000},
            "premium": {"rpm": 120, "rph": 5000},
            "enterprise": {"rpm": 300, "rph": 20000},
            "api": {"rpm": 1000, "rph": 50000}
        }
    
    def check_rate_limit(self, identifier: str, tier: str, endpoint: str = None) -> dict:
        """Check rate limit for identifier"""
        limits = self.rate_limits.get(tier, self.rate_limits["anonymous"])
        
        # Check per-minute limit
        minute_key = f"rate_limit:{identifier}:minute:{int(time.time() // 60)}"
        minute_count = self.redis_client.get(minute_key)
        
        if minute_count and int(minute_count) >= limits["rpm"]:
            return {
                "allowed": False,
                "limit": limits["rpm"],
                "remaining": 0,
                "reset_time": int(time.time() // 60) * 60 + 60,
                "reason": "minute_limit_exceeded"
            }
        
        # Check per-hour limit
        hour_key = f"rate_limit:{identifier}:hour:{int(time.time() // 3600)}"
        hour_count = self.redis_client.get(hour_key)
        
        if hour_count and int(hour_count) >= limits["rph"]:
            return {
                "allowed": False,
                "limit": limits["rph"],
                "remaining": 0,
                "reset_time": int(time.time() // 3600) * 3600 + 3600,
                "reason": "hour_limit_exceeded"
            }
        
        # Increment counters
        self.redis_client.incr(minute_key)
        self.redis_client.expire(minute_key, 60)
        
        self.redis_client.incr(hour_key)
        self.redis_client.expire(hour_key, 3600)
        
        # Calculate remaining
        minute_remaining = limits["rpm"] - (int(minute_count) + 1 if minute_count else 1)
        hour_remaining = limits["rph"] - (int(hour_count) + 1 if hour_count else 1)
        
        return {
            "allowed": True,
            "limit": limits["rpm"],
            "remaining": min(minute_remaining, hour_remaining),
            "reset_time": int(time.time() // 60) * 60 + 60,
            "reason": "allowed"
        }
    
    def get_rate_limit_info(self, identifier: str, tier: str) -> dict:
        """Get rate limit information for identifier"""
        limits = self.rate_limits.get(tier, self.rate_limits["anonymous"])
        
        # Get current counts
        minute_key = f"rate_limit:{identifier}:minute:{int(time.time() // 60)}"
        hour_key = f"rate_limit:{identifier}:hour:{int(time.time() // 3600)}"
        
        minute_count = int(self.redis_client.get(minute_key) or 0)
        hour_count = int(self.redis_client.get(hour_key) or 0)
        
        return {
            "tier": tier,
            "minute_limit": limits["rpm"],
            "minute_used": minute_count,
            "minute_remaining": max(0, limits["rpm"] - minute_count),
            "hour_limit": limits["rph"],
            "hour_used": hour_count,
            "hour_remaining": max(0, limits["rph"] - hour_count),
            "reset_time": int(time.time() // 60) * 60 + 60
        }
```

---

## 🔍 **Abuse Detection**

### **User Agent Fingerprinting**
| Fingerprint | Description | Risk Level | Action |
|-------------|-------------|------------|--------|
| **Browser** | Standard browser UA | Low | Allow |
| **Bot** | Known bot UA | Medium | Rate limit |
| **Suspicious** | Unusual UA pattern | High | Block |
| **Empty** | Missing or empty UA | High | Block |

### **User Agent Fingerprinting Implementation**
```python
# Example user agent fingerprinting implementation
class UserAgentFingerprinter:
    def __init__(self):
        self.bot_patterns = [
            r"bot", r"crawler", r"spider", r"scraper",
            r"curl", r"wget", r"python", r"java",
            r"postman", r"insomnia", r"httpie"
        ]
        
        self.suspicious_patterns = [
            r"^$", r"^Mozilla$", r"^User-Agent$",
            r"^[A-Za-z]{1,3}$", r"^[0-9]+$"
        ]
        
        self.risk_scores = {
            "browser": 0.1,
            "bot": 0.5,
            "suspicious": 0.8,
            "empty": 1.0
        }
    
    def analyze_user_agent(self, user_agent: str) -> dict:
        """Analyze user agent string"""
        if not user_agent or user_agent.strip() == "":
            return {
                "type": "empty",
                "risk_score": self.risk_scores["empty"],
                "action": "block",
                "reason": "empty_user_agent"
            }
        
        user_agent_lower = user_agent.lower()
        
        # Check for bot patterns
        for pattern in self.bot_patterns:
            if re.search(pattern, user_agent_lower):
                return {
                    "type": "bot",
                    "risk_score": self.risk_scores["bot"],
                    "action": "rate_limit",
                    "reason": f"bot_pattern_detected: {pattern}"
                }
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.match(pattern, user_agent):
                return {
                    "type": "suspicious",
                    "risk_score": self.risk_scores["suspicious"],
                    "action": "block",
                    "reason": f"suspicious_pattern: {pattern}"
                }
        
        # Check for standard browser patterns
        browser_patterns = [
            r"mozilla", r"chrome", r"firefox", r"safari", r"edge"
        ]
        
        for pattern in browser_patterns:
            if re.search(pattern, user_agent_lower):
                return {
                    "type": "browser",
                    "risk_score": self.risk_scores["browser"],
                    "action": "allow",
                    "reason": "standard_browser"
                }
        
        # Default to suspicious if no patterns match
        return {
            "type": "suspicious",
            "risk_score": self.risk_scores["suspicious"],
            "action": "rate_limit",
            "reason": "unknown_user_agent"
        }
    
    def get_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate fingerprint from user agent and IP"""
        # Normalize user agent
        normalized_ua = user_agent.lower().strip()
        
        # Create fingerprint
        fingerprint_data = f"{normalized_ua}:{ip_address}"
        fingerprint_hash = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        return fingerprint_hash
```

### **IP Address Analysis**
| IP Type | Description | Risk Level | Action |
|---------|-------------|------------|--------|
| **Residential** | Home internet | Low | Allow |
| **Corporate** | Business network | Low | Allow |
| **Datacenter** | Cloud/VPS | Medium | Rate limit |
| **VPN/Proxy** | Anonymizing service | High | Block |
| **Tor** | Tor network | High | Block |

### **IP Address Analysis Implementation**
```python
# Example IP address analysis implementation
class IPAddressAnalyzer:
    def __init__(self):
        self.datacenter_ranges = [
            "104.16.0.0/12",  # Cloudflare
            "172.16.0.0/12",  # Private
            "10.0.0.0/8",     # Private
            "192.168.0.0/16"  # Private
        ]
        
        self.vpn_proxy_ranges = [
            "185.220.0.0/16",  # Tor
            "198.96.0.0/16",   # Tor
            "199.87.0.0/16"    # Tor
        ]
        
        self.risk_scores = {
            "residential": 0.1,
            "corporate": 0.2,
            "datacenter": 0.5,
            "vpn_proxy": 0.8,
            "tor": 1.0
        }
    
    def analyze_ip_address(self, ip_address: str) -> dict:
        """Analyze IP address"""
        try:
            ip_obj = ipaddress.ip_address(ip_address)
        except ValueError:
            return {
                "type": "invalid",
                "risk_score": 1.0,
                "action": "block",
                "reason": "invalid_ip_address"
            }
        
        # Check for private IPs
        if ip_obj.is_private:
            return {
                "type": "private",
                "risk_score": 0.3,
                "action": "rate_limit",
                "reason": "private_ip_address"
            }
        
        # Check for datacenter ranges
        for range_str in self.datacenter_ranges:
            if ip_obj in ipaddress.ip_network(range_str):
                return {
                    "type": "datacenter",
                    "risk_score": self.risk_scores["datacenter"],
                    "action": "rate_limit",
                    "reason": f"datacenter_range: {range_str}"
                }
        
        # Check for VPN/Proxy ranges
        for range_str in self.vpn_proxy_ranges:
            if ip_obj in ipaddress.ip_network(range_str):
                return {
                    "type": "vpn_proxy",
                    "risk_score": self.risk_scores["vpn_proxy"],
                    "action": "block",
                    "reason": f"vpn_proxy_range: {range_str}"
                }
        
        # Check for Tor
        if self._is_tor_ip(ip_address):
            return {
                "type": "tor",
                "risk_score": self.risk_scores["tor"],
                "action": "block",
                "reason": "tor_network"
            }
        
        # Default to residential
        return {
            "type": "residential",
            "risk_score": self.risk_scores["residential"],
            "action": "allow",
            "reason": "residential_ip"
        }
    
    def _is_tor_ip(self, ip_address: str) -> bool:
        """Check if IP is Tor exit node"""
        # Implementation to check Tor exit node list
        # This would typically query a Tor exit node API
        return False
```

---

## 🚨 **Burst Logic**

### **Burst Detection**
| Burst Type | Description | Threshold | Action |
|------------|-------------|-----------|--------|
| **Normal** | Regular traffic | < 10 req/min | Allow |
| **Moderate** | Slightly elevated | 10-50 req/min | Rate limit |
| **High** | Burst traffic | 50-100 req/min | Block temporarily |
| **Extreme** | Attack traffic | > 100 req/min | Block permanently |

### **Burst Logic Implementation**
```python
# Example burst logic implementation
class BurstDetector:
    def __init__(self):
        self.burst_thresholds = {
            "normal": 10,
            "moderate": 50,
            "high": 100,
            "extreme": 200
        }
        
        self.burst_actions = {
            "normal": "allow",
            "moderate": "rate_limit",
            "high": "block_temporary",
            "extreme": "block_permanent"
        }
        
        self.block_durations = {
            "block_temporary": 300,  # 5 minutes
            "block_permanent": 86400  # 24 hours
        }
    
    def detect_burst(self, identifier: str, current_count: int) -> dict:
        """Detect burst traffic"""
        # Get recent request counts
        recent_counts = self._get_recent_counts(identifier)
        
        # Calculate burst score
        burst_score = self._calculate_burst_score(recent_counts, current_count)
        
        # Determine burst type
        burst_type = self._classify_burst(burst_score)
        
        # Get action
        action = self.burst_actions.get(burst_type, "allow")
        
        return {
            "burst_type": burst_type,
            "burst_score": burst_score,
            "action": action,
            "block_duration": self.block_durations.get(action, 0),
            "reason": f"burst_detected: {burst_type}"
        }
    
    def _get_recent_counts(self, identifier: str) -> list:
        """Get recent request counts"""
        # Get counts for last 10 minutes
        counts = []
        for i in range(10):
            minute_key = f"burst:{identifier}:minute:{int(time.time() // 60) - i}"
            count = int(self.redis_client.get(minute_key) or 0)
            counts.append(count)
        
        return counts
    
    def _calculate_burst_score(self, recent_counts: list, current_count: int) -> float:
        """Calculate burst score"""
        if not recent_counts:
            return 0.0
        
        # Calculate average
        average = sum(recent_counts) / len(recent_counts)
        
        # Calculate variance
        variance = sum((count - average) ** 2 for count in recent_counts) / len(recent_counts)
        
        # Calculate burst score
        if average == 0:
            burst_score = current_count
        else:
            burst_score = (current_count - average) / average
        
        return burst_score
    
    def _classify_burst(self, burst_score: float) -> str:
        """Classify burst type"""
        if burst_score < 0.5:
            return "normal"
        elif burst_score < 2.0:
            return "moderate"
        elif burst_score < 5.0:
            return "high"
        else:
            return "extreme"
```

---

## 🛡️ **Abuse Prevention System**

### **Abuse Prevention Implementation**
```python
# Example abuse prevention system implementation
class AbusePreventionSystem:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.ua_fingerprinter = UserAgentFingerprinter()
        self.ip_analyzer = IPAddressAnalyzer()
        self.burst_detector = BurstDetector()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def analyze_request(self, request) -> dict:
        """Analyze request for abuse"""
        # Extract request information
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        endpoint = request.path
        method = request.method
        
        # Generate identifier
        identifier = self._generate_identifier(ip_address, user_agent)
        
        # Analyze user agent
        ua_analysis = self.ua_fingerprinter.analyze_user_agent(user_agent)
        
        # Analyze IP address
        ip_analysis = self.ip_analyzer.analyze_ip_address(ip_address)
        
        # Check rate limits
        rate_limit_result = self.rate_limiter.check_rate_limit(identifier, "anonymous", endpoint)
        
        # Detect burst
        burst_result = self.burst_detector.detect_burst(identifier, rate_limit_result.get("remaining", 0))
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(ua_analysis, ip_analysis, burst_result)
        
        # Determine final action
        action = self._determine_action(risk_score, ua_analysis, ip_analysis, burst_result)
        
        return {
            "identifier": identifier,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "endpoint": endpoint,
            "method": method,
            "ua_analysis": ua_analysis,
            "ip_analysis": ip_analysis,
            "rate_limit_result": rate_limit_result,
            "burst_result": burst_result,
            "risk_score": risk_score,
            "action": action,
            "timestamp": time.time()
        }
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host
    
    def _generate_identifier(self, ip_address: str, user_agent: str) -> str:
        """Generate unique identifier"""
        fingerprint = self.ua_fingerprinter.get_fingerprint(user_agent, ip_address)
        return f"abuse:{fingerprint}"
    
    def _calculate_risk_score(self, ua_analysis: dict, ip_analysis: dict, burst_result: dict) -> float:
        """Calculate overall risk score"""
        ua_risk = ua_analysis.get("risk_score", 0.0)
        ip_risk = ip_analysis.get("risk_score", 0.0)
        burst_risk = burst_result.get("burst_score", 0.0)
        
        # Weighted average
        overall_risk = (ua_risk * 0.3) + (ip_risk * 0.4) + (burst_risk * 0.3)
        
        return min(overall_risk, 1.0)
    
    def _determine_action(self, risk_score: float, ua_analysis: dict, ip_analysis: dict, burst_result: dict) -> str:
        """Determine final action"""
        # Check for immediate blocks
        if ua_analysis.get("action") == "block":
            return "block"
        
        if ip_analysis.get("action") == "block":
            return "block"
        
        if burst_result.get("action") == "block_permanent":
            return "block"
        
        # Check risk score
        if risk_score > 0.8:
            return "block"
        elif risk_score > 0.6:
            return "rate_limit"
        elif risk_score > 0.4:
            return "monitor"
        else:
            return "allow"
    
    def apply_action(self, action: str, identifier: str, duration: int = 0):
        """Apply abuse prevention action"""
        if action == "block":
            # Block identifier
            block_key = f"blocked:{identifier}"
            self.redis_client.setex(block_key, duration or 3600, "blocked")
        
        elif action == "rate_limit":
            # Apply stricter rate limits
            rate_limit_key = f"rate_limit_strict:{identifier}"
            self.redis_client.setex(rate_limit_key, duration or 1800, "strict")
        
        elif action == "monitor":
            # Add to monitoring list
            monitor_key = f"monitor:{identifier}"
            self.redis_client.setex(monitor_key, duration or 3600, "monitoring")
    
    def is_blocked(self, identifier: str) -> bool:
        """Check if identifier is blocked"""
        block_key = f"blocked:{identifier}"
        return self.redis_client.exists(block_key)
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        rate_limit_key = f"rate_limit_strict:{identifier}"
        return self.redis_client.exists(rate_limit_key)
    
    def is_monitored(self, identifier: str) -> bool:
        """Check if identifier is monitored"""
        monitor_key = f"monitor:{identifier}"
        return self.redis_client.exists(monitor_key)
```

---

## 📊 **Monitoring & Analytics**

### **Abuse Metrics**
| Metric | Description | Threshold | Action |
|--------|-------------|-----------|--------|
| **Block Rate** | Percentage of blocked requests | > 5% | Investigate |
| **Rate Limit Hits** | Rate limit violations | > 100/hour | Review limits |
| **Burst Events** | Burst detection events | > 50/hour | Analyze patterns |
| **False Positives** | Legitimate requests blocked | > 1% | Adjust rules |

### **Abuse Monitoring Implementation**
```python
# Example abuse monitoring implementation
class AbuseMonitor:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "rate_limited_requests": 0,
            "burst_events": 0,
            "false_positives": 0
        }
        
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def record_request(self, analysis_result: dict):
        """Record request analysis result"""
        self.metrics["total_requests"] += 1
        
        action = analysis_result.get("action", "allow")
        
        if action == "block":
            self.metrics["blocked_requests"] += 1
        elif action == "rate_limit":
            self.metrics["rate_limited_requests"] += 1
        
        # Record burst events
        burst_result = analysis_result.get("burst_result", {})
        if burst_result.get("burst_type") != "normal":
            self.metrics["burst_events"] += 1
        
        # Store detailed metrics
        self._store_detailed_metrics(analysis_result)
    
    def _store_detailed_metrics(self, analysis_result: dict):
        """Store detailed metrics"""
        timestamp = int(time.time())
        
        # Store by hour
        hour_key = f"abuse_metrics:hour:{timestamp // 3600}"
        
        metrics_data = {
            "timestamp": timestamp,
            "action": analysis_result.get("action", "allow"),
            "risk_score": analysis_result.get("risk_score", 0.0),
            "ua_type": analysis_result.get("ua_analysis", {}).get("type", "unknown"),
            "ip_type": analysis_result.get("ip_analysis", {}).get("type", "unknown"),
            "burst_type": analysis_result.get("burst_result", {}).get("burst_type", "normal")
        }
        
        self.redis_client.lpush(hour_key, json.dumps(metrics_data))
        self.redis_client.expire(hour_key, 86400 * 7)  # Keep for 7 days
    
    def get_abuse_summary(self, hours: int = 24) -> dict:
        """Get abuse summary for specified hours"""
        current_time = int(time.time())
        summary = {
            "total_requests": 0,
            "blocked_requests": 0,
            "rate_limited_requests": 0,
            "burst_events": 0,
            "block_rate": 0.0,
            "rate_limit_rate": 0.0,
            "burst_rate": 0.0,
            "top_ua_types": {},
            "top_ip_types": {},
            "top_burst_types": {}
        }
        
        for i in range(hours):
            hour_key = f"abuse_metrics:hour:{(current_time - i * 3600) // 3600}"
            hour_data = self.redis_client.lrange(hour_key, 0, -1)
            
            for data_str in hour_data:
                data = json.loads(data_str)
                
                summary["total_requests"] += 1
                
                if data["action"] == "block":
                    summary["blocked_requests"] += 1
                elif data["action"] == "rate_limit":
                    summary["rate_limited_requests"] += 1
                
                if data["burst_type"] != "normal":
                    summary["burst_events"] += 1
                
                # Count types
                ua_type = data["ua_type"]
                if ua_type not in summary["top_ua_types"]:
                    summary["top_ua_types"][ua_type] = 0
                summary["top_ua_types"][ua_type] += 1
                
                ip_type = data["ip_type"]
                if ip_type not in summary["top_ip_types"]:
                    summary["top_ip_types"][ip_type] = 0
                summary["top_ip_types"][ip_type] += 1
                
                burst_type = data["burst_type"]
                if burst_type not in summary["top_burst_types"]:
                    summary["top_burst_types"][burst_type] = 0
                summary["top_burst_types"][burst_type] += 1
        
        # Calculate rates
        if summary["total_requests"] > 0:
            summary["block_rate"] = summary["blocked_requests"] / summary["total_requests"]
            summary["rate_limit_rate"] = summary["rate_limited_requests"] / summary["total_requests"]
            summary["burst_rate"] = summary["burst_events"] / summary["total_requests"]
        
        return summary
    
    def check_abuse_thresholds(self) -> list:
        """Check abuse thresholds and generate alerts"""
        alerts = []
        summary = self.get_abuse_summary(1)  # Last hour
        
        # Check block rate
        if summary["block_rate"] > 0.05:  # 5%
            alerts.append({
                "type": "high_block_rate",
                "severity": "warning",
                "message": f"High block rate: {summary['block_rate']:.2%}",
                "threshold": "5%",
                "current": f"{summary['block_rate']:.2%}"
            })
        
        # Check rate limit hits
        if summary["rate_limited_requests"] > 100:
            alerts.append({
                "type": "high_rate_limit_hits",
                "severity": "info",
                "message": f"High rate limit hits: {summary['rate_limited_requests']}",
                "threshold": "100/hour",
                "current": f"{summary['rate_limited_requests']}/hour"
            })
        
        # Check burst events
        if summary["burst_events"] > 50:
            alerts.append({
                "type": "high_burst_events",
                "severity": "warning",
                "message": f"High burst events: {summary['burst_events']}",
                "threshold": "50/hour",
                "current": f"{summary['burst_events']}/hour"
            })
        
        return alerts
```

---

## 📚 **References**

- Security & Privacy: `10_security_and_privacy.md`
- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This rate limit and abuse prevention specification provides comprehensive protection for SarvanOM v2 system against malicious traffic and abuse.*
