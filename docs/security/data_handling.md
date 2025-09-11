# Data Handling - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Create data handling spec for PII rules, retention, redaction, and audit

---

## 🎯 **Data Handling Overview**

SarvanOM v2 implements comprehensive data handling policies to ensure privacy, security, and compliance with data protection regulations.

### **Core Principles**
1. **Privacy by Design**: Privacy considerations from the start
2. **Data Minimization**: Collect only necessary data
3. **Purpose Limitation**: Use data only for stated purposes
4. **Transparency**: Clear data handling practices
5. **User Control**: Users control their data

---

## 🔒 **Data Classification**

### **Data Sensitivity Levels**
| Level | Description | Examples | Handling Requirements |
|-------|-------------|----------|----------------------|
| **Public** | Non-sensitive data | Public content, metadata | Standard handling |
| **Internal** | Business data | Analytics, logs | Access controls |
| **Confidential** | Sensitive business data | API keys, configs | Encryption, access logs |
| **Restricted** | Highly sensitive data | PII, financial data | Strong encryption, audit |

### **Data Classification Implementation**
```python
# Example data classification implementation
class DataClassifier:
    def __init__(self):
        self.classification_rules = {
            "email": "restricted",
            "phone": "restricted",
            "name": "restricted",
            "address": "restricted",
            "ssn": "restricted",
            "credit_card": "restricted",
            "ip_address": "confidential",
            "user_agent": "confidential",
            "session_id": "confidential",
            "api_key": "confidential",
            "query": "internal",
            "response": "internal",
            "timestamp": "public",
            "version": "public"
        }
        
        self.pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        }
    
    def classify_data(self, data: dict) -> dict:
        """Classify data based on content"""
        classification_result = {
            "overall_classification": "public",
            "field_classifications": {},
            "pii_detected": [],
            "recommendations": []
        }
        
        for field, value in data.items():
            # Get field classification
            field_classification = self.classification_rules.get(field, "internal")
            classification_result["field_classifications"][field] = field_classification
            
            # Check for PII
            pii_detected = self._detect_pii(field, str(value))
            if pii_detected:
                classification_result["pii_detected"].extend(pii_detected)
                classification_result["field_classifications"][field] = "restricted"
            
            # Update overall classification
            if field_classification == "restricted":
                classification_result["overall_classification"] = "restricted"
            elif field_classification == "confidential" and classification_result["overall_classification"] != "restricted":
                classification_result["overall_classification"] = "confidential"
            elif field_classification == "internal" and classification_result["overall_classification"] == "public":
                classification_result["overall_classification"] = "internal"
        
        # Generate recommendations
        classification_result["recommendations"] = self._generate_recommendations(classification_result)
        
        return classification_result
    
    def _detect_pii(self, field: str, value: str) -> list:
        """Detect PII in field value"""
        detected_pii = []
        
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, value, re.IGNORECASE):
                detected_pii.append({
                    "type": pii_type,
                    "field": field,
                    "pattern": pattern,
                    "severity": "high" if pii_type in ["ssn", "credit_card"] else "medium"
                })
        
        return detected_pii
    
    def _generate_recommendations(self, classification_result: dict) -> list:
        """Generate data handling recommendations"""
        recommendations = []
        
        if classification_result["overall_classification"] == "restricted":
            recommendations.append("Apply strong encryption and access controls")
            recommendations.append("Implement data retention policies")
            recommendations.append("Enable audit logging")
        
        if classification_result["pii_detected"]:
            recommendations.append("Implement PII redaction for logs")
            recommendations.append("Apply data minimization principles")
            recommendations.append("Ensure GDPR/CCPA compliance")
        
        if classification_result["overall_classification"] == "confidential":
            recommendations.append("Implement access controls")
            recommendations.append("Enable audit logging")
        
        return recommendations
```

---

## 🎯 **Guided Prompt Confirmation Data Handling**

