#!/usr/bin/env python3
"""
Comprehensive Health Check for Oatie AI Reporting Platform
Checks all components without requiring external dependencies
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def run_command(cmd: str, cwd: str = None) -> tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()

def check_directory_structure() -> Dict[str, Any]:
    """Check if the required directory structure exists"""
    base_path = Path(".")
    required_dirs = [
        "backend",
        "backend/api", 
        "backend/api/v1",
        "backend/core",
        "backend/integrations",
        "frontend",
        "frontend/src",
        "tests",
        "docs"
    ]
    
    results = {}
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        results[dir_path] = {
            "exists": full_path.exists(),
            "is_directory": full_path.is_dir() if full_path.exists() else False
        }
    
    return results

def check_required_files() -> Dict[str, Any]:
    """Check if required files exist"""
    required_files = [
        "requirements.txt",
        "package.json", 
        ".env",
        "backend/main.py",
        "backend/core/config.py",
        "verify_oracle_integration.py"
    ]
    
    results = {}
    for file_path in required_files:
        results[file_path] = {
            "exists": check_file_exists(file_path),
            "size": Path(file_path).stat().st_size if check_file_exists(file_path) else 0
        }
    
    return results

def check_python_syntax() -> Dict[str, Any]:
    """Check Python files for syntax errors"""
    python_files = []
    for root, dirs, files in os.walk("backend"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    results = {}
    for py_file in python_files:
        success, output = run_command(f"python -m py_compile {py_file}")
        results[py_file] = {
            "valid_syntax": success,
            "error": output if not success else None
        }
    
    return results

def check_frontend_dependencies() -> Dict[str, Any]:
    """Check frontend dependencies status"""
    if not check_file_exists("package.json"):
        return {"error": "package.json not found"}
    
    # Check if node_modules exists
    node_modules_exists = check_file_exists("node_modules")
    
    # Try to run npm commands
    npm_list_success, npm_list_output = run_command("npm list --depth=0")
    npm_audit_success, npm_audit_output = run_command("npm audit --json")
    
    return {
        "node_modules_exists": node_modules_exists,
        "npm_list_success": npm_list_success,
        "npm_list_output": npm_list_output[:500] if npm_list_output else "",
        "npm_audit_success": npm_audit_success,
        "npm_audit_output": npm_audit_output[:500] if npm_audit_output else ""
    }

def check_environment_config() -> Dict[str, Any]:
    """Check environment configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        return {"error": ".env file not found"}
    
    try:
        with open(env_file) as f:
            env_content = f.read()
        
        # Check for key configurations
        required_vars = [
            "DEBUG", "PORT", "DATABASE_URL", "REDIS_URL", 
            "SECRET_KEY", "ORACLE_BI_ENABLED"
        ]
        
        found_vars = {}
        for var in required_vars:
            found_vars[var] = var in env_content
        
        return {
            "env_file_exists": True,
            "env_file_size": env_file.stat().st_size,
            "required_variables": found_vars
        }
    except Exception as e:
        return {"error": f"Failed to read .env file: {str(e)}"}

def test_simple_import() -> Dict[str, Any]:
    """Test if we can import basic Python modules"""
    test_imports = [
        "json", "os", "sys", "pathlib", "subprocess"
    ]
    
    results = {}
    for module in test_imports:
        try:
            __import__(module)
            results[module] = {"importable": True}
        except ImportError as e:
            results[module] = {"importable": False, "error": str(e)}
    
    return results

def main():
    """Run comprehensive health check"""
    print("🏥 Oatie AI Reporting Platform - Health Check")
    print("=" * 60)
    
    health_report = {
        "timestamp": os.popen("date").read().strip(),
        "checks": {}
    }
    
    # 1. Directory Structure Check
    print("\n📁 Checking Directory Structure...")
    dir_check = check_directory_structure()
    health_report["checks"]["directory_structure"] = dir_check
    
    missing_dirs = [d for d, info in dir_check.items() if not info["exists"]]
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
    else:
        print("✅ All required directories present")
    
    # 2. Required Files Check
    print("\n📄 Checking Required Files...")
    file_check = check_required_files()
    health_report["checks"]["required_files"] = file_check
    
    missing_files = [f for f, info in file_check.items() if not info["exists"]]
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    else:
        print("✅ All required files present")
    
    # 3. Python Syntax Check
    print("\n🐍 Checking Python Syntax...")
    syntax_check = check_python_syntax()
    health_report["checks"]["python_syntax"] = syntax_check
    
    syntax_errors = [f for f, info in syntax_check.items() if not info["valid_syntax"]]
    if syntax_errors:
        print(f"❌ Syntax errors in: {syntax_errors[:3]}{'...' if len(syntax_errors) > 3 else ''}")
    else:
        print("✅ All Python files have valid syntax")
    
    # 4. Environment Configuration Check
    print("\n⚙️ Checking Environment Configuration...")
    env_check = check_environment_config()
    health_report["checks"]["environment_config"] = env_check
    
    if "error" in env_check:
        print(f"❌ Environment config error: {env_check['error']}")
    else:
        missing_vars = [var for var, found in env_check["required_variables"].items() if not found]
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
        else:
            print("✅ Environment configuration looks good")
    
    # 5. Frontend Dependencies Check
    print("\n📦 Checking Frontend Dependencies...")
    frontend_check = check_frontend_dependencies()
    health_report["checks"]["frontend_dependencies"] = frontend_check
    
    if "error" in frontend_check:
        print(f"❌ Frontend check error: {frontend_check['error']}")
    elif not frontend_check["node_modules_exists"]:
        print("⚠️ node_modules not found - need to run 'npm install'")
    else:
        print("✅ Frontend dependencies appear to be installed")
    
    # 6. Basic Import Test
    print("\n🧪 Testing Basic Imports...")
    import_check = test_simple_import()
    health_report["checks"]["basic_imports"] = import_check
    
    failed_imports = [mod for mod, info in import_check.items() if not info["importable"]]
    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
    else:
        print("✅ Basic Python imports working")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    total_checks = len(health_report["checks"])
    passed_checks = 0
    
    for check_name, check_results in health_report["checks"].items():
        if check_name == "directory_structure":
            passed = all(info["exists"] for info in check_results.values())
        elif check_name == "required_files":
            passed = all(info["exists"] for info in check_results.values())
        elif check_name == "python_syntax":
            passed = all(info["valid_syntax"] for info in check_results.values())
        elif check_name == "environment_config":
            passed = "error" not in check_results
        elif check_name == "frontend_dependencies":
            passed = "error" not in check_results and check_results.get("node_modules_exists", False)
        elif check_name == "basic_imports":
            passed = all(info["importable"] for info in check_results.values())
        else:
            passed = True
            
        if passed:
            passed_checks += 1
            print(f"✅ {check_name.replace('_', ' ').title()}")
        else:
            print(f"❌ {check_name.replace('_', ' ').title()}")
    
    health_score = (passed_checks / total_checks) * 100
    print(f"\n🎯 Overall Health Score: {health_score:.1f}% ({passed_checks}/{total_checks} checks passed)")
    
    # Save detailed report
    with open("health_check_report.json", "w") as f:
        json.dump(health_report, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: health_check_report.json")
    
    if health_score >= 80:
        print("🎉 Application health is GOOD!")
    elif health_score >= 60:
        print("⚠️ Application health is FAIR - some issues need attention")
    else:
        print("🚨 Application health is POOR - immediate attention required")
    
    return health_score >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)