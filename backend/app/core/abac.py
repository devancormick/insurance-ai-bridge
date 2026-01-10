"""
Attribute-Based Access Control (ABAC)
Fine-grained permissions based on user/resource attributes
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from app.core.rbac import Permission, get_rbac_manager


class AttributeType(Enum):
    """Attribute types for ABAC"""
    USER = "user"
    RESOURCE = "resource"
    ENVIRONMENT = "environment"
    ACTION = "action"
    CONTEXT = "context"


@dataclass
class PolicyRule:
    """ABAC policy rule"""
    rule_id: str
    name: str
    effect: str  # "allow" or "deny"
    conditions: Dict[str, Any]  # Attribute conditions
    actions: List[str]
    resources: List[str]
    priority: int = 0
    enabled: bool = True


class ABACManager:
    """Manages attribute-based access control"""
    
    def __init__(self):
        self.policies: List[PolicyRule] = []
        self.rbac_manager = get_rbac_manager()
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default ABAC policies"""
        # Example: Users can only edit their own claims
        self.policies.append(PolicyRule(
            rule_id="claim-owner-edit",
            name="Claim Owner Edit Policy",
            effect="allow",
            conditions={
                "resource.owner_id": "user.id",
                "action": "claim:edit"
            },
            actions=["claim:edit"],
            resources=["claim/*"],
            priority=100
        ))
        
        # Example: Regional data access restrictions
        self.policies.append(PolicyRule(
            rule_id="regional-data-access",
            name="Regional Data Access Policy",
            effect="allow",
            conditions={
                "user.region": "resource.region",
                "action": ["claim:view", "member:view"]
            },
            actions=["claim:view", "member:view"],
            resources=["claim/*", "member/*"],
            priority=90
        ))
        
        # Example: Business hours access restriction
        self.policies.append(PolicyRule(
            rule_id="business-hours-access",
            name="Business Hours Access Policy",
            effect="allow",
            conditions={
                "context.hour": {"$gte": 9, "$lte": 17},
                "context.day_of_week": {"$in": [1, 2, 3, 4, 5]},  # Mon-Fri
                "user.role": {"$ne": "admin"}  # Admins exempt
            },
            actions=["*"],
            resources=["*"],
            priority=50
        ))
        
        # Example: Compliance data access
        self.policies.append(PolicyRule(
            rule_id="compliance-data-access",
            name="Compliance Data Access Policy",
            effect="allow",
            conditions={
                "resource.data_classification": "compliance",
                "user.compliance_access": True,
                "user.role": {"$in": ["auditor", "admin"]}
            },
            actions=["claim:view", "member:view", "policy:view"],
            resources=["*"],
            priority=200
        ))
    
    def evaluate(
        self,
        user_attributes: Dict[str, Any],
        resource_attributes: Dict[str, Any],
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Evaluate ABAC policy for access request
        
        Args:
            user_attributes: User attributes (id, role, region, etc.)
            resource_attributes: Resource attributes (id, owner_id, region, data_classification, etc.)
            action: Action being requested
            context: Additional context (time, IP, etc.)
        
        Returns:
            True if access is allowed, False otherwise
        """
        if context is None:
            context = {
                "timestamp": datetime.utcnow(),
                "hour": datetime.utcnow().hour,
                "day_of_week": datetime.utcnow().weekday()
            }
        
        # First check RBAC (coarse-grained)
        user_roles = user_attributes.get("roles", [])
        if not self._check_rbac(user_roles, action):
            return False
        
        # Then evaluate ABAC policies (fine-grained)
        applicable_policies = self._get_applicable_policies(action, resource_attributes)
        
        # Sort by priority (higher priority first)
        applicable_policies.sort(key=lambda p: p.priority, reverse=True)
        
        # Evaluate policies in order
        for policy in applicable_policies:
            if not policy.enabled:
                continue
            
            if self._evaluate_policy_conditions(policy, user_attributes, resource_attributes, context):
                # Policy matched - return effect
                return policy.effect == "allow"
        
        # Default deny if no policy matches
        return False
    
    def _check_rbac(self, user_roles: List[str], action: str) -> bool:
        """Check RBAC permissions first (coarse-grained check)"""
        from app.core.enterprise_auth import Role
        
        roles = [Role(r) for r in user_roles if r in [r.value for r in Role]]
        
        try:
            permission = Permission(action)
            return self.rbac_manager.has_permission(roles, permission)
        except ValueError:
            # Unknown permission - check if it's a wildcard or custom action
            return False
    
    def _get_applicable_policies(
        self,
        action: str,
        resource_attributes: Dict[str, Any]
    ) -> List[PolicyRule]:
        """Get policies applicable to the action and resource"""
        applicable = []
        
        for policy in self.policies:
            # Check if action matches
            if "*" in policy.actions or action in policy.actions:
                # Check if resource matches (simplified - would use pattern matching)
                applicable.append(policy)
        
        return applicable
    
    def _evaluate_policy_conditions(
        self,
        policy: PolicyRule,
        user_attributes: Dict[str, Any],
        resource_attributes: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate policy conditions"""
        for condition_key, condition_value in policy.conditions.items():
            # Parse condition key (e.g., "user.role", "resource.owner_id")
            parts = condition_key.split(".", 1)
            if len(parts) != 2:
                continue
            
            attribute_type, attribute_name = parts
            
            # Get attribute value based on type
            if attribute_type == "user":
                actual_value = user_attributes.get(attribute_name)
            elif attribute_type == "resource":
                actual_value = resource_attributes.get(attribute_name)
            elif attribute_type == "context":
                actual_value = context.get(attribute_name)
            elif attribute_type == "action":
                actual_value = context.get("action")  # Would be passed in context
            else:
                continue
            
            # Evaluate condition
            if not self._evaluate_condition(actual_value, condition_value):
                return False
        
        return True
    
    def _evaluate_condition(self, actual_value: Any, condition_value: Any) -> bool:
        """Evaluate a single condition"""
        if isinstance(condition_value, dict):
            # Complex condition (e.g., {"$gte": 9, "$lte": 17})
            for operator, expected_value in condition_value.items():
                if operator == "$eq" or operator == "=":
                    if actual_value != expected_value:
                        return False
                elif operator == "$ne" or operator == "!=":
                    if actual_value == expected_value:
                        return False
                elif operator == "$in":
                    if actual_value not in expected_value:
                        return False
                elif operator == "$nin" or operator == "$not_in":
                    if actual_value in expected_value:
                        return False
                elif operator == "$gte" or operator == ">=":
                    if actual_value < expected_value:
                        return False
                elif operator == "$lte" or operator == "<=":
                    if actual_value > expected_value:
                        return False
                elif operator == "$gt" or operator == ">":
                    if actual_value <= expected_value:
                        return False
                elif operator == "$lt" or operator == "<":
                    if actual_value >= expected_value:
                        return False
            return True
        elif isinstance(condition_value, list):
            # List condition (e.g., ["admin", "user"])
            return actual_value in condition_value
        else:
            # Simple equality
            return actual_value == condition_value
    
    def add_policy(self, policy: PolicyRule):
        """Add a new ABAC policy"""
        self.policies.append(policy)
        # Sort by priority
        self.policies.sort(key=lambda p: p.priority, reverse=True)
    
    def remove_policy(self, rule_id: str):
        """Remove an ABAC policy"""
        self.policies = [p for p in self.policies if p.rule_id != rule_id]
    
    def update_policy(self, rule_id: str, updates: Dict[str, Any]):
        """Update an existing ABAC policy"""
        for policy in self.policies:
            if policy.rule_id == rule_id:
                for key, value in updates.items():
                    if hasattr(policy, key):
                        setattr(policy, key, value)
                break


# Global ABAC manager instance
abac_manager: Optional[ABACManager] = None


def get_abac_manager() -> ABACManager:
    """Get the global ABAC manager instance"""
    global abac_manager
    if abac_manager is None:
        abac_manager = ABACManager()
    return abac_manager

