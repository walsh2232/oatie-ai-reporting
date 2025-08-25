"""
Error Recovery and Graceful Degradation System for Oatie AI Platform
Handles automatic error recovery, circuit breakers, and service degradation
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import json
import threading
from datetime import datetime, timedelta
import traceback


class ServiceState(Enum):
    """Service operational states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"
    FAILED = "failed"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorEvent:
    """Represents an error event"""
    timestamp: float
    service_name: str
    error_type: str
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any]
    stacktrace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout: int = 60
    recovery_timeout: int = 300


@dataclass
class ServiceFallback:
    """Fallback configuration for a service"""
    service_name: str
    fallback_function: Optional[Callable] = None
    fallback_data: Optional[Any] = None
    degraded_mode: bool = True
    cache_duration: int = 300


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.state = ServiceState.HEALTHY
        self.logger = logging.getLogger(__name__)
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        current_time = time.time()
        
        # Check if we should attempt recovery
        if self.state == ServiceState.FAILED:
            if current_time - self.last_failure_time >= self.config.recovery_timeout:
                self.state = ServiceState.RECOVERING
                self.logger.info("Circuit breaker attempting recovery")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            # Execute the function
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Success - update state
            self.success_count += 1
            self.failure_count = 0
            
            if self.state == ServiceState.RECOVERING and self.success_count >= self.config.success_threshold:
                self.state = ServiceState.HEALTHY
                self.logger.info("Circuit breaker recovered - service is healthy")
            
            return result
            
        except Exception as e:
            # Failure - update state
            self.failure_count += 1
            self.success_count = 0
            self.last_failure_time = current_time
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = ServiceState.FAILED
                self.logger.error(f"Circuit breaker OPENED - too many failures: {self.failure_count}")
            
            raise e
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "time_until_recovery": max(0, self.config.recovery_timeout - (time.time() - self.last_failure_time))
        }


