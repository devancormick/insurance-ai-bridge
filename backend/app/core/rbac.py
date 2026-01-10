"""
Role-Based Access Control (RBAC)
Hierarchical role-based permissions
"""

from typing import List, Dict, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from app.core.enterprise_auth import Role


class Permission(Enum):
    """Resource permissions"""
    # Claims
    CLAIM_VIEW = "claim:view"
    CLAIM_CREATE = "claim:create"
    CLAIM_EDIT = "claim:edit"
    CLAIM_DELETE = "claim:delete"
    CLAIM_APPROVE = "claim:approve"
    
    # Members
    MEMBER_VIEW = "member:view"
    MEMBER_CREATE = "member:create"
    MEMBER_EDIT = "member:edit"
    MEMBER_DELETE = "member:delete"
    
    # Policies
    POLICY_VIEW = "policy:view"
    POLICY_CREATE = "policy:create"
    POLICY_EDIT = "policy:edit"
    POLICY_DELETE = "policy:delete"
    
    # Admin
    ADMIN_VIEW = "admin:view"
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_MANAGE_ROLES = "admin:manage_roles"
    ADMIN_VIEW_AUDIT = "admin:view_audit"
    ADMIN_SYSTEM_CONFIG = "admin:system_config"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"


@dataclass
class RolePermission:
    """Role permission mapping"""
    role: Role
    permissions: Set[Permission]
    inherited_roles: List[Role] = None
    
    def __post_init__(self):
        if self.inherited_roles is None:
            self.inherited_roles = []


class RBACManager:
    """Manages role-based access control"""
    
    def __init__(self):
        self.role_permissions = self._initialize_role_permissions()
        self.role_hierarchy = self._initialize_role_hierarchy()
    
    def _initialize_role_permissions(self) -> Dict[Role, RolePermission]:
        """Initialize role permissions"""
        return {
            Role.SUPER_ADMIN: RolePermission(
                role=Role.SUPER_ADMIN,
                permissions=set(Permission),  # All permissions
                inherited_roles=[]
            ),
            Role.ADMIN: RolePermission(
                role=Role.ADMIN,
                permissions={
                    Permission.CLAIM_VIEW,
                    Permission.CLAIM_CREATE,
                    Permission.CLAIM_EDIT,
                    Permission.CLAIM_DELETE,
                    Permission.CLAIM_APPROVE,
                    Permission.MEMBER_VIEW,
                    Permission.MEMBER_CREATE,
                    Permission.MEMBER_EDIT,
                    Permission.MEMBER_DELETE,
                    Permission.POLICY_VIEW,
                    Permission.POLICY_CREATE,
                    Permission.POLICY_EDIT,
                    Permission.POLICY_DELETE,
                    Permission.ADMIN_VIEW,
                    Permission.ADMIN_MANAGE_USERS,
                    Permission.ANALYTICS_VIEW,
                    Permission.ANALYTICS_EXPORT,
                },
                inherited_roles=[Role.USER]
            ),
            Role.USER: RolePermission(
                role=Role.USER,
                permissions={
                    Permission.CLAIM_VIEW,
                    Permission.CLAIM_CREATE,
                    Permission.CLAIM_EDIT,
                    Permission.MEMBER_VIEW,
                    Permission.MEMBER_CREATE,
                    Permission.MEMBER_EDIT,
                    Permission.POLICY_VIEW,
                    Permission.ANALYTICS_VIEW,
                },
                inherited_roles=[Role.VIEWER]
            ),
            Role.VIEWER: RolePermission(
                role=Role.VIEWER,
                permissions={
                    Permission.CLAIM_VIEW,
                    Permission.MEMBER_VIEW,
                    Permission.POLICY_VIEW,
                },
                inherited_roles=[]
            ),
            Role.AUDITOR: RolePermission(
                role=Role.AUDITOR,
                permissions={
                    Permission.CLAIM_VIEW,
                    Permission.MEMBER_VIEW,
                    Permission.POLICY_VIEW,
                    Permission.ADMIN_VIEW_AUDIT,
                    Permission.ANALYTICS_VIEW,
                },
                inherited_roles=[]
            ),
        }
    
    def _initialize_role_hierarchy(self) -> Dict[Role, List[Role]]:
        """Initialize role hierarchy (child roles inherit from parent)"""
        return {
            Role.SUPER_ADMIN: [],
            Role.ADMIN: [Role.USER, Role.VIEWER],
            Role.USER: [Role.VIEWER],
            Role.VIEWER: [],
            Role.AUDITOR: [],
        }
    
    def has_permission(self, user_roles: List[Role], permission: Permission) -> bool:
        """
        Check if user with given roles has a permission
        
        Args:
            user_roles: List of user roles
            permission: Permission to check
        
        Returns:
            True if user has permission, False otherwise
        """
        for role in user_roles:
            # Check direct permissions
            role_perm = self.role_permissions.get(role)
            if role_perm and permission in role_perm.permissions:
                return True
            
            # Check inherited roles
            inherited = self.role_hierarchy.get(role, [])
            for inherited_role in inherited:
                inherited_perm = self.role_permissions.get(inherited_role)
                if inherited_perm and permission in inherited_perm.permissions:
                    return True
        
        return False
    
    def get_permissions(self, user_roles: List[Role]) -> Set[Permission]:
        """
        Get all permissions for user roles
        
        Args:
            user_roles: List of user roles
        
        Returns:
            Set of all permissions
        """
        permissions = set()
        
        for role in user_roles:
            role_perm = self.role_permissions.get(role)
            if role_perm:
                permissions.update(role_perm.permissions)
            
            # Add inherited role permissions
            inherited = self.role_hierarchy.get(role, [])
            for inherited_role in inherited:
                inherited_perm = self.role_permissions.get(inherited_role)
                if inherited_perm:
                    permissions.update(inherited_perm.permissions)
        
        return permissions
    
    def can_access_resource(
        self,
        user_roles: List[Role],
        resource_type: str,
        action: str
    ) -> bool:
        """
        Check if user can perform action on resource type
        
        Args:
            user_roles: User roles
            resource_type: Type of resource (claim, member, policy, etc.)
            action: Action to perform (view, create, edit, delete, approve)
        
        Returns:
            True if allowed, False otherwise
        """
        permission_name = f"{resource_type}:{action}".lower()
        
        try:
            permission = Permission(permission_name)
            return self.has_permission(user_roles, permission)
        except ValueError:
            # Unknown permission
            return False
    
    def add_role_permission(self, role: Role, permission: Permission):
        """Add permission to a role"""
        if role not in self.role_permissions:
            self.role_permissions[role] = RolePermission(
                role=role,
                permissions=set(),
                inherited_roles=[]
            )
        
        self.role_permissions[role].permissions.add(permission)
    
    def remove_role_permission(self, role: Role, permission: Permission):
        """Remove permission from a role"""
        if role in self.role_permissions:
            self.role_permissions[role].permissions.discard(permission)


# Global RBAC manager instance
rbac_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get the global RBAC manager instance"""
    global rbac_manager
    if rbac_manager is None:
        rbac_manager = RBACManager()
    return rbac_manager

