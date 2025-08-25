"""
Oracle BI Publisher authentication and identity management
Enterprise security integration with Oracle Identity Cloud Service (IDCS)
"""

import base64
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import structlog
from cryptography.fernet import Fernet

from .models import OracleUser, OracleSessionInfo, OracleAPIResponse

logger = structlog.get_logger(__name__)


class OracleAuthManager:
    """
    Enterprise Oracle BI Publisher authentication manager
    
    Features:
    - Oracle Identity Cloud Service (IDCS) integration
    - SAML and OAuth2/OIDC support
    - Session management and token validation
    - Role-based access control (RBAC)
    - Single Sign-On (SSO) integration
    """
    
    def __init__(
        self,
        server_url: str,
        encryption_key: str,
        session_timeout: int = 3600,  # 1 hour
        sso_enabled: bool = False,
        idcs_tenant: Optional[str] = None,
        saml_metadata_url: Optional[str] = None
    ):
        self.server_url = server_url.rstrip('/')
        self.encryption_key = encryption_key
        self.session_timeout = session_timeout
        self.sso_enabled = sso_enabled
        self.idcs_tenant = idcs_tenant
        self.saml_metadata_url = saml_metadata_url
        
        # Initialize encryption
        self.cipher = Fernet(base64.urlsafe_b64encode(encryption_key.encode()[:32].ljust(32, b'0')))
        
        # Session storage (in production, use Redis or database)
        self.active_sessions: Dict[str, OracleSessionInfo] = {}
        self.user_cache: Dict[str, OracleUser] = {}
        
        # Authentication statistics
        self.auth_stats = {
            "successful_logins": 0,
            "failed_logins": 0,
            "sso_logins": 0,
            "active_sessions": 0,
            "expired_sessions": 0
        }
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OracleAPIResponse:
        """
        Authenticate user with Oracle BI Publisher
        
        Args:
            username: Oracle BI Publisher username
            password: User password
            ip_address: Client IP address for audit logging
            user_agent: Client user agent for security tracking
            
        Returns:
            OracleAPIResponse with session information or error
        """
        try:
            logger.info("Authenticating Oracle user", username=username, ip_address=ip_address)
            
            # Validate credentials against Oracle BI Publisher
            auth_result = await self._validate_oracle_credentials(username, password)
            
            if not auth_result["success"]:
                self.auth_stats["failed_logins"] += 1
                logger.warning(
                    "Oracle authentication failed",
                    username=username,
                    reason=auth_result.get("error", "Invalid credentials")
                )
                return OracleAPIResponse(
                    success=False,
                    error="Authentication failed",
                    error_code="AUTH_FAILED"
                )
            
            # Create user session
            user = await self._get_or_create_user(username, auth_result["user_data"])
            session = await self._create_session(user, ip_address, user_agent)
            
            self.auth_stats["successful_logins"] += 1
            self.auth_stats["active_sessions"] = len(self.active_sessions)
            
            logger.info(
                "Oracle authentication successful",
                username=username,
                session_id=session.session_id
            )
            
            return OracleAPIResponse(
                success=True,
                data={
                    "session_id": session.session_id,
                    "user": user.dict(),
                    "expires_at": session.expires_at.isoformat(),
                    "server_url": self.server_url
                }
            )
            
        except Exception as e:
            self.auth_stats["failed_logins"] += 1
            logger.error("Oracle authentication error", username=username, error=str(e))
            
            return OracleAPIResponse(
                success=False,
                error="Authentication system error",
                error_code="AUTH_ERROR"
            )
    
    async def authenticate_sso(
        self,
        sso_token: str,
        provider: str = "SAML",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OracleAPIResponse:
        """
        Authenticate user via Single Sign-On (SSO)
        
        Args:
            sso_token: SSO token from identity provider
            provider: SSO provider type (SAML, OAuth2, OIDC)
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            OracleAPIResponse with session information or error
        """
        if not self.sso_enabled:
            return OracleAPIResponse(
                success=False,
                error="SSO authentication not enabled",
                error_code="SSO_DISABLED"
            )
        
        try:
            logger.info("Authenticating Oracle SSO user", provider=provider, ip_address=ip_address)
            
            # Validate SSO token
            sso_result = await self._validate_sso_token(sso_token, provider)
            
            if not sso_result["success"]:
                self.auth_stats["failed_logins"] += 1
                logger.warning(
                    "Oracle SSO authentication failed",
                    provider=provider,
                    reason=sso_result.get("error", "Invalid SSO token")
                )
                return OracleAPIResponse(
                    success=False,
                    error="SSO authentication failed",
                    error_code="SSO_AUTH_FAILED"
                )
            
            # Create or update user from SSO data
            username = sso_result["user_data"]["username"]
            user = await self._get_or_create_user(username, sso_result["user_data"])
            session = await self._create_session(user, ip_address, user_agent)
            
            self.auth_stats["successful_logins"] += 1
            self.auth_stats["sso_logins"] += 1
            self.auth_stats["active_sessions"] = len(self.active_sessions)
            
            logger.info(
                "Oracle SSO authentication successful",
                username=username,
                provider=provider,
                session_id=session.session_id
            )
            
            return OracleAPIResponse(
                success=True,
                data={
                    "session_id": session.session_id,
                    "user": user.dict(),
                    "expires_at": session.expires_at.isoformat(),
                    "server_url": self.server_url,
                    "sso_provider": provider
                }
            )
            
        except Exception as e:
            self.auth_stats["failed_logins"] += 1
            logger.error("Oracle SSO authentication error", provider=provider, error=str(e))
            
            return OracleAPIResponse(
                success=False,
                error="SSO authentication system error",
                error_code="SSO_ERROR"
            )
    
    async def validate_session(self, session_id: str) -> Optional[OracleSessionInfo]:
        """
        Validate an active Oracle BI Publisher session
        
        Args:
            session_id: Session identifier
            
        Returns:
            OracleSessionInfo if valid, None if invalid/expired
        """
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Check if session has expired
        if session.is_expired:
            await self._expire_session(session_id)
            return None
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        
        logger.debug("Oracle session validated", session_id=session_id, username=session.user.username)
        return session
    
    async def refresh_session(self, session_id: str) -> OracleAPIResponse:
        """
        Refresh an Oracle BI Publisher session
        
        Args:
            session_id: Session identifier to refresh
            
        Returns:
            OracleAPIResponse with updated session information
        """
        session = await self.validate_session(session_id)
        
        if not session:
            return OracleAPIResponse(
                success=False,
                error="Invalid or expired session",
                error_code="SESSION_INVALID"
            )
        
        # Extend session expiration
        session.expires_at = datetime.utcnow() + timedelta(seconds=self.session_timeout)
        session.last_activity = datetime.utcnow()
        
        logger.info(
            "Oracle session refreshed",
            session_id=session_id,
            username=session.user.username,
            new_expiry=session.expires_at.isoformat()
        )
        
        return OracleAPIResponse(
            success=True,
            data={
                "session_id": session.session_id,
                "expires_at": session.expires_at.isoformat(),
                "user": session.user.dict()
            }
        )
    
    async def logout(self, session_id: str) -> OracleAPIResponse:
        """
        Logout user and invalidate Oracle BI Publisher session
        
        Args:
            session_id: Session identifier to logout
            
        Returns:
            OracleAPIResponse confirming logout
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            await self._expire_session(session_id)
            
            logger.info(
                "Oracle user logged out",
                session_id=session_id,
                username=session.user.username
            )
        
        return OracleAPIResponse(
            success=True,
            data={"message": "Logout successful"}
        )
    
    async def get_user_permissions(self, username: str) -> List[str]:
        """
        Get user permissions from Oracle BI Publisher RBAC
        
        Args:
            username: Oracle BI Publisher username
            
        Returns:
            List of permission strings
        """
        try:
            # In a real implementation, this would query Oracle BI Publisher for user roles/permissions
            user = self.user_cache.get(username)
            if not user:
                return []
            
            # Map Oracle roles to permissions
            permissions = []
            for role in user.roles:
                permissions.extend(self._get_role_permissions(role))
            
            return list(set(permissions))  # Remove duplicates
            
        except Exception as e:
            logger.error("Failed to get user permissions", username=username, error=str(e))
            return []
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Map Oracle BI Publisher roles to specific permissions"""
        role_permissions = {
            "BI_ADMINISTRATOR": [
                "oracle.admin",
                "oracle.reports.manage",
                "oracle.datasources.manage",
                "oracle.users.manage",
                "oracle.catalogs.manage"
            ],
            "BI_AUTHOR": [
                "oracle.reports.create",
                "oracle.reports.edit",
                "oracle.reports.delete",
                "oracle.datasources.view"
            ],
            "BI_CONSUMER": [
                "oracle.reports.view",
                "oracle.reports.execute",
                "oracle.reports.schedule"
            ],
            "BI_DEVELOPER": [
                "oracle.reports.create",
                "oracle.reports.edit",
                "oracle.datasources.create",
                "oracle.datasources.edit"
            ]
        }
        
        return role_permissions.get(role, [])
    
    async def _validate_oracle_credentials(self, username: str, password: str) -> Dict[str, Any]:
        """Validate credentials against Oracle BI Publisher"""
        try:
            # In a real implementation, this would make an API call to Oracle BI Publisher
            # to validate the username/password combination
            
            # For demo purposes, we'll simulate credential validation
            if username and password and len(password) >= 6:
                # Simulate successful authentication
                return {
                    "success": True,
                    "user_data": {
                        "username": username,
                        "display_name": f"{username.title()} User",
                        "email": f"{username}@company.com",
                        "roles": ["BI_CONSUMER", "BI_AUTHOR"] if username != "admin" else ["BI_ADMINISTRATOR"],
                        "active": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
                
        except Exception as e:
            logger.error("Oracle credential validation error", error=str(e))
            return {
                "success": False,
                "error": "Authentication system error"
            }
    
    async def _validate_sso_token(self, token: str, provider: str) -> Dict[str, Any]:
        """Validate SSO token with identity provider"""
        try:
            # In a real implementation, this would validate the SSO token
            # against the appropriate identity provider (SAML, OAuth2, OIDC)
            
            if provider == "SAML" and self.saml_metadata_url:
                # Validate SAML assertion
                pass
            elif provider == "OIDC" and self.idcs_tenant:
                # Validate OIDC token with Oracle IDCS
                pass
            
            # For demo purposes, simulate successful SSO validation
            decoded_data = base64.b64decode(token + "==").decode('utf-8', errors='ignore')
            if "username" in decoded_data:
                return {
                    "success": True,
                    "user_data": {
                        "username": "sso_user",
                        "display_name": "SSO User",
                        "email": "sso_user@company.com",
                        "roles": ["BI_CONSUMER"],
                        "active": True
                    }
                }
            
            return {
                "success": False,
                "error": "Invalid SSO token"
            }
            
        except Exception as e:
            logger.error("SSO token validation error", provider=provider, error=str(e))
            return {
                "success": False,
                "error": "SSO validation system error"
            }
    
    async def _get_or_create_user(self, username: str, user_data: Dict[str, Any]) -> OracleUser:
        """Get existing user or create new user from authentication data"""
        if username in self.user_cache:
            user = self.user_cache[username]
            # Update user data if needed
            user.display_name = user_data.get("display_name", user.display_name)
            user.email = user_data.get("email", user.email)
            user.roles = user_data.get("roles", user.roles)
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = OracleUser(
                username=username,
                display_name=user_data.get("display_name", username),
                email=user_data.get("email"),
                roles=user_data.get("roles", []),
                active=user_data.get("active", True),
                last_login=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            self.user_cache[username] = user
        
        return user
    
    async def _create_session(
        self,
        user: OracleUser,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OracleSessionInfo:
        """Create a new Oracle BI Publisher session"""
        session_id = self._generate_session_id()
        expires_at = datetime.utcnow() + timedelta(seconds=self.session_timeout)
        
        session = OracleSessionInfo(
            session_id=session_id,
            user=user,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        return session
    
    async def _expire_session(self, session_id: str):
        """Expire and remove a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.auth_stats["expired_sessions"] += 1
            self.auth_stats["active_sessions"] = len(self.active_sessions)
    
    def _generate_session_id(self) -> str:
        """Generate a secure session identifier"""
        timestamp = str(int(time.time()))
        random_bytes = secrets.token_bytes(16)
        session_data = f"{timestamp}:{random_bytes.hex()}"
        
        # Create session ID hash
        session_hash = hashlib.sha256(session_data.encode()).hexdigest()
        return f"oracle_session_{session_hash[:32]}"
    
    async def cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions"""
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_expired:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self._expire_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired Oracle sessions")
    
    def get_auth_statistics(self) -> Dict[str, Any]:
        """Get authentication and session statistics"""
        return {
            **self.auth_stats,
            "active_sessions": len(self.active_sessions),
            "cached_users": len(self.user_cache),
            "sso_enabled": self.sso_enabled,
            "session_timeout": self.session_timeout
        }