"""
Enterprise Role-Based Access Control (RBAC) system
Supports hierarchical roles, permissions, and resource-level access control
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class Permission(str, Enum):
    """System permissions"""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Report management
    REPORT_CREATE = "report:create"
    REPORT_READ = "report:read"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"
    REPORT_LIST = "report:list"
    REPORT_EXPORT = "report:export"
    REPORT_SHARE = "report:share"
    
    # Query management
    QUERY_CREATE = "query:create"
    QUERY_EXECUTE = "query:execute"
    QUERY_READ = "query:read"
    QUERY_UPDATE = "query:update"
    QUERY_DELETE = "query:delete"
    QUERY_LIST = "query:list"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_ADVANCED = "analytics:advanced"
    
    # System administration
    ADMIN_CONFIG = "admin:config"
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_SECURITY = "admin:security"
    
    # Data access levels
    DATA_READ_OWN = "data:read:own"
    DATA_READ_TEAM = "data:read:team"
    DATA_READ_ALL = "data:read:all"
    DATA_WRITE_OWN = "data:write:own"
    DATA_WRITE_TEAM = "data:write:team"
    DATA_WRITE_ALL = "data:write:all"


@dataclass
class Role:
    """Role definition with permissions and metadata"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    is_system: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourcePermission:
    """Resource-level permission definition"""
    resource_type: str
    resource_id: str
    user_id: str
    permissions: Set[Permission]
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class RBACManager:
    """Role-Based Access Control manager"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.resource_permissions: Dict[str, List[ResourcePermission]] = {}
        self._initialize_system_roles()
    
    def _initialize_system_roles(self):
        """Initialize default system roles"""
        # Super Admin - all permissions
        super_admin = Role(
            name="super_admin",
            description="Super Administrator with full system access",
            permissions=set(Permission),
            is_system=True
        )
        
        # Admin - most permissions except super admin functions
        admin = Role(
            name="admin",
            description="System Administrator",
            permissions={
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.USER_DELETE, Permission.USER_LIST,
                Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_UPDATE,
                Permission.REPORT_DELETE, Permission.REPORT_LIST, Permission.REPORT_EXPORT,
                Permission.REPORT_SHARE,
                Permission.QUERY_CREATE, Permission.QUERY_EXECUTE, Permission.QUERY_READ,
                Permission.QUERY_UPDATE, Permission.QUERY_DELETE, Permission.QUERY_LIST,
                Permission.ANALYTICS_VIEW, Permission.ANALYTICS_ADVANCED,
                Permission.ADMIN_CONFIG, Permission.ADMIN_USERS, Permission.ADMIN_AUDIT,
                Permission.DATA_READ_ALL, Permission.DATA_WRITE_ALL
            },
            is_system=True
        )
        
        # Manager - team-level management
        manager = Role(
            name="manager",
            description="Team Manager",
            permissions={
                Permission.USER_READ, Permission.USER_LIST,
                Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_UPDATE,
                Permission.REPORT_DELETE, Permission.REPORT_LIST, Permission.REPORT_EXPORT,
                Permission.REPORT_SHARE,
                Permission.QUERY_CREATE, Permission.QUERY_EXECUTE, Permission.QUERY_READ,
                Permission.QUERY_UPDATE, Permission.QUERY_DELETE, Permission.QUERY_LIST,
                Permission.ANALYTICS_VIEW, Permission.ANALYTICS_ADVANCED,
                Permission.DATA_READ_TEAM, Permission.DATA_WRITE_TEAM
            },
            is_system=True
        )
        
        # Analyst - data analysis and reporting
        analyst = Role(
            name="analyst",
            description="Data Analyst",
            permissions={
                Permission.REPORT_CREATE, Permission.REPORT_READ, Permission.REPORT_UPDATE,
                Permission.REPORT_LIST, Permission.REPORT_EXPORT,
                Permission.QUERY_CREATE, Permission.QUERY_EXECUTE, Permission.QUERY_READ,
                Permission.QUERY_UPDATE, Permission.QUERY_LIST,
                Permission.ANALYTICS_VIEW,
                Permission.DATA_READ_TEAM, Permission.DATA_WRITE_OWN
            },
            is_system=True
        )
        
        # Viewer - read-only access
        viewer = Role(
            name="viewer",
            description="Read-only User",
            permissions={
                Permission.REPORT_READ, Permission.REPORT_LIST,
                Permission.QUERY_READ, Permission.QUERY_LIST,
                Permission.ANALYTICS_VIEW,
                Permission.DATA_READ_OWN
            },
            is_system=True
        )
        
        # Store system roles
        for role in [super_admin, admin, manager, analyst, viewer]:
            self.roles[role.name] = role
        
        logger.info("System roles initialized", roles=list(self.roles.keys()))
    
    async def create_role(self, name: str, description: str, 
                         permissions: Set[Permission], 
                         parent_roles: Optional[Set[str]] = None) -> Role:
        """Create a new custom role"""
        if name in self.roles:
            raise ValueError(f"Role '{name}' already exists")
        
        # Validate parent roles exist
        parent_roles = parent_roles or set()
        for parent in parent_roles:
            if parent not in self.roles:
                raise ValueError(f"Parent role '{parent}' does not exist")
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions,
            parent_roles=parent_roles,
            is_system=False
        )
        
        self.roles[name] = role
        logger.info("Role created", role_name=name, permissions=len(permissions))
        return role
    
    async def update_role(self, name: str, permissions: Optional[Set[Permission]] = None,
                         description: Optional[str] = None) -> Role:
        """Update an existing role"""
        if name not in self.roles:
            raise ValueError(f"Role '{name}' not found")
        
        role = self.roles[name]
        
        if role.is_system:
            raise ValueError("Cannot modify system roles")
        
        if permissions is not None:
            role.permissions = permissions
        
        if description is not None:
            role.description = description
        
        role.updated_at = datetime.utcnow()
        logger.info("Role updated", role_name=name)
        return role
    
    async def delete_role(self, name: str) -> bool:
        """Delete a custom role"""
        if name not in self.roles:
            return False
        
        role = self.roles[name]
        if role.is_system:
            raise ValueError("Cannot delete system roles")
        
        # Remove role from all users
        for user_id, user_roles in self.user_roles.items():
            user_roles.discard(name)
        
        del self.roles[name]
        logger.info("Role deleted", role_name=name)
        return True
    
    async def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user"""
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' not found")
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        
        self.user_roles[user_id].add(role_name)
        logger.info("Role assigned", user_id=user_id, role=role_name)
        return True
    
    async def revoke_role_from_user(self, user_id: str, role_name: str) -> bool:
        """Revoke a role from a user"""
        if user_id not in self.user_roles:
            return False
        
        if role_name in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role_name)
            logger.info("Role revoked", user_id=user_id, role=role_name)
            return True
        
        return False
    
    async def get_user_roles(self, user_id: str) -> Set[str]:
        """Get all roles assigned to a user"""
        return self.user_roles.get(user_id, set())
    
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user (including inherited from roles)"""
        permissions = set()
        user_roles = await self.get_user_roles(user_id)
        
        # Collect permissions from all roles (including parent roles)
        for role_name in user_roles:
            permissions.update(await self._get_role_permissions_recursive(role_name))
        
        # Add resource-specific permissions
        resource_key = f"user:{user_id}"
        if resource_key in self.resource_permissions:
            for resource_perm in self.resource_permissions[resource_key]:
                if resource_perm.expires_at is None or resource_perm.expires_at > datetime.utcnow():
                    permissions.update(resource_perm.permissions)
        
        return permissions
    
    async def _get_role_permissions_recursive(self, role_name: str) -> Set[Permission]:
        """Get permissions for a role including parent role permissions"""
        if role_name not in self.roles:
            return set()
        
        role = self.roles[role_name]
        permissions = role.permissions.copy()
        
        # Add permissions from parent roles
        for parent_role in role.parent_roles:
            permissions.update(await self._get_role_permissions_recursive(parent_role))
        
        return permissions
    
    async def has_permission(self, user_id: str, permission: Permission, 
                           resource_type: Optional[str] = None, 
                           resource_id: Optional[str] = None) -> bool:
        """Check if user has a specific permission"""
        user_permissions = await self.get_user_permissions(user_id)
        
        # Check direct permission
        if permission in user_permissions:
            return True
        
        # Check resource-specific permissions
        if resource_type and resource_id:
            return await self.has_resource_permission(user_id, resource_type, resource_id, permission)
        
        return False
    
    async def grant_resource_permission(self, user_id: str, resource_type: str, 
                                      resource_id: str, permissions: Set[Permission],
                                      granted_by: str, expires_at: Optional[datetime] = None) -> bool:
        """Grant specific permissions on a resource to a user"""
        resource_key = f"{resource_type}:{resource_id}"
        
        if resource_key not in self.resource_permissions:
            self.resource_permissions[resource_key] = []
        
        resource_perm = ResourcePermission(
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            permissions=permissions,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        self.resource_permissions[resource_key].append(resource_perm)
        logger.info("Resource permission granted", 
                   user_id=user_id, resource=resource_key, permissions=len(permissions))
        return True
    
    async def revoke_resource_permission(self, user_id: str, resource_type: str, 
                                       resource_id: str, permissions: Set[Permission]) -> bool:
        """Revoke specific permissions on a resource from a user"""
        resource_key = f"{resource_type}:{resource_id}"
        
        if resource_key not in self.resource_permissions:
            return False
        
        # Remove matching permissions
        updated_permissions = []
        for resource_perm in self.resource_permissions[resource_key]:
            if resource_perm.user_id == user_id:
                # Remove the specified permissions
                resource_perm.permissions -= permissions
                # Keep the permission entry if it still has permissions
                if resource_perm.permissions:
                    updated_permissions.append(resource_perm)
            else:
                updated_permissions.append(resource_perm)
        
        self.resource_permissions[resource_key] = updated_permissions
        logger.info("Resource permission revoked", 
                   user_id=user_id, resource=resource_key, permissions=len(permissions))
        return True
    
    async def has_resource_permission(self, user_id: str, resource_type: str, 
                                    resource_id: str, permission: Permission) -> bool:
        """Check if user has specific permission on a resource"""
        resource_key = f"{resource_type}:{resource_id}"
        
        if resource_key not in self.resource_permissions:
            return False
        
        for resource_perm in self.resource_permissions[resource_key]:
            if (resource_perm.user_id == user_id and 
                permission in resource_perm.permissions and
                (resource_perm.expires_at is None or resource_perm.expires_at > datetime.utcnow())):
                return True
        
        return False
    
    async def get_user_accessible_resources(self, user_id: str, resource_type: str, 
                                          permission: Permission) -> List[str]:
        """Get list of resources user can access with given permission"""
        accessible_resources = []
        
        for resource_key, permissions_list in self.resource_permissions.items():
            if resource_key.startswith(f"{resource_type}:"):
                resource_id = resource_key.split(":", 1)[1]
                if await self.has_resource_permission(user_id, resource_type, resource_id, permission):
                    accessible_resources.append(resource_id)
        
        return accessible_resources
    
    async def get_role_hierarchy(self) -> Dict[str, Any]:
        """Get the complete role hierarchy"""
        hierarchy = {}
        
        for role_name, role in self.roles.items():
            hierarchy[role_name] = {
                "description": role.description,
                "permissions": [p.value for p in role.permissions],
                "parent_roles": list(role.parent_roles),
                "is_system": role.is_system,
                "user_count": len([uid for uid, roles in self.user_roles.items() if role_name in roles])
            }
        
        return hierarchy
    
    async def cleanup_expired_permissions(self) -> int:
        """Clean up expired resource permissions"""
        cleanup_count = 0
        current_time = datetime.utcnow()
        
        for resource_key in list(self.resource_permissions.keys()):
            original_count = len(self.resource_permissions[resource_key])
            
            # Filter out expired permissions
            self.resource_permissions[resource_key] = [
                perm for perm in self.resource_permissions[resource_key]
                if perm.expires_at is None or perm.expires_at > current_time
            ]
            
            cleanup_count += original_count - len(self.resource_permissions[resource_key])
            
            # Remove empty resource entries
            if not self.resource_permissions[resource_key]:
                del self.resource_permissions[resource_key]
        
        if cleanup_count > 0:
            logger.info("Expired permissions cleaned up", count=cleanup_count)
        
        return cleanup_count