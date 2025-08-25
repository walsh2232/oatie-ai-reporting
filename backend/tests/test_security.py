"""
Basic tests for the enterprise security framework
"""

import asyncio
import pytest
from datetime import datetime

# Since we can't install dependencies, we'll create a simple test that can be run manually

async def test_security_manager():
    """Test basic SecurityManager functionality"""
    
    # Mock settings class
    class MockSettings:
        def __init__(self):
            self.encryption_key = "test-encryption-key-32-chars-long"
            self.secret_key = "test-secret-key"
            self.algorithm = "HS256"
            self.access_token_expire_minutes = 30
            self.app_name = "Oatie AI Reporting Platform"
    
    try:
        # Import our security framework
        from backend.core.security import SecurityManager
        from backend.core.mfa import MFAMethod
        from backend.core.rbac import Permission
        
        # Initialize SecurityManager
        settings = MockSettings()
        security_manager = SecurityManager(settings)
        
        print("✓ SecurityManager initialized successfully")
        
        # Test password hashing
        password = "test123"
        hashed = await security_manager.hash_password(password)
        verified = await security_manager.verify_password(password, hashed)
        assert verified, "Password verification failed"
        print("✓ Password hashing and verification working")
        
        # Test token creation and verification
        token_data = {"sub": "test_user_123", "email": "test@example.com"}
        token = await security_manager.create_access_token(token_data)
        payload = await security_manager.verify_token(token)
        assert payload["sub"] == "test_user_123", "Token verification failed"
        print("✓ JWT token creation and verification working")
        
        # Test encryption/decryption
        test_data = "sensitive information"
        encrypted = await security_manager.encrypt_sensitive_data(test_data)
        decrypted = await security_manager.decrypt_sensitive_data(encrypted)
        assert decrypted == test_data, "Encryption/decryption failed"
        print("✓ Data encryption and decryption working")
        
        # Test MFA setup
        user_id = "test_user_123"
        user_email = "test@example.com"
        mfa_setup = await security_manager.setup_mfa(user_id, MFAMethod.TOTP, user_email)
        assert "secret" in mfa_setup, "MFA setup failed"
        print("✓ MFA setup working")
        
        # Test RBAC
        await security_manager.assign_role(user_id, "analyst", "admin_user")
        user_permissions = await security_manager.get_user_permissions(user_id)
        assert "analyst" in user_permissions["roles"], "Role assignment failed"
        print("✓ RBAC role assignment working")
        
        # Test permission checking
        has_permission = await security_manager.check_permission(user_id, Permission.REPORT_READ)
        assert has_permission, "Permission check failed"
        print("✓ Permission checking working")
        
        # Test audit logging
        from backend.core.security import AuditEventType
        await security_manager.log_audit_event(
            AuditEventType.LOGIN,
            user_id=user_id,
            details={"test": True}
        )
        assert len(security_manager.audit_logs) > 0, "Audit logging failed"
        print("✓ Audit logging working")
        
        # Test security report generation
        report = await security_manager.generate_security_report()
        assert "report_generated_at" in report, "Security report generation failed"
        print("✓ Security report generation working")
        
        print("\n🎉 All basic security framework tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Note: This is expected if dependencies are not installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_rbac_hierarchy():
    """Test RBAC role hierarchy"""
    
    try:
        from backend.core.rbac import RBACManager, Permission
        
        rbac = RBACManager()
        
        # Test system roles exist
        assert "admin" in rbac.roles, "Admin role not found"
        assert "analyst" in rbac.roles, "Analyst role not found"
        assert "viewer" in rbac.roles, "Viewer role not found"
        print("✓ System roles initialized correctly")
        
        # Test role hierarchy
        hierarchy = await rbac.get_role_hierarchy()
        assert len(hierarchy) >= 5, "Not enough roles in hierarchy"
        print("✓ Role hierarchy working")
        
        # Test permission inheritance
        admin_permissions = await rbac._get_role_permissions_recursive("admin")
        viewer_permissions = await rbac._get_role_permissions_recursive("viewer")
        assert len(admin_permissions) > len(viewer_permissions), "Permission inheritance not working"
        print("✓ Permission inheritance working")
        
        print("✓ RBAC hierarchy tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ RBAC test failed: {e}")
        return False


async def test_abac_policies():
    """Test ABAC policy evaluation"""
    
    try:
        from backend.core.abac import ABACManager, PolicyEffect
        
        abac = ABACManager()
        
        # Test default policies exist
        assert len(abac.policies) > 0, "No default policies found"
        print("✓ Default ABAC policies initialized")
        
        # Test policy evaluation
        test_context = {
            "user_data": {"role": "admin", "clearance_level": 3},
            "resource_data": {"sensitivity": "high", "owner": "test_user"},
            "environment": {"time": "10:00", "country": "US"}
        }
        
        result = await abac.evaluate_access(
            user_id="test_user",
            action="read",
            resource_type="report",
            resource_id="test_report",
            context=test_context
        )
        
        assert "decision" in result, "ABAC evaluation failed"
        print("✓ ABAC policy evaluation working")
        
        print("✓ ABAC policy tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ ABAC test failed: {e}")
        return False


def run_tests():
    """Run all tests"""
    print("🔒 Testing Enterprise Security Framework")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_security_manager(),
        test_rbac_hierarchy(), 
        test_abac_policies()
    ]
    
    # Since we can't use asyncio.run in all environments, we'll use this approach
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    results = []
    for test in tests:
        try:
            result = loop.run_until_complete(test)
            results.append(result)
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            results.append(False)
    
    loop.close()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Enterprise security framework is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    run_tests()