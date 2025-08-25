# Enterprise Security Framework Documentation

## Overview

This document describes the enterprise-grade security framework implemented for the Oatie AI Reporting Platform. The framework provides comprehensive authentication, authorization, audit logging, threat detection, and compliance capabilities.

## Security Architecture

### Core Components

1. **SecurityManager** - Central security orchestrator
2. **MFAManager** - Multi-factor authentication handling
3. **RBACManager** - Role-based access control
4. **ABACManager** - Attribute-based access control
5. **Security Monitoring** - Real-time threat detection and analytics

## Multi-Factor Authentication (MFA)

### Supported Methods

- **TOTP (Time-based One-Time Password)** - Google Authenticator, Authy compatible
- **SMS** - Text message verification codes
- **Email** - Email-based verification codes
- **Biometric** - For future hardware token integration

### API Endpoints

```
POST /api/v1/auth/mfa/setup          # Setup MFA for user
POST /api/v1/auth/mfa/setup/verify   # Verify MFA setup
POST /api/v1/auth/mfa/challenge      # Initiate MFA challenge
POST /api/v1/auth/mfa/verify         # Verify MFA response
GET  /api/v1/auth/mfa/status         # Get MFA status
DELETE /api/v1/auth/mfa/disable      # Disable MFA
```

### Usage Example

```python
# Setup TOTP MFA
response = await client.post("/api/v1/auth/mfa/setup", json={
    "method": "totp",
    "contact_info": "user@example.com"
})

# Response includes QR code for authenticator app
qr_code = response.json()["qr_code"]
secret = response.json()["secret"]
backup_codes = response.json()["backup_codes"]
```

## Role-Based Access Control (RBAC)

### System Roles

- **super_admin** - Full system access
- **admin** - Administrative privileges
- **manager** - Team management capabilities
- **analyst** - Data analysis and reporting
- **viewer** - Read-only access

### Permissions

Permissions follow the format `resource:action`:

```
# User management
user:create, user:read, user:update, user:delete, user:list

# Report management
report:create, report:read, report:update, report:delete, report:export

# Data access levels
data:read:own, data:read:team, data:read:all
data:write:own, data:write:team, data:write:all

# Administration
admin:config, admin:users, admin:system, admin:audit, admin:security
```

### API Endpoints

```
GET    /api/v1/roles                    # List all roles
POST   /api/v1/roles                    # Create custom role
PUT    /api/v1/roles/{role_name}        # Update role
DELETE /api/v1/roles/{role_name}        # Delete role
POST   /api/v1/roles/users/assign-role  # Assign role to user
POST   /api/v1/roles/users/revoke-role  # Revoke role from user
GET    /api/v1/roles/users/{user_id}/permissions  # Get user permissions
```

### Usage Example

```python
# Create custom role
role_data = {
    "name": "custom_analyst",
    "description": "Custom analyst with specific permissions",
    "permissions": ["report:read", "report:create", "data:read:team"],
    "parent_roles": ["viewer"]
}
await client.post("/api/v1/roles", json=role_data)

# Assign role to user
await client.post("/api/v1/roles/users/assign-role", json={
    "user_id": "user_123",
    "role_name": "custom_analyst"
})
```

## Attribute-Based Access Control (ABAC)

### Policy Engine

ABAC policies provide fine-grained access control based on:

- **User attributes** - role, clearance level, department, location
- **Resource attributes** - sensitivity, classification, owner, team
- **Environment attributes** - time, location, network, device
- **Action attributes** - operation type, purpose

### Default Policies

1. **Admin Access Policy** - Administrators have full access during business hours
2. **Data Access Control** - Control based on data sensitivity and user clearance
3. **Time-based Access** - Restrict access based on time and day
4. **Geographic Access** - Control access based on user location
5. **Resource Ownership** - Users can access their own resources

### Policy Structure

```python
policy = Policy(
    name="sensitive_data_access",
    description="Control access to sensitive data",
    rules=[
        PolicyRule(
            name="high_clearance_access",
            effect=PolicyEffect.ALLOW,
            conditions=[
                Condition("resource.sensitivity", "eq", "high"),
                Condition("user.clearance_level", "gte", 3),
                Condition("environment.time", "gte", "08:00"),
                Condition("environment.time", "lte", "18:00")
            ]
        )
    ]
)
```

## Security Monitoring & Threat Detection

### Real-time Monitoring

The platform continuously monitors for:

- Failed login attempts
- Unusual access patterns
- Security policy violations
- Privilege escalations
- Data access anomalies

### Threat Detection

Advanced threat detection includes:

- **Brute force attack detection** - Multiple failed login attempts
- **Anomaly detection** - Unusual user behavior patterns
- **Risk scoring** - Dynamic risk assessment for users and actions
- **Behavioral analytics** - ML-based behavior profiling

### API Endpoints

```
GET  /api/v1/security/metrics           # Real-time security metrics
GET  /api/v1/security/alerts            # Active security alerts
GET  /api/v1/security/threat-detection/{user_id}  # User threat analysis
GET  /api/v1/security/user-activity     # User activity summary
GET  /api/v1/security/reports/security  # Security reports
POST /api/v1/security/alerts/{alert_id}/acknowledge  # Acknowledge alert
```

### Security Metrics

```python
metrics = {
    "total_events_24h": 1250,
    "failed_logins_24h": 15,
    "security_violations_24h": 3,
    "unique_users_24h": 45,
    "active_sessions": 23,
    "blocked_users": 2,
    "mfa_enabled_users": 38,
    "high_risk_events": 1
}
```

## Enhanced Authentication Flow

### Standard Login with MFA

