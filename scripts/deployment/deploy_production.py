#!/usr/bin/env python3
"""
Cross-platform production deployment script for Oatie AI Platform
Supports cloud environments, GitHub Codespaces, and local deployments
"""

import os
import sys
import platform
import subprocess
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union
import argparse
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Supported deployment environments"""
    LOCAL = "local"
    CODESPACES = "codespaces"
    CLOUD = "cloud"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"


class Platform(Enum):
    """Supported platforms"""
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"


@dataclass
class DeploymentConfig:
    """Deployment configuration settings"""
    environment: Environment
    platform: Platform
    use_docker: bool = True
    use_kubernetes: bool = False
    service_port: int = 8000
    workers: int = 4
    log_level: str = "INFO"
    enable_ssl: bool = False
    auto_restart: bool = True
    health_check_enabled: bool = True
    monitoring_enabled: bool = True


class EnvironmentDetector:
    """Detects the current deployment environment and platform"""
    
    @staticmethod
    def detect_platform() -> Platform:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == "linux":
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        elif system == "windows":
            return Platform.WINDOWS
        else:
            raise ValueError(f"Unsupported platform: {system}")
    
    @staticmethod
    def detect_environment() -> Environment:
        """Detect the current deployment environment"""
        # Check for GitHub Codespaces
        if os.environ.get('CODESPACES') == 'true':
            return Environment.CODESPACES
        
        # Check for Kubernetes environment
        if os.path.exists('/var/run/secrets/kubernetes.io'):
            return Environment.KUBERNETES
        
        # Check for cloud environment indicators
        cloud_indicators = [
            'AWS_REGION', 'GOOGLE_CLOUD_PROJECT', 'AZURE_RESOURCE_GROUP',
            'RAILWAY_ENVIRONMENT', 'HEROKU_APP_NAME', 'VERCEL_ENV'
        ]
        if any(os.environ.get(indicator) for indicator in cloud_indicators):
            return Environment.CLOUD
        
        # Check for Docker environment
        if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
            return Environment.DOCKER
        
        # Default to local
        return Environment.LOCAL
    
    @staticmethod
    def is_cloud_environment() -> bool:
        """Check if running in any cloud environment"""
        env = EnvironmentDetector.detect_environment()
        return env in [Environment.CLOUD, Environment.CODESPACES, Environment.KUBERNETES]


class DeploymentManager:
    """Main deployment management class"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.project_root = Path(__file__).parent.parent.parent
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup structured logging"""
        import logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        getattr(self.logger, level.lower())(message)
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, 
                   check: bool = True) -> subprocess.CompletedProcess:
        """Run a command with proper error handling"""
        self.log(f"Running command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                check=check,
                capture_output=True,
                text=True
            )
            if result.stdout:
                self.log(f"Command output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                self.log(f"Error output: {e.stderr}", "ERROR")
            raise
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        self.log("Checking prerequisites...")
        
        required_tools = []
        
        if self.config.use_docker:
            required_tools.extend(['docker', 'docker-compose'])
        
        if self.config.use_kubernetes:
            required_tools.append('kubectl')
        
        # Check Python dependencies
        python_deps = ['fastapi', 'uvicorn', 'structlog']
        
        missing_tools = []
        for tool in required_tools:
            try:
                subprocess.run([tool, '--version'], check=True, 
                             capture_output=True, text=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
        
        if missing_tools:
            self.log(f"Missing required tools: {', '.join(missing_tools)}", "ERROR")
            return False
        
        self.log("All prerequisites are available")
        return True
    
    def setup_environment_config(self):
        """Setup environment-specific configuration"""
        self.log("Setting up environment configuration...")
        
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists() and env_example.exists():
            self.log("Creating .env file from .env.example")
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                content = src.read()
                
                # Environment-specific modifications
                if self.config.environment == Environment.CODESPACES:
                    content = content.replace('DEBUG=false', 'DEBUG=true')
                    content = content.replace('PORT=8000', 'PORT=8000')
                    content = content.replace('CORS_ORIGINS=http://localhost:3000', 
                                            'CORS_ORIGINS=*')
                
                elif EnvironmentDetector.is_cloud_environment():
                    content = content.replace('DEBUG=true', 'DEBUG=false')
                    # Add cloud-specific settings
                    content += "\n# Cloud Environment Settings\n"
                    content += "CLOUD_DEPLOYMENT=true\n"
                    content += f"WORKERS={self.config.workers}\n"
                
                dst.write(content)
        
        # Set environment variables
        os.environ['DEPLOYMENT_ENVIRONMENT'] = self.config.environment.value
        os.environ['DEPLOYMENT_PLATFORM'] = self.config.platform.value
        
        self.log("Environment configuration completed")
    
    def deploy_with_docker(self):
        """Deploy using Docker Compose"""
        self.log("Starting Docker deployment...")
        
        compose_file = 'docker-compose.yml'
        if EnvironmentDetector.is_cloud_environment():
            compose_file = 'docker-compose.prod.yml'
        
        compose_path = self.project_root / compose_file
        if not compose_path.exists():
            compose_path = self.project_root / 'docker-compose.yml'
        
        # Build and start services
        self.run_command(['docker-compose', '-f', str(compose_path), 'build'])
        self.run_command(['docker-compose', '-f', str(compose_path), 'up', '-d'])
        
        self.log("Docker deployment completed")
    
    def deploy_with_kubernetes(self):
        """Deploy using Kubernetes"""
        self.log("Starting Kubernetes deployment...")
        
        k8s_dir = self.project_root / 'infrastructure' / 'kubernetes'
        if not k8s_dir.exists():
            raise FileNotFoundError("Kubernetes manifests not found")
        
        # Apply Kubernetes manifests
        for manifest in k8s_dir.glob('*.yaml'):
            self.run_command(['kubectl', 'apply', '-f', str(manifest)])
        
        # Wait for deployment to be ready
        self.run_command(['kubectl', 'rollout', 'status', 'deployment/oatie-backend'])
        
        self.log("Kubernetes deployment completed")
    
    def deploy_standalone(self):
        """Deploy as standalone Python application"""
        self.log("Starting standalone deployment...")
        
        # Install dependencies
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            self.run_command([sys.executable, '-m', 'pip', 'install', '-r', 
                            str(requirements_file)])
        
        # Start the application
        backend_path = self.project_root / 'backend'
        start_script = self.project_root / 'scripts' / 'deployment' / 'start_production.sh'
        
        if start_script.exists() and self.config.platform != Platform.WINDOWS:
            self.run_command(['bash', str(start_script)], cwd=backend_path)
        else:
            # Fallback to direct Python execution
            self.run_command([
                sys.executable, '-m', 'uvicorn', 'backend.main:app',
                '--host', '0.0.0.0',
                '--port', str(self.config.service_port),
                '--workers', str(self.config.workers),
                '--log-level', self.config.log_level.lower()
            ])
        
        self.log("Standalone deployment completed")
    
    def perform_health_check(self) -> bool:
        """Perform post-deployment health check"""
        if not self.config.health_check_enabled:
            return True
        
        self.log("Performing health check...")
        
        import urllib.request
        import urllib.error
        
        health_url = f"http://localhost:{self.config.service_port}/health"
        max_retries = 30
        retry_interval = 2
        
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(health_url, timeout=5) as response:
                    if response.status == 200:
                        self.log("Health check passed")
                        return True
            except (urllib.error.URLError, ConnectionError):
                if attempt < max_retries - 1:
                    self.log(f"Health check attempt {attempt + 1} failed, retrying in {retry_interval}s...")
                    time.sleep(retry_interval)
                else:
                    self.log("Health check failed after all attempts", "ERROR")
                    return False
        
        return False
    
    def deploy(self):
        """Main deployment method"""
        self.log(f"Starting deployment on {self.config.platform.value} in {self.config.environment.value} environment")
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                raise RuntimeError("Prerequisites check failed")
            
            # Setup environment
            self.setup_environment_config()
            
            # Choose deployment method
            if self.config.use_kubernetes:
                self.deploy_with_kubernetes()
            elif self.config.use_docker:
                self.deploy_with_docker()
            else:
                self.deploy_standalone()
            
            # Perform health check
            if not self.perform_health_check():
                raise RuntimeError("Health check failed")
            
            self.log("Deployment completed successfully!", "SUCCESS")
            
        except Exception as e:
            self.log(f"Deployment failed: {str(e)}", "ERROR")
            sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy Oatie AI Platform")
    parser.add_argument('--environment', choices=[e.value for e in Environment], 
                       help='Target environment')
    parser.add_argument('--platform', choices=[p.value for p in Platform], 
                       help='Target platform')
    parser.add_argument('--use-docker', action='store_true', default=True,
                       help='Use Docker for deployment')
    parser.add_argument('--use-kubernetes', action='store_true',
                       help='Use Kubernetes for deployment')
    parser.add_argument('--port', type=int, default=8000,
                       help='Service port')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of workers')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level')
    parser.add_argument('--no-health-check', action='store_true',
                       help='Skip health check')
    
    args = parser.parse_args()
    
    # Auto-detect environment and platform if not specified
    environment = Environment(args.environment) if args.environment else EnvironmentDetector.detect_environment()
    platform = Platform(args.platform) if args.platform else EnvironmentDetector.detect_platform()
    
    config = DeploymentConfig(
        environment=environment,
        platform=platform,
        use_docker=args.use_docker and not args.use_kubernetes,
        use_kubernetes=args.use_kubernetes,
        service_port=args.port,
        workers=args.workers,
        log_level=args.log_level,
        health_check_enabled=not args.no_health_check
    )
    
    # Create and run deployment
    deployment_manager = DeploymentManager(config)
    deployment_manager.deploy()


if __name__ == "__main__":
    main()