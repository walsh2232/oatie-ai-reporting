#!/usr/bin/env python3
"""
Performance Regression Detection Script
Compares current performance results against historical baselines
"""

import json
import sys
import statistics
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class PerformanceRegression:
    """Detects performance regressions in test results"""
    
    def __init__(self, baseline_file: str = "performance_baseline.json"):
        self.baseline_file = baseline_file
        self.regression_thresholds = {
            "response_time_increase": 20,  # 20% increase is a regression
            "success_rate_decrease": 2,   # 2% decrease is a regression
            "throughput_decrease": 15     # 15% decrease is a regression
        }
    
    def check_regression(self, current_results_file: str) -> Dict[str, Any]:
        """Check current results against baseline for regressions"""
        
        try:
            with open(current_results_file, 'r') as f:
                current_results = json.load(f)
        except FileNotFoundError:
            return {"error": f"Current results file not found: {current_results_file}"}
        
        baseline = self._load_baseline()
        if "error" in baseline:
            return baseline
        
        # Perform regression analysis
        regression_analysis = self._analyze_regression(current_results, baseline)
        
        # Update baseline if no major regressions
        if not regression_analysis["has_major_regression"]:
            self._update_baseline(current_results)
        
        return regression_analysis
    
    def _load_baseline(self) -> Dict[str, Any]:
        """Load performance baseline data"""
        
        if not Path(self.baseline_file).exists():
            # Create initial baseline
            return {"error": "No baseline exists. Current results will become the baseline."}
        
        try:
            with open(self.baseline_file, 'r') as f:
                baseline = json.load(f)
                return baseline
        except Exception as e:
            return {"error": f"Failed to load baseline: {e}"}
    
    def _analyze_regression(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current results against baseline for regressions"""
        
        regressions = []
        improvements = []
        metrics_comparison = {}
        
        # Extract metrics from both current and baseline
        current_metrics = self._extract_metrics(current)
        baseline_metrics = self._extract_metrics(baseline)
        
        # Compare response times
        if "avg_response_time" in current_metrics and "avg_response_time" in baseline_metrics:
            current_time = current_metrics["avg_response_time"]
            baseline_time = baseline_metrics["avg_response_time"]
            
            if baseline_time > 0:
                change_percent = ((current_time - baseline_time) / baseline_time) * 100
                metrics_comparison["avg_response_time"] = {
                    "current": current_time,
                    "baseline": baseline_time,
                    "change_percent": change_percent,
                    "change_direction": "increase" if change_percent > 0 else "decrease"
                }
                
                if change_percent > self.regression_thresholds["response_time_increase"]:
                    regressions.append({
                        "metric": "Average Response Time",
                        "current_value": f"{current_time:.2f}ms",
                        "baseline_value": f"{baseline_time:.2f}ms",
                        "change_percent": f"{change_percent:.1f}%",
                        "severity": "HIGH" if change_percent > 50 else "MEDIUM"
                    })
                elif change_percent < -10:  # 10% improvement
                    improvements.append({
                        "metric": "Average Response Time",
                        "improvement_percent": f"{abs(change_percent):.1f}%"
                    })
        
        # Compare success rates
        if "success_rate" in current_metrics and "success_rate" in baseline_metrics:
            current_rate = current_metrics["success_rate"]
            baseline_rate = baseline_metrics["success_rate"]
            
            change_percent = current_rate - baseline_rate
            metrics_comparison["success_rate"] = {
                "current": current_rate,
                "baseline": baseline_rate,
                "change_percent": change_percent,
                "change_direction": "increase" if change_percent > 0 else "decrease"
            }
            
            if change_percent < -self.regression_thresholds["success_rate_decrease"]:
                regressions.append({
                    "metric": "Success Rate",
                    "current_value": f"{current_rate:.1f}%",
                    "baseline_value": f"{baseline_rate:.1f}%",
                    "change_percent": f"{change_percent:.1f}%",
                    "severity": "HIGH" if abs(change_percent) > 5 else "MEDIUM"
                })
            elif change_percent > 1:  # 1% improvement
                improvements.append({
                    "metric": "Success Rate",
                    "improvement_percent": f"{change_percent:.1f}%"
                })
        
        # Compare throughput
        if "rps" in current_metrics and "rps" in baseline_metrics:
            current_rps = current_metrics["rps"]
            baseline_rps = baseline_metrics["rps"]
            
            if baseline_rps > 0:
                change_percent = ((current_rps - baseline_rps) / baseline_rps) * 100
                metrics_comparison["throughput"] = {
                    "current": current_rps,
                    "baseline": baseline_rps,
                    "change_percent": change_percent,
                    "change_direction": "increase" if change_percent > 0 else "decrease"
                }
                
                if change_percent < -self.regression_thresholds["throughput_decrease"]:
                    regressions.append({
                        "metric": "Throughput",
                        "current_value": f"{current_rps:.1f} RPS",
                        "baseline_value": f"{baseline_rps:.1f} RPS",
                        "change_percent": f"{change_percent:.1f}%",
                        "severity": "HIGH" if abs(change_percent) > 30 else "MEDIUM"
                    })
                elif change_percent > 10:  # 10% improvement
                    improvements.append({
                        "metric": "Throughput",
                        "improvement_percent": f"{change_percent:.1f}%"
                    })
        
        # Determine overall status
        has_major_regression = any(r["severity"] == "HIGH" for r in regressions)
        has_any_regression = len(regressions) > 0
        
        status = "FAILED" if has_major_regression else \
                "WARNING" if has_any_regression else \
                "PASSED"
        
        return {
            "status": status,
            "has_major_regression": has_major_regression,
            "has_any_regression": has_any_regression,
            "regressions": regressions,
            "improvements": improvements,
            "metrics_comparison": metrics_comparison,
            "timestamp": datetime.utcnow().isoformat(),
            "baseline_file": self.baseline_file
        }
    
    def _extract_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract standardized metrics from results"""
        
        metrics = {}
        
        # Handle different result formats
        if "avg_response_time" in results:
            # Python performance test format
            metrics["avg_response_time"] = results.get("avg_response_time", 0) * 1000  # Convert to ms
            metrics["success_rate"] = results.get("success_rate", 0)
            metrics["rps"] = results.get("rps", 0)
        elif "performance_metrics" in results:
            # Database stress test format
            perf = results["performance_metrics"]
            metrics["avg_response_time"] = perf.get("avg_execution_time_ms", 0)
            metrics["success_rate"] = results.get("test_summary", {}).get("success_rate", 0)
            metrics["rps"] = perf.get("queries_per_second", 0)
        elif "overall_metrics" in results:
            # Combined analysis format
            overall = results["overall_metrics"]
            metrics["avg_response_time"] = overall.get("avg_response_time_ms", 0)
            metrics["success_rate"] = overall.get("avg_success_rate_percent", 0)
            metrics["rps"] = overall.get("avg_requests_per_second", 0)
        
        return metrics
    
    def _update_baseline(self, current_results: Dict[str, Any]) -> None:
        """Update baseline with current results"""
        
        # Load existing baseline or create new one
        try:
            with open(self.baseline_file, 'r') as f:
                baseline = json.load(f)
        except FileNotFoundError:
            baseline = {"history": []}
        
        # Add current results to history
        current_metrics = self._extract_metrics(current_results)
        baseline_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": current_metrics,
            "full_results": current_results
        }
        
        # Keep only last 30 entries
        baseline.setdefault("history", []).append(baseline_entry)
        baseline["history"] = baseline["history"][-30:]
        
        # Calculate rolling averages for more stable baselines
        if len(baseline["history"]) >= 5:
            recent_metrics = [entry["metrics"] for entry in baseline["history"][-5:]]
            
            baseline["current_baseline"] = {
                "avg_response_time": statistics.mean([m.get("avg_response_time", 0) for m in recent_metrics]),
                "success_rate": statistics.mean([m.get("success_rate", 0) for m in recent_metrics]),
                "rps": statistics.mean([m.get("rps", 0) for m in recent_metrics]),
                "updated": datetime.utcnow().isoformat()
            }
        else:
            baseline["current_baseline"] = current_metrics
            baseline["current_baseline"]["updated"] = datetime.utcnow().isoformat()
        
        # Save updated baseline
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
    
    def generate_regression_report(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable regression report"""
        
        status_emoji = {
            "PASSED": "✅",
            "WARNING": "⚠️", 
            "FAILED": "❌"
        }
        
        report = f"""
# Performance Regression Report

## Status: {status_emoji.get(analysis['status'], '❓')} {analysis['status']}

**Analysis Time:** {analysis['timestamp']}
**Baseline File:** {analysis['baseline_file']}

"""
        
        if analysis["regressions"]:
            report += "## 🔻 Performance Regressions Detected\n\n"
            for regression in analysis["regressions"]:
                severity_emoji = "🔴" if regression["severity"] == "HIGH" else "🟡"
                report += f"{severity_emoji} **{regression['metric']}** ({regression['severity']})\n"
                report += f"  - Current: {regression['current_value']}\n"
                report += f"  - Baseline: {regression['baseline_value']}\n"
                report += f"  - Change: {regression['change_percent']}\n\n"
        
        if analysis["improvements"]:
            report += "## 📈 Performance Improvements\n\n"
            for improvement in analysis["improvements"]:
                report += f"✨ **{improvement['metric']}**\n"
                report += f"  - Improvement: {improvement['improvement_percent']}\n\n"
        
        if analysis["metrics_comparison"]:
            report += "## 📊 Metrics Comparison\n\n"
            for metric, comparison in analysis["metrics_comparison"].items():
                direction_emoji = "📈" if comparison["change_direction"] == "increase" else "📉"
                report += f"{direction_emoji} **{metric.replace('_', ' ').title()}**\n"
                report += f"  - Current: {comparison['current']:.2f}\n"
                report += f"  - Baseline: {comparison['baseline']:.2f}\n"
                report += f"  - Change: {comparison['change_percent']:+.1f}%\n\n"
        
        if analysis["status"] == "PASSED":
            report += "## ✅ All Performance Metrics Within Acceptable Range\n\n"
            report += "No significant regressions detected. Baseline will be updated.\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Performance regression detection')
    parser.add_argument('results_file', help='Current performance test results file')
    parser.add_argument('--baseline', default='performance_baseline.json',
                       help='Baseline file for comparison')
    parser.add_argument('--output', default='regression_report.md',
                       help='Output file for regression report')
    parser.add_argument('--fail-on-regression', action='store_true',
                       help='Exit with error code if regressions detected')
    
    args = parser.parse_args()
    
    # Run regression analysis
    detector = PerformanceRegression(args.baseline)
    analysis = detector.check_regression(args.results_file)
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        if "No baseline exists" in analysis['error']:
            # Create initial baseline
            detector._update_baseline({})
            print("Created initial baseline. Run tests again to enable regression detection.")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Generate report
    report = detector.generate_regression_report(analysis)
    
    # Save report
    with open(args.output, 'w') as f:
        f.write(report)
    
    # Print summary
    print(f"Regression Analysis: {analysis['status']}")
    if analysis["regressions"]:
        print(f"Regressions found: {len(analysis['regressions'])}")
        for reg in analysis["regressions"]:
            print(f"  - {reg['metric']}: {reg['change_percent']} ({reg['severity']})")
    
    if analysis["improvements"]:
        print(f"Improvements found: {len(analysis['improvements'])}")
        for imp in analysis["improvements"]:
            print(f"  + {imp['metric']}: {imp['improvement_percent']}")
    
    print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    if args.fail_on_regression and analysis["has_major_regression"]:
        print("Failing due to major performance regressions")
        sys.exit(1)
    elif analysis["has_any_regression"]:
        print("Warning: Performance regressions detected")
        sys.exit(0)  # Don't fail on minor regressions
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()