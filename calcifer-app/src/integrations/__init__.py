"""
Calcifer Integrations

This package contains optional integrations that extend Calcifer's functionality.
Each integration is self-contained and can be enabled/disabled independently.

Available Integrations:
- git: Git operations and version control (core integration)
- monitoring: Synthetic monitoring and endpoint health checks

Future Integrations:
- uptime_kuma: Uptime Kuma API integration
- grafana: Grafana dashboard integration  
- notifications: Slack, Discord, email notifications
- backups: Automated backup management
"""

from .git import GitManager, git_manager
from .monitoring import MonitoringIntegration, monitoring

__all__ = [
    'GitManager',
    'git_manager',
    'MonitoringIntegration',
    'monitoring'
]