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


class UserLogin(BaseModel):
    username: str
    password: str


class SSOLoginResponse(BaseModel):
    redirect_url: str
    state: str


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
    
    # Return user information
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("roles", [])
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