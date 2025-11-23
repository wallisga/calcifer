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
        config_path: Optional[str] = None
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
            config_path=config_path
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


# Singleton instance for easy import
service_catalog_module = ServiceCatalogModule()