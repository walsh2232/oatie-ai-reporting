"""
Enterprise security framework with SSO, audit logging, and encryption
Implements comprehensive security controls for enterprise compliance
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import json
import base64

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import structlog

logger = structlog.get_logger(__name__)


class AuditEventType(str, Enum):
    """Audit event types for compliance tracking"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    DATA_ACCESS = "DATA_ACCESS"
    DATA_EXPORT = "DATA_EXPORT"
    REPORT_GENERATED = "REPORT_GENERATED"
    QUERY_EXECUTED = "QUERY_EXECUTED"
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SYSTEM_ACCESS = "SYSTEM_ACCESS"


class SecurityManager:
    """Comprehensive security manager for enterprise authentication and authorization"""
    
    def __init__(self, settings):
        self.settings = settings
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Initialize encryption
        key = settings.encryption_key.encode()[:32].ljust(32, b'\0')
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(key))
        
        # Audit log storage (in production, use dedicated audit database)
        self.audit_logs: List[Dict] = []
    
    async def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.settings.secret_key, 
            algorithm=self.settings.algorithm
        )
        
        await self.log_audit_event(
            AuditEventType.SYSTEM_ACCESS,
            user_id=data.get("sub"),
            details={"token_created": True, "expires": expire.isoformat()}
        )
        
        return encoded_jwt
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )
            
            # Verify token type
            if payload.get("type") not in ["access", "refresh"]:
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning("Token verification failed", error=str(e))
            await self.log_audit_event(
                AuditEventType.SECURITY_VIOLATION,
                details={"invalid_token": True, "error": str(e)}
            )
            return None
    
    async def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet encryption"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error("Data encryption failed", error=str(e))
            raise
    
    async def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error("Data decryption failed", error=str(e))
            raise
    
    async def log_audit_event(self, event_type: AuditEventType, user_id: Optional[str] = None,
                            ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                            resource: Optional[str] = None, details: Optional[Dict] = None):
        """Log audit event for compliance tracking"""
        audit_event = {
            "event_id": secrets.token_hex(16),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "resource": resource,
            "details": details or {},
            "severity": self._get_event_severity(event_type)
        }
        
        # In production, store in dedicated audit database
        self.audit_logs.append(audit_event)
        
        # Log to structured logger
        logger.info(
            "Audit event logged",
            event_type=event_type.value,
            user_id=user_id,
            severity=audit_event["severity"]
        )
    
    def _get_event_severity(self, event_type: AuditEventType) -> str:
        """Determine event severity level"""
        high_severity_events = {
            AuditEventType.LOGIN_FAILED,
            AuditEventType.SECURITY_VIOLATION,
            AuditEventType.PERMISSION_GRANTED,
            AuditEventType.USER_DELETED
        }
        
        medium_severity_events = {
            AuditEventType.DATA_EXPORT,
            AuditEventType.USER_CREATED,
            AuditEventType.USER_UPDATED,
            AuditEventType.PERMISSION_REVOKED
        }
        
        if event_type in high_severity_events:
            return "HIGH"
        elif event_type in medium_severity_events:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def check_rate_limit(self, user_id: str, action: str, limit: int = 100, 
                             window_minutes: int = 60) -> bool:
        """Check if user has exceeded rate limit for specific action"""
        # In production, use Redis for distributed rate limiting
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=window_minutes)
        
        # Count recent actions for this user
        recent_actions = [
            log for log in self.audit_logs
            if (log.get("user_id") == user_id and 
                log.get("details", {}).get("action") == action and
                datetime.fromisoformat(log["timestamp"]) > window_start)
        ]
        
        if len(recent_actions) >= limit:
            await self.log_audit_event(
                AuditEventType.SECURITY_VIOLATION,
                user_id=user_id,
                details={"rate_limit_exceeded": True, "action": action, "limit": limit}
            )
            return False
        
        return True
    
    async def validate_sso_token(self, sso_provider: str, token: str) -> Optional[Dict[str, Any]]:
        """Validate SSO token from external providers (SAML, OAuth)"""
        # Mock SSO validation - replace with actual provider integration
        try:
            # Decode and validate SSO token based on provider
            if sso_provider == "okta":
                # Okta token validation logic
                user_info = await self._validate_okta_token(token)
            elif sso_provider == "azure_ad":
                # Azure AD token validation logic
                user_info = await self._validate_azure_token(token)
            else:
                logger.warning("Unsupported SSO provider", provider=sso_provider)
                return None
            
            await self.log_audit_event(
                AuditEventType.LOGIN,
                user_id=user_info.get("user_id"),
                details={"sso_provider": sso_provider, "sso_login": True}
            )
            
            return user_info
            
        except Exception as e:
            logger.error("SSO token validation failed", provider=sso_provider, error=str(e))
            await self.log_audit_event(
                AuditEventType.LOGIN_FAILED,
                details={"sso_provider": sso_provider, "error": str(e)}
            )
            return None
    
    async def _validate_okta_token(self, token: str) -> Dict[str, Any]:
        """Validate Okta SSO token"""
        # Mock implementation - replace with actual Okta SDK
        return {
            "user_id": "okta_user_123",
            "email": "user@company.com",
            "name": "John Doe",
            "roles": ["analyst"],
            "sso_provider": "okta"
        }
    
    async def _validate_azure_token(self, token: str) -> Dict[str, Any]:
        """Validate Azure AD SSO token"""
        # Mock implementation - replace with actual Azure AD validation
        return {
            "user_id": "azure_user_456",
            "email": "user@company.com",
            "name": "Jane Smith",
            "roles": ["admin"],
            "sso_provider": "azure_ad"
        }
    
    async def get_audit_logs(self, user_id: Optional[str] = None, 
                           event_type: Optional[AuditEventType] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           limit: int = 100) -> List[Dict]:
        """Retrieve audit logs with filtering options"""
        filtered_logs = self.audit_logs.copy()
        
        # Apply filters
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log.get("event_type") == event_type.value]
        
        if start_date:
            filtered_logs = [
                log for log in filtered_logs 
                if datetime.fromisoformat(log["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_logs = [
                log for log in filtered_logs 
                if datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
        
        # Sort by timestamp (newest first) and limit
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered_logs[:limit]
    
    async def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        last_7d = current_time - timedelta(days=7)
        
        # Count events by type in last 24h
        recent_events = [
            log for log in self.audit_logs
            if datetime.fromisoformat(log["timestamp"]) > last_24h
        ]
        
        event_counts = {}
        for event_type in AuditEventType:
            event_counts[event_type.value] = len([
                log for log in recent_events if log["event_type"] == event_type.value
            ])
        
        # Security violations in last 7 days
        violations = [
            log for log in self.audit_logs
            if (log["event_type"] == AuditEventType.SECURITY_VIOLATION.value and
                datetime.fromisoformat(log["timestamp"]) > last_7d)
        ]
        
        # Failed login attempts
        failed_logins = [
            log for log in recent_events
            if log["event_type"] == AuditEventType.LOGIN_FAILED.value
        ]
        
        return {
            "report_generated_at": current_time.isoformat(),
            "time_period": {
                "last_24h_events": len(recent_events),
                "last_7d_violations": len(violations)
            },
            "event_counts_24h": event_counts,
            "security_summary": {
                "total_violations_7d": len(violations),
                "failed_logins_24h": len(failed_logins),
                "unique_users_24h": len(set(log.get("user_id") for log in recent_events if log.get("user_id"))),
                "high_severity_events_24h": len([
                    log for log in recent_events if log.get("severity") == "HIGH"
                ])
            },
            "recommendations": self._generate_security_recommendations(violations, failed_logins)
        }
    
    def _generate_security_recommendations(self, violations: List[Dict], failed_logins: List[Dict]) -> List[str]:
        """Generate security recommendations based on recent events"""
        recommendations = []
        
        if len(failed_logins) > 10:
            recommendations.append("High number of failed login attempts detected. Consider implementing account lockout policies.")
        
        if len(violations) > 5:
            recommendations.append("Multiple security violations detected. Review access controls and user permissions.")
        
        # Check for suspicious patterns
        user_violations = {}
        for violation in violations:
            user_id = violation.get("user_id")
            if user_id:
                user_violations[user_id] = user_violations.get(user_id, 0) + 1
        
        for user_id, count in user_violations.items():
            if count > 3:
                recommendations.append(f"User {user_id} has {count} security violations. Consider reviewing their access.")
        
        if not recommendations:
            recommendations.append("Security posture appears normal. Continue monitoring.")
        
        return recommendations