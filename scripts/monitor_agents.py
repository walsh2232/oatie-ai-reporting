#!/usr/bin/env python3
"""
Automated Agent Monitoring & Management Script
Monitors GitHub Copilot Coding Agent progress and provides status updates
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentMonitor:
    """Monitor GitHub Copilot Coding Agents and provide automated status updates"""
    
    def __init__(self, repo_owner: str = "walsh2232", repo_name: str = "oatie-ai-reporting"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.monitoring_interval = 3600  # 1 hour in seconds
        
    async def get_pull_requests(self) -> List[Dict]:
        """Get current pull requests via GitHub CLI"""
        try:
            cmd = f"gh pr list --repo {self.repo_owner}/{self.repo_name} --json number,title,state,createdAt,updatedAt,author,draft"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Failed to get PRs: {result.stderr}")
                return []
        except Exception as e:
            logger.error(f"Error fetching PRs: {e}")
            return []
    
    async def get_issues(self) -> List[Dict]:
        """Get current issues via GitHub CLI"""
        try:
            cmd = f"gh issue list --repo {self.repo_owner}/{self.repo_name} --json number,title,state,createdAt,updatedAt,assignees,labels"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Failed to get issues: {result.stderr}")
                return []
        except Exception as e:
            logger.error(f"Error fetching issues: {e}")
            return []
    
    def analyze_pr_status(self, pr: Dict) -> str:
        """Analyze PR status and determine completion level"""
        updated_at = datetime.fromisoformat(pr['updatedAt'].replace('Z', '+00:00'))
        time_since_update = datetime.now().astimezone() - updated_at
        
        # Determine status based on various factors
        if pr['draft']:
            if time_since_update.days >= 2:
                return "🔴 STALE - No updates for 2+ days"
            elif "complete" in pr['title'].lower() or "✅" in pr['title']:
                return "✅ COMPLETE - Ready for review/merge"
            else:
                return "🟡 IN_PROGRESS - Active development"
        else:
            return "✅ READY - Awaiting merge"
    
    def analyze_issue_status(self, issue: Dict) -> str:
        """Analyze issue status and agent assignment"""
        assignees = issue.get('assignees', [])
        has_copilot = any('copilot' in assignee.get('login', '').lower() for assignee in assignees)
        
        updated_at = datetime.fromisoformat(issue['updatedAt'].replace('Z', '+00:00'))
        time_since_update = datetime.now().astimezone() - updated_at
        
        if has_copilot:
            if time_since_update.days >= 3:
                return "🔴 AGENT_STALE - No activity for 3+ days"
            else:
                return "🟡 AGENT_ACTIVE - Copilot working"
        else:
            return "⚪ UNASSIGNED - Available for agent"
    
    async def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        prs = await self.get_pull_requests()
        issues = await self.get_issues()
        
        report = f"""
# 🤖 Automated Agent Status Report
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Pull Request Status ({len(prs)} total)
"""
        
        # Categorize PRs
        completed_prs = []
        active_prs = []
        stale_prs = []
        
        for pr in prs:
            status = self.analyze_pr_status(pr)
            if "COMPLETE" in status or "READY" in status:
                completed_prs.append((pr, status))
            elif "STALE" in status:
                stale_prs.append((pr, status))
            else:
                active_prs.append((pr, status))
        
        # Report completed PRs
        if completed_prs:
            report += f"\n### ✅ Completed/Ready for Merge ({len(completed_prs)})\n"
            for pr, status in completed_prs:
                report += f"- **PR #{pr['number']}**: {pr['title']} - {status}\n"
        
        # Report active PRs
        if active_prs:
            report += f"\n### 🟡 Active Development ({len(active_prs)})\n"
            for pr, status in active_prs:
                report += f"- **PR #{pr['number']}**: {pr['title']} - {status}\n"
        
        # Report stale PRs
        if stale_prs:
            report += f"\n### 🔴 Attention Needed ({len(stale_prs)})\n"
            for pr, status in stale_prs:
                report += f"- **PR #{pr['number']}**: {pr['title']} - {status}\n"
        
        # Issue/Agent Analysis
        report += f"\n## 🎯 Agent Assignment Status\n"
        
        assigned_issues = []
        unassigned_issues = []
        stale_agents = []
        
        for issue in issues:
            if issue['state'] == 'open':
                status = self.analyze_issue_status(issue)
                if "AGENT_ACTIVE" in status:
                    assigned_issues.append((issue, status))
                elif "AGENT_STALE" in status:
                    stale_agents.append((issue, status))
                elif "UNASSIGNED" in status:
                    unassigned_issues.append((issue, status))
        
        if assigned_issues:
            report += f"\n### 🟡 Active Agents ({len(assigned_issues)})\n"
            for issue, status in assigned_issues:
                report += f"- **Issue #{issue['number']}**: {issue['title']} - {status}\n"
        
        if stale_agents:
            report += f"\n### 🔴 Stale Agents - Intervention Needed ({len(stale_agents)})\n"
            for issue, status in stale_agents:
                report += f"- **Issue #{issue['number']}**: {issue['title']} - {status}\n"
        
        if unassigned_issues:
            report += f"\n### ⚪ Available for Assignment ({len(unassigned_issues)})\n"
            for issue, status in unassigned_issues[:5]:  # Show top 5
                report += f"- **Issue #{issue['number']}**: {issue['title']} - {status}\n"
        
        # Recommendations
        report += f"\n## 🎯 Recommended Actions\n"
        
        if completed_prs:
            report += f"1. **MERGE READY PRS**: {len(completed_prs)} PRs are ready for review/merge\n"
        
        if stale_prs:
            report += f"2. **CHECK STALE PRS**: {len(stale_prs)} PRs need attention\n"
        
        if stale_agents:
            report += f"3. **REASSIGN STALE AGENTS**: {len(stale_agents)} agents may need reassignment\n"
        
        if unassigned_issues:
            report += f"4. **ASSIGN NEW AGENTS**: {len(unassigned_issues)} issues available for agents\n"
        
        # API Utilization estimate
        total_active = len(assigned_issues) + len(active_prs)
        api_utilization = min(total_active * 15, 100)  # Rough estimate
        
        report += f"\n## 📊 Resource Utilization\n"
        report += f"- **Active Agents**: {len(assigned_issues)}\n"
        report += f"- **Active PRs**: {len(active_prs)}\n"
        report += f"- **Estimated API Utilization**: {api_utilization}%\n"
        
        return report
    
    async def save_report(self, report: str):
        """Save report to file and optionally create GitHub issue"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"agent_status_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Status report saved to {filename}")
        
        # Optionally create GitHub issue with report
        # This could be enabled for critical situations
        
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting agent monitoring loop...")
        
        while True:
            try:
                logger.info("Generating status report...")
                report = await self.generate_status_report()
                await self.save_report(report)
                
                # Print summary to console
                print("\n" + "="*60)
                print("🤖 AGENT MONITORING SUMMARY")
                print("="*60)
                print(report[:500] + "..." if len(report) > 500 else report)
                print("="*60)
                
                # Wait for next check
                logger.info(f"Next check in {self.monitoring_interval/3600} hours...")
                await asyncio.sleep(self.monitoring_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

async def main():
    """Main entry point"""
    monitor = AgentMonitor()
    
    # Generate immediate report
    print("🚀 Generating immediate status report...")
    report = await monitor.generate_status_report()
    await monitor.save_report(report)
    print(report)
    
    # Ask if user wants continuous monitoring
    response = input("\n🔄 Start continuous monitoring? (y/n): ")
    if response.lower() in ['y', 'yes']:
        await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main())
