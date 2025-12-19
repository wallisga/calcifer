"""
Core Service Catalog Module

Manages the catalog of infrastructure services being monitored and maintained.

"Services" in this context refers to INFRASTRUCTURE SERVICES:
- Routers, switches, storage systems
- Virtual machines, containers
- Applications and web services

This is CORE functionality - required for Calcifer to work.
"""

from typing import List, Optional, Tuple
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
    def create_service_with_work_item(
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
        git_repo_path: Optional[str] = None,
        git_repo_url: Optional[str] = None,
        git_repo_private: bool = True,
        git_provider: Optional[str] = None,
        deployment_type: Optional[str] = None,
        docker_compose_path: Optional[str] = None,
        readme_path: Optional[str] = None,
        architecture_doc: Optional[str] = None
    ) -> Tuple[models.Service, models.WorkItem]:
        """Create service with automatic work item tracking."""
        from . import work_module
        from . import service_metadata_module
        
        # 1. Create work item first
        work_item = work_module.create_work_item(
            db,
            title=f"Create service: {name}",
            category="service",
            action_type="new",
            description=f"""Set up {service_type} service on {host}

{description or 'No additional description provided.'}

This work item was automatically created to track the service setup process.
"""
        )
        
        # 2. Create service - PASS ALL PARAMETERS!
        service = ServiceCatalogModule.create_service(
            db,
            name=name,
            service_type=service_type,
            host=host,
            url=url,
            description=description,
            ports=ports,
            cpu=cpu,
            memory=memory,
            config_path=config_path,
            git_repo_path=git_repo_path,              # ← Make sure these are here
            git_repo_url=git_repo_url,                # ← Make sure these are here
            git_repo_private=git_repo_private,        # ← Make sure these are here
            git_provider=git_provider,                # ← Make sure these are here
            deployment_type=deployment_type,          # ← Make sure these are here
            docker_compose_path=docker_compose_path,  # ← Make sure these are here
            readme_path=readme_path,                  # ← Make sure these are here
            architecture_doc=architecture_doc         # ← Make sure these are here
        )
        
        # 3. Initialize service metadata if Git repo configured
        if git_repo_path:
            try:
                service_metadata_module.initialize_metadata_files(
                    git_repo_path,
                    name
                )
                logger.info(f"Initialized .calcifer/ metadata for {name}")
            except Exception as e:
                logger.error(f"Failed to initialize metadata: {e}")
        
        # 4. Update work item with service_id (link them)
        work_item.service_id = service.id
        db.commit()
        
        # 5. Update work item notes with service details
        work_module.update_notes(
            db,
            work_item.id,
            f"""# Service Created: {name}

**Service ID:** {service.id}  
**Type:** {service_type}  
**Host:** {host}  
**Status:** {service.status}

## Service Details

{f"**URL:** {url}" if url else ""}
{f"**Ports:** {ports}" if ports else ""}
{f"**Resources:** {cpu} CPU, {memory} RAM" if cpu or memory else ""}

## Description

{description or 'No description provided.'}

## Git Repository

{f"**Path:** {git_repo_path}" if git_repo_path else ""}
{f"**Remote:** {git_repo_url}" if git_repo_url else ""}
{f"**Provider:** {git_provider}" if git_provider else ""}
{f"**Private:** {'Yes' if git_repo_private else 'No'}" if git_repo_path else ""}

## Deployment

{f"**Type:** {deployment_type}" if deployment_type else ""}
{f"**Docker Compose:** {docker_compose_path}" if docker_compose_path else ""}

## Next Steps

The service has been created and cataloged. Complete these steps:

1. ✅ Service registered in catalog
2. Add hosts (if multi-host service)
3. Track configuration files
4. Set up monitoring endpoints
5. Complete service documentation
6. Verify deployment

Once the service is fully configured and documented, you can complete this work item.
"""
        )
        
        return service, work_item
    
    @staticmethod
    def get_service_detail(
        db: Session,
        service_id: int
    ) -> Optional[dict]:
        """
        Get service with all related data for detail page.
        
        Args:
            db: Database session
            service_id: Service ID
            
        Returns:
            Dictionary with service and related data, or None if not found
        """
        service = db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
        
        if not service:
            return None
        
        # NEW: Get work items related to this service
        from . import work_module
        work_items = work_module.get_work_items_for_service(db, service_id)
        
        # NEW: Get endpoints related to this service
        endpoints = db.query(models.Endpoint).filter(
            models.Endpoint.service_id == service_id
        ).order_by(models.Endpoint.name).all()
        
        return {
            "service": service,
            "work_items": work_items,
            "endpoints": endpoints
        }   

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

# Singleton instance for easy import
service_catalog_module = ServiceCatalogModule()