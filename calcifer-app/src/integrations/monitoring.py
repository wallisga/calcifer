import subprocess
import socket
import urllib.request
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session


class MonitoringIntegration:
    """
    Synthetic monitoring integration for Calcifer.
    
    Provides health checking for various endpoint types:
    - Network (ICMP ping)
    - TCP (port connectivity)
    - HTTP/HTTPS (web service availability)
    
    Future endpoint types:
    - OS (WMI for Windows, SNMP for Linux)
    - Application (custom instrumentation)
    - Database (connection checks)
    """
    
    def __init__(self, timeout: int = 5):
        """
        Initialize monitoring integration.
        
        Args:
            timeout: Default timeout in seconds for checks
        """
        self.timeout = timeout
    
    def check_connectivity(self) -> bool:
        """
        Test if monitoring integration is working.
        
        Returns:
            True if monitoring can be performed
        """
        # Basic test - can we run subprocess commands?
        try:
            result = subprocess.run(['echo', 'test'], capture_output=True, timeout=1)
            return result.returncode == 0
        except:
            return False
    
    def check_endpoint(self, endpoint) -> Tuple[bool, Optional[str]]:
        """
        Perform health check on an endpoint.
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            Tuple of (is_up: bool, error_message: Optional[str])
        """
        check_method = {
            'network': self._check_network,
            'tcp': self._check_tcp,
            'http': self._check_http,
            'https': self._check_https,
        }.get(endpoint.endpoint_type)
        
        if not check_method:
            return False, f"Unknown endpoint type: {endpoint.endpoint_type}"
        
        try:
            return check_method(endpoint)
        except Exception as e:
            return False, f"Check failed: {str(e)}"
    
    def _check_network(self, endpoint) -> Tuple[bool, Optional[str]]:
        """Perform ICMP ping check."""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(self.timeout), endpoint.target],
                capture_output=True,
                timeout=self.timeout + 1
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, "Host unreachable"
        except subprocess.TimeoutExpired:
            return False, "Ping timeout"
        except Exception as e:
            return False, f"Ping error: {str(e)}"
    
    def _check_tcp(self, endpoint) -> Tuple[bool, Optional[str]]:
        """Perform TCP port connectivity check."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((endpoint.target, endpoint.port))
            sock.close()
            
            if result == 0:
                return True, None
            else:
                return False, f"Port {endpoint.port} closed or filtered"
        except socket.timeout:
            return False, f"Connection timeout to port {endpoint.port}"
        except Exception as e:
            return False, f"TCP error: {str(e)}"
    
    def _check_http(self, endpoint) -> Tuple[bool, Optional[str]]:
        """Perform HTTP request check."""
        return self._check_web(endpoint, 'http')
    
    def _check_https(self, endpoint) -> Tuple[bool, Optional[str]]:
        """Perform HTTPS request check."""
        return self._check_web(endpoint, 'https')
    
    def _check_web(self, endpoint, protocol: str) -> Tuple[bool, Optional[str]]:
        """Perform HTTP/HTTPS request check."""
        try:
            port_part = f":{endpoint.port}" if endpoint.port else ""
            url = f"{protocol}://{endpoint.target}{port_part}"
            
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Calcifer-Monitor/1.0')
            
            response = urllib.request.urlopen(req, timeout=self.timeout)
            status = response.status
            
            if status < 400:
                return True, None
            else:
                return False, f"HTTP {status}"
                
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return False, f"URL error: {str(e.reason)}"
        except Exception as e:
            return False, f"Web check error: {str(e)}"
    
    def update_endpoint_status(self, endpoint, db: Session) -> bool:
        """
        Check endpoint and update its status in database.
        
        Args:
            endpoint: Endpoint model instance
            db: Database session
            
        Returns:
            True if endpoint is up, False otherwise
        """
        is_up, error_msg = self.check_endpoint(endpoint)
        
        # Update status
        endpoint.last_check = datetime.utcnow()
        
        if is_up:
            endpoint.status = "up"
            endpoint.last_up = datetime.utcnow()
            endpoint.consecutive_failures = 0
        else:
            endpoint.status = "down"
            endpoint.last_down = datetime.utcnow()
            endpoint.consecutive_failures += 1
            
            # Store error message in monitor_config for debugging
            if not isinstance(endpoint.monitor_config, dict):
                endpoint.monitor_config = {}
            endpoint.monitor_config['last_error'] = error_msg
        
        db.commit()
        return is_up


# Singleton instance for easy import
monitoring = MonitoringIntegration()