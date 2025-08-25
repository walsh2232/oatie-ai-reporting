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