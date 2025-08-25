"""
Environment Management Module for Oatie AI Platform
Handles automatic environment detection, configuration switching, and secrets management
"""

import os
import sys
import json
import platform
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import subprocess
from urllib.parse import urlparse


class EnvironmentType(Enum):
    """Supported environment types"""
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CODESPACES = "codespaces"
    CLOUD = "cloud"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    HEROKU = "heroku"
    RAILWAY = "railway"
    VERCEL = "vercel"
    DIGITALOCEAN = "digitalocean"
    UNKNOWN = "unknown"


@dataclass
class EnvironmentConfig:
    """Environment configuration data"""
    environment_type: EnvironmentType
    cloud_provider: Optional[CloudProvider] = None
    platform: str = ""
    is_containerized: bool = False
    is_kubernetes: bool = False
    supports_ssl: bool = False
    debug_enabled: bool = False
    auto_restart: bool = True
    monitoring_enabled: bool = True
    secrets_backend: str = "env"
    config_overrides: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config_overrides is None:
            self.config_overrides = {}


class EnvironmentDetector:
    """Detects current environment and platform"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_environment_type(self) -> EnvironmentType:
        """Detect the current environment type"""
        
        # Check for explicit environment variable
        env_type = os.environ.get('ENVIRONMENT', '').lower()
        if env_type in [e.value for e in EnvironmentType]:
            return EnvironmentType(env_type)
        
        # Check for specific environments
        if os.environ.get('CODESPACES') == 'true':
            return EnvironmentType.CODESPACES
        
        if os.path.exists('/var/run/secrets/kubernetes.io'):
            return EnvironmentType.KUBERNETES
        
        if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
            return EnvironmentType.DOCKER
        
        # Check for cloud environments
        if self._is_cloud_environment():
            return EnvironmentType.CLOUD
        
        # Check for common environment indicators
        if os.environ.get('NODE_ENV') == 'production' or os.environ.get('DEBUG') == 'false':
            return EnvironmentType.PRODUCTION
        
        if os.environ.get('NODE_ENV') in ['staging', 'test']:
            return EnvironmentType.STAGING
        
        if os.environ.get('DEBUG') == 'true' or os.environ.get('NODE_ENV') == 'development':
            return EnvironmentType.DEVELOPMENT
        
        # Default to local
        return EnvironmentType.LOCAL
    
    def detect_cloud_provider(self) -> CloudProvider:
        """Detect the cloud provider"""
        
        # AWS
        if any(os.environ.get(var) for var in ['AWS_REGION', 'AWS_LAMBDA_FUNCTION_NAME', 'AWS_EXECUTION_ENV']):
            return CloudProvider.AWS
        
        # Google Cloud
        if any(os.environ.get(var) for var in ['GOOGLE_CLOUD_PROJECT', 'GCLOUD_PROJECT', 'GCP_PROJECT']):
            return CloudProvider.GOOGLE_CLOUD
        
        # Azure
        if any(os.environ.get(var) for var in ['AZURE_RESOURCE_GROUP', 'WEBSITE_SITE_NAME', 'FUNCTIONS_WORKER_RUNTIME']):
            return CloudProvider.AZURE
        
        # Heroku
        if os.environ.get('DYNO') or os.environ.get('HEROKU_APP_NAME'):
            return CloudProvider.HEROKU
        
        # Railway
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            return CloudProvider.RAILWAY
        
        # Vercel
        if os.environ.get('VERCEL_ENV') or os.environ.get('VERCEL_URL'):
            return CloudProvider.VERCEL
        
        # DigitalOcean
        if os.environ.get('DIGITALOCEAN_APP_ID'):
            return CloudProvider.DIGITALOCEAN
        
        return CloudProvider.UNKNOWN
    
    def _is_cloud_environment(self) -> bool:
        """Check if running in any cloud environment"""
        return self.detect_cloud_provider() != CloudProvider.UNKNOWN
    
    def detect_platform(self) -> str:
        """Detect the platform"""
        return platform.system().lower()
    
    def is_containerized(self) -> bool:
        """Check if running in a container"""
        return (
            os.path.exists('/.dockerenv') or
            os.environ.get('DOCKER_CONTAINER') == 'true' or
            os.path.exists('/var/run/secrets/kubernetes.io')
        )
    
    def supports_ssl(self) -> bool:
        """Check if the environment supports SSL"""
        cloud_provider = self.detect_cloud_provider()
        
        # Most cloud providers support SSL by default
        if cloud_provider in [CloudProvider.HEROKU, CloudProvider.VERCEL, CloudProvider.RAILWAY]:
            return True
        
        # Check for SSL certificate files
        ssl_paths = [
            '/etc/ssl/certs',
            '/etc/letsencrypt/live',
            './ssl',
            './certs'
        ]
        
        for path in ssl_paths:
            if os.path.exists(path):
                return True
        
        return False
    
    def get_full_config(self) -> EnvironmentConfig:
        """Get complete environment configuration"""
        env_type = self.detect_environment_type()
        cloud_provider = self.detect_cloud_provider()
        
        config = EnvironmentConfig(
            environment_type=env_type,
            cloud_provider=cloud_provider if cloud_provider != CloudProvider.UNKNOWN else None,
            platform=self.detect_platform(),
            is_containerized=self.is_containerized(),
            is_kubernetes=env_type == EnvironmentType.KUBERNETES,
            supports_ssl=self.supports_ssl(),
            debug_enabled=env_type in [EnvironmentType.LOCAL, EnvironmentType.DEVELOPMENT, EnvironmentType.CODESPACES],
            auto_restart=env_type in [EnvironmentType.PRODUCTION, EnvironmentType.STAGING, EnvironmentType.CLOUD],
            monitoring_enabled=env_type != EnvironmentType.LOCAL,
            secrets_backend=self._get_secrets_backend(cloud_provider)
        )
        
        return config
    
    def _get_secrets_backend(self, cloud_provider: CloudProvider) -> str:
        """Determine the appropriate secrets backend"""
        if cloud_provider == CloudProvider.AWS:
            return "aws_secrets_manager"
        elif cloud_provider == CloudProvider.GOOGLE_CLOUD:
            return "gcp_secret_manager"
        elif cloud_provider == CloudProvider.AZURE:
            return "azure_key_vault"
        elif cloud_provider == CloudProvider.HEROKU:
            return "heroku_config"
        else:
            return "env"


class ConfigurationManager:
    """Manages environment-specific configuration"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.detector = EnvironmentDetector()
        self.env_config = self.detector.get_full_config()
        self.logger = logging.getLogger(__name__)
    
    def load_environment_file(self) -> Dict[str, str]:
        """Load appropriate environment file based on environment"""
        env_files = [
            f".env.{self.env_config.environment_type.value}",
            f".env.{self.env_config.cloud_provider.value if self.env_config.cloud_provider else 'local'}",
            ".env.local",
            ".env"
        ]
        
        loaded_vars = {}
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self.logger.info(f"Loading environment file: {env_file}")
                loaded_vars.update(self._parse_env_file(env_path))
                break
        
        # Apply environment-specific overrides
        self._apply_environment_overrides(loaded_vars)
        
        return loaded_vars
    
    def _parse_env_file(self, env_path: Path) -> Dict[str, str]:
        """Parse environment file"""
        env_vars = {}
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        env_vars[key.strip()] = value
        except Exception as e:
            self.logger.error(f"Error parsing env file {env_path}: {e}")
        
        return env_vars
    
    def _apply_environment_overrides(self, env_vars: Dict[str, str]):
        """Apply environment-specific configuration overrides"""
        
        # Common overrides based on environment type
        if self.env_config.environment_type == EnvironmentType.CODESPACES:
            env_vars.update({
                'DEBUG': 'true',
                'CORS_ORIGINS': '*',
                'ALLOWED_HOSTS': '*',
                'PORT': str(os.environ.get('PORT', '8000'))
            })
        
        elif self.env_config.environment_type in [EnvironmentType.PRODUCTION, EnvironmentType.CLOUD]:
            env_vars.update({
                'DEBUG': 'false',
                'LOG_LEVEL': 'INFO',
                'WORKERS': str(os.environ.get('WORKERS', '4'))
            })
        
        elif self.env_config.environment_type == EnvironmentType.DEVELOPMENT:
            env_vars.update({
                'DEBUG': 'true',
                'LOG_LEVEL': 'DEBUG'
            })
        
        # Cloud provider specific overrides
        if self.env_config.cloud_provider == CloudProvider.HEROKU:
            env_vars.update({
                'PORT': str(os.environ.get('PORT', '8000')),
                'DATABASE_URL': os.environ.get('DATABASE_URL', env_vars.get('DATABASE_URL', ''))
            })
        
        elif self.env_config.cloud_provider == CloudProvider.RAILWAY:
            env_vars.update({
                'PORT': str(os.environ.get('PORT', '8000')),
                'RAILWAY_STATIC_URL': os.environ.get('RAILWAY_STATIC_URL', '')
            })
        
        # Kubernetes specific overrides
        if self.env_config.is_kubernetes:
            env_vars.update({
                'KUBERNETES_DEPLOYMENT': 'true',
                'HEALTH_CHECK_ENABLED': 'true'
            })
        
        # Container specific overrides
        if self.env_config.is_containerized:
            env_vars.update({
                'CONTAINERIZED': 'true',
                'HOST': '0.0.0.0'
            })
    
    def apply_configuration(self):
        """Apply configuration to the current environment"""
        env_vars = self.load_environment_file()
        
        # Set environment variables
        for key, value in env_vars.items():
            if key not in os.environ:  # Don't override existing env vars
                os.environ[key] = value
        
        # Set deployment metadata
        os.environ['DEPLOYMENT_ENVIRONMENT'] = self.env_config.environment_type.value
        os.environ['DEPLOYMENT_PLATFORM'] = self.env_config.platform
        if self.env_config.cloud_provider:
            os.environ['CLOUD_PROVIDER'] = self.env_config.cloud_provider.value
        
        self.logger.info(f"Configuration applied for {self.env_config.environment_type.value} environment")
    
    def get_database_url(self) -> str:
        """Get appropriate database URL for the environment"""
        # Check for environment-specific database URLs
        if self.env_config.cloud_provider == CloudProvider.HEROKU:
            return os.environ.get('DATABASE_URL', '')
        
        elif self.env_config.cloud_provider == CloudProvider.RAILWAY:
            return os.environ.get('DATABASE_URL', '')
        
        elif self.env_config.environment_type == EnvironmentType.KUBERNETES:
            # Use Kubernetes service names
            return "postgresql://postgres:password@postgres-service:5432/oatie_db"
        
        elif self.env_config.is_containerized:
            # Use Docker service names
            return "postgresql://postgres:password@postgres:5432/oatie_db"
        
        else:
            # Local development
            return os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/oatie_db')
    
    def get_redis_url(self) -> str:
        """Get appropriate Redis URL for the environment"""
        if self.env_config.cloud_provider in [CloudProvider.HEROKU, CloudProvider.RAILWAY]:
            return os.environ.get('REDIS_URL', '')
        
        elif self.env_config.environment_type == EnvironmentType.KUBERNETES:
            return "redis://redis-service:6379/0"
        
        elif self.env_config.is_containerized:
            return "redis://redis:6379/0"
        
        else:
            return os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    def get_secrets(self) -> Dict[str, Any]:
        """Get secrets from appropriate backend"""
        if self.env_config.secrets_backend == "aws_secrets_manager":
            return self._get_aws_secrets()
        elif self.env_config.secrets_backend == "gcp_secret_manager":
            return self._get_gcp_secrets()
        elif self.env_config.secrets_backend == "azure_key_vault":
            return self._get_azure_secrets()
        else:
            return self._get_env_secrets()
    
    def _get_env_secrets(self) -> Dict[str, Any]:
        """Get secrets from environment variables"""
        secret_keys = [
            'SECRET_KEY', 'ENCRYPTION_KEY', 'DATABASE_PASSWORD',
            'REDIS_PASSWORD', 'OAUTH2_CLIENT_SECRET', 'WEBHOOK_SIGNING_SECRET'
        ]
        
        secrets = {}
        for key in secret_keys:
            value = os.environ.get(key)
            if value:
                secrets[key] = value
        
        return secrets
    
    def _get_aws_secrets(self) -> Dict[str, Any]:
        """Get secrets from AWS Secrets Manager"""
        try:
            import boto3
            client = boto3.client('secretsmanager')
            
            secret_name = os.environ.get('AWS_SECRET_NAME', 'oatie-ai-secrets')
            response = client.get_secret_value(SecretId=secret_name)
            
            return json.loads(response['SecretString'])
        except Exception as e:
            self.logger.error(f"Failed to get AWS secrets: {e}")
            return self._get_env_secrets()
    
    def _get_gcp_secrets(self) -> Dict[str, Any]:
        """Get secrets from Google Cloud Secret Manager"""
        try:
            from google.cloud import secretmanager
            
            client = secretmanager.SecretManagerServiceClient()
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
            
            secrets = {}
            secret_names = ['secret-key', 'encryption-key', 'database-password']
            
            for secret_name in secret_names:
                name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                secrets[secret_name.replace('-', '_').upper()] = response.payload.data.decode("UTF-8")
            
            return secrets
        except Exception as e:
            self.logger.error(f"Failed to get GCP secrets: {e}")
            return self._get_env_secrets()
    
    def _get_azure_secrets(self) -> Dict[str, Any]:
        """Get secrets from Azure Key Vault"""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            vault_url = os.environ.get('AZURE_KEY_VAULT_URL')
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            
            secrets = {}
            secret_names = ['secret-key', 'encryption-key', 'database-password']
            
            for secret_name in secret_names:
                secret = client.get_secret(secret_name)
                secrets[secret_name.replace('-', '_').upper()] = secret.value
            
            return secrets
        except Exception as e:
            self.logger.error(f"Failed to get Azure secrets: {e}")
            return self._get_env_secrets()
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues"""
        issues = []
        
        # Check required environment variables
        required_vars = ['SECRET_KEY']
        for var in required_vars:
            if not os.environ.get(var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Check database connectivity
        db_url = self.get_database_url()
        if not db_url:
            issues.append("Database URL not configured")
        
        # Check SSL configuration for production
        if (self.env_config.environment_type == EnvironmentType.PRODUCTION and 
            not self.env_config.supports_ssl):
            issues.append("SSL not configured for production environment")
        
        return issues


# Global configuration manager instance
config_manager = ConfigurationManager()

def get_environment_config() -> EnvironmentConfig:
    """Get current environment configuration"""
    return config_manager.env_config

def initialize_environment():
    """Initialize environment configuration"""
    config_manager.apply_configuration()
    
    issues = config_manager.validate_configuration()
    if issues:
        logger = logging.getLogger(__name__)
        for issue in issues:
            logger.warning(f"Configuration issue: {issue}")

def get_config_for_service(service_name: str) -> Dict[str, Any]:
    """Get configuration specific to a service"""
    base_config = {
        'environment': config_manager.env_config.environment_type.value,
        'debug': config_manager.env_config.debug_enabled,
        'monitoring_enabled': config_manager.env_config.monitoring_enabled
    }
    
    if service_name == 'database':
        base_config['url'] = config_manager.get_database_url()
    elif service_name == 'cache':
        base_config['url'] = config_manager.get_redis_url()
    
    return base_config