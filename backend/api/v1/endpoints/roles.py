"""
Role and Permission Management API endpoints
"""

from typing import List, Set, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

from backend.core.security import SecurityManager, AuditEventType
from backend.core.rbac import Permission, Role
from backend.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()


class RoleCreateRequest(BaseModel):
    name: str
    description: str
    permissions: List[str]
    parent_roles: Optional[List[str]] = None


class RoleUpdateRequest(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    name: str
    description: str
    permissions: List[str]
    parent_roles: List[str]
    is_system: bool
    created_at: str
    updated_at: str


class UserRoleAssignment(BaseModel):
    user_id: str
    role_name: str


class ResourcePermissionRequest(BaseModel):
    user_id: str
    resource_type: str
    resource_id: str
    permissions: List[str]
    expires_at: Optional[str] = None


class PermissionCheckRequest(BaseModel):
    user_id: str
    permission: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None


class PermissionCheckResponse(BaseModel):
    allowed: bool
    user_id: str
    permission: str
    resource: Optional[str] = None
    reason: str


# === Role Management Endpoints ===

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """List all available roles"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        hierarchy = await security_manager.rbac_manager.get_role_hierarchy()
        roles = []
        
        for role_name, role_info in hierarchy.items():
            role = security_manager.rbac_manager.roles[role_name]
            roles.append(RoleResponse(
                name=role_name,
                description=role_info["description"],
                permissions=role_info["permissions"],
                parent_roles=role_info["parent_roles"],
                is_system=role_info["is_system"],
                created_at=role.created_at.isoformat(),
                updated_at=role.updated_at.isoformat()
            ))
        
        return roles
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list roles: {str(e)}"
        )


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    request: Request,
    role_request: RoleCreateRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create a new custom role"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        # Convert permission strings to Permission enum
        permissions = set()
        for perm_str in role_request.permissions:
            try:
                permissions.add(Permission(perm_str))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permission: {perm_str}"
                )
        
        parent_roles = set(role_request.parent_roles) if role_request.parent_roles else set()
        
        role = await security_manager.rbac_manager.create_role(
            role_request.name,
            role_request.description,
            permissions,
            parent_roles
        )
        
        await security_manager.log_audit_event(
            AuditEventType.SYSTEM_ACCESS,
            user_id=user_id,
            details={"role_created": role_request.name, "permissions": role_request.permissions}
        )
        
        return RoleResponse(
            name=role.name,
            description=role.description,
            permissions=[p.value for p in role.permissions],
            parent_roles=list(role.parent_roles),
            is_system=role.is_system,
            created_at=role.created_at.isoformat(),
            updated_at=role.updated_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.put("/roles/{role_name}", response_model=RoleResponse)
async def update_role(
    request: Request,
    role_name: str,
    role_update: RoleUpdateRequest,
    token: str = Depends(oauth2_scheme)
):
    """Update an existing role"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        permissions = None
        if role_update.permissions is not None:
            permissions = set()
            for perm_str in role_update.permissions:
                try:
                    permissions.add(Permission(perm_str))
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid permission: {perm_str}"
                    )
        
        role = await security_manager.rbac_manager.update_role(
            role_name,
            permissions,
            role_update.description
        )
        
        await security_manager.log_audit_event(
            AuditEventType.SYSTEM_ACCESS,
            user_id=user_id,
            details={"role_updated": role_name}
        )
        
        return RoleResponse(
            name=role.name,
            description=role.description,
            permissions=[p.value for p in role.permissions],
            parent_roles=list(role.parent_roles),
            is_system=role.is_system,
            created_at=role.created_at.isoformat(),
            updated_at=role.updated_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


@router.delete("/roles/{role_name}")
async def delete_role(
    request: Request,
    role_name: str,
    token: str = Depends(oauth2_scheme)
):
    """Delete a custom role"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        result = await security_manager.rbac_manager.delete_role(role_name)
        
        if result:
            await security_manager.log_audit_event(
                AuditEventType.SYSTEM_ACCESS,
                user_id=user_id,
                details={"role_deleted": role_name}
            )
            return {"message": f"Role '{role_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}"
        )


# === User Role Assignment Endpoints ===

@router.post("/users/assign-role")
async def assign_role_to_user(
    request: Request,
    assignment: UserRoleAssignment,
    token: str = Depends(oauth2_scheme)
):
    """Assign role to user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    admin_user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(admin_user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        result = await security_manager.assign_role(
            assignment.user_id, assignment.role_name, admin_user_id
        )
        
        if result:
            return {"message": f"Role '{assignment.role_name}' assigned to user '{assignment.user_id}'"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to assign role")
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign role: {str(e)}"
        )


@router.post("/users/revoke-role")
async def revoke_role_from_user(
    request: Request,
    assignment: UserRoleAssignment,
    token: str = Depends(oauth2_scheme)
):
    """Revoke role from user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    admin_user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(admin_user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        result = await security_manager.revoke_role(
            assignment.user_id, assignment.role_name, admin_user_id
        )
        
        if result:
            return {"message": f"Role '{assignment.role_name}' revoked from user '{assignment.user_id}'"}
        else:
            return {"message": "Role was not assigned to user"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke role: {str(e)}"
        )


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    request: Request,
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get user's permissions and roles"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify token and check if user can view permissions
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    requester_id = payload.get("sub")
    
    # Allow users to view their own permissions, or admins to view any
    if requester_id != user_id:
        has_permission = await security_manager.check_permission(requester_id, Permission.ADMIN_USERS)
        if not has_permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view other user's permissions")
    
    try:
        permissions_info = await security_manager.get_user_permissions(user_id)
        return permissions_info
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user permissions: {str(e)}"
        )


# === Permission Checking Endpoints ===

@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_permission(
    request: Request,
    check_request: PermissionCheckRequest,
    token: str = Depends(oauth2_scheme)
):
    """Check if user has specific permission"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    requester_id = payload.get("sub")
    has_permission = await security_manager.check_permission(requester_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        # Convert permission string to Permission enum
        permission = Permission(check_request.permission)
        
        # Prepare context for ABAC evaluation if needed
        context = {
            "user_data": {},  # Would populate from database in production
            "resource_data": {},  # Would populate from database in production
            "environment": {
                "ip_address": request.client.host if request.client else "",
                "user_agent": request.headers.get("user-agent", ""),
                "timestamp": "2024-08-25T17:37:00Z"
            }
        }
        
        allowed = await security_manager.check_permission(
            check_request.user_id,
            permission,
            check_request.resource_type,
            check_request.resource_id,
            context
        )
        
        resource_str = None
        if check_request.resource_type and check_request.resource_id:
            resource_str = f"{check_request.resource_type}:{check_request.resource_id}"
        
        return PermissionCheckResponse(
            allowed=allowed,
            user_id=check_request.user_id,
            permission=check_request.permission,
            resource=resource_str,
            reason="Permission granted by RBAC/ABAC evaluation" if allowed else "Permission denied"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid permission: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check permission: {str(e)}"
        )


# === Resource Permission Management ===

@router.post("/resource-permissions/grant")
async def grant_resource_permission(
    request: Request,
    perm_request: ResourcePermissionRequest,
    token: str = Depends(oauth2_scheme)
):
    """Grant specific permissions on a resource to a user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    admin_user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(admin_user_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        # Convert permission strings to Permission enum
        permissions = set()
        for perm_str in perm_request.permissions:
            try:
                permissions.add(Permission(perm_str))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid permission: {perm_str}"
                )
        
        from datetime import datetime
        expires_at = None
        if perm_request.expires_at:
            expires_at = datetime.fromisoformat(perm_request.expires_at)
        
        result = await security_manager.rbac_manager.grant_resource_permission(
            perm_request.user_id,
            perm_request.resource_type,
            perm_request.resource_id,
            permissions,
            admin_user_id,
            expires_at
        )
        
        if result:
            return {"message": "Resource permissions granted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to grant permissions")
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to grant resource permission: {str(e)}"
        )


@router.get("/permissions/available")
async def list_available_permissions(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """List all available permissions in the system"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    requester_id = payload.get("sub")
    has_permission = await security_manager.check_permission(requester_id, Permission.ADMIN_USERS)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    try:
        permissions = []
        for perm in Permission:
            permissions.append({
                "name": perm.value,
                "category": perm.value.split(":")[0],
                "action": perm.value.split(":")[-1] if ":" in perm.value else perm.value
            })
        
        # Group by category
        categories = {}
        for perm in permissions:
            category = perm["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(perm)
        
        return {
            "permissions": permissions,
            "categories": categories,
            "total_count": len(permissions)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list permissions: {str(e)}"
        )