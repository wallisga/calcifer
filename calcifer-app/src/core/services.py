"""
Services Core Module

Handles service catalog functionality:
- Service registration and management
- Service dependencies
- Service status tracking
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models


class ServicesCore:
    """Core functionality for service catalog management."""
    
    def create_service(
        self,
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
            ports: Optional port mapping
            cpu: Optional CPU allocation
            memory: Optional memory allocation
            config_path: Optional path to config in repo
            
        Returns:
            Created service
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
    
    def update_service(
        self,
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
            Updated service or None if not found
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
    
    def delete_service(
        self,
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
    
    def get_all_services(self, db: Session) -> List[models.Service]:
        """Get all services ordered by name."""
        return db.query(models.Service).order_by(models.Service.name).all()
    
    def get_service_by_id(
        self,
        db: Session,
        service_id: int
    ) -> Optional[models.Service]:
        """Get service by ID."""
        return db.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
    
    def get_services_by_host(
        self,
        db: Session,
        host: str
    ) -> List[models.Service]:
        """Get all services running on a specific host."""
        return db.query(models.Service).filter(
            models.Service.host == host
        ).order_by(models.Service.name).all()
    
    def get_services_by_type(
        self,
        db: Session,
        service_type: str
    ) -> List[models.Service]:
        """Get all services of a specific type."""
        return db.query(models.Service).filter(
            models.Service.service_type == service_type
        ).order_by(models.Service.name).all()
    
    def add_dependency(
        self,
        db: Session,
        service_id: int,
        depends_on_id: int
    ) -> bool:
        """
        Add a dependency relationship between services.
        
        Args:
            db: Database session
            service_id: Service that depends on another
            depends_on_id: Service that is depended upon
            
        Returns:
            True if added, False if services not found
        """
        service = self.get_service_by_id(db, service_id)
        depends_on = self.get_service_by_id(db, depends_on_id)
        
        if not service or not depends_on:
            return False
        
        # Add to depends_on list if not already there
        if depends_on_id not in service.depends_on:
            service.depends_on.append(depends_on_id)
        
        # Add to required_by list if not already there
        if service_id not in depends_on.required_by:
            depends_on.required_by.append(service_id)
        
        db.commit()
        return True
    
    def remove_dependency(
        self,
        db: Session,
        service_id: int,
        depends_on_id: int
    ) -> bool:
        """
        Remove a dependency relationship between services.
        
        Args:
            db: Database session
            service_id: Service that depends on another
            depends_on_id: Service that is depended upon
            
        Returns:
            True if removed, False if services not found
        """
        service = self.get_service_by_id(db, service_id)
        depends_on = self.get_service_by_id(db, depends_on_id)
        
        if not service or not depends_on:
            return False
        
        # Remove from depends_on list
        if depends_on_id in service.depends_on:
            service.depends_on.remove(depends_on_id)
        
        # Remove from required_by list
        if service_id in depends_on.required_by:
            depends_on.required_by.remove(service_id)
        
        db.commit()
        return True