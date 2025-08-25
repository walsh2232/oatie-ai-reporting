"""
Enterprise configuration management with environment-based settings
Supports multi-environment deployments and security best practices
"""

from functools import lru_cache
from typing import List, Optional, Dict
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with enterprise security and performance configuration"""
    
    # Application
    app_name: str = "Oatie AI Reporting Platform"
    version: str = "3.0.0"
    debug: bool = False
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: str = Field(default="postgresql+asyncpg://postgres:password@localhost/oatie", description="PostgreSQL connection URL")
    database_pool_size: int = 20
    database_max_overflow: int = 30
    database_pool_timeout: int = 30
    
    # Redis Cache
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    redis_cluster_mode: bool = False
    cache_ttl_default: int = 3600  # 1 hour
    cache_ttl_reports: int = 1800  # 30 minutes
    cache_ttl_queries: int = 7200  # 2 hours
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # SSO Configuration
    sso_enabled: bool = False
    saml_metadata_url: Optional[str] = None
    oauth2_client_id: Optional[str] = None
    oauth2_client_secret: Optional[str] = None
    active_directory_domain: Optional[str] = None
    
    # Multi-Factor Authentication
    mfa_required_for_admins: bool = True
    mfa_token_validity_minutes: int = 5
    mfa_backup_codes_count: int = 10
    totp_issuer_name: str = "Oatie AI Reporting"
    
    # Session Management
    session_timeout_hours: int = 8
    max_concurrent_sessions: int = 5
    session_cleanup_interval_minutes: int = 30
    
    # Account Security
    max_failed_login_attempts: int = 5
    account_lockout_duration_minutes: int = 30
    password_min_length: int = 8
    password_require_special_chars: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    
    # Encryption
    encryption_key: str = Field(default="your-encryption-key-32-chars-long", description="Data encryption key")
    encryption_algorithm: str = "AES-256-GCM"
    
    # Security Monitoring
    enable_threat_detection: bool = True
    security_alert_thresholds: Dict[str, int] = {
        "failed_logins_24h": 10,
        "security_violations_24h": 5,
        "high_risk_events_24h": 3
    }
    
    # Compliance
    audit_log_retention_days: int = 365
    compliance_mode: str = "soc2"  # soc2, gdpr, hipaa, pci_dss
    data_classification_enabled: bool = True
    
    # CORS and Security Headers
    cors_origins: List[str] = ["http://localhost:3000", "https://app.oatie.com"]
    allowed_hosts: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    
    # Monitoring and Observability
    monitoring_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    log_level: str = "INFO"
    
    # Oracle BI Publisher Integration
    oracle_bi_enabled: bool = False
    oracle_bi_urls: List[str] = Field(default=[], description="List of Oracle BI Publisher server URLs for load balancing")
    oracle_bi_username: Optional[str] = None
    oracle_bi_password: Optional[str] = None
    oracle_bi_timeout: int = 30
    oracle_bi_pool_size: int = 50
    oracle_bi_max_connections: int = 100
    oracle_bi_cache_ttl: int = 300  # 5 minutes
    oracle_bi_enable_audit: bool = True
    
    # Oracle Identity Cloud Service (IDCS) Integration
    oracle_idcs_enabled: bool = False
    oracle_idcs_tenant: Optional[str] = None
    oracle_idcs_client_id: Optional[str] = None
    oracle_idcs_client_secret: Optional[str] = None
    oracle_idcs_scope: str = "urn:opc:idm:__myscopes__"
    
    # Oracle SSO Configuration
    oracle_sso_enabled: bool = False
    oracle_saml_metadata_url: Optional[str] = None
    oracle_saml_entity_id: Optional[str] = None
    oracle_oidc_discovery_url: Optional[str] = None
    
    # Performance Optimization
    async_workers: int = 4
    connection_pool_size: int = 100
    query_timeout: int = 30
    max_query_complexity: int = 1000
    
    # CDN Configuration
    cdn_enabled: bool = False
    cdn_base_url: Optional[str] = None
    static_files_cache_ttl: int = 86400  # 24 hours
    
    # Webhooks
    webhook_signing_secret: str = Field(default="webhook-secret-change-in-production", description="Webhook signature secret")
    webhook_timeout: int = 30
    webhook_retry_attempts: int = 3
    
    # Background Tasks
    celery_broker_url: str = Field(default="redis://localhost:6379/1", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", description="Celery result backend URL")
    
    @validator('cors_origins', pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator('allowed_hosts', pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()