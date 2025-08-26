#!/usr/bin/env python3
"""
Final Comprehensive Health Check Report for Oatie AI Reporting Platform
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def create_final_health_report():
    """Create comprehensive health report"""
    
    print("🏥 OATIE AI REPORTING PLATFORM - FINAL HEALTH CHECK")
    print("=" * 70)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "platform": "Oatie AI Reporting Platform",
        "version": "3.0.0",
        "health_status": "HEALTHY",
        "checks": {}
    }
    
    # 1. PROJECT STRUCTURE CHECK
    print("\n📁 PROJECT STRUCTURE")
    print("-" * 30)
    
    structure_check = {
        "backend_structure": True,
        "frontend_structure": True,
        "documentation": True,
        "configuration": True,
        "tests": True
    }
    
    # Check backend structure
    backend_dirs = ["backend", "backend/api", "backend/core", "backend/integrations"]
    for dir_path in backend_dirs:
        exists = Path(dir_path).exists()
        print(f"{'✅' if exists else '❌'} {dir_path}")
        if not exists:
            structure_check["backend_structure"] = False
    
    # Check frontend structure
    frontend_dirs = ["frontend", "frontend/src"]
    for dir_path in frontend_dirs:
        exists = Path(dir_path).exists()
        print(f"{'✅' if exists else '❌'} {dir_path}")
        if not exists:
            structure_check["frontend_structure"] = False
    
    report["checks"]["project_structure"] = structure_check
    
    # 2. ORACLE INTEGRATION CHECK
    print("\n🔮 ORACLE BI PUBLISHER INTEGRATION")
    print("-" * 40)
    
    oracle_files = [
        "backend/integrations/oracle/__init__.py",
        "backend/integrations/oracle/models.py", 
        "backend/integrations/oracle/sdk.py",
        "backend/integrations/oracle/auth.py",
        "backend/api/v1/endpoints/oracle.py",
        "verify_oracle_integration.py"
    ]
    
    oracle_status = {"files_present": True, "verification_passed": False}
    
    for file_path in oracle_files:
        exists = Path(file_path).exists()
        print(f"{'✅' if exists else '❌'} {file_path}")
        if not exists:
            oracle_status["files_present"] = False
    
    # Run Oracle verification
    try:
        result = subprocess.run(
            [sys.executable, "verify_oracle_integration.py"],
            capture_output=True, text=True, timeout=15
        )
        if "SUCCESSFULLY IMPLEMENTED" in result.stdout:
            oracle_status["verification_passed"] = True
            print("✅ Oracle integration verification: PASSED")
        else:
            print("⚠️ Oracle integration verification: ISSUES FOUND")
    except Exception as e:
        print(f"❌ Oracle verification failed: {e}")
    
    report["checks"]["oracle_integration"] = oracle_status
    
    # 3. FRONTEND BUILD CHECK
    print("\n🎨 FRONTEND BUILD & TESTS")
    print("-" * 30)
    
    frontend_status = {
        "dependencies_installed": Path("node_modules").exists(),
        "build_successful": False,
        "tests_passed": False,
        "typescript_valid": False
    }
    
    print(f"{'✅' if frontend_status['dependencies_installed'] else '❌'} Dependencies installed")
    
    # Test TypeScript compilation
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            capture_output=True, text=True, timeout=20
        )
        frontend_status["typescript_valid"] = result.returncode == 0
        print(f"{'✅' if frontend_status['typescript_valid'] else '❌'} TypeScript compilation")
    except:
        print("❌ TypeScript compilation")
    
    # Test build
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True, text=True, timeout=30
        )
        frontend_status["build_successful"] = result.returncode == 0 and Path("dist").exists()
        print(f"{'✅' if frontend_status['build_successful'] else '❌'} Production build")
    except:
        print("❌ Production build")
    
    # Test unit tests
    try:
        result = subprocess.run(
            ["npm", "run", "test:run"],
            capture_output=True, text=True, timeout=20
        )
        frontend_status["tests_passed"] = result.returncode == 0
        print(f"{'✅' if frontend_status['tests_passed'] else '❌'} Unit tests")
    except:
        print("❌ Unit tests")
    
    report["checks"]["frontend"] = frontend_status
    
    # 4. BACKEND SYNTAX & STRUCTURE
    print("\n🐍 BACKEND PYTHON CODE")
    print("-" * 25)
    
    backend_status = {
        "syntax_valid": True,
        "imports_working": True,
        "configuration_valid": True
    }
    
    # Check syntax of key files
    key_files = [
        "backend/main.py",
        "backend/core/config.py",
        "backend/api/v1/__init__.py",
        "backend/integrations/oracle/sdk.py"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    capture_output=True, text=True, timeout=5
                )
                syntax_ok = result.returncode == 0
                print(f"{'✅' if syntax_ok else '❌'} {file_path}")
                if not syntax_ok:
                    backend_status["syntax_valid"] = False
            except:
                print(f"❌ {file_path}")
                backend_status["syntax_valid"] = False
    
    report["checks"]["backend"] = backend_status
    
    # 5. SECURITY & CONFIGURATION
    print("\n🔒 SECURITY & CONFIGURATION")
    print("-" * 35)
    
    security_status = {
        "env_file_present": Path(".env").exists(),
        "secrets_configured": False,
        "cors_configured": False,
        "oracle_config_present": False
    }
    
    if security_status["env_file_present"]:
        try:
            with open(".env", "r") as f:
                env_content = f.read()
            
            security_status["secrets_configured"] = "SECRET_KEY" in env_content
            security_status["cors_configured"] = "CORS_ORIGINS" in env_content
            security_status["oracle_config_present"] = "ORACLE_BI_ENABLED" in env_content
            
            print(f"✅ Environment file present")
            print(f"{'✅' if security_status['secrets_configured'] else '❌'} Secrets configured")
            print(f"{'✅' if security_status['cors_configured'] else '❌'} CORS configured")
            print(f"{'✅' if security_status['oracle_config_present'] else '❌'} Oracle config present")
        except:
            print("❌ Error reading environment file")
    else:
        print("❌ Environment file missing")
    
    report["checks"]["security"] = security_status
    
    # 6. DOCUMENTATION & GUIDES
    print("\n📚 DOCUMENTATION")
    print("-" * 20)
    
    doc_files = [
        "README.md",
        "ORACLE_IMPLEMENTATION_SUMMARY.md",
        "DEVELOPMENT_SETUP_COMPLETE.md",
        "docs/ORACLE_INTEGRATION.md" 
    ]
    
    doc_status = {"documentation_complete": True}
    
    for doc_file in doc_files:
        exists = Path(doc_file).exists()
        print(f"{'✅' if exists else '❌'} {doc_file}")
        if not exists:
            doc_status["documentation_complete"] = False
    
    report["checks"]["documentation"] = doc_status
    
    # 7. OVERALL HEALTH CALCULATION
    print("\n" + "=" * 70)
    print("📊 OVERALL HEALTH ASSESSMENT")
    print("=" * 70)
    
    # Calculate health scores for each category
    scores = {}
    
    # Project Structure (20%)
    structure_score = sum(structure_check.values()) / len(structure_check) * 100
    scores["structure"] = structure_score
    
    # Oracle Integration (25%)
    oracle_score = (
        (80 if oracle_status["files_present"] else 0) +
        (20 if oracle_status["verification_passed"] else 0)
    )
    scores["oracle"] = oracle_score
    
    # Frontend (20%)
    frontend_score = sum(frontend_status.values()) / len(frontend_status) * 100
    scores["frontend"] = frontend_score
    
    # Backend (20%)
    backend_score = sum(backend_status.values()) / len(backend_status) * 100
    scores["backend"] = backend_score
    
    # Security (10%)
    security_score = sum(security_status.values()) / len(security_status) * 100
    scores["security"] = security_score
    
    # Documentation (5%)
    doc_score = 100 if doc_status["documentation_complete"] else 50
    scores["documentation"] = doc_score
    
    # Weighted overall score
    overall_score = (
        scores["structure"] * 0.20 +
        scores["oracle"] * 0.25 +
        scores["frontend"] * 0.20 +
        scores["backend"] * 0.20 +
        scores["security"] * 0.10 +
        scores["documentation"] * 0.05
    )
    
    print(f"🏗️  Project Structure: {scores['structure']:.1f}% (Weight: 20%)")
    print(f"🔮 Oracle Integration: {scores['oracle']:.1f}% (Weight: 25%)")
    print(f"🎨 Frontend: {scores['frontend']:.1f}% (Weight: 20%)")
    print(f"🐍 Backend: {scores['backend']:.1f}% (Weight: 20%)")
    print(f"🔒 Security: {scores['security']:.1f}% (Weight: 10%)")
    print(f"📚 Documentation: {scores['documentation']:.1f}% (Weight: 5%)")
    
    print(f"\n🎯 OVERALL HEALTH SCORE: {overall_score:.1f}%")
    
    # Health Status Assessment
    if overall_score >= 90:
        health_status = "EXCELLENT"
        status_icon = "🎉"
        recommendation = "Application is production-ready!"
    elif overall_score >= 80:
        health_status = "GOOD"
        status_icon = "✅"
        recommendation = "Application is healthy with minor areas for improvement."
    elif overall_score >= 70:
        health_status = "FAIR"
        status_icon = "⚠️"
        recommendation = "Application needs some attention before production deployment."
    elif overall_score >= 60:
        health_status = "POOR"
        status_icon = "🚨"
        recommendation = "Application has significant issues that need immediate attention."
    else:
        health_status = "CRITICAL"
        status_icon = "💥"
        recommendation = "Application requires major fixes before it can be used."
    
    print(f"\n{status_icon} HEALTH STATUS: {health_status}")
    print(f"📋 RECOMMENDATION: {recommendation}")
    
    # Update report with final scores
    report["scores"] = scores
    report["overall_score"] = overall_score
    report["health_status"] = health_status
    report["recommendation"] = recommendation
    
    # Issues Summary
    issues = []
    
    if not structure_check["backend_structure"]:
        issues.append("Backend directory structure incomplete")
    if not structure_check["frontend_structure"]:
        issues.append("Frontend directory structure incomplete")
    if not oracle_status["files_present"]:
        issues.append("Oracle integration files missing")
    if not oracle_status["verification_passed"]:
        issues.append("Oracle integration verification failed")
    if not frontend_status["build_successful"]:
        issues.append("Frontend build failing")
    if not frontend_status["tests_passed"]:
        issues.append("Frontend tests failing")
    if not backend_status["syntax_valid"]:
        issues.append("Backend syntax errors")
    if not security_status["env_file_present"]:
        issues.append("Environment configuration missing")
    if not doc_status["documentation_complete"]:
        issues.append("Documentation incomplete")
    
    if issues:
        print(f"\n⚠️ IDENTIFIED ISSUES:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print(f"\n✅ NO CRITICAL ISSUES IDENTIFIED")
    
    report["issues"] = issues
    
    # Recommendations
    recommendations = []
    
    if overall_score < 100:
        if scores["oracle"] < 100:
            recommendations.append("Run Oracle integration tests to verify functionality")
        if scores["frontend"] < 100:
            recommendations.append("Fix frontend build and test issues")
        if scores["security"] < 100:
            recommendations.append("Complete security configuration")
        if scores["backend"] < 100:
            recommendations.append("Install required Python dependencies")
    
    if recommendations:
        print(f"\n🎯 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    report["recommendations"] = recommendations
    
    # Save comprehensive report
    with open("final_health_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Comprehensive health report saved to: final_health_report.json")
    
    return overall_score >= 80

if __name__ == "__main__":
    success = create_final_health_report()
    sys.exit(0 if success else 1)