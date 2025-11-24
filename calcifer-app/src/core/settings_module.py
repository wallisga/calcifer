"""
Core Settings Module

Manages Calcifer configuration and settings.
This will grow as configuration needs expand.

This is CORE functionality - required for Calcifer to work.
"""

import os
from typing import Optional, Dict, Any

class SettingsModule:
    """
    Core module for managing Calcifer settings and configuration.
    
    Currently handles basic path configuration.
    Future: integration toggles, user preferences, system config.
    """
    
    def __init__(self):
        """Initialize settings with defaults."""
        self._settings = self._load_defaults()
    
    def _load_defaults(self) -> Dict[str, Any]:
        """
        Load default settings.
        
        Returns:
            Dictionary of default settings
        """
        return {
            # Paths
            "repo_path": os.getenv("REPO_PATH", "."),
            "db_path": os.getenv("DB_PATH", "./data/calcifer.db"),
            "docs_path": "docs",
            
            # Git configuration
            "default_branch": "main",
            "auto_stage": True,
            
            # Integration toggles (future)
            "monitoring_enabled": True,
            "remote_git_enabled": False,
            "notifications_enabled": False,
            
            # UI preferences (future)
            "theme": "default",
            "items_per_page": 10,
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.
        
        Returns:
            Dictionary of all settings
        """
        return self._settings.copy()
    
    # ========================================================================
    # CONVENIENCE METHODS FOR COMMON SETTINGS
    # ========================================================================
    
    @property
    def repo_path(self) -> str:
        """Get repository path."""
        return self.get("repo_path")
    
    @property
    def db_path(self) -> str:
        """Get database path."""
        return self.get("db_path")
    
    @property
    def docs_path(self) -> str:
        """Get docs directory path."""
        return self.get("docs_path")
    
    @property
    def default_branch(self) -> str:
        """Get default Git branch name."""
        return self.get("default_branch")
    
    # ========================================================================
    # INTEGRATION TOGGLES (FUTURE)
    # ========================================================================
    
    def is_integration_enabled(self, integration_name: str) -> bool:
        """
        Check if an integration is enabled.
        
        Args:
            integration_name: Name of the integration (e.g., 'monitoring')
            
        Returns:
            True if enabled, False otherwise
        """
        key = f"{integration_name}_enabled"
        return self.get(key, False)
    
    def enable_integration(self, integration_name: str) -> None:
        """
        Enable an integration.
        
        Args:
            integration_name: Name of the integration
        """
        key = f"{integration_name}_enabled"
        self.set(key, True)
    
    def disable_integration(self, integration_name: str) -> None:
        """
        Disable an integration.
        
        Args:
            integration_name: Name of the integration
        """
        key = f"{integration_name}_enabled"
        self.set(key, False)
    
    # ========================================================================
    # PERSISTENCE (FUTURE)
    # ========================================================================
    
    def save_to_file(self, path: Optional[str] = None) -> bool:
        """
        Save settings to file (future implementation).
        
        Args:
            path: Path to settings file
            
        Returns:
            True if successful
        """
        # TODO: Implement settings persistence
        # Could use JSON, YAML, or TOML format
        pass
    
    def load_from_file(self, path: Optional[str] = None) -> bool:
        """
        Load settings from file (future implementation).
        
        Args:
            path: Path to settings file
            
        Returns:
            True if successful
        """
        # TODO: Implement settings loading
        pass


# Singleton instance for easy import
settings_module = SettingsModule()