### **Refinement Data Classification**
| Data Type | Classification | Retention | Redaction Required | Purpose |
|-----------|----------------|-----------|-------------------|---------|
| **Raw User Query** | Restricted | Not stored by default | Yes | Input for refinement |
| **Refined Query** | Internal | 30 days | No | Final processed query |
| **Refinement Suggestions** | Internal | 7 days | No | User experience improvement |
| **User Interactions** | Internal | 90 days | No | Analytics and optimization |
| **Constraint Selections** | Internal | 30 days | No | User preference tracking |

### **Guided Prompt Privacy Rules**
```python
# Example Guided Prompt data handling
class GuidedPromptDataHandler:
    def __init__(self):
        self.pii_redaction_rules = {
            "email": self._redact_email,
            "phone": self._redact_phone,
            "address": self._redact_address,
            "ssn": self._redact_ssn,
            "credit_card": self._redact_credit_card
        }
        
        self.retention_policies = {
            "raw_query": 0,  # Not stored by default
            "refined_query": 30,  # 30 days
            "suggestions": 7,  # 7 days
            "interactions": 90,  # 90 days
            "constraints": 30  # 30 days
        }
    
    def process_refinement_data(self, raw_query: str, user_id: str) -> dict:
        """Process refinement data with privacy protection"""
        # Redact PII from raw query
        redacted_query = self._redact_pii(raw_query)
        
        # Generate refinement suggestions
        suggestions = self._generate_suggestions(redacted_query)
        
        # Store only necessary data
        refinement_data = {
            "user_id": user_id,
            "redacted_query": redacted_query,
            "suggestions": suggestions,
            "timestamp": datetime.now(),
            "retention_days": self.retention_policies["suggestions"]
        }
        
        return refinement_data
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        redacted_text = text
        
        for pii_type, redaction_func in self.pii_redaction_rules.items():
            redacted_text = redaction_func(redacted_text)
        
        return redacted_text
    
    def _redact_email(self, text: str) -> str:
        """Redact email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '[EMAIL_REDACTED]', text)
    
    def _redact_phone(self, text: str) -> str:
        """Redact phone numbers"""
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        return re.sub(phone_pattern, '[PHONE_REDACTED]', text)
    
    def _redact_address(self, text: str) -> str:
        """Redact addresses"""
        address_pattern = r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
        return re.sub(address_pattern, '[ADDRESS_REDACTED]', text, flags=re.IGNORECASE)
    
    def _redact_ssn(self, text: str) -> str:
        """Redact SSN"""
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        return re.sub(ssn_pattern, '[SSN_REDACTED]', text)
    
    def _redact_credit_card(self, text: str) -> str:
        """Redact credit card numbers"""
        cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        return re.sub(cc_pattern, '[CC_REDACTED]', text)
    
    def store_refinement_data(self, refinement_data: dict, consent_given: bool = False):
        """Store refinement data based on consent"""
        if not consent_given:
            # Store only aggregated, non-identifiable data
            aggregated_data = {
                "refinement_type": refinement_data.get("refinement_type"),
                "acceptance_rate": refinement_data.get("acceptance_rate"),
                "timestamp": refinement_data["timestamp"]
            }
            self._store_aggregated_data(aggregated_data)
        else:
            # Store full refinement data with user consent
            self._store_full_data(refinement_data)
    
    def _store_aggregated_data(self, data: dict):
        """Store aggregated, non-identifiable data"""
        # Implementation for storing aggregated data
        pass
    
    def _store_full_data(self, data: dict):
        """Store full refinement data with consent"""
        # Implementation for storing full data
        pass
```

