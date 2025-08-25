"""
Security monitoring and analytics endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel

from backend.core.security import SecurityManager, AuditEventType
from backend.core.rbac import Permission
from backend.api.v1.endpoints.auth import oauth2_scheme

router = APIRouter()


class SecurityAlert(BaseModel):
    id: str
    type: str
    severity: str
    title: str
    description: str
    user_id: Optional[str] = None
    resource: Optional[str] = None
    timestamp: str
    status: str = "active"
    metadata: Dict[str, Any] = {}


class SecurityMetrics(BaseModel):
    total_events_24h: int
    failed_logins_24h: int
    security_violations_24h: int
    unique_users_24h: int
    active_sessions: int
    blocked_users: int
    mfa_enabled_users: int
    high_risk_events: int


class ThreatDetectionResult(BaseModel):
    threat_detected: bool
    threat_type: Optional[str] = None
    risk_score: float
    user_id: str
    indicators: List[str] = []
    recommended_actions: List[str] = []
    timestamp: str


class UserActivitySummary(BaseModel):
    user_id: str
    username: str
    login_count_24h: int
    failed_login_count_24h: int
    last_login: Optional[str] = None
    risk_score: float
    unusual_activity: List[str] = []
    mfa_enabled: bool


class SecurityReport(BaseModel):
    report_id: str
    type: str
    generated_at: str
    period: str
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_status: Dict[str, Any]


# === Security Monitoring Endpoints ===

@router.get("/metrics", response_model=SecurityMetrics)
async def get_security_metrics(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    """Get real-time security metrics"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify security admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_SECURITY)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security admin access required")
    
    try:
        # Generate security report to get metrics
        report = await security_manager.generate_security_report()
        
        # Count different metrics
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        
        recent_events = [
            log for log in security_manager.audit_logs
            if datetime.fromisoformat(log["timestamp"]) > last_24h
        ]
        
        failed_logins = len([
            log for log in recent_events
            if log["event_type"] == AuditEventType.LOGIN_FAILED.value
        ])
        
        security_violations = len([
            log for log in recent_events
            if log["event_type"] == AuditEventType.SECURITY_VIOLATION.value
        ])
        
        unique_users = len(set(
            log.get("user_id") for log in recent_events 
            if log.get("user_id")
        ))
        
        active_sessions = len(await security_manager.get_active_sessions())
        blocked_users = len(security_manager.blocked_users)
        
        # Estimate MFA-enabled users (in production, query from database)
        mfa_enabled_users = len(security_manager.mfa_manager.user_mfa_configs)
        
        high_risk_events = len([
            log for log in recent_events
            if log.get("severity") == "HIGH"
        ])
        
        return SecurityMetrics(
            total_events_24h=len(recent_events),
            failed_logins_24h=failed_logins,
            security_violations_24h=security_violations,
            unique_users_24h=unique_users,
            active_sessions=active_sessions,
            blocked_users=blocked_users,
            mfa_enabled_users=mfa_enabled_users,
            high_risk_events=high_risk_events
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security metrics: {str(e)}"
        )


