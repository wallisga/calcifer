"""
Monitoring Integration Module

Optional integration for endpoint monitoring and health checks.
"""

from .integration import MonitoringIntegration, monitoring
from .endpoint_module import EndpointModule, endpoint_module

__all__ = [
    'MonitoringIntegration',
    'monitoring',
    'EndpointModule',
    'endpoint_module',
]