### **Consent Management for Guided Prompt**
```python
# Example consent management
class GuidedPromptConsentManager:
    def __init__(self):
        self.consent_types = {
            "refinement_storage": "Store refinement data for product improvement",
            "analytics_tracking": "Track refinement interactions for analytics",
            "personalization": "Use refinement history for personalization",
            "research": "Use anonymized data for research purposes"
        }
    
    def get_consent_status(self, user_id: str) -> dict:
        """Get user consent status for Guided Prompt features"""
        return {
            "refinement_storage": self._check_consent(user_id, "refinement_storage"),
            "analytics_tracking": self._check_consent(user_id, "analytics_tracking"),
            "personalization": self._check_consent(user_id, "personalization"),
            "research": self._check_consent(user_id, "research")
        }
    
    def update_consent(self, user_id: str, consent_type: str, granted: bool):
        """Update user consent for specific feature"""
        # Implementation for updating consent
        pass
    
    def _check_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given consent for specific feature"""
        # Implementation for checking consent
        return False
```

### **Guided Prompt Data Retention**
| Data Type | Default Retention | With Consent | Purpose |
|-----------|------------------|--------------|---------|
| **Raw Queries** | Not stored | Not stored | Privacy protection |
| **Refined Queries** | 30 days | 90 days | User experience |
| **Refinement Suggestions** | 7 days | 30 days | Product improvement |
| **User Interactions** | 90 days | 1 year | Analytics |
| **Constraint Preferences** | 30 days | 1 year | Personalization |

---

## 🗑️ **Data Retention**

### **Retention Policies**
| Data Type | Retention Period | Purpose | Disposal Method |
|-----------|------------------|---------|-----------------|
| **User Data** | 7 years | Legal compliance | Secure deletion |
| **Query Logs** | 90 days | Analytics | Automated deletion |
| **Error Logs** | 1 year | Debugging | Automated deletion |
| **Audit Logs** | 7 years | Compliance | Archive then delete |
| **Cache Data** | 24 hours | Performance | Automated deletion |
| **Session Data** | 30 days | Security | Automated deletion |

