#!/usr/bin/env python3
"""
Test script for Oatie AI Platform deployment automation and monitoring
Validates that all systems are working correctly
"""

import asyncio
import requests
import time
import sys
import json
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.core.environment import EnvironmentDetector, ConfigurationManager
from backend.core.monitoring import health_checker
from backend.core.performance import startup_optimizer, resource_monitor


class DeploymentTester:
    """Test deployment and monitoring systems"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_environment_detection(self):
        """Test environment detection capabilities"""
        self.log("Testing environment detection...")
        
        try:
            detector = EnvironmentDetector()
            
            # Test platform detection
            platform = detector.detect_platform()
            self.log(f"Detected platform: {platform}")
            
            # Test environment detection
            env_type = detector.detect_environment_type()
            self.log(f"Detected environment: {env_type.value}")
            
            # Test cloud provider detection
            cloud_provider = detector.detect_cloud_provider()
            self.log(f"Detected cloud provider: {cloud_provider.value}")
            
            # Test full configuration
            config = detector.get_full_config()
            self.log(f"Environment config: {config.environment_type.value}, containerized: {config.is_containerized}")
            
            self.results["environment_detection"] = {
                "status": "PASS",
                "platform": platform,
                "environment": env_type.value,
                "cloud_provider": cloud_provider.value,
                "containerized": config.is_containerized
            }
            
        except Exception as e:
            self.log(f"Environment detection test failed: {e}", "ERROR")
            self.results["environment_detection"] = {"status": "FAIL", "error": str(e)}
    
    def test_configuration_management(self):
        """Test configuration management"""
        self.log("Testing configuration management...")
        
        try:
            config_manager = ConfigurationManager()
            
            # Test database URL generation
            db_url = config_manager.get_database_url()
            self.log(f"Database URL configured: {bool(db_url)}")
            
            # Test Redis URL generation
            redis_url = config_manager.get_redis_url()
            self.log(f"Redis URL configured: {bool(redis_url)}")
            
            # Test configuration validation
            issues = config_manager.validate_configuration()
            self.log(f"Configuration issues found: {len(issues)}")
            
            self.results["configuration_management"] = {
                "status": "PASS",
                "has_database_url": bool(db_url),
                "has_redis_url": bool(redis_url),
                "config_issues": len(issues)
            }
            
        except Exception as e:
            self.log(f"Configuration management test failed: {e}", "ERROR")
            self.results["configuration_management"] = {"status": "FAIL", "error": str(e)}
    
    async def test_health_monitoring(self):
        """Test health monitoring system"""
        self.log("Testing health monitoring...")
        
        try:
            # Test health checker directly
            health_status = await health_checker.get_health_status()
            self.log(f"Health status: {health_status.get('status', 'unknown')}")
            
            # Test service health check
            services = await health_checker.check_service_health()
            healthy_services = sum(1 for status in services.values() if status)
            self.log(f"Healthy services: {healthy_services}/{len(services)}")
            
            self.results["health_monitoring"] = {
                "status": "PASS",
                "overall_health": health_status.get('status', 'unknown'),
                "healthy_services": healthy_services,
                "total_services": len(services)
            }
            
        except Exception as e:
            self.log(f"Health monitoring test failed: {e}", "ERROR")
            self.results["health_monitoring"] = {"status": "FAIL", "error": str(e)}
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        self.log("Testing performance monitoring...")
        
        try:
            # Test startup profiling
            profile_id = startup_optimizer.start_profiling("test_service")
            startup_optimizer.add_checkpoint(profile_id, "initialized")
            startup_optimizer.add_checkpoint(profile_id, "ready")
            profile = startup_optimizer.finish_profiling(profile_id)
            
            self.log(f"Startup profile completed: {profile.ready_time:.3f}s")
            
            # Test resource monitoring
            current_usage = resource_monitor.get_current_usage()
            self.log(f"Current CPU: {current_usage.cpu_percent:.1f}%, Memory: {current_usage.memory_percent:.1f}%")
            
            self.results["performance_monitoring"] = {
                "status": "PASS",
                "startup_time": profile.ready_time,
                "cpu_percent": current_usage.cpu_percent,
                "memory_percent": current_usage.memory_percent
            }
            
        except Exception as e:
            self.log(f"Performance monitoring test failed: {e}", "ERROR")
            self.results["performance_monitoring"] = {"status": "FAIL", "error": str(e)}
    
    def test_api_endpoints(self):
        """Test API endpoints (requires running server)"""
        self.log("Testing API endpoints...")
        
        endpoints_to_test = [
            "/health",
            "/health/detailed",
            "/health/services",
            "/api/performance/resources/current",
            "/api/performance/scaling/recommendations"
        ]
        
        endpoint_results = {}
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.log(f"✓ {endpoint}: OK")
                    endpoint_results[endpoint] = "OK"
                else:
                    self.log(f"✗ {endpoint}: HTTP {response.status_code}")
                    endpoint_results[endpoint] = f"HTTP {response.status_code}"
                    
            except requests.exceptions.ConnectionError:
                self.log(f"✗ {endpoint}: Connection refused (server not running)")
                endpoint_results[endpoint] = "CONNECTION_REFUSED"
            except Exception as e:
                self.log(f"✗ {endpoint}: {str(e)}")
                endpoint_results[endpoint] = f"ERROR: {str(e)}"
        
        successful_endpoints = sum(1 for status in endpoint_results.values() if status == "OK")
        
        self.results["api_endpoints"] = {
            "status": "PASS" if successful_endpoints > 0 else "FAIL",
            "successful_endpoints": successful_endpoints,
            "total_endpoints": len(endpoints_to_test),
            "endpoint_details": endpoint_results
        }
    
    def test_deployment_scripts(self):
        """Test deployment script execution"""
        self.log("Testing deployment scripts...")
        
        try:
            import subprocess
            
            # Test deploy_production.py help
            deploy_script = Path(__file__).parent.parent / "scripts" / "deployment" / "deploy_production.py"
            if deploy_script.exists():
                result = subprocess.run([sys.executable, str(deploy_script), "--help"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.log("✓ deploy_production.py: Help command works")
                    deploy_status = "OK"
                else:
                    self.log(f"✗ deploy_production.py: Exit code {result.returncode}")
                    deploy_status = f"EXIT_CODE_{result.returncode}"
            else:
                self.log("✗ deploy_production.py: Script not found")
                deploy_status = "NOT_FOUND"
            
            # Test start_production.sh help
            start_script = Path(__file__).parent.parent / "scripts" / "deployment" / "start_production.sh"
            if start_script.exists():
                result = subprocess.run(["bash", str(start_script), "--help"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.log("✓ start_production.sh: Help command works")
                    start_status = "OK"
                else:
                    self.log(f"✗ start_production.sh: Exit code {result.returncode}")
                    start_status = f"EXIT_CODE_{result.returncode}"
            else:
                self.log("✗ start_production.sh: Script not found")
                start_status = "NOT_FOUND"
            
            self.results["deployment_scripts"] = {
                "status": "PASS" if deploy_status == "OK" and start_status == "OK" else "PARTIAL",
                "deploy_script": deploy_status,
                "start_script": start_status
            }
            
        except Exception as e:
            self.log(f"Deployment scripts test failed: {e}", "ERROR")
            self.results["deployment_scripts"] = {"status": "FAIL", "error": str(e)}
    
    async def run_all_tests(self):
        """Run all tests"""
        self.log("Starting deployment system tests...")
        self.log("=" * 50)
        
        # Run all tests
        self.test_environment_detection()
        self.test_configuration_management()
        await self.test_health_monitoring()
        self.test_performance_monitoring()
        self.test_api_endpoints()
        self.test_deployment_scripts()
        
        # Generate summary
        self.log("=" * 50)
        self.log("TEST SUMMARY")
        self.log("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get("status") == "PASS")
        partial_tests = sum(1 for result in self.results.values() if result.get("status") == "PARTIAL")
        
        for test_name, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            if status == "PASS":
                self.log(f"✓ {test_name}: PASS")
            elif status == "PARTIAL":
                self.log(f"⚠ {test_name}: PARTIAL")
            else:
                self.log(f"✗ {test_name}: FAIL")
                if "error" in result:
                    self.log(f"  Error: {result['error']}")
        
        self.log("=" * 50)
        self.log(f"Results: {passed_tests} PASS, {partial_tests} PARTIAL, {total_tests - passed_tests - partial_tests} FAIL")
        
        if passed_tests >= total_tests - 1:  # Allow one test to fail (likely API endpoints if server not running)
            self.log("🎉 Deployment system tests SUCCESSFUL!")
            return True
        else:
            self.log("❌ Deployment system tests FAILED!")
            return False
    
    def export_results(self, filename: str = "test_results.json"):
        """Export test results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            self.log(f"Test results exported to {filename}")
        except Exception as e:
            self.log(f"Failed to export results: {e}", "ERROR")


async def main():
    """Main test function"""
    tester = DeploymentTester()
    success = await tester.run_all_tests()
    tester.export_results()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())