@router.get("/alerts", response_model=List[SecurityAlert])
async def get_security_alerts(
    request: Request,
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    limit: int = Query(50, description="Maximum number of alerts to return"),
    token: str = Depends(oauth2_scheme)
):
    """Get active security alerts"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify security admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_SECURITY)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security admin access required")
    
    try:
        alerts = []
        
        # Generate alerts from recent security violations
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        
        violations = [
            log for log in security_manager.audit_logs
            if (log["event_type"] == AuditEventType.SECURITY_VIOLATION.value and
                datetime.fromisoformat(log["timestamp"]) > last_24h)
        ]
        
        for violation in violations:
            alert_severity = violation.get("severity", "MEDIUM").lower()
            
            if severity and alert_severity != severity.lower():
                continue
            
            details = violation.get("details", {})
            
            if details.get("rate_limit_exceeded"):
                alert = SecurityAlert(
                    id=violation["event_id"],
                    type="rate_limit_violation",
                    severity=alert_severity,
                    title="Rate Limit Exceeded",
                    description=f"User {violation.get('user_id', 'unknown')} exceeded rate limit",
                    user_id=violation.get("user_id"),
                    timestamp=violation["timestamp"],
                    metadata=details
                )
            elif details.get("invalid_token"):
                alert = SecurityAlert(
                    id=violation["event_id"],
                    type="invalid_token",
                    severity=alert_severity,
                    title="Invalid Token Access Attempt",
                    description="Attempt to access system with invalid token",
                    timestamp=violation["timestamp"],
                    metadata=details
                )
            elif details.get("too_many_failed_attempts"):
                alert = SecurityAlert(
                    id=violation["event_id"],
                    type="brute_force",
                    severity="high",
                    title="Potential Brute Force Attack",
                    description=f"User {details.get('username', 'unknown')} blocked due to repeated failed login attempts",
                    timestamp=violation["timestamp"],
                    metadata=details
                )
            else:
                alert = SecurityAlert(
                    id=violation["event_id"],
                    type="security_violation",
                    severity=alert_severity,
                    title="Security Violation Detected",
                    description="Unspecified security violation detected",
                    user_id=violation.get("user_id"),
                    timestamp=violation["timestamp"],
                    metadata=details
                )
            
            alerts.append(alert)
        
        # Sort by timestamp (newest first) and limit
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return alerts[:limit]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security alerts: {str(e)}"
        )


@router.get("/threat-detection/{user_id}", response_model=ThreatDetectionResult)
async def analyze_user_threats(
    request: Request,
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Analyze potential threats for a specific user"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify security admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    admin_user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(admin_user_id, Permission.ADMIN_SECURITY)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security admin access required")
    
    try:
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        last_7d = current_time - timedelta(days=7)
        
        # Get user's recent activities
        user_events = [
            log for log in security_manager.audit_logs
            if log.get("user_id") == user_id and datetime.fromisoformat(log["timestamp"]) > last_7d
        ]
        
        # Analyze threat indicators
        threat_indicators = []
        risk_score = 0.0
        
        # Check for multiple failed logins
        failed_logins_24h = len([
            log for log in user_events
            if (log["event_type"] == AuditEventType.LOGIN_FAILED.value and
                datetime.fromisoformat(log["timestamp"]) > last_24h)
        ])
        
        if failed_logins_24h > 5:
            threat_indicators.append("High number of failed login attempts in 24h")
            risk_score += 0.3
        
        # Check for security violations
        violations = [
            log for log in user_events
            if log["event_type"] == AuditEventType.SECURITY_VIOLATION.value
        ]
        
        if len(violations) > 3:
            threat_indicators.append("Multiple security violations detected")
            risk_score += 0.4
        
        # Check for unusual access patterns
        login_hours = []
        for log in user_events:
            if log["event_type"] == AuditEventType.LOGIN.value:
                timestamp = datetime.fromisoformat(log["timestamp"])
                login_hours.append(timestamp.hour)
        
        # Check for logins outside business hours (9 AM - 6 PM)
        unusual_hours = [hour for hour in login_hours if hour < 9 or hour > 18]
        if len(unusual_hours) > len(login_hours) * 0.5:  # More than 50% outside business hours
            threat_indicators.append("Frequent access outside business hours")
            risk_score += 0.2
        
        # Check if MFA is disabled on a high-privilege account
        user_roles = await security_manager.rbac_manager.get_user_roles(user_id)
        has_admin_role = any(role in ["admin", "super_admin"] for role in user_roles)
        mfa_enabled = await security_manager.is_mfa_enabled(user_id)
        
        if has_admin_role and not mfa_enabled:
            threat_indicators.append("Administrative account without MFA enabled")
            risk_score += 0.5
        
        # Generate recommendations
        recommendations = []
        if failed_logins_24h > 5:
            recommendations.append("Consider temporarily blocking account or requiring password reset")
        if len(violations) > 3:
            recommendations.append("Review user access permissions and audit recent activities")
        if has_admin_role and not mfa_enabled:
            recommendations.append("Enforce MFA for administrative accounts")
        if not recommendations:
            recommendations.append("Continue monitoring user activity")
        
        threat_detected = risk_score > 0.5
        threat_type = None
        if threat_detected:
            if failed_logins_24h > 10:
                threat_type = "brute_force_attack"
            elif len(violations) > 5:
                threat_type = "suspicious_activity"
            else:
                threat_type = "elevated_risk"
        
        return ThreatDetectionResult(
            threat_detected=threat_detected,
            threat_type=threat_type,
            risk_score=min(risk_score, 1.0),  # Cap at 1.0
            user_id=user_id,
            indicators=threat_indicators,
            recommended_actions=recommendations,
            timestamp=current_time.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze user threats: {str(e)}"
        )


@router.get("/user-activity", response_model=List[UserActivitySummary])
async def get_user_activity_summary(
    request: Request,
    limit: int = Query(20, description="Maximum number of users to return"),
    risk_threshold: float = Query(0.0, description="Minimum risk score to include"),
    token: str = Depends(oauth2_scheme)
):
    """Get user activity summary with risk analysis"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify security admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_SECURITY)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security admin access required")
    
    try:
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        
        # Get all users with recent activity
        recent_events = [
            log for log in security_manager.audit_logs
            if datetime.fromisoformat(log["timestamp"]) > last_24h and log.get("user_id")
        ]
        
        user_activities = {}
        
        for log in recent_events:
            user_id_log = log["user_id"]
            
            if user_id_log not in user_activities:
                user_activities[user_id_log] = {
                    "login_count": 0,
                    "failed_login_count": 0,
                    "last_login": None,
                    "unusual_activity": []
                }
            
            activity = user_activities[user_id_log]
            
            if log["event_type"] == AuditEventType.LOGIN.value:
                activity["login_count"] += 1
                if not activity["last_login"] or log["timestamp"] > activity["last_login"]:
                    activity["last_login"] = log["timestamp"]
            elif log["event_type"] == AuditEventType.LOGIN_FAILED.value:
                activity["failed_login_count"] += 1
            elif log["event_type"] == AuditEventType.SECURITY_VIOLATION.value:
                activity["unusual_activity"].append("Security violation detected")
        
        # Generate summaries
        summaries = []
        
        for user_id_activity, activity in user_activities.items():
            # Calculate risk score
            risk_score = 0.0
            
            if activity["failed_login_count"] > 3:
                risk_score += 0.3
            if activity["failed_login_count"] > activity["login_count"]:
                risk_score += 0.2
            if len(activity["unusual_activity"]) > 0:
                risk_score += 0.2 * len(activity["unusual_activity"])
            
            risk_score = min(risk_score, 1.0)
            
            if risk_score < risk_threshold:
                continue
            
            # Check MFA status
            mfa_enabled = await security_manager.is_mfa_enabled(user_id_activity)
            
            summary = UserActivitySummary(
                user_id=user_id_activity,
                username=f"user_{user_id_activity[-6:]}",  # Mock username
                login_count_24h=activity["login_count"],
                failed_login_count_24h=activity["failed_login_count"],
                last_login=activity["last_login"],
                risk_score=risk_score,
                unusual_activity=activity["unusual_activity"],
                mfa_enabled=mfa_enabled
            )
            
            summaries.append(summary)
        
        # Sort by risk score (highest first) and limit
        summaries.sort(key=lambda x: x.risk_score, reverse=True)
        return summaries[:limit]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity summary: {str(e)}"
        )