### **Data Retention Implementation**
```python
# Example data retention implementation
class DataRetentionManager:
    def __init__(self):
        self.retention_policies = {
            "user_data": {
                "retention_days": 2555,  # 7 years
                "purpose": "legal_compliance",
                "disposal_method": "secure_deletion",
                "auto_delete": False
            },
            "query_logs": {
                "retention_days": 90,
                "purpose": "analytics",
                "disposal_method": "automated_deletion",
                "auto_delete": True
            },
            "error_logs": {
                "retention_days": 365,
                "purpose": "debugging",
                "disposal_method": "automated_deletion",
                "auto_delete": True
            },
            "audit_logs": {
                "retention_days": 2555,  # 7 years
                "purpose": "compliance",
                "disposal_method": "archive_then_delete",
                "auto_delete": False
            },
            "cache_data": {
                "retention_days": 1,
                "purpose": "performance",
                "disposal_method": "automated_deletion",
                "auto_delete": True
            },
            "session_data": {
                "retention_days": 30,
                "purpose": "security",
                "disposal_method": "automated_deletion",
                "auto_delete": True
            }
        }
        
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.db_client = None  # Database client
    
    def apply_retention_policy(self, data_type: str, data_id: str, created_at: datetime):
        """Apply retention policy to data"""
        if data_type not in self.retention_policies:
            raise ValueError(f"Unknown data type: {data_type}")
        
        policy = self.retention_policies[data_type]
        
        # Calculate expiration date
        expiration_date = created_at + timedelta(days=policy["retention_days"])
        
        # Store retention information
        retention_key = f"retention:{data_type}:{data_id}"
        retention_data = {
            "data_type": data_type,
            "data_id": data_id,
            "created_at": created_at.isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "retention_days": policy["retention_days"],
            "purpose": policy["purpose"],
            "disposal_method": policy["disposal_method"],
            "auto_delete": policy["auto_delete"]
        }
        
        self.redis_client.setex(
            retention_key,
            policy["retention_days"] * 24 * 3600,  # Convert to seconds
            json.dumps(retention_data)
        )
        
        return retention_data
    
    def check_expired_data(self) -> list:
        """Check for expired data"""
        expired_data = []
        
        # Get all retention keys
        retention_keys = self.redis_client.keys("retention:*")
        
        for key in retention_keys:
            retention_data_str = self.redis_client.get(key)
            if retention_data_str:
                retention_data = json.loads(retention_data_str)
                
                # Check if expired
                expiration_date = datetime.fromisoformat(retention_data["expiration_date"])
                if datetime.now() > expiration_date:
                    expired_data.append(retention_data)
        
        return expired_data
    
    def dispose_expired_data(self, expired_data: list) -> dict:
        """Dispose of expired data"""
        disposal_result = {
            "disposed_count": 0,
            "failed_count": 0,
            "disposal_methods": {},
            "errors": []
        }
        
        for data in expired_data:
            try:
                disposal_method = data["disposal_method"]
                
                if disposal_method == "automated_deletion":
                    self._automated_deletion(data)
                elif disposal_method == "secure_deletion":
                    self._secure_deletion(data)
                elif disposal_method == "archive_then_delete":
                    self._archive_then_delete(data)
                
                disposal_result["disposed_count"] += 1
                
                if disposal_method not in disposal_result["disposal_methods"]:
                    disposal_result["disposal_methods"][disposal_method] = 0
                disposal_result["disposal_methods"][disposal_method] += 1
                
            except Exception as e:
                disposal_result["failed_count"] += 1
                disposal_result["errors"].append({
                    "data_id": data["data_id"],
                    "error": str(e)
                })
        
        return disposal_result
    
    def _automated_deletion(self, data: dict):
        """Automated deletion of data"""
        data_type = data["data_type"]
        data_id = data["data_id"]
        
        # Delete from database
        if data_type == "query_logs":
            self._delete_query_logs(data_id)
        elif data_type == "error_logs":
            self._delete_error_logs(data_id)
        elif data_type == "cache_data":
            self._delete_cache_data(data_id)
        elif data_type == "session_data":
            self._delete_session_data(data_id)
        
        # Remove retention record
        retention_key = f"retention:{data_type}:{data_id}"
        self.redis_client.delete(retention_key)
    
    def _secure_deletion(self, data: dict):
        """Secure deletion of data"""
        data_type = data["data_type"]
        data_id = data["data_id"]
        
        # Overwrite data with random bytes
        if data_type == "user_data":
            self._overwrite_user_data(data_id)
        
        # Delete from database
        self._delete_user_data(data_id)
        
        # Remove retention record
        retention_key = f"retention:{data_type}:{data_id}"
        self.redis_client.delete(retention_key)
    
    def _archive_then_delete(self, data: dict):
        """Archive data then delete"""
        data_type = data["data_type"]
        data_id = data["data_id"]
        
        # Archive to long-term storage
        if data_type == "audit_logs":
            self._archive_audit_logs(data_id)
        
        # Delete from active database
        self._delete_audit_logs(data_id)
        
        # Remove retention record
        retention_key = f"retention:{data_type}:{data_id}"
        self.redis_client.delete(retention_key)
    
    def _delete_query_logs(self, data_id: str):
        """Delete query logs"""
        # Implementation for deleting query logs
        pass
    
    def _delete_error_logs(self, data_id: str):
        """Delete error logs"""
        # Implementation for deleting error logs
        pass
    
    def _delete_cache_data(self, data_id: str):
        """Delete cache data"""
        # Implementation for deleting cache data
        pass
    
    def _delete_session_data(self, data_id: str):
        """Delete session data"""
        # Implementation for deleting session data
        pass
    
    def _overwrite_user_data(self, data_id: str):
        """Overwrite user data with random bytes"""
        # Implementation for overwriting user data
        pass
    
    def _delete_user_data(self, data_id: str):
        """Delete user data"""
        # Implementation for deleting user data
        pass
    
    def _archive_audit_logs(self, data_id: str):
        """Archive audit logs"""
        # Implementation for archiving audit logs
        pass
    
    def _delete_audit_logs(self, data_id: str):
        """Delete audit logs"""
        # Implementation for deleting audit logs
        pass
```

