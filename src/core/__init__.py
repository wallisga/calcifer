"""
Core Modules

Business logic for core Calcifer functionality.
These modules are REQUIRED for Calcifer to work.

Core modules handle:
- Work item management (work_module)
- Service catalog management (service_catalog_module)  
- Documentation management (documentation_module)
- Local Git operations (git_module)
- Settings/configuration (settings_module)

Core modules can use other core modules but CANNOT use integrations.
"""

from .work_module import WorkModule, work_module
from .service_catalog_module import ServiceCatalogModule, service_catalog_module
from .documentation_module import DocumentationModule, documentation_module
from .git_module import GitModule, git_module
from .settings_module import SettingsModule, settings_module
from .service_metadata_module import ServiceMetadataModule, service_metadata_module

__all__ = [
    'WorkModule', 'work_module',
    'ServiceCatalogModule', 'service_catalog_module',
    'DocumentationModule', 'documentation_module',
    'GitModule', 'git_module',
    'SettingsModule', 'settings_module',
    'ServiceMetadataModule', 'service_metadata_module'
]