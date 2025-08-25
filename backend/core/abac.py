"""
Attribute-Based Access Control (ABAC) system
Supports fine-grained policy-based access control with dynamic evaluation
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
import json
import structlog

logger = structlog.get_logger(__name__)


class PolicyEffect(str, Enum):
    """Policy evaluation effects"""
    ALLOW = "allow"
    DENY = "deny"


class AttributeType(str, Enum):
    """Attribute types for policy evaluation"""
    USER = "user"
    RESOURCE = "resource"
    ENVIRONMENT = "environment"
    ACTION = "action"


@dataclass
class Attribute:
    """Attribute definition for ABAC evaluation"""
    name: str
    type: AttributeType
    value: Any
    data_type: str = "string"  # string, number, boolean, datetime, list


@dataclass
class Condition:
    """Policy condition for attribute evaluation"""
    attribute: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, not_in, contains, matches
    value: Any
    negated: bool = False


@dataclass
class PolicyRule:
    """Individual policy rule with conditions and effect"""
    name: str
    effect: PolicyEffect
    conditions: List[Condition] = field(default_factory=list)
    description: str = ""


@dataclass
class Policy:
    """Complete policy with metadata and rules"""
    name: str
    description: str
    rules: List[PolicyRule] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""


class ABACManager:
    """Attribute-Based Access Control manager"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.attribute_providers: Dict[str, Callable] = {}
        self._initialize_default_policies()
        self._register_default_attribute_providers()
    
    def _initialize_default_policies(self):
        """Initialize default security policies"""
        
        # Admin access policy
        admin_policy = Policy(
            name="admin_access",
            description="Administrators have full access during business hours",
            rules=[
                PolicyRule(
                    name="admin_full_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("user.role", "in", ["admin", "super_admin"]),
                        Condition("environment.time", "gte", "08:00"),
                        Condition("environment.time", "lte", "18:00")
                    ]
                )
            ],
            priority=100
        )
        
        # Data access policy
        data_access_policy = Policy(
            name="data_access_control",
            description="Control data access based on sensitivity and user clearance",
            rules=[
                PolicyRule(
                    name="sensitive_data_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("resource.sensitivity", "eq", "high"),
                        Condition("user.clearance_level", "gte", 3)
                    ]
                ),
                PolicyRule(
                    name="confidential_data_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("resource.sensitivity", "eq", "confidential"),
                        Condition("user.clearance_level", "gte", 2)
                    ]
                ),
                PolicyRule(
                    name="public_data_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("resource.sensitivity", "eq", "public")
                    ]
                )
            ],
            priority=90
        )
        
        # Time-based access policy
        time_based_policy = Policy(
            name="time_based_access",
            description="Restrict access based on time and location",
            rules=[
                PolicyRule(
                    name="business_hours_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("environment.time", "gte", "06:00"),
                        Condition("environment.time", "lte", "22:00"),
                        Condition("environment.day_of_week", "not_in", ["saturday", "sunday"])
                    ]
                ),
                PolicyRule(
                    name="weekend_admin_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("user.role", "in", ["admin", "super_admin"]),
                        Condition("environment.day_of_week", "in", ["saturday", "sunday"])
                    ]
                )
            ],
            priority=80
        )
        
        # Geographic access policy
        geo_policy = Policy(
            name="geographic_access",
            description="Control access based on geographic location",
            rules=[
                PolicyRule(
                    name="allowed_countries",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("environment.country", "in", ["US", "CA", "UK", "DE", "FR"])
                    ]
                ),
                PolicyRule(
                    name="deny_restricted_countries",
                    effect=PolicyEffect.DENY,
                    conditions=[
                        Condition("environment.country", "in", ["CN", "RU", "IR", "KP"])
                    ]
                )
            ],
            priority=95
        )
        
        # Resource ownership policy
        ownership_policy = Policy(
            name="resource_ownership",
            description="Users can access their own resources",
            rules=[
                PolicyRule(
                    name="owner_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("resource.owner", "eq", "user.id")
                    ]
                ),
                PolicyRule(
                    name="team_member_access",
                    effect=PolicyEffect.ALLOW,
                    conditions=[
                        Condition("resource.team", "eq", "user.team"),
                        Condition("action.type", "in", ["read", "list"])
                    ]
                )
            ],
            priority=85
        )
        
        # Store default policies
        for policy in [admin_policy, data_access_policy, time_based_policy, geo_policy, ownership_policy]:
            self.policies[policy.name] = policy
        
        logger.info("Default ABAC policies initialized", policies=list(self.policies.keys()))
    
    def _register_default_attribute_providers(self):
        """Register default attribute providers"""
        
        def get_current_time_attributes() -> Dict[str, Any]:
            now = datetime.now()
            return {
                "environment.time": now.strftime("%H:%M"),
                "environment.hour": now.hour,
                "environment.day_of_week": now.strftime("%A").lower(),
                "environment.date": now.strftime("%Y-%m-%d"),
                "environment.timestamp": now.isoformat()
            }
        
        def get_user_attributes(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "user.id": user_id,
                "user.email": user_data.get("email", ""),
                "user.role": user_data.get("role", "viewer"),
                "user.team": user_data.get("team", ""),
                "user.department": user_data.get("department", ""),
                "user.clearance_level": user_data.get("clearance_level", 1),
                "user.employment_type": user_data.get("employment_type", "employee"),
                "user.location": user_data.get("location", ""),
                "user.created_at": user_data.get("created_at", "")
            }
        
        def get_resource_attributes(resource_type: str, resource_id: str, 
                                  resource_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "resource.id": resource_id,
                "resource.type": resource_type,
                "resource.owner": resource_data.get("owner", ""),
                "resource.team": resource_data.get("team", ""),
                "resource.sensitivity": resource_data.get("sensitivity", "public"),
                "resource.classification": resource_data.get("classification", "unclassified"),
                "resource.created_at": resource_data.get("created_at", ""),
                "resource.size": resource_data.get("size", 0),
                "resource.tags": resource_data.get("tags", [])
            }
        
        def get_environment_attributes(request_context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "environment.ip_address": request_context.get("ip_address", ""),
                "environment.user_agent": request_context.get("user_agent", ""),
                "environment.country": request_context.get("country", ""),
                "environment.region": request_context.get("region", ""),
                "environment.network": request_context.get("network", "public"),
                "environment.protocol": request_context.get("protocol", "https"),
                "environment.device_type": request_context.get("device_type", "unknown")
            }
        
        self.attribute_providers["time"] = get_current_time_attributes
        self.attribute_providers["user"] = get_user_attributes
        self.attribute_providers["resource"] = get_resource_attributes
        self.attribute_providers["environment"] = get_environment_attributes
    
    async def create_policy(self, policy: Policy) -> bool:
        """Create a new ABAC policy"""
        if policy.name in self.policies:
            raise ValueError(f"Policy '{policy.name}' already exists")
        
        policy.created_at = datetime.utcnow()
        policy.updated_at = datetime.utcnow()
        self.policies[policy.name] = policy
        
        logger.info("ABAC policy created", policy_name=policy.name, rules=len(policy.rules))
        return True
    
    async def update_policy(self, policy_name: str, updated_policy: Policy) -> bool:
        """Update an existing ABAC policy"""
        if policy_name not in self.policies:
            raise ValueError(f"Policy '{policy_name}' not found")
        
        updated_policy.updated_at = datetime.utcnow()
        self.policies[policy_name] = updated_policy
        
        logger.info("ABAC policy updated", policy_name=policy_name)
        return True
    
    async def delete_policy(self, policy_name: str) -> bool:
        """Delete an ABAC policy"""
        if policy_name not in self.policies:
            return False
        
        del self.policies[policy_name]
        logger.info("ABAC policy deleted", policy_name=policy_name)
        return True
    
    async def evaluate_access(self, user_id: str, action: str, resource_type: str, 
                            resource_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate access request against all policies"""
        
        # Gather attributes from all providers
        attributes = await self._gather_attributes(user_id, resource_type, resource_id, context)
        attributes["action.type"] = action
        
        # Evaluate all enabled policies
        policy_results = []
        final_decision = PolicyEffect.DENY  # Default deny
        
        # Sort policies by priority (higher priority first)
        sorted_policies = sorted(
            [(name, policy) for name, policy in self.policies.items() if policy.enabled],
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        for policy_name, policy in sorted_policies:
            policy_result = await self._evaluate_policy(policy, attributes)
            policy_results.append({
                "policy": policy_name,
                "effect": policy_result["effect"],
                "matched_rules": policy_result["matched_rules"]
            })
            
            # Apply policy combining algorithm (first applicable)
            if policy_result["effect"] != "not_applicable":
                final_decision = policy_result["effect"]
                break
        
        evaluation_result = {
            "decision": final_decision,
            "user_id": user_id,
            "action": action,
            "resource": f"{resource_type}:{resource_id}",
            "timestamp": datetime.utcnow().isoformat(),
            "policy_results": policy_results,
            "attributes_evaluated": len(attributes)
        }
        
        logger.info("ABAC access evaluation completed", 
                   user_id=user_id, decision=final_decision, 
                   policies_evaluated=len(policy_results))
        
        return evaluation_result
    
    async def _gather_attributes(self, user_id: str, resource_type: str, 
                               resource_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all attributes for policy evaluation"""
        attributes = {}
        
        # Get time-based attributes
        if "time" in self.attribute_providers:
            attributes.update(self.attribute_providers["time"]())
        
        # Get user attributes
        if "user" in self.attribute_providers:
            user_data = context.get("user_data", {})
            attributes.update(self.attribute_providers["user"](user_id, user_data))
        
        # Get resource attributes
        if "resource" in self.attribute_providers:
            resource_data = context.get("resource_data", {})
            attributes.update(self.attribute_providers["resource"](resource_type, resource_id, resource_data))
        
        # Get environment attributes
        if "environment" in self.attribute_providers:
            env_context = context.get("environment", {})
            attributes.update(self.attribute_providers["environment"](env_context))
        
        return attributes
    
    async def _evaluate_policy(self, policy: Policy, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single policy against attributes"""
        matched_rules = []
        
        for rule in policy.rules:
            if await self._evaluate_rule(rule, attributes):
                matched_rules.append(rule.name)
                # Return the effect of the first matching rule
                return {
                    "effect": rule.effect,
                    "matched_rules": matched_rules
                }
        
        return {
            "effect": "not_applicable",
            "matched_rules": matched_rules
        }
    
    async def _evaluate_rule(self, rule: PolicyRule, attributes: Dict[str, Any]) -> bool:
        """Evaluate a single rule against attributes"""
        # All conditions must be true for the rule to match
        for condition in rule.conditions:
            if not await self._evaluate_condition(condition, attributes):
                return False
        
        return True
    
    async def _evaluate_condition(self, condition: Condition, attributes: Dict[str, Any]) -> bool:
        """Evaluate a single condition against attributes"""
        attribute_value = attributes.get(condition.attribute)
        
        if attribute_value is None:
            return False
        
        result = False
        
        try:
            if condition.operator == "eq":
                result = attribute_value == condition.value
            elif condition.operator == "ne":
                result = attribute_value != condition.value
            elif condition.operator == "gt":
                result = attribute_value > condition.value
            elif condition.operator == "lt":
                result = attribute_value < condition.value
            elif condition.operator == "gte":
                result = attribute_value >= condition.value
            elif condition.operator == "lte":
                result = attribute_value <= condition.value
            elif condition.operator == "in":
                result = attribute_value in condition.value
            elif condition.operator == "not_in":
                result = attribute_value not in condition.value
            elif condition.operator == "contains":
                result = condition.value in str(attribute_value)
            elif condition.operator == "matches":
                import re
                result = bool(re.match(condition.value, str(attribute_value)))
            else:
                logger.warning("Unknown condition operator", operator=condition.operator)
                return False
            
        except Exception as e:
            logger.error("Error evaluating condition", 
                        condition=condition.attribute, 
                        operator=condition.operator, 
                        error=str(e))
            return False
        
        # Apply negation if specified
        if condition.negated:
            result = not result
        
        return result
    
    async def get_applicable_policies(self, user_id: str, action: str, 
                                    resource_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of policies that would apply to a given request"""
        applicable_policies = []
        
        # Simplified attribute gathering for policy checking
        attributes = await self._gather_attributes(user_id, resource_type, "test", context)
        attributes["action.type"] = action
        
        for policy_name, policy in self.policies.items():
            if not policy.enabled:
                continue
            
            policy_info = {
                "name": policy_name,
                "description": policy.description,
                "priority": policy.priority,
                "rules": len(policy.rules),
                "applicable": False
            }
            
            # Check if any rule in the policy could apply
            for rule in policy.rules:
                if await self._could_rule_apply(rule, attributes):
                    policy_info["applicable"] = True
                    break
            
            applicable_policies.append(policy_info)
        
        return sorted(applicable_policies, key=lambda x: x["priority"], reverse=True)
    
    async def _could_rule_apply(self, rule: PolicyRule, attributes: Dict[str, Any]) -> bool:
        """Check if a rule could potentially apply given available attributes"""
        # Check if we have all required attributes for this rule
        for condition in rule.conditions:
            if condition.attribute not in attributes:
                return False
        
        return True
    
    async def test_policy(self, policy_name: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test a policy against a set of test cases"""
        if policy_name not in self.policies:
            raise ValueError(f"Policy '{policy_name}' not found")
        
        policy = self.policies[policy_name]
        results = []
        
        for i, test_case in enumerate(test_cases):
            attributes = test_case.get("attributes", {})
            expected_effect = test_case.get("expected_effect")
            
            policy_result = await self._evaluate_policy(policy, attributes)
            actual_effect = policy_result["effect"]
            
            results.append({
                "test_case": i + 1,
                "expected": expected_effect,
                "actual": actual_effect,
                "passed": expected_effect == actual_effect,
                "matched_rules": policy_result["matched_rules"]
            })
        
        passed_tests = sum(1 for r in results if r["passed"])
        
        return {
            "policy": policy_name,
            "total_tests": len(test_cases),
            "passed": passed_tests,
            "failed": len(test_cases) - passed_tests,
            "results": results
        }
    
    async def get_policy_statistics(self) -> Dict[str, Any]:
        """Get statistics about policies and their usage"""
        stats = {
            "total_policies": len(self.policies),
            "enabled_policies": len([p for p in self.policies.values() if p.enabled]),
            "disabled_policies": len([p for p in self.policies.values() if not p.enabled]),
            "total_rules": sum(len(p.rules) for p in self.policies.values()),
            "policies_by_priority": {},
            "policies": []
        }
        
        # Group by priority
        for policy in self.policies.values():
            priority = policy.priority
            if priority not in stats["policies_by_priority"]:
                stats["policies_by_priority"][priority] = 0
            stats["policies_by_priority"][priority] += 1
        
        # Policy details
        for name, policy in self.policies.items():
            stats["policies"].append({
                "name": name,
                "description": policy.description,
                "rules": len(policy.rules),
                "priority": policy.priority,
                "enabled": policy.enabled,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat()
            })
        
        return stats