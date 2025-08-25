"""
Integration tests for Oracle BI Publisher SDK
"""

import asyncio
import pytest
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.integrations.oracle import OracleBIPublisherSDK
from backend.integrations.oracle.models import OracleReportFormat, OracleReportStatus


class TestOracleIntegration:
    """Test Oracle BI Publisher integration functionality"""
    
    @pytest.fixture
    async def oracle_sdk(self):
        """Create Oracle SDK instance for testing"""
        sdk = OracleBIPublisherSDK(
            server_urls=["http://localhost:9502"],  # Mock Oracle BI Publisher server
            username="test_user",
            password="test_pass",
            encryption_key="test_encryption_key_32_chars_long",
            pool_size=5,
            timeout=10,
            enable_caching=True,
            cache_ttl=60
        )
        
        await sdk.initialize()
        yield sdk
        await sdk.shutdown()
    
    async def test_oracle_health_check(self, oracle_sdk):
        """Test Oracle BI Publisher health check"""
        result = await oracle_sdk.health_check()
        
        assert result.success is True
        assert "healthy" in result.data
        assert "server_status" in result.data
        assert "connection_pool" in result.data
        
        print("✓ Oracle health check passed")
    
    async def test_list_reports(self, oracle_sdk):
        """Test listing Oracle BI Publisher reports"""
        result = await oracle_sdk.list_reports(
            catalog_path="/",
            include_subfolders=True,
            filter_active=True
        )
        
        assert result.success is True
        assert isinstance(result.data, list)
        
        if result.data:
            report = result.data[0]
            assert "id" in report
            assert "name" in report
            assert "catalog_path" in report
        
        print(f"✓ Listed {len(result.data)} Oracle reports")
    
    async def test_execute_report(self, oracle_sdk):
        """Test Oracle BI Publisher report execution"""
        # First list reports to get a valid report ID
        list_result = await oracle_sdk.list_reports()
        assert list_result.success is True
        
        if not list_result.data:
            print("! No reports available for execution test")
            return
        
        report_id = list_result.data[0]["id"]
        
        # Execute the report
        result = await oracle_sdk.execute_report(
            report_id=report_id,
            format=OracleReportFormat.PDF,
            parameters={"test_param": "test_value"},
            async_execution=True
        )
        
        assert result.success is True
        assert "execution_id" in result.data
        assert "status" in result.data
        
        execution_id = result.data["execution_id"]
        
        # Check execution status
        status_result = await oracle_sdk.get_execution_status(execution_id)
        assert status_result.success is True
        
        print(f"✓ Report execution started: {execution_id}")
    
    async def test_list_data_sources(self, oracle_sdk):
        """Test listing Oracle BI Publisher data sources"""
        result = await oracle_sdk.list_data_sources()
        
        assert result.success is True
        assert isinstance(result.data, list)
        
        if result.data:
            datasource = result.data[0]
            assert "name" in datasource
            assert "type" in datasource
            assert "active" in datasource
        
        print(f"✓ Listed {len(result.data)} Oracle data sources")
    
    async def test_list_folders(self, oracle_sdk):
        """Test listing Oracle BI Publisher catalog folders"""
        result = await oracle_sdk.list_folders("/")
        
        assert result.success is True
        assert isinstance(result.data, list)
        
        if result.data:
            folder = result.data[0]
            assert "path" in folder
            assert "name" in folder
        
        print(f"✓ Listed {len(result.data)} Oracle catalog folders")
    
    async def test_performance_metrics(self, oracle_sdk):
        """Test Oracle SDK performance metrics"""
        metrics = oracle_sdk.get_performance_metrics()
        
        assert "api_calls" in metrics
        assert "successful_calls" in metrics
        assert "connection_pool" in metrics
        assert "auth_stats" in metrics
        
        print("✓ Performance metrics retrieved")
    
    async def test_connection_pool(self, oracle_sdk):
        """Test Oracle connection pool functionality"""
        pool_metrics = oracle_sdk.connection_pool.get_metrics()
        
        assert "total_connections" in pool_metrics
        assert "active_connections" in pool_metrics
        assert "servers" in pool_metrics
        assert "healthy_servers" in pool_metrics
        
        print("✓ Connection pool metrics validated")


async def run_integration_tests():
    """Run all Oracle integration tests"""
    print("🔄 Starting Oracle BI Publisher Integration Tests...")
    print("=" * 60)
    
    # Create test instance
    test_instance = TestOracleIntegration()
    
    # Create Oracle SDK fixture
    sdk = OracleBIPublisherSDK(
        server_urls=["http://localhost:9502"],
        username="test_user", 
        password="test_pass",
        encryption_key="test_encryption_key_32_chars_long",
        pool_size=5,
        timeout=10,
        enable_caching=True,
        cache_ttl=60
    )
    
    try:
        await sdk.initialize()
        
        # Run tests
        print("\n1. Testing Oracle Health Check...")
        await test_instance.test_oracle_health_check(sdk)
        
        print("\n2. Testing Report Listing...")
        await test_instance.test_list_reports(sdk)
        
        print("\n3. Testing Report Execution...")
        await test_instance.test_execute_report(sdk)
        
        print("\n4. Testing Data Sources...")
        await test_instance.test_list_data_sources(sdk)
        
        print("\n5. Testing Catalog Folders...")
        await test_instance.test_list_folders(sdk)
        
        print("\n6. Testing Performance Metrics...")
        await test_instance.test_performance_metrics(sdk)
        
        print("\n7. Testing Connection Pool...")
        await test_instance.test_connection_pool(sdk)
        
        print("\n" + "=" * 60)
        print("✅ All Oracle BI Publisher integration tests passed!")
        
        # Display final metrics
        metrics = sdk.get_performance_metrics()
        print(f"\nFinal Metrics:")
        print(f"  API Calls: {metrics['api_calls']}")
        print(f"  Successful: {metrics['successful_calls']}")
        print(f"  Failed: {metrics['failed_calls']}")
        print(f"  Cache Hits: {metrics['cache_hits']}")
        print(f"  Average Response Time: {metrics['average_response_time']:.3f}s")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        await sdk.shutdown()


if __name__ == "__main__":
    asyncio.run(run_integration_tests())