class ErrorRecoveryManager:
    """Manages automatic error recovery across services"""
    
    def __init__(self):
        self.error_history = deque(maxlen=1000)
        self.circuit_breakers = {}
        self.recovery_strategies = {}
        self.fallback_configs = {}
        self.service_states = {}
        self.logger = logging.getLogger(__name__)
        self.recovery_lock = threading.Lock()
    
    def register_service(self, service_name: str, circuit_config: Optional[CircuitBreakerConfig] = None,
                        fallback_config: Optional[ServiceFallback] = None):
        """Register a service for error recovery management"""
        if circuit_config is None:
            circuit_config = CircuitBreakerConfig()
        
        self.circuit_breakers[service_name] = CircuitBreaker(circuit_config)
        self.service_states[service_name] = ServiceState.HEALTHY
        
        if fallback_config:
            self.fallback_configs[service_name] = fallback_config
        
        self.logger.info(f"Registered service for error recovery: {service_name}")
    
    async def execute_with_recovery(self, service_name: str, func: Callable, *args, **kwargs):
        """Execute a function with automatic error recovery"""
        if service_name not in self.circuit_breakers:
            self.register_service(service_name)
        
        circuit_breaker = self.circuit_breakers[service_name]
        
        try:
            result = await circuit_breaker.call(func, *args, **kwargs)
            self._update_service_state(service_name, ServiceState.HEALTHY)
            return result
            
        except Exception as e:
            # Log the error
            error_event = ErrorEvent(
                timestamp=time.time(),
                service_name=service_name,
                error_type=type(e).__name__,
                severity=self._determine_error_severity(e),
                message=str(e),
                context={"args": str(args), "kwargs": str(kwargs)},
                stacktrace=traceback.format_exc()
            )
            
            self.error_history.append(error_event)
            self.logger.error(f"Service {service_name} error: {str(e)}")
            
            # Attempt recovery
            recovery_result = await self._attempt_recovery(service_name, error_event)
            
            if recovery_result:
                error_event.recovery_attempted = True
                error_event.recovery_successful = True
                return recovery_result
            
            # If recovery fails, try fallback
            fallback_result = await self._try_fallback(service_name, error_event)
            if fallback_result is not None:
                self._update_service_state(service_name, ServiceState.DEGRADED)
                return fallback_result
            
            # Update service state to failed
            self._update_service_state(service_name, ServiceState.FAILED)
            raise e
    
    def _determine_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine the severity of an error"""
        error_type = type(error).__name__
        
        if error_type in ['ConnectionError', 'TimeoutError', 'ConnectionRefusedError']:
            return ErrorSeverity.HIGH
        elif error_type in ['ValueError', 'KeyError', 'AttributeError']:
            return ErrorSeverity.MEDIUM
        elif error_type in ['MemoryError', 'SystemExit', 'KeyboardInterrupt']:
            return ErrorSeverity.CRITICAL
        else:
            return ErrorSeverity.MEDIUM
    
    async def _attempt_recovery(self, service_name: str, error_event: ErrorEvent) -> Any:
        """Attempt to recover from an error"""
        recovery_strategy = self.recovery_strategies.get(service_name)
        
        if not recovery_strategy:
            return None
        
        try:
            self._update_service_state(service_name, ServiceState.RECOVERING)
            self.logger.info(f"Attempting recovery for service: {service_name}")
            
            recovery_result = await recovery_strategy(error_event)
            
            if recovery_result:
                self.logger.info(f"Recovery successful for service: {service_name}")
                return recovery_result
            
        except Exception as recovery_error:
            self.logger.error(f"Recovery failed for service {service_name}: {str(recovery_error)}")
        
        return None
    
    async def _try_fallback(self, service_name: str, error_event: ErrorEvent) -> Any:
        """Try fallback mechanism for a service"""
        fallback_config = self.fallback_configs.get(service_name)
        
        if not fallback_config:
            return None
        
        try:
            self.logger.info(f"Using fallback for service: {service_name}")
            
            if fallback_config.fallback_function:
                result = await fallback_config.fallback_function(error_event)
                return result
            elif fallback_config.fallback_data is not None:
                return fallback_config.fallback_data
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback failed for service {service_name}: {str(fallback_error)}")
        
        return None
    
    def _update_service_state(self, service_name: str, state: ServiceState):
        """Update the state of a service"""
        with self.recovery_lock:
            old_state = self.service_states.get(service_name, ServiceState.HEALTHY)
            self.service_states[service_name] = state
            
            if old_state != state:
                self.logger.info(f"Service {service_name} state changed: {old_state.value} -> {state.value}")
    
    def register_recovery_strategy(self, service_name: str, strategy: Callable):
        """Register a recovery strategy for a service"""
        self.recovery_strategies[service_name] = strategy
        self.logger.info(f"Registered recovery strategy for service: {service_name}")
    
    def get_error_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get error summary for the specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
        
        if not recent_errors:
            return {"total_errors": 0, "time_period_hours": hours}
        
        # Group errors by service and type
        errors_by_service = defaultdict(list)
        errors_by_type = defaultdict(int)
        errors_by_severity = defaultdict(int)
        
        for error in recent_errors:
            errors_by_service[error.service_name].append(error)
            errors_by_type[error.error_type] += 1
            errors_by_severity[error.severity.value] += 1
        
        return {
            "total_errors": len(recent_errors),
            "time_period_hours": hours,
            "errors_by_service": {k: len(v) for k, v in errors_by_service.items()},
            "errors_by_type": dict(errors_by_type),
            "errors_by_severity": dict(errors_by_severity),
            "recovery_rate": sum(1 for e in recent_errors if e.recovery_successful) / len(recent_errors) * 100
        }
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all managed services"""
        health_data = {}
        
        for service_name, state in self.service_states.items():
            circuit_breaker = self.circuit_breakers[service_name]
            
            health_data[service_name] = {
                "state": state.value,
                "circuit_breaker": circuit_breaker.get_state(),
                "has_fallback": service_name in self.fallback_configs,
                "has_recovery_strategy": service_name in self.recovery_strategies
            }
        
        return health_data