@router.get("/reports/security", response_model=SecurityReport)
async def generate_security_report(
    request: Request,
    report_type: str = Query("comprehensive", description="Type of report: comprehensive, compliance, threats"),
    period: str = Query("24h", description="Time period: 24h, 7d, 30d"),
    token: str = Depends(oauth2_scheme)
):
    """Generate comprehensive security report"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify security admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_SECURITY)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security admin access required")
    
    try:
        import secrets
        report_id = secrets.token_hex(8)
        current_time = datetime.utcnow()
        
        # Get base security report
        base_report = await security_manager.generate_security_report()
        
        # Generate findings based on report type
        findings = []
        compliance_status = {}
        
        if report_type == "comprehensive":
            findings.extend([
                {
                    "id": "finding_001",
                    "category": "authentication",
                    "severity": "medium",
                    "title": "MFA Adoption Rate",
                    "description": f"Currently {len(security_manager.mfa_manager.user_mfa_configs)} users have MFA enabled",
                    "recommendation": "Encourage or enforce MFA for all users"
                },
                {
                    "id": "finding_002",
                    "category": "access_control",
                    "severity": "low",
                    "title": "Role Distribution",
                    "description": f"Total of {len(security_manager.rbac_manager.roles)} roles configured",
                    "recommendation": "Review role permissions periodically"
                }
            ])
            
            compliance_status = {
                "soc2": "in_progress",
                "gdpr": "compliant",
                "hipaa": "not_applicable",
                "pci_dss": "not_applicable"
            }
        
        elif report_type == "compliance":
            compliance_status = {
                "soc2": {
                    "status": "in_progress",
                    "controls_implemented": 75,
                    "controls_total": 100,
                    "gaps": [
                        "Automated backup verification",
                        "Incident response automation"
                    ]
                },
                "gdpr": {
                    "status": "compliant",
                    "data_retention_policy": "implemented",
                    "right_to_be_forgotten": "implemented",
                    "data_encryption": "implemented"
                }
            }
            
            findings.append({
                "id": "compliance_001",
                "category": "compliance",
                "severity": "medium",
                "title": "SOC 2 Gap Analysis",
                "description": "25% of controls still need implementation",
                "recommendation": "Prioritize automated backup verification and incident response"
            })
        
        elif report_type == "threats":
            # Analyze threats from recent events
            threat_count = len([
                log for log in security_manager.audit_logs
                if log.get("severity") == "HIGH"
            ])
            
            findings.append({
                "id": "threat_001",
                "category": "threats",
                "severity": "high" if threat_count > 10 else "low",
                "title": "High-Severity Security Events",
                "description": f"Detected {threat_count} high-severity security events",
                "recommendation": "Investigate high-severity events and implement additional monitoring"
            })
        
        return SecurityReport(
            report_id=report_id,
            type=report_type,
            generated_at=current_time.isoformat(),
            period=period,
            summary=base_report,
            findings=findings,
            recommendations=base_report.get("recommendations", []),
            compliance_status=compliance_status
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate security report: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    request: Request,
    alert_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Acknowledge a security alert"""
    security_manager: SecurityManager = request.app.state.security_manager
    
    # Verify security admin permission
    payload = await security_manager.verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    has_permission = await security_manager.check_permission(user_id, Permission.ADMIN_SECURITY)
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security admin access required")
    
    try:
        # Log the acknowledgment
        await security_manager.log_audit_event(
            AuditEventType.SYSTEM_ACCESS,
            user_id=user_id,
            details={"alert_acknowledged": alert_id, "acknowledged_by": user_id}
        )
        
        return {"message": f"Alert {alert_id} acknowledged successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )