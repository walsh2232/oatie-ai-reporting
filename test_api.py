#!/usr/bin/env python3
"""
Test script to demonstrate the Oatie AI Reporting Platform API
"""

import asyncio
import json

import httpx


async def test_api():
    """Test the development API endpoints"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("🧪 Testing Oatie AI Reporting Platform API")
        print("=" * 50)

        # Test root endpoint
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                data = response.json()
                print("✅ Root endpoint working")
                print(f"   Platform: {data['message']}")
                print(f"   Version: {data['version']}")
                print()
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print(
                "💡 Make sure the server is running: uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000"
            )
            return

        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check endpoint working")
                print(f"   Status: {data['status']}")
                print(f"   Environment: {data['environment']}")
                print()
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")

        # Test Oracle features endpoint
        try:
            response = await client.get(f"{base_url}/api/v1/oracle/features")
            if response.status_code == 200:
                data = response.json()
                print("✅ Oracle features endpoint working")
                print(f"   Implementation: {data['implementation_status']}")
                print("   Core Features:")
                for feature, details in data["features"].items():
                    print(f"     • {feature}: {details['status']}")
                print()
            else:
                print(f"❌ Oracle features endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Oracle features test failed: {e}")

        # Test Oracle health endpoint
        try:
            response = await client.get(f"{base_url}/api/v1/oracle/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Oracle health endpoint working")
                print(
                    f"   Oracle BI Publisher: {data['oracle_bi_publisher']['status']}"
                )
                print(
                    f"   Integration Complete: {data['oracle_bi_publisher']['integration_complete']}"
                )
                print(f"   SDK Version: {data['sdk']['version']}")
                print()
            else:
                print(f"❌ Oracle health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Oracle health test failed: {e}")

    print("🎉 API testing complete!")
    print()
    print("📱 Access your application at:")
    print("   • Main API: http://localhost:8000")
    print("   • Interactive Docs: http://localhost:8000/docs")
    print("   • Alternative Docs: http://localhost:8000/redoc")


if __name__ == "__main__":
    asyncio.run(test_api())
