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

from .mfa import MFAManager, MFAMethod, MFAStatus
from .rbac import RBACManager, Permission
from .abac import ABACManager, PolicyEffect

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
    # New SQL-related audit events
    SQL_GENERATION = "SQL_GENERATION"
    SQL_OPTIMIZATION = "SQL_OPTIMIZATION"
    SQL_VALIDATION = "SQL_VALIDATION"
    SQL_EXPLAIN = "SQL_EXPLAIN"


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
        
        # Initialize security subsystems
        self.mfa_manager = MFAManager(settings)
        self.rbac_manager = RBACManager()
        self.abac_manager = ABACManager()
        
        # User sessions and security state
        self.active_sessions: Dict[str, Dict] = {}
        self.failed_login_attempts: Dict[str, List[datetime]] = {}
        self.blocked_users: Dict[str, datetime] = {}
    
    # === Multi-Factor Authentication Methods ===
    
    async def setup_mfa(self, user_id: str, method: MFAMethod, user_email: str, 
                       contact_info: Optional[str] = None) -> Dict[str, Any]:
        """Setup MFA for a user"""
        if method == MFAMethod.TOTP:
            result = await self.mfa_manager.setup_totp(user_id, user_email)
        else:
            raise ValueError(f"MFA setup not supported for method: {method}")
        
        await self.log_audit_event(
            AuditEventType.USER_UPDATED,
            user_id=user_id,
            details={"mfa_setup": True, "method": method.value}
        )
        
        return result
    
    async def verify_mfa_setup(self, user_id: str, token: str) -> bool:
        """Verify MFA setup completion"""
        result = await self.mfa_manager.verify_totp_setup(user_id, token)
        
        await self.log_audit_event(
            AuditEventType.USER_UPDATED if result else AuditEventType.SECURITY_VIOLATION,
            user_id=user_id,
            details={"mfa_setup_verification": result}
        )
        
        return result
    
    async def initiate_mfa_challenge(self, user_id: str, method: MFAMethod, 
                                   contact_info: Optional[str] = None) -> Dict[str, Any]:
        """Initiate MFA challenge during login"""
        result = await self.mfa_manager.initiate_mfa_challenge(user_id, method, contact_info)
        
        await self.log_audit_event(
            AuditEventType.LOGIN,
            user_id=user_id,
            details={"mfa_challenge_initiated": True, "method": method.value}
        )
        
        return result
    
    async def verify_mfa_challenge(self, challenge_id: str, response: str) -> Dict[str, Any]:
        """Verify MFA challenge response"""
        result = await self.mfa_manager.verify_mfa_challenge(challenge_id, response)
        
        if result.get("status") == MFAStatus.VERIFIED:
            await self.log_audit_event(
                AuditEventType.LOGIN,
                user_id=result.get("user_id"),
                details={"mfa_verified": True, "method": result.get("method")}
            )
        else:
            await self.log_audit_event(
                AuditEventType.LOGIN_FAILED,
                user_id=result.get("user_id"),
                details={"mfa_failed": True, "reason": result.get("message")}
            )
        
        return result
    
    async def is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for user"""
        return await self.mfa_manager.is_mfa_enabled(user_id)
    
    # === Role-Based Access Control Methods ===
    
    async def assign_role(self, user_id: str, role_name: str, assigned_by: str) -> bool:
        """Assign role to user"""
        result = await self.rbac_manager.assign_role_to_user(user_id, role_name)
        
        await self.log_audit_event(
            AuditEventType.PERMISSION_GRANTED,
            user_id=user_id,
            details={"role_assigned": role_name, "assigned_by": assigned_by}
        )
        
        return result
    
    async def revoke_role(self, user_id: str, role_name: str, revoked_by: str) -> bool:
        """Revoke role from user"""
        result = await self.rbac_manager.revoke_role_from_user(user_id, role_name)
        
        await self.log_audit_event(
            AuditEventType.PERMISSION_REVOKED,
            user_id=user_id,
            details={"role_revoked": role_name, "revoked_by": revoked_by}
        )
        
        return result
    
    async def check_permission(self, user_id: str, permission: Permission, 
                             resource_type: Optional[str] = None, 
                             resource_id: Optional[str] = None,
                             context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if user has permission with RBAC and ABAC evaluation"""
        
        # First check RBAC permissions
        rbac_result = await self.rbac_manager.has_permission(
            user_id, permission, resource_type, resource_id
        )
        
        if rbac_result:
            return True
        
        # If RBAC denies, check ABAC policies if context is provided
        if context and resource_type and resource_id:
            abac_result = await self.abac_manager.evaluate_access(
                user_id, permission.value, resource_type, resource_id, context
            )
            
            await self.log_audit_event(
                AuditEventType.DATA_ACCESS,
                user_id=user_id,
                resource=f"{resource_type}:{resource_id}",
                details={
                    "permission": permission.value,
                    "rbac_result": rbac_result,
                    "abac_result": abac_result["decision"],
                    "access_granted": abac_result["decision"] == PolicyEffect.ALLOW
                }
            )
            
            return abac_result["decision"] == PolicyEffect.ALLOW
        
        return False
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user permissions from RBAC"""
        permissions = await self.rbac_manager.get_user_permissions(user_id)
        roles = await self.rbac_manager.get_user_roles(user_id)
        
        return {
            "user_id": user_id,
            "roles": list(roles),
            "permissions": [p.value for p in permissions],
            "permission_count": len(permissions)
        }
    
    # === Enhanced Authentication Methods ===
    
    async def authenticate_with_mfa(self, username: str, password: str, 
                                  mfa_token: Optional[str] = None,
                                  challenge_id: Optional[str] = None,
                                  request_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced authentication with MFA support"""
        
        # Check if user is blocked
        if await self._is_user_blocked(username):
            await self.log_audit_event(
                AuditEventType.LOGIN_FAILED,
                details={"username": username, "reason": "user_blocked"}
            )
            return {"success": False, "message": "Account temporarily blocked"}
        
        # Verify password (mock implementation - replace with actual user lookup)
        user_data = await self._get_user_by_username(username)
        if not user_data or not await self.verify_password(password, user_data.get("password_hash", "")):
            await self._record_failed_login(username)
            await self.log_audit_event(
                AuditEventType.LOGIN_FAILED,
                details={"username": username, "reason": "invalid_credentials"}
            )
            return {"success": False, "message": "Invalid credentials"}
        
        user_id = user_data["id"]
        
        # Check if MFA is required
        if await self.is_mfa_enabled(user_id):
            if not mfa_token and not challenge_id:
                # Initiate MFA challenge
                mfa_methods = await self.mfa_manager.get_user_mfa_methods(user_id)
                if mfa_methods:
                    challenge_result = await self.initiate_mfa_challenge(user_id, mfa_methods[0])
                    return {
                        "success": False,
                        "requires_mfa": True,
                        "challenge_id": challenge_result["challenge_id"],
                        "method": challenge_result["method"]
                    }
            else:
                # Verify MFA
                if challenge_id and mfa_token:
                    mfa_result = await self.verify_mfa_challenge(challenge_id, mfa_token)
                    if mfa_result["status"] != MFAStatus.VERIFIED:
                        return {"success": False, "message": "Invalid MFA token"}
                else:
                    return {"success": False, "message": "MFA token required"}
        
        # Clear failed login attempts
        if username in self.failed_login_attempts:
            del self.failed_login_attempts[username]
        
        # Create session and token
        session_data = {
            "user_id": user_id,
            "username": username,
            "roles": list(await self.rbac_manager.get_user_roles(user_id)),
            "login_time": datetime.utcnow().isoformat(),
            "mfa_verified": await self.is_mfa_enabled(user_id),
            "context": request_context or {}
        }
        
        access_token = await self.create_access_token({"sub": user_id, **session_data})
        session_id = secrets.token_hex(32)
        self.active_sessions[session_id] = session_data
        
        await self.log_audit_event(
            AuditEventType.LOGIN,
            user_id=user_id,
            details={
                "username": username,
                "mfa_used": await self.is_mfa_enabled(user_id),
                "session_id": session_id
            }
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "session_id": session_id,
            "user": {
                "id": user_id,
                "username": username,
                "roles": session_data["roles"]
            }
        }
    
    async def _is_user_blocked(self, username: str) -> bool:
        """Check if user is temporarily blocked due to failed login attempts"""
        if username in self.blocked_users:
            block_until = self.blocked_users[username]
            if datetime.utcnow() < block_until:
                return True
            else:
                # Block period expired
                del self.blocked_users[username]
        
        return False
    
    async def _record_failed_login(self, username: str):
        """Record failed login attempt and block user if threshold exceeded"""
        current_time = datetime.utcnow()
        
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        
        # Remove attempts older than 1 hour
        cutoff_time = current_time - timedelta(hours=1)
        self.failed_login_attempts[username] = [
            attempt for attempt in self.failed_login_attempts[username]
            if attempt > cutoff_time
        ]
        
        self.failed_login_attempts[username].append(current_time)
        
        # Block user if too many failed attempts
        if len(self.failed_login_attempts[username]) >= 5:
            self.blocked_users[username] = current_time + timedelta(minutes=30)
            await self.log_audit_event(
                AuditEventType.SECURITY_VIOLATION,
                details={
                    "username": username,
                    "reason": "too_many_failed_attempts",
                    "blocked_until": self.blocked_users[username].isoformat()
                }
            )
    
    async def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Mock user lookup - replace with actual database query"""
        # This is a mock implementation
        mock_users = {
            "admin": {
                "id": "admin_user_123",
                "username": "admin",
                "email": "admin@company.com",
                "password_hash": await self.hash_password("admin123"),
                "roles": ["admin"]
            },
            "analyst": {
                "id": "analyst_user_456",
                "username": "analyst",
                "email": "analyst@company.com",
                "password_hash": await self.hash_password("analyst123"),
                "roles": ["analyst"]
            }
        }
        
        return mock_users.get(username)
    
    # === Session Management ===
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate active session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        login_time = datetime.fromisoformat(session["login_time"])
        
        # Check session timeout (configurable)
        session_timeout = timedelta(hours=8)
        if datetime.utcnow() - login_time > session_timeout:
            await self.terminate_session(session_id)
            return None
        
        return session
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate user session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            
            await self.log_audit_event(
                AuditEventType.LOGOUT,
                user_id=session.get("user_id"),
                details={"session_id": session_id, "terminated": True}
            )
            
            return True
        
        return False
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active sessions, optionally filtered by user"""
        sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if user_id is None or session_data.get("user_id") == user_id:
                sessions.append({
                    "session_id": session_id,
                    "user_id": session_data.get("user_id"),
                    "username": session_data.get("username"),
                    "login_time": session_data.get("login_time"),
                    "mfa_verified": session_data.get("mfa_verified", False)
                })
        
        return sessions
    
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