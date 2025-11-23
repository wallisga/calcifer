"""
Calcifer Integrations

This package contains optional integrations that extend Calcifer's functionality.
Each integration is self-contained and can be enabled/disabled independently.

Available Integrations:
- monitoring: Synthetic monitoring and endpoint health checks
- git: Git operations and version control (core integration)

Future Integrations:
- uptime_kuma: Uptime Kuma API integration
- grafana: Grafana dashboard integration  
- notifications: Slack, Discord, email notifications
- backups: Automated backup management
"""

from .monitoring import MonitoringIntegration

__all__ = ['MonitoringIntegration']