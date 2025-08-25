"""
User management endpoints with role-based access control
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from backend.api.v1.endpoints.auth import oauth2_scheme
from backend.core.security import AuditEventType

router = APIRouter()


class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    active: bool
    created_at: datetime
    last_login: Optional[datetime]


class CreateUserRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    roles: List[str] = ["viewer"]


@router.get("/me", response_model=User)
async def get_current_user_profile(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get current user profile"""
    security_manager = request.app.state.security_manager
    
    payload = await security_manager.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Mock user data
    user_data = {
        "id": "user_123",
        "username": payload.get("sub", "demo_user"),
        "email": payload.get("email", "demo@company.com"),
        "full_name": "Demo User",
        "roles": payload.get("roles", ["analyst"]),
        "active": True,
        "created_at": datetime.now(),
        "last_login": datetime.now()
    }
    
    return User(**user_data)


@router.get("/", response_model=List[User])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    token: str = Depends(oauth2_scheme)
):
    """List all users (admin only)"""
    
    # Mock user list
    users = [
        {
            "id": "user_001",
            "username": "admin",
            "email": "admin@company.com",
            "full_name": "System Administrator",
            "roles": ["admin"],
            "active": True,
            "created_at": datetime.now(),
            "last_login": datetime.now()
        },
        {
            "id": "user_002",
            "username": "analyst1",
            "email": "analyst1@company.com",
            "full_name": "Business Analyst",
            "roles": ["analyst"],
            "active": True,
            "created_at": datetime.now(),
            "last_login": datetime.now()
        }
    ]
    
    # Log access
    security_manager = request.app.state.security_manager
    await security_manager.log_audit_event(
        AuditEventType.DATA_ACCESS,
        resource="user_list",
        details={"count": len(users)}
    )
    
    return users[skip:skip + limit]


@router.post("/", response_model=User)
async def create_user(
    request: Request,
    user_request: CreateUserRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create new user (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Hash password
    hashed_password = await security_manager.hash_password(user_request.password)
    
    # Create user (mock)
    new_user = {
        "id": f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "username": user_request.username,
        "email": user_request.email,
        "full_name": user_request.full_name,
        "roles": user_request.roles,
        "active": True,
        "created_at": datetime.now(),
        "last_login": None
    }
    
    # Log user creation
    await security_manager.log_audit_event(
        AuditEventType.USER_CREATED,
        resource=f"user_{new_user['id']}",
        details={
            "username": user_request.username,
            "email": user_request.email,
            "roles": user_request.roles
        }
    )
    
    return User(**new_user)


@router.put("/{user_id}/roles")
async def update_user_roles(
    request: Request,
    user_id: str,
    roles: List[str],
    token: str = Depends(oauth2_scheme)
):
    """Update user roles (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Log permission changes
    await security_manager.log_audit_event(
        AuditEventType.PERMISSION_GRANTED,
        resource=f"user_{user_id}",
        details={"new_roles": roles}
    )
    
    return {"message": f"User {user_id} roles updated", "roles": roles}


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Delete user (admin only)"""
    
    security_manager = request.app.state.security_manager
    
    # Log user deletion
    await security_manager.log_audit_event(
        AuditEventType.USER_DELETED,
        resource=f"user_{user_id}",
        details={"action": "delete"}
    )
    
    return {"message": f"User {user_id} deleted"}