---

## 🔍 **Data Redaction**

### **Redaction Rules**
| Data Type | Redaction Method | Example | Use Case |
|-----------|------------------|---------|----------|
| **Email** | Partial redaction | `j***@example.com` | Logs, analytics |
| **Phone** | Partial redaction | `***-***-1234` | Logs, analytics |
| **SSN** | Full redaction | `***-**-****` | All contexts |
| **Credit Card** | Full redaction | `****-****-****-1234` | All contexts |
| **IP Address** | Partial redaction | `192.168.***.***` | Logs, analytics |
| **Name** | Partial redaction | `J*** S***` | Logs, analytics |

### **Data Redaction Implementation**
```python
# Example data redaction implementation
class DataRedactor:
    def __init__(self):
        self.redaction_rules = {
            "email": {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "method": "partial",
                "replacement": r"\1***@\2",
                "groups": [r"([A-Za-z0-9._%+-]+)", r"([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})"]
            },
            "phone": {
                "pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                "method": "partial",
                "replacement": r"***-***-\1",
                "groups": [r"(\d{4})"]
            },
            "ssn": {
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "method": "full",
                "replacement": "***-**-****",
                "groups": []
            },
            "credit_card": {
                "pattern": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                "method": "partial",
                "replacement": r"****-****-****-\1",
                "groups": [r"(\d{4})"]
            },
            "ip_address": {
                "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
                "method": "partial",
                "replacement": r"\1.\2.***.***",
                "groups": [r"(\d{1,3})", r"(\d{1,3})"]
            },
            "name": {
                "pattern": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                "method": "partial",
                "replacement": r"\1*** \2***",
                "groups": [r"([A-Z][a-z]+)", r"([A-Z][a-z]+)"]
            }
        }
        
        self.context_rules = {
            "logs": ["email", "phone", "ssn", "credit_card", "ip_address", "name"],
            "analytics": ["email", "phone", "ssn", "credit_card", "ip_address", "name"],
            "debug": ["ssn", "credit_card"],
            "public": ["email", "phone", "ssn", "credit_card", "ip_address", "name"]
        }
    
    def redact_data(self, data: str, context: str = "logs") -> str:
        """Redact sensitive data from string"""
        if context not in self.context_rules:
            context = "logs"
        
        redacted_data = data
        redaction_applied = []
        
        for data_type in self.context_rules[context]:
            if data_type in self.redaction_rules:
                rule = self.redaction_rules[data_type]
                
                # Apply redaction
                if rule["method"] == "full":
                    redacted_data = re.sub(rule["pattern"], rule["replacement"], redacted_data)
                elif rule["method"] == "partial":
                    redacted_data = re.sub(rule["pattern"], rule["replacement"], redacted_data)
                
                # Check if redaction was applied
                if re.search(rule["pattern"], data) and not re.search(rule["pattern"], redacted_data):
                    redaction_applied.append(data_type)
        
        return redacted_data, redaction_applied
    
    def redact_dict(self, data: dict, context: str = "logs") -> dict:
        """Redact sensitive data from dictionary"""
        redacted_data = {}
        redaction_summary = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                redacted_value, redaction_applied = self.redact_data(value, context)
                redacted_data[key] = redacted_value
                
                if redaction_applied:
                    redaction_summary[key] = redaction_applied
            elif isinstance(value, dict):
                redacted_value, child_redaction = self.redact_dict(value, context)
                redacted_data[key] = redacted_value
                
                if child_redaction:
                    redaction_summary[key] = child_redaction
            else:
                redacted_data[key] = value
        
        return redacted_data, redaction_summary
    
    def redact_log_entry(self, log_entry: dict) -> dict:
        """Redact sensitive data from log entry"""
        # Redact message
        if "message" in log_entry:
            redacted_message, _ = self.redact_data(log_entry["message"], "logs")
            log_entry["message"] = redacted_message
        
        # Redact extra fields
        if "extra" in log_entry:
            redacted_extra, _ = self.redact_dict(log_entry["extra"], "logs")
            log_entry["extra"] = redacted_extra
        
        # Redact context
        if "context" in log_entry:
            redacted_context, _ = self.redact_dict(log_entry["context"], "logs")
            log_entry["context"] = redacted_context
        
        return log_entry
    
    def redact_analytics_data(self, analytics_data: dict) -> dict:
        """Redact sensitive data from analytics data"""
        redacted_data, redaction_summary = self.redact_dict(analytics_data, "analytics")
        
        # Add redaction metadata
        redacted_data["_redaction_applied"] = redaction_summary
        redacted_data["_redaction_timestamp"] = datetime.now().isoformat()
        
        return redacted_data
```

