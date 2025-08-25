#!/usr/bin/env python3
"""
Performance Analysis and Reporting Script
Analyzes performance test results and generates comprehensive reports
"""

import json
import sys
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

class PerformanceAnalyzer:
    """Analyzes performance test results from multiple sources"""
    
    def __init__(self):
        self.thresholds = {
            "avg_response_time_ms": 2000,  # 2 seconds
            "p95_response_time_ms": 5000,  # 5 seconds
            "success_rate_percent": 99.0,  # 99%
            "min_rps": 100,  # Minimum requests per second
            "max_error_rate_percent": 1.0  # 1%
        }
    
    def analyze_results(self, result_files: List[str]) -> Dict[str, Any]:
        """Analyze performance results from multiple test files"""
        
        all_results = []
        combined_metrics = {}
        
        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    result_data = json.load(f)
                    all_results.append({
                        "file": file_path,
                        "data": result_data
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        if not all_results:
            return {"error": "No valid result files found"}
        
        # Analyze each result set
        analysis_results = []
        for result in all_results:
            analysis = self._analyze_single_result(result["data"], result["file"])
            analysis_results.append(analysis)
        
        # Generate combined analysis
        combined_analysis = self._generate_combined_analysis(analysis_results)
        
        # Generate HTML report
        html_report = self._generate_html_report(analysis_results, combined_analysis)
        
        return {
            "individual_analyses": analysis_results,
            "combined_analysis": combined_analysis,
            "html_report": html_report,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _analyze_single_result(self, data: Dict[str, Any], source_file: str) -> Dict[str, Any]:
        """Analyze a single performance test result"""
        
        analysis = {
            "source_file": source_file,
            "test_type": self._identify_test_type(data),
            "metrics": {},
            "assessment": {},
            "recommendations": []
        }
        
        # Extract metrics based on test type
        if "avg_response_time" in data:
            # Python performance test format
            analysis["metrics"] = {
                "avg_response_time_ms": data.get("avg_response_time", 0) * 1000,
                "p95_response_time_ms": data.get("p95_response_time", 0) * 1000,
                "success_rate_percent": data.get("success_rate", 0),
                "requests_per_second": data.get("rps", 0),
                "total_requests": data.get("total_requests", 0)
            }
        elif "http_req_duration" in data:
            # K6 format
            analysis["metrics"] = self._extract_k6_metrics(data)
        elif "artillery" in source_file:
            # Artillery format
            analysis["metrics"] = self._extract_artillery_metrics(data)
        
        # Assess performance against thresholds
        analysis["assessment"] = self._assess_metrics(analysis["metrics"])
        
        return analysis
    
    def _identify_test_type(self, data: Dict[str, Any]) -> str:
        """Identify the type of performance test from data structure"""
        
        if "avg_response_time" in data and "assessment" in data:
            return "python_load_test"
        elif "http_req_duration" in data:
            return "k6_load_test"
        elif "aggregate" in data:
            return "artillery_load_test"
        elif "test_summary" in data and "performance_metrics" in data:
            return "database_stress_test"
        else:
            return "unknown"
    
    def _extract_k6_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from K6 test results"""
        
        metrics = {}
        
        # Extract from K6 metrics structure
        if "metrics" in data:
            k6_metrics = data["metrics"]
            
            if "http_req_duration" in k6_metrics:
                duration = k6_metrics["http_req_duration"]
                metrics["avg_response_time_ms"] = duration.get("avg", 0)
                metrics["p95_response_time_ms"] = duration.get("p(95)", 0)
            
            if "http_req_failed" in k6_metrics:
                failed = k6_metrics["http_req_failed"]
                fail_rate = failed.get("rate", 0) * 100
                metrics["success_rate_percent"] = 100 - fail_rate
            
            if "http_reqs" in k6_metrics:
                reqs = k6_metrics["http_reqs"]
                metrics["requests_per_second"] = reqs.get("rate", 0)
                metrics["total_requests"] = reqs.get("count", 0)
        
        return metrics
    
    def _extract_artillery_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from Artillery test results"""
        
        metrics = {}
        
        if "aggregate" in data:
            agg = data["aggregate"]
            
            # Response times
            if "latency" in agg:
                latency = agg["latency"]
                metrics["avg_response_time_ms"] = latency.get("mean", 0)
                metrics["p95_response_time_ms"] = latency.get("p95", 0)
            
            # Request counts
            if "counters" in agg:
                counters = agg["counters"]
                total_requests = counters.get("http.requests", 0)
                errors = counters.get("http.responses.errors", 0)
                
                metrics["total_requests"] = total_requests
                if total_requests > 0:
                    metrics["success_rate_percent"] = ((total_requests - errors) / total_requests) * 100
            
            # Request rate
            if "rates" in agg:
                rates = agg["rates"]
                metrics["requests_per_second"] = rates.get("http.request_rate", 0)
        
        return metrics
    
    def _assess_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess metrics against performance thresholds"""
        
        issues = []
        recommendations = []
        score = 100
        
        # Response time assessment
        avg_time = metrics.get("avg_response_time_ms", 0)
        if avg_time > self.thresholds["avg_response_time_ms"]:
            issues.append(f"Average response time ({avg_time:.0f}ms) exceeds threshold ({self.thresholds['avg_response_time_ms']}ms)")
            recommendations.append("Optimize slow endpoints and implement caching")
            score -= 20
        
        p95_time = metrics.get("p95_response_time_ms", 0)
        if p95_time > self.thresholds["p95_response_time_ms"]:
            issues.append(f"P95 response time ({p95_time:.0f}ms) exceeds threshold ({self.thresholds['p95_response_time_ms']}ms)")
            recommendations.append("Investigate and optimize worst-performing requests")
            score -= 15
        
        # Success rate assessment
        success_rate = metrics.get("success_rate_percent", 0)
        if success_rate < self.thresholds["success_rate_percent"]:
            issues.append(f"Success rate ({success_rate:.1f}%) below threshold ({self.thresholds['success_rate_percent']}%)")
            recommendations.append("Improve error handling and system reliability")
            score -= 25
        
        # Throughput assessment
        rps = metrics.get("requests_per_second", 0)
        if rps < self.thresholds["min_rps"]:
            issues.append(f"Request rate ({rps:.1f} RPS) below threshold ({self.thresholds['min_rps']} RPS)")
            recommendations.append("Scale infrastructure and optimize performance")
            score -= 20
        
        # Overall grade
        if score >= 90:
            grade = "EXCELLENT"
        elif score >= 80:
            grade = "GOOD"
        elif score >= 70:
            grade = "ACCEPTABLE"
        else:
            grade = "NEEDS_IMPROVEMENT"
        
        return {
            "grade": grade,
            "score": max(0, score),
            "issues": issues,
            "recommendations": recommendations,
            "meets_requirements": len(issues) == 0
        }
    
    def _generate_combined_analysis(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate combined analysis across all test results"""
        
        total_tests = len(analyses)
        successful_tests = len([a for a in analyses if a["assessment"].get("meets_requirements", False)])
        
        # Aggregate metrics
        all_avg_times = [a["metrics"].get("avg_response_time_ms", 0) for a in analyses if a["metrics"]]
        all_success_rates = [a["metrics"].get("success_rate_percent", 0) for a in analyses if a["metrics"]]
        all_rps = [a["metrics"].get("requests_per_second", 0) for a in analyses if a["metrics"]]
        
        overall_metrics = {}
        if all_avg_times:
            overall_metrics["avg_response_time_ms"] = statistics.mean(all_avg_times)
        if all_success_rates:
            overall_metrics["avg_success_rate_percent"] = statistics.mean(all_success_rates)
        if all_rps:
            overall_metrics["avg_requests_per_second"] = statistics.mean(all_rps)
        
        # Overall assessment
        overall_grade = "EXCELLENT" if successful_tests == total_tests else \
                      "GOOD" if successful_tests >= total_tests * 0.8 else \
                      "ACCEPTABLE" if successful_tests >= total_tests * 0.6 else \
                      "NEEDS_IMPROVEMENT"
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_percentage": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "overall_grade": overall_grade,
            "overall_metrics": overall_metrics,
            "test_types": list(set(a["test_type"] for a in analyses))
        }
    
    def _generate_html_report(self, analyses: List[Dict[str, Any]], combined: Dict[str, Any]) -> str:
        """Generate HTML performance report"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Oatie AI Performance Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #312e81; padding-bottom: 20px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #312e81; }}
        .grade-excellent {{ border-left-color: #28a745; }}
        .grade-good {{ border-left-color: #17a2b8; }}
        .grade-acceptable {{ border-left-color: #ffc107; }}
        .grade-needs-improvement {{ border-left-color: #dc3545; }}
        .test-result {{ margin-bottom: 30px; padding: 20px; border: 1px solid #dee2e6; border-radius: 6px; }}
        .issues {{ background-color: #f8d7da; padding: 10px; border-radius: 4px; margin-top: 10px; }}
        .recommendations {{ background-color: #d1ecf1; padding: 10px; border-radius: 4px; margin-top: 10px; }}
        h1, h2, h3 {{ color: #312e81; }}
        .timestamp {{ color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Oatie AI Performance Test Report</h1>
            <p class="timestamp">Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <div class="summary">
            <div class="metric-card grade-{combined['overall_grade'].lower().replace('_', '-')}">
                <h3>Overall Grade</h3>
                <h2>{combined['overall_grade']}</h2>
                <p>{combined['successful_tests']}/{combined['total_tests']} tests passed</p>
            </div>
            
            <div class="metric-card">
                <h3>Test Coverage</h3>
                <p><strong>Test Types:</strong> {len(combined['test_types'])}</p>
                <p>{', '.join(combined['test_types'])}</p>
            </div>
            
            <div class="metric-card">
                <h3>Average Performance</h3>
                <p><strong>Response Time:</strong> {combined['overall_metrics'].get('avg_response_time_ms', 0):.0f}ms</p>
                <p><strong>Success Rate:</strong> {combined['overall_metrics'].get('avg_success_rate_percent', 0):.1f}%</p>
                <p><strong>Throughput:</strong> {combined['overall_metrics'].get('avg_requests_per_second', 0):.1f} RPS</p>
            </div>
        </div>
        
        <h2>Individual Test Results</h2>
        """
        
        for analysis in analyses:
            grade = analysis['assessment']['grade']
            metrics = analysis['metrics']
            
            html += f"""
        <div class="test-result">
            <h3>{analysis['test_type'].replace('_', ' ').title()} - {grade}</h3>
            <p><strong>Source:</strong> {analysis['source_file']}</p>
            
            <div class="summary">
                <div class="metric-card">
                    <h4>Response Time</h4>
                    <p>Average: {metrics.get('avg_response_time_ms', 0):.0f}ms</p>
                    <p>P95: {metrics.get('p95_response_time_ms', 0):.0f}ms</p>
                </div>
                
                <div class="metric-card">
                    <h4>Reliability</h4>
                    <p>Success Rate: {metrics.get('success_rate_percent', 0):.1f}%</p>
                    <p>Total Requests: {metrics.get('total_requests', 0):,}</p>
                </div>
                
                <div class="metric-card">
                    <h4>Throughput</h4>
                    <p>RPS: {metrics.get('requests_per_second', 0):.1f}</p>
                    <p>Score: {analysis['assessment']['score']}/100</p>
                </div>
            </div>
            """
            
            if analysis['assessment']['issues']:
                html += f"""
            <div class="issues">
                <h4>⚠️ Issues Found:</h4>
                <ul>
                    {''.join(f'<li>{issue}</li>' for issue in analysis['assessment']['issues'])}
                </ul>
            </div>
            """
            
            if analysis['assessment']['recommendations']:
                html += f"""
            <div class="recommendations">
                <h4>💡 Recommendations:</h4>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in analysis['assessment']['recommendations'])}
                </ul>
            </div>
            """
            
            html += "</div>"
        
        html += """
        <div class="footer" style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d;">
            <p>Oatie AI Reporting Platform - Enterprise Performance Testing Suite</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html

def main():
    parser = argparse.ArgumentParser(description='Analyze performance test results')
    parser.add_argument('result_files', nargs='+', help='Performance test result files to analyze')
    parser.add_argument('--output-html', default='performance_report.html', 
                       help='Output HTML report file')
    parser.add_argument('--output-json', default='performance_analysis.json',
                       help='Output JSON analysis file')
    
    args = parser.parse_args()
    
    # Analyze results
    analyzer = PerformanceAnalyzer()
    analysis = analyzer.analyze_results(args.result_files)
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        sys.exit(1)
    
    # Save HTML report
    with open(args.output_html, 'w') as f:
        f.write(analysis['html_report'])
    
    # Save JSON analysis
    analysis_copy = analysis.copy()
    del analysis_copy['html_report']  # Don't include HTML in JSON
    with open(args.output_json, 'w') as f:
        json.dump(analysis_copy, f, indent=2, default=str)
    
    # Print summary
    combined = analysis['combined_analysis']
    print(f"Performance Analysis Complete!")
    print(f"Overall Grade: {combined['overall_grade']}")
    print(f"Tests Passed: {combined['successful_tests']}/{combined['total_tests']}")
    print(f"HTML Report: {args.output_html}")
    print(f"JSON Analysis: {args.output_json}")

if __name__ == "__main__":
    main()