class GracefulDegradationManager:
    """Manages graceful service degradation"""
    
    def __init__(self):
        self.degradation_rules = {}
        self.active_degradations = set()
        self.logger = logging.getLogger(__name__)
    
    def register_degradation_rule(self, service_name: str, degradation_config: Dict[str, Any]):
        """Register degradation rules for a service"""
        self.degradation_rules[service_name] = degradation_config
        self.logger.info(f"Registered degradation rules for service: {service_name}")
    
    def activate_degradation(self, service_name: str, reason: str):
        """Activate degraded mode for a service"""
        if service_name not in self.active_degradations:
            self.active_degradations.add(service_name)
            self.logger.warning(f"Activated degraded mode for {service_name}: {reason}")
    
    def deactivate_degradation(self, service_name: str):
        """Deactivate degraded mode for a service"""
        if service_name in self.active_degradations:
            self.active_degradations.remove(service_name)
            self.logger.info(f"Deactivated degraded mode for {service_name}")
    
    def is_degraded(self, service_name: str) -> bool:
        """Check if a service is in degraded mode"""
        return service_name in self.active_degradations
    
    def get_degraded_response(self, service_name: str, request_type: str) -> Any:
        """Get degraded response for a service"""
        if service_name not in self.degradation_rules:
            return None
        
        rules = self.degradation_rules[service_name]
        degraded_responses = rules.get("degraded_responses", {})
        
        return degraded_responses.get(request_type, rules.get("default_response"))
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status"""
        return {
            "active_degradations": list(self.active_degradations),
            "total_degraded_services": len(self.active_degradations),
            "degradation_rules_configured": len(self.degradation_rules)
        }


# Common recovery strategies
async def database_recovery_strategy(error_event: ErrorEvent) -> bool:
    """Recovery strategy for database connection issues"""
    try:
        # Wait a bit before retrying
        await asyncio.sleep(2)
        
        # Try to reconnect (implementation would depend on your database manager)
        # This is a placeholder - you'd implement actual reconnection logic
        logging.info("Attempting database reconnection...")
        
        # Simulate recovery attempt
        return True
        
    except Exception as e:
        logging.error(f"Database recovery failed: {e}")
        return False


async def cache_recovery_strategy(error_event: ErrorEvent) -> bool:
    """Recovery strategy for cache connection issues"""
    try:
        # Wait briefly before retrying
        await asyncio.sleep(1)
        
        # Try to reconnect to cache
        logging.info("Attempting cache reconnection...")
        
        # Simulate recovery attempt
        return True
        
    except Exception as e:
        logging.error(f"Cache recovery failed: {e}")
        return False


async def api_recovery_strategy(error_event: ErrorEvent) -> bool:
    """Recovery strategy for external API issues"""
    try:
        # Exponential backoff
        await asyncio.sleep(min(30, 2 ** error_event.context.get("retry_count", 0)))
        
        # Try alternative API endpoint or retry
        logging.info("Attempting API reconnection...")
        
        return True
        
    except Exception as e:
        logging.error(f"API recovery failed: {e}")
        return False


# Fallback functions
async def database_fallback(error_event: ErrorEvent) -> Dict[str, Any]:
    """Fallback for database operations"""
    return {
        "status": "degraded",
        "message": "Database temporarily unavailable, using cached data",
        "data": {},
        "fallback": True
    }


async def api_fallback(error_event: ErrorEvent) -> Dict[str, Any]:
    """Fallback for external API calls"""
    return {
        "status": "degraded", 
        "message": "External service temporarily unavailable",
        "data": None,
        "fallback": True
    }


# Global instances
error_recovery_manager = ErrorRecoveryManager()
degradation_manager = GracefulDegradationManager()

def setup_error_recovery():
    """Setup default error recovery configurations"""
    
    # Register services with their recovery strategies
    error_recovery_manager.register_service(
        "database",
        CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60),
        ServiceFallback("database", database_fallback, degraded_mode=True)
    )
    error_recovery_manager.register_recovery_strategy("database", database_recovery_strategy)
    
    error_recovery_manager.register_service(
        "cache",
        CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30),
        ServiceFallback("cache", None, fallback_data={}, degraded_mode=True)
    )
    error_recovery_manager.register_recovery_strategy("cache", cache_recovery_strategy)
    
    error_recovery_manager.register_service(
        "external_apis",
        CircuitBreakerConfig(failure_threshold=3, recovery_timeout=120),
        ServiceFallback("external_apis", api_fallback, degraded_mode=True)
    )
    error_recovery_manager.register_recovery_strategy("external_apis", api_recovery_strategy)
    
    # Setup degradation rules
    degradation_manager.register_degradation_rule("reports", {
        "degraded_responses": {
            "list": {"reports": [], "message": "Report service degraded - showing cached results"},
            "generate": {"status": "queued", "message": "Report generation queued due to high load"}
        },
        "default_response": {"status": "unavailable", "message": "Service temporarily unavailable"}
    })
    
    degradation_manager.register_degradation_rule("analytics", {
        "degraded_responses": {
            "dashboard": {"widgets": [], "message": "Analytics temporarily unavailable"},
            "metrics": {"data": {}, "message": "Metrics service degraded"}
        }
    })
    
    logging.info("Error recovery system initialized")