---

## 📋 **Audit Logging**

### **Audit Events**
| Event Type | Description | Data Captured | Retention |
|------------|-------------|---------------|-----------|
| **Data Access** | Data accessed | User, data type, timestamp | 7 years |
| **Data Modification** | Data changed | User, changes, timestamp | 7 years |
| **Data Deletion** | Data deleted | User, data type, timestamp | 7 years |
| **Data Export** | Data exported | User, data type, timestamp | 7 years |
| **Data Import** | Data imported | User, data type, timestamp | 7 years |
| **Access Denied** | Access denied | User, resource, reason | 1 year |
| **Policy Violation** | Policy violated | User, policy, details | 7 years |

### **Audit Logging Implementation**
```python
# Example audit logging implementation
class AuditLogger:
    def __init__(self):
        self.audit_events = {
            "data_access": "Data accessed",
            "data_modification": "Data changed",
            "data_deletion": "Data deleted",
            "data_export": "Data exported",
            "data_import": "Data imported",
            "access_denied": "Access denied",
            "policy_violation": "Policy violated"
        }
        
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.db_client = None  # Database client
    
    def log_audit_event(self, event_type: str, user_id: str, resource: str, 
                       details: dict = None, success: bool = True) -> str:
        """Log audit event"""
        if event_type not in self.audit_events:
            raise ValueError(f"Unknown audit event type: {event_type}")
        
        audit_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        audit_entry = {
            "audit_id": audit_id,
            "event_type": event_type,
            "event_description": self.audit_events[event_type],
            "user_id": user_id,
            "resource": resource,
            "details": details or {},
            "success": success,
            "timestamp": timestamp.isoformat(),
            "ip_address": self._get_client_ip(),
            "user_agent": self._get_user_agent()
        }
        
        # Store in Redis for immediate access
        audit_key = f"audit:{audit_id}"
        self.redis_client.setex(audit_key, 86400, json.dumps(audit_entry))  # 24 hours
        
        # Store in database for long-term retention
        self._store_audit_entry(audit_entry)
        
        return audit_id
    
    def log_data_access(self, user_id: str, data_type: str, data_id: str, 
                       access_method: str = "read") -> str:
        """Log data access event"""
        details = {
            "data_type": data_type,
            "data_id": data_id,
            "access_method": access_method
        }
        
        return self.log_audit_event("data_access", user_id, f"{data_type}:{data_id}", details)
    
    def log_data_modification(self, user_id: str, data_type: str, data_id: str, 
                             changes: dict) -> str:
        """Log data modification event"""
        details = {
            "data_type": data_type,
            "data_id": data_id,
            "changes": changes
        }
        
        return self.log_audit_event("data_modification", user_id, f"{data_type}:{data_id}", details)
    
    def log_data_deletion(self, user_id: str, data_type: str, data_id: str, 
                         deletion_reason: str = None) -> str:
        """Log data deletion event"""
        details = {
            "data_type": data_type,
            "data_id": data_id,
            "deletion_reason": deletion_reason
        }
        
        return self.log_audit_event("data_deletion", user_id, f"{data_type}:{data_id}", details)
    
    def log_access_denied(self, user_id: str, resource: str, reason: str) -> str:
        """Log access denied event"""
        details = {
            "reason": reason
        }
        
        return self.log_audit_event("access_denied", user_id, resource, details, success=False)
    
    def log_policy_violation(self, user_id: str, policy: str, violation_details: dict) -> str:
        """Log policy violation event"""
        details = {
            "policy": policy,
            "violation_details": violation_details
        }
        
        return self.log_audit_event("policy_violation", user_id, policy, details, success=False)
    
    def get_audit_trail(self, user_id: str = None, resource: str = None, 
                       event_type: str = None, start_date: datetime = None, 
                       end_date: datetime = None) -> list:
        """Get audit trail"""
        # Implementation for retrieving audit trail
        pass
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Implementation for getting client IP
        return "127.0.0.1"
    
    def _get_user_agent(self) -> str:
        """Get user agent"""
        # Implementation for getting user agent
        return "Unknown"
    
    def _store_audit_entry(self, audit_entry: dict):
        """Store audit entry in database"""
        # Implementation for storing audit entry
        pass
```

