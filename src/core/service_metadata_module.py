"""
Service Metadata Module

Manages Calcifer-specific metadata stored in service Git repositories.

Each service repository has a .calcifer/ directory containing:
- endpoints.json: Endpoint configurations for this service
- integrations.json: Which integrations are enabled/disabled
- metadata.json: General service metadata

This is CORE functionality - required for multi-service management.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .logging_module import get_logger

logger = get_logger('calcifer.core.service_metadata')


class ServiceMetadataModule:
    """
    Manage .calcifer/ metadata directory in service repositories.
    
    This stores Calcifer-specific configuration that doesn't belong
    in the service's actual config files.
    """
    
    @staticmethod
    def ensure_metadata_directory(service_git_repo_path: str) -> Path:
        """
        Ensure .calcifer/ directory exists in service repo.
        
        Creates the directory if it doesn't exist and ensures it's
        not ignored by Git.
        
        Args:
            service_git_repo_path: Path to service Git repository
            
        Returns:
            Path to .calcifer/ directory
            
        Raises:
            ValueError: If service_git_repo_path is None or empty
        """
        if not service_git_repo_path:
            raise ValueError("service_git_repo_path cannot be None or empty")
        
        repo_path = Path(os.path.expanduser(service_git_repo_path))
        
        # Create repo directory if it doesn't exist
        repo_path.mkdir(parents=True, exist_ok=True)
        
        # Create .calcifer directory
        calcifer_dir = repo_path / ".calcifer"
        calcifer_dir.mkdir(exist_ok=True)
        
        logger.info(f"Ensured .calcifer directory exists: {calcifer_dir}")
        
        # Ensure .gitignore doesn't ignore .calcifer/
        gitignore_path = repo_path / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if ".calcifer/" in content or ".calcifer" in content:
                # Remove .calcifer/ from gitignore if present
                lines = content.split('\n')
                lines = [l for l in lines if '.calcifer' not in l]
                gitignore_path.write_text('\n'.join(lines))
                logger.info("Removed .calcifer/ from .gitignore")
        
        return calcifer_dir
    
    @staticmethod
    def initialize_metadata_files(service_git_repo_path: str, service_name: str) -> None:
        """
        Initialize empty metadata files if they don't exist.
        
        Args:
            service_git_repo_path: Path to service Git repository
            service_name: Service name
        """
        calcifer_dir = ServiceMetadataModule.ensure_metadata_directory(service_git_repo_path)
        
        # Initialize endpoints.json
        endpoints_file = calcifer_dir / "endpoints.json"
        if not endpoints_file.exists():
            endpoints_file.write_text(json.dumps({
                "endpoints": [],
                "last_updated": datetime.utcnow().isoformat()
            }, indent=2))
            logger.info(f"Initialized {endpoints_file}")
        
        # Initialize integrations.json
        integrations_file = calcifer_dir / "integrations.json"
        if not integrations_file.exists():
            integrations_file.write_text(json.dumps({
                "monitoring_enabled": True,
                "git_provider_sync": True,
                "automatic_documentation": True
            }, indent=2))
            logger.info(f"Initialized {integrations_file}")
        
        # Initialize metadata.json
        metadata_file = calcifer_dir / "metadata.json"
        if not metadata_file.exists():
            metadata_file.write_text(json.dumps({
                "service_name": service_name,
                "created_date": datetime.utcnow().isoformat(),
                "managed_by": "calcifer",
                "version": "1.0.0"
            }, indent=2))
            logger.info(f"Initialized {metadata_file}")
    
    # ========================================================================
    # ENDPOINT CONFIGURATION MANAGEMENT
    # ========================================================================
    
    @staticmethod
    def save_endpoints_config(
        service_git_repo_path: str,
        endpoints: List[Dict[str, Any]]
    ) -> None:
        """
        Save endpoint configurations to service metadata.
        
        Args:
            service_git_repo_path: Path to service Git repository
            endpoints: List of endpoint configurations
        """
        calcifer_dir = ServiceMetadataModule.ensure_metadata_directory(service_git_repo_path)
        
        endpoints_file = calcifer_dir / "endpoints.json"
        with open(endpoints_file, 'w') as f:
            json.dump({
                "endpoints": endpoints,
                "last_updated": datetime.utcnow().isoformat()
            }, f, indent=2)
        
        logger.info(f"Saved {len(endpoints)} endpoints to {endpoints_file}")
    
    @staticmethod
    def load_endpoints_config(
        service_git_repo_path: str
    ) -> List[Dict[str, Any]]:
        """
        Load endpoint configurations from service metadata.
        
        Args:
            service_git_repo_path: Path to service Git repository
            
        Returns:
            List of endpoint configurations
        """
        if not service_git_repo_path:
            return []
        
        calcifer_dir = Path(os.path.expanduser(service_git_repo_path)) / ".calcifer"
        endpoints_file = calcifer_dir / "endpoints.json"
        
        if not endpoints_file.exists():
            return []
        
        try:
            with open(endpoints_file, 'r') as f:
                data = json.load(f)
                return data.get("endpoints", [])
        except Exception as e:
            logger.error(f"Error loading endpoints config: {e}")
            return []
    
    @staticmethod
    def add_endpoint_to_config(
        service_git_repo_path: str,
        endpoint_data: Dict[str, Any]
    ) -> None:
        """
        Add a single endpoint to the service's endpoint configuration.
        
        Args:
            service_git_repo_path: Path to service Git repository
            endpoint_data: Endpoint data dictionary
        """
        endpoints = ServiceMetadataModule.load_endpoints_config(service_git_repo_path)
        endpoints.append(endpoint_data)
        ServiceMetadataModule.save_endpoints_config(service_git_repo_path, endpoints)
        logger.info(f"Added endpoint {endpoint_data.get('name')} to config")
    
    @staticmethod
    def remove_endpoint_from_config(
        service_git_repo_path: str,
        endpoint_id: int
    ) -> None:
        """
        Remove an endpoint from the service's endpoint configuration.
        
        Args:
            service_git_repo_path: Path to service Git repository
            endpoint_id: Endpoint ID to remove
        """
        endpoints = ServiceMetadataModule.load_endpoints_config(service_git_repo_path)
        endpoints = [e for e in endpoints if e.get('id') != endpoint_id]
        ServiceMetadataModule.save_endpoints_config(service_git_repo_path, endpoints)
        logger.info(f"Removed endpoint {endpoint_id} from config")
    
    # ========================================================================
    # INTEGRATION SETTINGS MANAGEMENT
    # ========================================================================
    
    @staticmethod
    def save_integration_settings(
        service_git_repo_path: str,
        settings: Dict[str, Any]
    ) -> None:
        """
        Save integration settings (which integrations enabled/disabled).
        
        Args:
            service_git_repo_path: Path to service Git repository
            settings: Integration settings dictionary
        """
        calcifer_dir = ServiceMetadataModule.ensure_metadata_directory(service_git_repo_path)
        
        integrations_file = calcifer_dir / "integrations.json"
        with open(integrations_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logger.info(f"Saved integration settings to {integrations_file}")
    
    @staticmethod
    def load_integration_settings(
        service_git_repo_path: str
    ) -> Dict[str, Any]:
        """
        Load integration settings for a service.
        
        Args:
            service_git_repo_path: Path to service Git repository
            
        Returns:
            Integration settings dictionary
        """
        if not service_git_repo_path:
            return {
                "monitoring_enabled": True,
                "git_provider_sync": True,
                "automatic_documentation": True
            }
        
        calcifer_dir = Path(os.path.expanduser(service_git_repo_path)) / ".calcifer"
        integrations_file = calcifer_dir / "integrations.json"
        
        if not integrations_file.exists():
            # Return defaults
            return {
                "monitoring_enabled": True,
                "git_provider_sync": True,
                "automatic_documentation": True
            }
        
        try:
            with open(integrations_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading integration settings: {e}")
            return {}
    
    # ========================================================================
    # GENERAL METADATA MANAGEMENT
    # ========================================================================
    
    @staticmethod
    def save_metadata(
        service_git_repo_path: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Save general service metadata.
        
        Args:
            service_git_repo_path: Path to service Git repository
            metadata: Metadata dictionary
        """
        calcifer_dir = ServiceMetadataModule.ensure_metadata_directory(service_git_repo_path)
        
        metadata_file = calcifer_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata to {metadata_file}")
    
    @staticmethod
    def load_metadata(
        service_git_repo_path: str
    ) -> Dict[str, Any]:
        """
        Load general service metadata.
        
        Args:
            service_git_repo_path: Path to service Git repository
            
        Returns:
            Metadata dictionary
        """
        if not service_git_repo_path:
            return {}
        
        calcifer_dir = Path(os.path.expanduser(service_git_repo_path)) / ".calcifer"
        metadata_file = calcifer_dir / "metadata.json"
        
        if not metadata_file.exists():
            return {}
        
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}


# Singleton instance for easy import
service_metadata_module = ServiceMetadataModule()