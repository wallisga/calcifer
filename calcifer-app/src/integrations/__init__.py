"""
Calcifer Integrations

This package contains optional integrations that extend Calcifer's functionality.
Each integration is self-contained and can be enabled/disabled independently.

Available Integrations:
- git: Git operations and version control
- monitoring: Synthetic monitoring and endpoint health checks

Future Integrations:
- uptime_kuma: Uptime Kuma API integration
- grafana: Grafana dashboard integration  
- notifications: Slack, Discord, email notifications
- backups: Automated backup management
"""

from .git import GitIntegration
from .monitoring import MonitoringIntegration

__all__ = ['GitIntegration', 'MonitoringIntegration']