---

## 📊 **Data Handling Monitoring**

### **Data Handling Metrics**
| Metric | Description | Threshold | Action |
|--------|-------------|-----------|--------|
| **PII Detection Rate** | PII detected in data | > 5% | Review data collection |
| **Redaction Coverage** | Data redaction coverage | > 95% | Ensure compliance |
| **Retention Compliance** | Data retention compliance | 100% | Monitor violations |
| **Audit Log Coverage** | Audit log coverage | 100% | Ensure logging |

### **Data Handling Monitoring Implementation**
```python
# Example data handling monitoring implementation
class DataHandlingMonitor:
    def __init__(self):
        self.metrics = {
            "pii_detection_rate": 0.0,
            "redaction_coverage": 0.0,
            "retention_compliance": 0.0,
            "audit_log_coverage": 0.0
        }
        
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def monitor_data_handling(self, data: dict, context: str = "logs") -> dict:
        """Monitor data handling practices"""
        monitoring_result = {
            "pii_detected": False,
            "redaction_applied": False,
            "classification": "public",
            "recommendations": []
        }
        
        # Check for PII
        classifier = DataClassifier()
        classification_result = classifier.classify_data(data)
        
        if classification_result["pii_detected"]:
            monitoring_result["pii_detected"] = True
            monitoring_result["recommendations"].append("Apply PII redaction")
        
        # Check redaction
        redactor = DataRedactor()
        redacted_data, redaction_applied = redactor.redact_dict(data, context)
        
        if redaction_applied:
            monitoring_result["redaction_applied"] = True
        
        # Update classification
        monitoring_result["classification"] = classification_result["overall_classification"]
        
        # Generate recommendations
        monitoring_result["recommendations"].extend(classification_result["recommendations"])
        
        return monitoring_result
    
    def update_metrics(self, monitoring_result: dict):
        """Update data handling metrics"""
        # Update PII detection rate
        if monitoring_result["pii_detected"]:
            self.metrics["pii_detection_rate"] += 1
        
        # Update redaction coverage
        if monitoring_result["redaction_applied"]:
            self.metrics["redaction_coverage"] += 1
        
        # Store metrics
        self._store_metrics(self.metrics)
    
    def _store_metrics(self, metrics: dict):
        """Store metrics in Redis"""
        metrics_key = f"data_handling_metrics:{int(time.time())}"
        self.redis_client.setex(metrics_key, 86400, json.dumps(metrics))
    
    def get_metrics_summary(self, hours: int = 24) -> dict:
        """Get metrics summary"""
        # Implementation for retrieving metrics summary
        pass
```

---

## 📚 **References**

- Security & Privacy: `10_security_and_privacy.md`
- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This data handling specification provides comprehensive data protection, privacy, and compliance for SarvanOM v2 system.*
