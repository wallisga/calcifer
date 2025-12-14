"""
Core Service Catalog Module

Manages the catalog of infrastructure services being monitored and maintained.

"Services" in this context refers to INFRASTRUCTURE SERVICES:
- Routers, switches, storage systems
- Virtual machines, containers
- Applications and web services

This is CORE functionality - required for Calcifer to work.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from .. import models
from .logging_module import get_logger

logger = get_logger('calcifer.core.service_catalog')

class ServiceCatalogModule:
    """
    Core module for managing infrastructure service catalog.
    
    This tracks all the services in your infrastructure:
    what they are, where they run, how they're configured.
    """
    
    @staticmethod
    def create_service(
        db: Session,
        name: str,
        service_type: str,
        host: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
        ports: Optional[str] = None,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        config_path: Optional[str] = None,
        # NEW PARAMETERS:
        git_repo_path: Optional[str] = None,
        git_repo_url: Optional[str] = None,
        git_repo_private: bool = True,
        git_provider: Optional[str] = None,
        deployment_type: Optional[str] = None,
        docker_compose_path: Optional[str] = None,
        readme_path: Optional[str] = None,
        architecture_doc: Optional[str] = None
    ) -> models.Service:
        """
        Create a new service entry in the catalog.
        
        Args:
            db: Database session
            name: Service name
            service_type: Type (container, vm, bare_metal)
            host: Host/VM where service runs
            url: Optional service URL
            description: Optional description
            ports: Optional port mappings
            cpu: Optional CPU allocation
            memory: Optional memory allocation
            config_path: Optional path to config in repo
            git_repo_path: Path to service Git repository
            git_repo_url: Remote Git repository URL
            git_repo_private: Whether repo is private (default True)
            git_provider: Git provider (github, gitlab, gitea)
            deployment_type: Deployment type (bare_metal, docker, kubernetes)
            docker_compose_path: Path to docker-compose.yml
            readme_path: Path to service README
            architecture_doc: Service architecture documentation
            
        Returns:
            Created Service model instance
        """
        service = models.Service(
            name=name,
            service_type=service_type,
            host=host,
            url=url,
            description=description,
            ports=ports,
            cpu=cpu,
            memory=memory,
            config_path=config_path,
            git_repo_path=git_repo_path,
            git_repo_url=git_repo_url,
            git_repo_private=git_repo_private,
            git_provider=git_provider,
            deployment_type=deployment_type,
            docker_compose_path=docker_compose_path,
            readme_path=readme_path,
            architecture_doc=architecture_doc
        )
        
        db.add(service)
        db.commit()
        db.refresh(service)
        
        return service
    
    @staticmethod
    def update_service(
        db: Session,
        service_id: int,
        **kwargs
    ) -> Optional[models.Service]:
        """
        Update service attributes.
        
        Args:
            db: Database session
            service_id: Service ID
            **kwargs: Attributes to update
            
        Returns:
            Updated Service or None if not found
        """
        service = db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
        
        if not service:
            return None
        
        for key, value in kwargs.items():
            if hasattr(service, key):
                setattr(service, key, value)
        
        db.commit()
        db.refresh(service)
        
        return service
    
    @staticmethod
    def delete_service(
        db: Session,
        service_id: int
    ) -> bool:
        """
        Delete a service from the catalog.
        
        Args:
            db: Database session
            service_id: Service ID
            
        Returns:
            True if deleted, False if not found
        """
        service = db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
        
        if not service:
            return False
        
        db.delete(service)
        db.commit()
        
        return True
    
    @staticmethod
    def get_all_services(db: Session) -> List[models.Service]:
        """
        Get all services ordered by name.
        
        Args:
            db: Database session
            
        Returns:
            List of Service models
        """
        return db.query(models.Service).order_by(models.Service.name).all()
    
    @staticmethod
    def get_service_by_id(
        db: Session,
        service_id: int
    ) -> Optional[models.Service]:
        """
        Get service by ID.
        
        Args:
            db: Database session
            service_id: Service ID
            
        Returns:
            Service model or None if not found
        """
        return db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
    
    @staticmethod
    def get_services_by_host(
        db: Session,
        host: str
    ) -> List[models.Service]:
        """
        Get all services running on a specific host.
        
        Args:
            db: Database session
            host: Host name
            
        Returns:
            List of Service models
        """
        return db.query(models.Service).filter(
            models.Service.host == host
        ).order_by(models.Service.name).all()
    
    @staticmethod
    def get_services_by_type(
        db: Session,
        service_type: str
    ) -> List[models.Service]:
        """
        Get all services of a specific type.
        
        Args:
            db: Database session
            service_type: Service type (container, vm, bare_metal)
            
        Returns:
            List of Service models
        """
        return db.query(models.Service).filter(
            models.Service.service_type == service_type
        ).order_by(models.Service.name).all()
    
    @staticmethod
    def add_host_to_service(
        db: Session,
        service_id: int,
        hostname: str,
        ip_address: str = None,
        role: str = None,
        description: str = None
    ) -> Optional[models.ServiceHost]:
        """
        Add a host/VM to a service.
        
        Args:
            db: Database session
            service_id: Service ID
            hostname: Host name
            ip_address: IP address (optional)
            role: Host role (e.g., "vpn-client", "api-server")
            description: Optional description
            
        Returns:
            Created ServiceHost or None if service not found
        """
        # Verify service exists
        service = db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
        
        if not service:
            return None
        
        host = models.ServiceHost(
            service_id=service_id,
            hostname=hostname,
            ip_address=ip_address,
            role=role,
            description=description
        )
        
        db.add(host)
        db.commit()
        db.refresh(host)
        
        return host
    
    @staticmethod
    def update_host(
        db: Session,
        host_id: int,
        **kwargs
    ) -> Optional[models.ServiceHost]:
        """
        Update host attributes.
        
        Args:
            db: Database session
            host_id: Host ID
            **kwargs: Attributes to update
            
        Returns:
            Updated ServiceHost or None if not found
        """
        host = db.query(models.ServiceHost).filter(
            models.ServiceHost.id == host_id
        ).first()
        
        if not host:
            return None
        
        for key, value in kwargs.items():
            if hasattr(host, key):
                setattr(host, key, value)
        
        db.commit()
        db.refresh(host)
        
        return host
    
    @staticmethod
    def delete_host(
        db: Session,
        host_id: int
    ) -> bool:
        """
        Delete a host from a service.
        
        Args:
            db: Database session
            host_id: Host ID
            
        Returns:
            True if deleted, False if not found
        """
        host = db.query(models.ServiceHost).filter(
            models.ServiceHost.id == host_id
        ).first()
        
        if not host:
            return False
        
        db.delete(host)
        db.commit()
        
        return True
    
    @staticmethod
    def get_service_hosts(
        db: Session,
        service_id: int
    ) -> List[models.ServiceHost]:
        """
        Get all hosts for a service.
        
        Args:
            db: Database session
            service_id: Service ID
            
        Returns:
            List of ServiceHost models
        """
        return db.query(models.ServiceHost).filter(
            models.ServiceHost.service_id == service_id
        ).order_by(models.ServiceHost.hostname).all()
    
    @staticmethod
    def add_config_file(
        db: Session,
        service_id: int,
        filepath: str,
        description: str = None,
        is_template: bool = False,
        git_tracked: bool = True,
        secrets_file: bool = False
    ) -> Optional[models.ServiceConfigFile]:
        """
        Track a configuration file for a service.
        
        Args:
            db: Database session
            service_id: Service ID
            filepath: File path (e.g., "/etc/nginx/sites-available/app")
            description: Optional description
            is_template: True if this is a template file
            git_tracked: Whether file is tracked in Git
            secrets_file: True if file contains secrets (.env, etc.)
            
        Returns:
            Created ServiceConfigFile or None if service not found
        """
        # Verify service exists
        service = db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
        
        if not service:
            return None
        
        config_file = models.ServiceConfigFile(
            service_id=service_id,
            filepath=filepath,
            description=description,
            is_template=is_template,
            git_tracked=git_tracked,
            secrets_file=secrets_file
        )
        
        db.add(config_file)
        db.commit()
        db.refresh(config_file)
        
        return config_file
    
    @staticmethod
    def update_config_file(
        db: Session,
        config_file_id: int,
        **kwargs
    ) -> Optional[models.ServiceConfigFile]:
        """
        Update config file attributes.
        
        Args:
            db: Database session
            config_file_id: Config file ID
            **kwargs: Attributes to update
            
        Returns:
            Updated ServiceConfigFile or None if not found
        """
        config_file = db.query(models.ServiceConfigFile).filter(
            models.ServiceConfigFile.id == config_file_id
        ).first()
        
        if not config_file:
            return None
        
        for key, value in kwargs.items():
            if hasattr(config_file, key):
                setattr(config_file, key, value)
        
        db.commit()
        db.refresh(config_file)
        
        return config_file
    
    @staticmethod
    def delete_config_file(
        db: Session,
        config_file_id: int
    ) -> bool:
        """
        Delete a config file from tracking.
        
        Args:
            db: Database session
            config_file_id: Config file ID
            
        Returns:
            True if deleted, False if not found
        """
        config_file = db.query(models.ServiceConfigFile).filter(
            models.ServiceConfigFile.id == config_file_id
        ).first()
        
        if not config_file:
            return False
        
        db.delete(config_file)
        db.commit()
        
        return True
    
    @staticmethod
    def get_service_config_files(
        db: Session,
        service_id: int
    ) -> List[models.ServiceConfigFile]:
        """
        Get all config files for a service.
        
        Args:
            db: Database session
            service_id: Service ID
            
        Returns:
            List of ServiceConfigFile models
        """
        return db.query(models.ServiceConfigFile).filter(
            models.ServiceConfigFile.service_id == service_id
        ).order_by(models.ServiceConfigFile.filepath).all()    


# Singleton instance for easy import
service_catalog_module = ServiceCatalogModule()