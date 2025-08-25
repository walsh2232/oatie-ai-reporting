"""
Authentication endpoints with enterprise SSO support
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.core.security import SecurityManager, AuditEventType

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    requires_mfa: Optional[bool] = None
    challenge_id: Optional[str] = None
    mfa_method: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str
    mfa_token: Optional[str] = None
    challenge_id: Optional[str] = None


class SSOLoginResponse(BaseModel):
    redirect_url: str
    state: str


class MFATokenRequest(BaseModel):
    username: str
    password: str
    mfa_token: str
    challenge_id: str


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticate user and return access token"""
    settings = get_settings()
    security_manager: SecurityManager = request.app.state.security_manager
    
    # For demo purposes, accept any credentials
    # In production, validate against user database
    user_data = {
        "sub": form_data.username,
        "email": f"{form_data.username}@company.com",
        "roles": ["analyst"]
    }
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await security_manager.create_access_token(
        data=user_data,
        expires_delta=access_token_expires
    )
    
    # Log successful login
    await security_manager.log_audit_event(
        AuditEventType.LOGIN,
        user_id=form_data.username,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.post("/sso/initiate", response_model=SSOLoginResponse)
async def initiate_sso_login(request: Request):
    """Initiate SSO login flow"""
    settings = get_settings()
    
    if not settings.sso_enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SSO not configured"
        )
    
    # Generate state parameter for security
    import secrets
    state = secrets.token_urlsafe(32)
    
    # In production, redirect to actual SSO provider
    redirect_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={settings.oauth2_client_id}&response_type=code&state={state}"
    
    return {
        "redirect_url": redirect_url,
        "state": state
    }


@router.get("/me")
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get current user information"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return enhanced user information
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("roles", []),
        "mfa_enabled": await security_manager.is_mfa_enabled(payload.get("sub")),
        "login_time": payload.get("login_time"),
        "session_info": {
            "mfa_verified": payload.get("mfa_verified", False),
            "token_type": payload.get("type", "access")
        }
    }


@router.post("/token/mfa", response_model=Token)
async def complete_mfa_login(
    request: Request,
    mfa_request: MFATokenRequest
):
    """Complete login with MFA token"""
    security_manager: SecurityManager = request.app.state.security_manager
    settings = get_settings()
    
    request_context = {
        "ip_address": request.client.host if request.client else "",
        "user_agent": request.headers.get("user-agent", ""),
        "timestamp": "2024-08-25T17:37:00Z"
    }
    
    try:
        # Complete authentication with MFA
        auth_result = await security_manager.authenticate_with_mfa(
            username=mfa_request.username,
            password=mfa_request.password,
            mfa_token=mfa_request.mfa_token,
            challenge_id=mfa_request.challenge_id,
            request_context=request_context
        )
        
        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result.get("message", "MFA authentication failed"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return Token(
            access_token=auth_result["access_token"],
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            requires_mfa=False
        )
    
    except Exception as e:
        await security_manager.log_audit_event(
            AuditEventType.LOGIN_FAILED,
            details={"username": mfa_request.username, "mfa_failed": True, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Logout user and invalidate session"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    
    # Find and terminate session
    active_sessions = await security_manager.get_active_sessions(user_id)
    for session in active_sessions:
        await security_manager.terminate_session(session["session_id"])
    
    await security_manager.log_audit_event(
        AuditEventType.LOGOUT,
        user_id=user_id,
        details={"logout_method": "explicit"}
    )
    
    return {"message": "Logged out successfully"}


@router.get("/sessions")
async def get_active_sessions(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get active sessions for current user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    sessions = await security_manager.get_active_sessions(user_id)
    
    return {
        "active_sessions": sessions,
        "session_count": len(sessions)
    }


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Logout user and invalidate token"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    payload = await security_manager.verify_token(token)
    if payload:
        # Log logout event
        await security_manager.log_audit_event(
            AuditEventType.LOGOUT,
            user_id=payload.get("sub"),
            ip_address=request.client.host
        )
    
    return {"message": "Successfully logged out"}