```python
# 1. Initial login attempt
response = await client.post("/api/v1/auth/token", data={
    "username": "user@example.com",
    "password": "password123"
})

# 2. If MFA required, response includes challenge
if response.json().get("requires_mfa"):
    challenge_id = response.json()["challenge_id"]
    
    # 3. Complete login with MFA token
    response = await client.post("/api/v1/auth/token/mfa", json={
        "username": "user@example.com",
        "password": "password123",
        "mfa_token": "123456",
        "challenge_id": challenge_id
    })

# 4. Access token received
access_token = response.json()["access_token"]
```

### SSO Integration

```python
# Initiate SSO login
sso_response = await client.post("/api/v1/auth/sso/initiate")
redirect_url = sso_response.json()["redirect_url"]

# Redirect user to SSO provider
# After successful SSO, callback will create session
```

## Audit Logging & Compliance

### Audit Events

All security-relevant events are logged:

- Login/logout events
- Permission changes
- Data access
- System configuration changes
- Security violations

### Audit Event Structure

```python
audit_event = {
    "event_id": "abc123def456",
    "timestamp": "2024-08-25T17:37:00Z",
    "event_type": "LOGIN",
    "user_id": "user_123",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "resource": "user:profile",
    "details": {"mfa_verified": True},
    "severity": "LOW"
}
```

### Compliance Features

- **SOC 2 Type II** - System and Organization Controls
- **GDPR** - General Data Protection Regulation compliance
- **HIPAA** - Health Insurance Portability and Accountability Act
- **Data retention policies** - Configurable data retention
- **Right to be forgotten** - Data deletion capabilities

## Configuration

### Environment Variables

```bash
# MFA Configuration
MFA_REQUIRED_FOR_ADMINS=true
MFA_TOKEN_VALIDITY_MINUTES=5
TOTP_ISSUER_NAME="Oatie AI Reporting"

# Session Management
SESSION_TIMEOUT_HOURS=8
MAX_CONCURRENT_SESSIONS=5

# Account Security
MAX_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30
PASSWORD_MIN_LENGTH=8

# Security Monitoring
ENABLE_THREAT_DETECTION=true
COMPLIANCE_MODE=soc2
AUDIT_LOG_RETENTION_DAYS=365

# SSO Configuration
SSO_ENABLED=false
SAML_METADATA_URL=https://idp.example.com/metadata
OAUTH2_CLIENT_ID=your_client_id
OAUTH2_CLIENT_SECRET=your_client_secret
```

## Security Best Practices

### Implementation Guidelines

1. **Enable MFA** for all administrative accounts
2. **Use strong passwords** with complexity requirements
3. **Implement least privilege** principle for role assignments
4. **Monitor security events** and respond to alerts promptly
5. **Regular security reviews** of user permissions and policies
6. **Keep audit logs** for compliance and forensic analysis

### Production Deployment

1. **Use secure secrets management** (HashiCorp Vault, AWS Secrets Manager)
2. **Enable HTTPS** with strong SSL/TLS certificates
3. **Implement rate limiting** at the application and network level
4. **Use dedicated audit database** for audit log storage
5. **Set up security monitoring** with SIEM integration
6. **Regular security testing** including penetration testing

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/token` | Login with username/password |
| POST | `/api/v1/auth/token/mfa` | Complete MFA login |
| POST | `/api/v1/auth/logout` | Logout and invalidate session |
| GET | `/api/v1/auth/me` | Get current user info |
| GET | `/api/v1/auth/sessions` | Get active sessions |
| DELETE | `/api/v1/auth/sessions/{id}` | Terminate specific session |

### MFA Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/mfa/setup` | Setup MFA for user |
| POST | `/api/v1/auth/mfa/setup/verify` | Verify MFA setup |
| POST | `/api/v1/auth/mfa/challenge` | Initiate MFA challenge |
| POST | `/api/v1/auth/mfa/verify` | Verify MFA response |
| GET | `/api/v1/auth/mfa/status` | Get MFA status |
| DELETE | `/api/v1/auth/mfa/disable` | Disable MFA |

### Role Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/roles` | List all roles |
| POST | `/api/v1/roles` | Create custom role |
| PUT | `/api/v1/roles/{name}` | Update role |
| DELETE | `/api/v1/roles/{name}` | Delete role |
| POST | `/api/v1/roles/users/assign-role` | Assign role to user |
| POST | `/api/v1/roles/users/revoke-role` | Revoke role from user |

### Security Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/security/metrics` | Security metrics |
| GET | `/api/v1/security/alerts` | Security alerts |
| GET | `/api/v1/security/threat-detection/{user_id}` | Threat analysis |
| GET | `/api/v1/security/user-activity` | User activity summary |
| GET | `/api/v1/security/reports/security` | Security reports |

## Support & Troubleshooting

### Common Issues

1. **MFA Setup Fails** - Check QR code generation and TOTP secret validation
2. **Permission Denied** - Verify user roles and RBAC/ABAC policies
3. **Session Timeout** - Check session configuration and cleanup intervals
4. **Audit Log Storage** - Ensure adequate database storage for audit events

### Debugging

Enable debug logging for security components:

```python
import structlog
logger = structlog.get_logger("security")
logger.debug("Security event details", event_type="login", user_id="user_123")
```

### Performance Considerations

- **Cache user permissions** to reduce database queries
- **Use Redis for session storage** in distributed environments
- **Implement audit log archiving** for long-term retention
- **Optimize ABAC policy evaluation** for high-throughput scenarios

## Roadmap

### Future Enhancements

- [ ] Hardware security key support (WebAuthn/FIDO2)
- [ ] Advanced behavioral analytics with ML models
- [ ] Integration with external SIEM systems
- [ ] Automated compliance reporting
- [ ] Zero-trust network architecture
- [ ] Advanced threat intelligence integration

---

For technical support or security questions, please contact the security team or create an issue in the repository.