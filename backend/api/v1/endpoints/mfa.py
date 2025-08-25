"""
Multi-Factor Authentication API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.core.security import SecurityManager, AuditEventType
from backend.core.mfa import MFAMethod, MFAStatus
from backend.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()


class MFASetupRequest(BaseModel):
    method: MFAMethod
    contact_info: Optional[str] = None


class MFASetupResponse(BaseModel):
    secret: Optional[str] = None
    qr_code: Optional[str] = None
    backup_codes: Optional[list] = None
    message: str


class MFAVerifySetupRequest(BaseModel):
    token: str


class MFAChallengeRequest(BaseModel):
    method: MFAMethod
    contact_info: Optional[str] = None


class MFAChallengeResponse(BaseModel):
    challenge_id: str
    method: MFAMethod
    message: str
    expires_in: int


class MFAVerifyRequest(BaseModel):
    challenge_id: str
    token: str


class MFAVerifyResponse(BaseModel):
    success: bool
    message: str


class MFAStatusResponse(BaseModel):
    enabled: bool
    methods: list
    backup_codes_remaining: Optional[int] = None


@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    mfa_request: MFASetupRequest,
    token: str = Depends(oauth2_scheme)
):
    """Setup Multi-Factor Authentication for current user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify current user token
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    user_email = payload.get("email", "user@example.com")  # In production, get from user profile
    
    try:
        if mfa_request.method == MFAMethod.TOTP:
            setup_result = await security_manager.setup_mfa(
                user_id, mfa_request.method, user_email, mfa_request.contact_info
            )
            
            return MFASetupResponse(
                secret=setup_result.get("secret"),
                qr_code=setup_result.get("qr_code"),
                backup_codes=setup_result.get("backup_codes"),
                message="TOTP setup initiated. Scan QR code with authenticator app and verify."
            )
        else:
            # For SMS/Email, just store the contact info and enable
            return MFASetupResponse(
                message=f"{mfa_request.method.value.upper()} MFA setup completed."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MFA setup failed: {str(e)}"
        )


@router.post("/setup/verify", response_model=MFAVerifyResponse)
async def verify_mfa_setup(
    request: Request,
    verify_request: MFAVerifySetupRequest,
    token: str = Depends(oauth2_scheme)
):
    """Verify MFA setup with token from authenticator app"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify current user token
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    
    try:
        is_verified = await security_manager.verify_mfa_setup(user_id, verify_request.token)
        
        if is_verified:
            return MFAVerifyResponse(
                success=True,
                message="MFA setup completed successfully"
            )
        else:
            return MFAVerifyResponse(
                success=False,
                message="Invalid verification token"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MFA verification failed: {str(e)}"
        )


@router.post("/challenge", response_model=MFAChallengeResponse)
async def initiate_mfa_challenge(
    request: Request,
    challenge_request: MFAChallengeRequest,
    token: str = Depends(oauth2_scheme)
):
    """Initiate MFA challenge for current user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify current user token
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    
    # Check if MFA is enabled for user
    if not await security_manager.is_mfa_enabled(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled for user"
        )
    
    try:
        challenge_result = await security_manager.initiate_mfa_challenge(
            user_id, challenge_request.method, challenge_request.contact_info
        )
        
        return MFAChallengeResponse(**challenge_result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initiate MFA challenge: {str(e)}"
        )


@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa_challenge(
    request: Request,
    verify_request: MFAVerifyRequest
):
    """Verify MFA challenge response (no auth token required for this step)"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    try:
        verify_result = await security_manager.verify_mfa_challenge(
            verify_request.challenge_id, verify_request.token
        )
        
        success = verify_result.get("status") == MFAStatus.VERIFIED
        
        return MFAVerifyResponse(
            success=success,
            message=verify_result.get("message", "MFA verification completed")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MFA verification failed: {str(e)}"
        )


@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get MFA status for current user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify current user token
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    
    try:
        is_enabled = await security_manager.is_mfa_enabled(user_id)
        methods = await security_manager.mfa_manager.get_user_mfa_methods(user_id)
        
        return MFAStatusResponse(
            enabled=is_enabled,
            methods=[method.value for method in methods],
            backup_codes_remaining=None  # Would implement this with backup code tracking
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get MFA status: {str(e)}"
        )


@router.delete("/disable")
async def disable_mfa(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Disable MFA for current user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify current user token
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    
    try:
        result = await security_manager.mfa_manager.disable_mfa(user_id)
        
        if result:
            await security_manager.log_audit_event(
                AuditEventType.USER_UPDATED,
                user_id=user_id,
                details={"mfa_disabled": True}
            )
            
            return {"message": "MFA disabled successfully"}
        else:
            return {"message": "MFA was not enabled"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable MFA: {str(e)}"
        )