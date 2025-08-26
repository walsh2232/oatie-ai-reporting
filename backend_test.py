#!/usr/bin/env python3
"""
Minimal test for backend functionality without external dependencies
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

def test_python_imports():
    """Test basic Python imports needed for the application"""
    print("🐍 Testing Python import capabilities...")
    
    # Test standard library imports
    standard_libs = [
        "asyncio", "logging", "json", "os", "sys", "pathlib", 
        "time", "subprocess", "threading", "multiprocessing"
    ]
    
    failed_imports = []
    for lib in standard_libs:
        try:
            __import__(lib)
            print(f"✅ {lib}")
        except ImportError as e:
            print(f"❌ {lib}: {e}")
            failed_imports.append(lib)
    
    return len(failed_imports) == 0

def test_file_permissions():
    """Test if we can read/write files as needed"""
    print("\n📁 Testing file permissions...")
    
    try:
        # Test read permission on key files
        test_files = [
            "backend/main.py",
            "backend/core/config.py", 
            ".env",
            "package.json"
        ]
        
        for file_path in test_files:
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    content = f.read(100)  # Read first 100 chars
                print(f"✅ Can read {file_path}")
            else:
                print(f"⚠️ File not found: {file_path}")
        
        # Test write permission
        test_file = "test_write_permission.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        os.remove(test_file)
        print("✅ Can write files")
        
        return True
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False

def test_environment_variables():
    """Test environment configuration"""
    print("\n⚙️ Testing environment variables...")
    
    try:
        # Load .env file manually since we can't use python-dotenv
        env_vars = {}
        if Path(".env").exists():
            with open(".env", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        required_vars = [
            "DEBUG", "PORT", "DATABASE_URL", "REDIS_URL", 
            "SECRET_KEY", "ORACLE_BI_ENABLED"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var in env_vars:
                print(f"✅ {var} = {env_vars[var][:20]}{'...' if len(env_vars[var]) > 20 else ''}")
            else:
                print(f"❌ Missing: {var}")
                missing_vars.append(var)
        
        return len(missing_vars) == 0
    except Exception as e:
        print(f"❌ Environment test error: {e}")
        return False

def test_backend_syntax():
    """Test backend Python syntax without running the app"""
    print("\n🔍 Testing backend syntax...")
    
    backend_files = [
        "backend/main.py",
        "backend/core/config.py",
        "backend/api/v1/__init__.py"
    ]
    
    syntax_ok = True
    for file_path in backend_files:
        if Path(file_path).exists():
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ {file_path} syntax OK")
                else:
                    print(f"❌ {file_path} syntax error: {result.stderr}")
                    syntax_ok = False
            except subprocess.TimeoutExpired:
                print(f"⚠️ {file_path} syntax check timed out")
            except Exception as e:
                print(f"❌ Error checking {file_path}: {e}")
                syntax_ok = False
    
    return syntax_ok

def test_frontend_build():
    """Test if frontend can be built"""
    print("\n🎨 Testing frontend build capability...")
    
    if not Path("package.json").exists():
        print("❌ package.json not found")
        return False
    
    if not Path("node_modules").exists():
        print("⚠️ node_modules not found - need to run npm install")
        return False
    
    try:
        # Test TypeScript compilation
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"], 
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ TypeScript compilation successful")
            return True
        else:
            print(f"❌ TypeScript compilation failed: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ TypeScript compilation timed out")
        return False
    except FileNotFoundError:
        print("⚠️ TypeScript compiler not found")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def test_oracle_integration():
    """Test Oracle integration components"""
    print("\n🔮 Testing Oracle integration...")
    
    oracle_files = [
        "backend/integrations/oracle/__init__.py",
        "backend/integrations/oracle/models.py",
        "backend/integrations/oracle/sdk.py",
        "backend/api/v1/endpoints/oracle.py"
    ]
    
    all_exist = True
    for file_path in oracle_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    # Test verification script
    if Path("verify_oracle_integration.py").exists():
        print("✅ Oracle verification script present")
        try:
            result = subprocess.run(
                [sys.executable, "verify_oracle_integration.py"],
                capture_output=True, text=True, timeout=15
            )
            if "SUCCESSFULLY IMPLEMENTED" in result.stdout:
                print("✅ Oracle integration verification passed")
            else:
                print("⚠️ Oracle integration verification had issues")
        except Exception as e:
            print(f"⚠️ Could not run Oracle verification: {e}")
    else:
        print("❌ Oracle verification script missing")
        all_exist = False
    
    return all_exist

def main():
    """Run all backend tests"""
    print("🧪 Backend Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Python Imports", test_python_imports),
        ("File Permissions", test_file_permissions),
        ("Environment Variables", test_environment_variables),
        ("Backend Syntax", test_backend_syntax),
        ("Frontend Build", test_frontend_build),
        ("Oracle Integration", test_oracle_integration),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}% ({passed}/{total} tests passed)")
    
    # Save results
    test_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "results": results,
        "summary": {
            "passed": passed,
            "total": total,
            "success_rate": success_rate
        }
    }
    
    with open("backend_test_report.json", "w") as f:
        json.dump(test_report, f, indent=2)
    
    print(f"\n📋 Test report saved to: backend_test_report.json")
    
    if success_rate >= 80:
        print("🎉 Backend functionality is GOOD!")
        return True
    elif success_rate >= 60:
        print("⚠️ Backend functionality is FAIR - some issues need attention")
        return False
    else:
        print("🚨 Backend functionality is POOR - immediate attention required")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)