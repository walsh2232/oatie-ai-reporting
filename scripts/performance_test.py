"""
Enterprise Performance Testing Suite for 1000+ Concurrent Users
Comprehensive load testing with realistic scenarios for Oracle BI Publisher AI Assistant
"""

import asyncio
import aiohttp
import time
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import statistics

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TestResult:
    """Individual test result"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class TestScenario:
    """Performance test scenario definition"""
    name: str
    endpoint: str
    method: str = "GET"
    headers: Dict[str, str] = None
    payload: Dict[str, Any] = None
    weight: float = 1.0  # Relative frequency of this scenario
    timeout: int = 30


class PerformanceTestSuite:
    """Enterprise performance testing suite"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.results: List[TestResult] = []
        self.scenarios = self._define_test_scenarios()
    
    def _define_test_scenarios(self) -> List[TestScenario]:
        """Define realistic test scenarios for Oracle BI Publisher AI Assistant"""
        common_headers = {"Content-Type": "application/json"}
        if self.auth_token:
            common_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return [
            # Authentication scenarios
            TestScenario(
                name="login",
                endpoint="/api/v1/auth/login",
                method="POST",
                headers=common_headers,
                payload={
                    "username": f"testuser{random.randint(1, 1000)}",
                    "password": "testpass123"
                },
                weight=0.1
            ),
            
            # Health checks
            TestScenario(
                name="health_check",
                endpoint="/health",
                method="GET",
                weight=0.2
            ),
            
            # AI SQL Generation (core feature)
            TestScenario(
                name="generate_sql",
                endpoint="/api/v1/sql/generate",
                method="POST",
                headers=common_headers,
                payload={
                    "natural_language": random.choice([
                        "Show me sales by region for last quarter",
                        "Get top 10 customers by revenue",
                        "List all employees in finance department",
                        "Show monthly revenue trends",
                        "Get inventory levels by product category"
                    ]),
                    "context": "business_analytics"
                },
                weight=2.0,
                timeout=45
            ),
            
            # Report listing
            TestScenario(
                name="list_reports",
                endpoint="/api/v1/reports",
                method="GET",
                headers=common_headers,
                weight=1.5
            ),
            
            # Report generation
            TestScenario(
                name="generate_report",
                endpoint="/api/v1/reports/generate",
                method="POST",
                headers=common_headers,
                payload={
                    "template_id": f"template_{random.randint(1, 10)}",
                    "parameters": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31",
                        "region": random.choice(["North", "South", "East", "West"])
                    }
                },
                weight=1.0,
                timeout=60
            ),
            
            # Analytics dashboard
            TestScenario(
                name="dashboard_data",
                endpoint="/api/v1/analytics/dashboard",
                method="GET",
                headers=common_headers,
                weight=1.0
            ),
            
            # GraphQL queries
            TestScenario(
                name="graphql_query",
                endpoint="/graphql",
                method="POST",
                headers=common_headers,
                payload={
                    "query": """
                    query {
                        reports(limit: 10) {
                            id
                            name
                            description
                            execution_count
                        }
                        performance_metrics {
                            metric_name
                            value
                            unit
                        }
                    }
                    """
                },
                weight=0.8
            ),
            
            # User profile
            TestScenario(
                name="user_profile",
                endpoint="/api/v1/users/profile",
                method="GET",
                headers=common_headers,
                weight=0.5
            ),
            
            # Template browsing
            TestScenario(
                name="list_templates",
                endpoint="/api/v1/templates",
                method="GET",
                headers=common_headers,
                weight=0.8
            ),
            
            # Query execution history
            TestScenario(
                name="query_history",
                endpoint="/api/v1/queries/history",
                method="GET",
                headers=common_headers,
                weight=0.6
            )
        ]
    
    async def run_single_request(self, session: aiohttp.ClientSession, scenario: TestScenario) -> TestResult:
        """Execute a single test request"""
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{scenario.endpoint}"
            
            async with session.request(
                method=scenario.method,
                url=url,
                headers=scenario.headers or {},
                json=scenario.payload,
                timeout=aiohttp.ClientTimeout(total=scenario.timeout)
            ) as response:
                await response.read()  # Consume response body
                
                response_time = time.time() - start_time
                success = 200 <= response.status < 400
                
                return TestResult(
                    endpoint=scenario.endpoint,
                    method=scenario.method,
                    status_code=response.status,
                    response_time=response_time,
                    success=success
                )
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=scenario.endpoint,
                method=scenario.method,
                status_code=0,
                response_time=response_time,
                success=False,
                error="Timeout"
            )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=scenario.endpoint,
                method=scenario.method,
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def run_user_session(self, session: aiohttp.ClientSession, user_id: int, duration_seconds: int) -> List[TestResult]:
        """Simulate a realistic user session"""
        results = []
        start_time = time.time()
        
        # Create weighted scenario list
        weighted_scenarios = []
        for scenario in self.scenarios:
            count = int(scenario.weight * 10)  # Convert weight to count
            weighted_scenarios.extend([scenario] * count)
        
        while (time.time() - start_time) < duration_seconds:
            # Select random scenario based on weights
            scenario = random.choice(weighted_scenarios)
            
            # Execute request
            result = await self.run_single_request(session, scenario)
            results.append(result)
            
            # Add realistic delay between requests (0.5 to 3 seconds)
            delay = random.uniform(0.5, 3.0)
            await asyncio.sleep(delay)
        
        logger.info(f"User {user_id} completed session", requests=len(results))
        return results
    
    async def run_load_test(self, concurrent_users: int = 1000, duration_minutes: int = 10, 
                          ramp_up_seconds: int = 60) -> Dict[str, Any]:
        """Run comprehensive load test with specified parameters"""
        logger.info(
            "Starting load test",
            concurrent_users=concurrent_users,
            duration_minutes=duration_minutes,
            ramp_up_seconds=ramp_up_seconds
        )
        
        duration_seconds = duration_minutes * 60
        connector = aiohttp.TCPConnector(
            limit=concurrent_users * 2,  # Connection pool size
            limit_per_host=concurrent_users,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        session_timeout = aiohttp.ClientTimeout(total=None, connect=30)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=session_timeout
        ) as session:
            # Create tasks for all users
            tasks = []
            
            for user_id in range(concurrent_users):
                # Stagger user starts for realistic ramp-up
                start_delay = (user_id / concurrent_users) * ramp_up_seconds
                
                task = asyncio.create_task(
                    self._delayed_user_session(
                        session, user_id, duration_seconds, start_delay
                    )
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            start_time = time.time()
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Flatten results and filter out exceptions
            self.results = []
            for user_results in all_results:
                if isinstance(user_results, list):
                    self.results.extend(user_results)
                elif isinstance(user_results, Exception):
                    logger.error(f"User session failed: {user_results}")
        
        # Generate comprehensive report
        return self.generate_performance_report(total_time)
    
    async def _delayed_user_session(self, session: aiohttp.ClientSession, user_id: int, 
                                  duration_seconds: int, start_delay: float) -> List[TestResult]:
        """Run user session with initial delay for ramp-up"""
        await asyncio.sleep(start_delay)
        return await self.run_user_session(session, user_id, duration_seconds)
    
    def generate_performance_report(self, total_test_time: float) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Basic statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        # Response time statistics
        response_times = [r.response_time for r in self.results if r.success]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = self._percentile(response_times, 95)
            p99_response_time = self._percentile(response_times, 99)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = 0
            p99_response_time = min_response_time = max_response_time = 0
        
        # Throughput
        requests_per_second = total_requests / total_test_time if total_test_time > 0 else 0
        
        # Status code distribution
        status_codes = {}
        for result in self.results:
            status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1
        
        # Endpoint performance breakdown
        endpoint_stats = {}
        for result in self.results:
            key = f"{result.method} {result.endpoint}"
            if key not in endpoint_stats:
                endpoint_stats[key] = {
                    "count": 0,
                    "success_count": 0,
                    "total_time": 0,
                    "min_time": float('inf'),
                    "max_time": 0
                }
            
            stats = endpoint_stats[key]
            stats["count"] += 1
            if result.success:
                stats["success_count"] += 1
                stats["total_time"] += result.response_time
                stats["min_time"] = min(stats["min_time"], result.response_time)
                stats["max_time"] = max(stats["max_time"], result.response_time)
        
        # Calculate endpoint averages
        for stats in endpoint_stats.values():
            if stats["success_count"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["success_count"]
                stats["success_rate"] = (stats["success_count"] / stats["count"]) * 100
            else:
                stats["avg_time"] = 0
                stats["success_rate"] = 0
            
            # Clean up internal fields
            del stats["total_time"]
            if stats["min_time"] == float('inf'):
                stats["min_time"] = 0
        
        # Error analysis
        errors = {}
        for result in self.results:
            if not result.success and result.error:
                errors[result.error] = errors.get(result.error, 0) + 1
        
        # Performance assessment
        assessment = self._assess_performance(
            success_rate, avg_response_time, p95_response_time, requests_per_second
        )
        
        return {
            "test_summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate_percent": round(success_rate, 2),
                "test_duration_seconds": round(total_test_time, 2),
                "requests_per_second": round(requests_per_second, 2)
            },
            "response_times": {
                "average_ms": round(avg_response_time * 1000, 2),
                "median_ms": round(median_response_time * 1000, 2),
                "p95_ms": round(p95_response_time * 1000, 2),
                "p99_ms": round(p99_response_time * 1000, 2),
                "min_ms": round(min_response_time * 1000, 2),
                "max_ms": round(max_response_time * 1000, 2)
            },
            "status_codes": status_codes,
            "endpoint_performance": endpoint_stats,
            "errors": errors,
            "performance_assessment": assessment,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _assess_performance(self, success_rate: float, avg_response_time: float, 
                          p95_response_time: float, rps: float) -> Dict[str, Any]:
        """Assess overall performance against enterprise requirements"""
        issues = []
        recommendations = []
        
        # Success rate assessment
        if success_rate < 99.0:
            issues.append(f"Success rate ({success_rate:.1f}%) below target (99%)")
            recommendations.append("Investigate failed requests and improve error handling")
        
        # Response time assessment (target: <2s average, <5s p95)
        if avg_response_time > 2.0:
            issues.append(f"Average response time ({avg_response_time:.2f}s) exceeds target (2s)")
            recommendations.append("Optimize slow endpoints and consider caching strategies")
        
        if p95_response_time > 5.0:
            issues.append(f"P95 response time ({p95_response_time:.2f}s) exceeds target (5s)")
            recommendations.append("Review and optimize worst-performing requests")
        
        # Throughput assessment (target: handle 1000+ concurrent users)
        if rps < 100:  # Minimum expected for 1000 users
            issues.append(f"Throughput ({rps:.1f} RPS) may be insufficient for target load")
            recommendations.append("Scale infrastructure and optimize application performance")
        
        # Overall grade
        if not issues:
            grade = "EXCELLENT"
        elif len(issues) == 1:
            grade = "GOOD"
        elif len(issues) <= 2:
            grade = "ACCEPTABLE"
        else:
            grade = "NEEDS_IMPROVEMENT"
        
        return {
            "grade": grade,
            "issues": issues,
            "recommendations": recommendations,
            "meets_enterprise_requirements": len(issues) <= 1
        }


# CLI for running performance tests
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enterprise Performance Testing Suite")
    parser.add_argument("--base-url", required=True, help="Base URL of the application")
    parser.add_argument("--users", type=int, default=1000, help="Number of concurrent users")
    parser.add_argument("--duration", type=int, default=10, help="Test duration in minutes")
    parser.add_argument("--ramp-up", type=int, default=60, help="Ramp-up period in seconds")
    parser.add_argument("--auth-token", help="Authentication token")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Run performance test
    test_suite = PerformanceTestSuite(args.base_url, args.auth_token)
    
    results = await test_suite.run_load_test(
        concurrent_users=args.users,
        duration_minutes=args.duration,
        ramp_up_seconds=args.ramp_up
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())