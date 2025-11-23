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
        """Create a new service entry in the catalog."""
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
        """Update service attributes."""
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
        """Delete a service from the catalog."""
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