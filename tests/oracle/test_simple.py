"""
Simple Oracle BI Publisher integration test
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.integrations.oracle import OracleBIPublisherSDK
from backend.integrations.oracle.models import OracleReportFormat


async def test_oracle_integration():
    """Test Oracle BI Publisher integration functionality"""
    print("🔄 Starting Oracle BI Publisher Integration Test...")
    print("=" * 60)
    
    # Create Oracle SDK instance
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
        # Initialize SDK
        print("\n1. Initializing Oracle SDK...")
        await sdk.initialize()
        print("✓ Oracle SDK initialized successfully")
        
        # Test health check
        print("\n2. Testing Oracle Health Check...")
        result = await sdk.health_check()
        assert result.success is True, f"Health check failed: {result.error}"
        assert "healthy" in result.data
        print("✓ Oracle health check passed")
        
        # Test list reports
        print("\n3. Testing Report Listing...")
        result = await sdk.list_reports(
            catalog_path="/",
            include_subfolders=True,
            filter_active=True
        )
        assert result.success is True, f"List reports failed: {result.error}"
        assert isinstance(result.data, list)
        print(f"✓ Listed {len(result.data)} Oracle reports")
        
        # Test report execution if reports exist
        if result.data:
            print("\n4. Testing Report Execution...")
            report_id = result.data[0]["id"]
            
            exec_result = await sdk.execute_report(
                report_id=report_id,
                format=OracleReportFormat.PDF,
                parameters={"test_param": "test_value"},
                async_execution=True
            )
            assert exec_result.success is True, f"Report execution failed: {exec_result.error}"
            assert "execution_id" in exec_result.data
            
            execution_id = exec_result.data["execution_id"]
            print(f"✓ Report execution started: {execution_id}")
            
            # Check execution status
            status_result = await sdk.get_execution_status(execution_id)
            assert status_result.success is True, f"Status check failed: {status_result.error}"
            print("✓ Execution status retrieved")
        else:
            print("\n4. Skipping Report Execution (no reports available)")
        
        # Test data sources
        print("\n5. Testing Data Sources...")
        result = await sdk.list_data_sources()
        assert result.success is True, f"List data sources failed: {result.error}"
        assert isinstance(result.data, list)
        print(f"✓ Listed {len(result.data)} Oracle data sources")
        
        # Test folders
        print("\n6. Testing Catalog Folders...")
        result = await sdk.list_folders("/")
        assert result.success is True, f"List folders failed: {result.error}"
        assert isinstance(result.data, list)
        print(f"✓ Listed {len(result.data)} Oracle catalog folders")
        
        # Test performance metrics
        print("\n7. Testing Performance Metrics...")
        metrics = sdk.get_performance_metrics()
        assert "api_calls" in metrics
        assert "successful_calls" in metrics
        assert "connection_pool" in metrics
        print("✓ Performance metrics retrieved")
        
        # Test connection pool
        print("\n8. Testing Connection Pool...")
        pool_metrics = sdk.connection_pool.get_metrics()
        assert "total_connections" in pool_metrics
        assert "active_connections" in pool_metrics
        print("✓ Connection pool metrics validated")
        
        print("\n" + "=" * 60)
        print("✅ All Oracle BI Publisher integration tests passed!")
        
        # Display final metrics
        print(f"\nFinal Performance Metrics:")
        print(f"  API Calls: {metrics['api_calls']}")
        print(f"  Successful: {metrics['successful_calls']}")
        print(f"  Failed: {metrics['failed_calls']}")
        print(f"  Cache Hits: {metrics['cache_hits']}")
        print(f"  Cache Misses: {metrics['cache_misses']}")
        print(f"  Average Response Time: {metrics['average_response_time']:.3f}s")
        
        # Display connection pool metrics
        print(f"\nConnection Pool Metrics:")
        print(f"  Total Connections: {pool_metrics['total_connections']}")
        print(f"  Active Connections: {pool_metrics['active_connections']}")
        print(f"  Healthy Servers: {pool_metrics['healthy_servers']}/{pool_metrics['servers']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\n9. Shutting down Oracle SDK...")
        await sdk.shutdown()
        print("✓ Oracle SDK shutdown complete")


if __name__ == "__main__":
    success = asyncio.run(test_oracle_integration())
    sys.exit(0 if success else 1)