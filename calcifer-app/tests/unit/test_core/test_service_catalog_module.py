"""
Unit tests for service_catalog_module.

Tests service catalog CRUD operations and queries.
"""

import pytest
from src.core import service_catalog_module
from src import models


class TestServiceCatalogCreate:
    """Test service creation."""
    
    @pytest.mark.unit
    def test_create_service_basic(self, db_session):
        """Test basic service creation."""
        # Arrange
        name = "Test Service"
        service_type = "container"
        host = "test-host"
        
        # Act
        result = service_catalog_module.create_service(
            db_session,
            name=name,
            service_type=service_type,
            host=host
        )
        
        # Assert
        assert result is not None
        assert result.name == name
        assert result.service_type == service_type
        assert result.host == host
        assert result.status == "active"  # Default status
        assert result.id is not None
        
        # Verify persisted to database
        db_service = db_session.query(models.Service).filter(
            models.Service.id == result.id
        ).first()
        assert db_service is not None
    
    @pytest.mark.unit
    def test_create_service_with_all_fields(self, db_session):
        """Test service creation with all optional fields."""
        # Arrange
        service_data = {
            "name": "Full Service",
            "service_type": "vm",
            "host": "proxmox",
            "url": "http://example.com",
            "description": "Test description",
            "ports": "8080:80",
            "cpu": "4 vCPU",
            "memory": "8GB",
            "config_path": "/config/service.yml"
        }
        
        # Act
        result = service_catalog_module.create_service(db_session, **service_data)
        
        # Assert
        assert result.name == service_data["name"]
        assert result.url == service_data["url"]
        assert result.description == service_data["description"]
        assert result.ports == service_data["ports"]
        assert result.cpu == service_data["cpu"]
        assert result.memory == service_data["memory"]
        assert result.config_path == service_data["config_path"]
    
    @pytest.mark.unit
    def test_create_different_service_types(self, db_session):
        """Test creating services of different types."""
        # Arrange
        service_types = ["container", "vm", "bare_metal"]
        
        # Act & Assert
        for stype in service_types:
            service = service_catalog_module.create_service(
                db_session,
                name=f"Test {stype}",
                service_type=stype,
                host="test-host"
            )
            assert service.service_type == stype
            assert service.id is not None


class TestServiceCatalogRetrieve:
    """Test service retrieval operations."""
    
    @pytest.mark.unit
    def test_get_all_services_empty(self, db_session):
        """Test get_all_services with empty database."""
        # Act
        results = service_catalog_module.get_all_services(db_session)
        
        # Assert
        assert results == []
    
    @pytest.mark.unit
    def test_get_all_services(self, db_session, sample_service):
        """Test retrieving all services."""
        # Act
        results = service_catalog_module.get_all_services(db_session)
        
        # Assert
        assert len(results) >= 1
        assert sample_service.id in [s.id for s in results]
    
    @pytest.mark.unit
    def test_get_all_services_ordered_by_name(self, db_session):
        """Test that services are returned in alphabetical order."""
        # Arrange - Create services with different names
        service_catalog_module.create_service(
            db_session, name="Zebra Service", service_type="container", host="host1"
        )
        service_catalog_module.create_service(
            db_session, name="Alpha Service", service_type="container", host="host2"
        )
        service_catalog_module.create_service(
            db_session, name="Beta Service", service_type="container", host="host3"
        )
        
        # Act
        results = service_catalog_module.get_all_services(db_session)
        
        # Assert - Should be alphabetically ordered
        names = [s.name for s in results]
        assert names == sorted(names)
        assert names[0] == "Alpha Service"
    
    @pytest.mark.unit
    def test_get_service_by_id_success(self, db_session, sample_service):
        """Test retrieving service by ID."""
        # Act
        result = service_catalog_module.get_service_by_id(
            db_session, sample_service.id
        )
        
        # Assert
        assert result is not None
        assert result.id == sample_service.id
        assert result.name == sample_service.name
    
    @pytest.mark.unit
    def test_get_service_by_id_not_found(self, db_session):
        """Test retrieving non-existent service."""
        # Act
        result = service_catalog_module.get_service_by_id(db_session, 9999)
        
        # Assert
        assert result is None
    
    @pytest.mark.unit
    def test_get_services_by_host(self, db_session):
        """Test filtering services by host."""
        # Arrange - Create services on different hosts
        service_catalog_module.create_service(
            db_session, name="Service 1", service_type="container", host="host-a"
        )
        service_catalog_module.create_service(
            db_session, name="Service 2", service_type="container", host="host-a"
        )
        service_catalog_module.create_service(
            db_session, name="Service 3", service_type="container", host="host-b"
        )
        
        # Act
        results = service_catalog_module.get_services_by_host(db_session, "host-a")
        
        # Assert
        assert len(results) == 2
        assert all(s.host == "host-a" for s in results)
    
    @pytest.mark.unit
    def test_get_services_by_host_empty(self, db_session):
        """Test filtering by host with no matches."""
        # Act
        results = service_catalog_module.get_services_by_host(
            db_session, "nonexistent-host"
        )
        
        # Assert
        assert results == []
    
    @pytest.mark.unit
    def test_get_services_by_type(self, db_session):
        """Test filtering services by type."""
        # Arrange - Create services of different types
        service_catalog_module.create_service(
            db_session, name="Container 1", service_type="container", host="host1"
        )
        service_catalog_module.create_service(
            db_session, name="Container 2", service_type="container", host="host2"
        )
        service_catalog_module.create_service(
            db_session, name="VM 1", service_type="vm", host="host3"
        )
        
        # Act
        containers = service_catalog_module.get_services_by_type(
            db_session, "container"
        )
        vms = service_catalog_module.get_services_by_type(db_session, "vm")
        
        # Assert
        assert len(containers) == 2
        assert all(s.service_type == "container" for s in containers)
        assert len(vms) == 1
        assert vms[0].service_type == "vm"


class TestServiceCatalogUpdate:
    """Test service update operations."""
    
    @pytest.mark.unit
    def test_update_service_single_field(self, db_session, sample_service):
        """Test updating a single service field."""
        # Arrange
        new_description = "Updated description"
        
        # Act
        result = service_catalog_module.update_service(
            db_session,
            sample_service.id,
            description=new_description
        )
        
        # Assert
        assert result is not None
        assert result.description == new_description
        
        # Verify other fields unchanged
        assert result.name == sample_service.name
        assert result.service_type == sample_service.service_type
        
        # Verify persistence
        db_session.refresh(sample_service)
        assert sample_service.description == new_description
    
    @pytest.mark.unit
    def test_update_service_multiple_fields(self, db_session, sample_service):
        """Test updating multiple service fields."""
        # Arrange
        updates = {
            "url": "http://updated.com",
            "cpu": "8 vCPU",
            "memory": "16GB",
            "status": "maintenance"
        }
        
        # Act
        result = service_catalog_module.update_service(
            db_session,
            sample_service.id,
            **updates
        )
        
        # Assert
        assert result.url == updates["url"]
        assert result.cpu == updates["cpu"]
        assert result.memory == updates["memory"]
        assert result.status == updates["status"]
    
    @pytest.mark.unit
    def test_update_service_status(self, db_session, sample_service):
        """Test updating service status."""
        # Arrange
        statuses = ["active", "inactive", "maintenance"]
        
        # Act & Assert
        for status in statuses:
            result = service_catalog_module.update_service(
                db_session,
                sample_service.id,
                status=status
            )
            assert result.status == status
    
    @pytest.mark.unit
    def test_update_nonexistent_service(self, db_session):
        """Test updating non-existent service."""
        # Act
        result = service_catalog_module.update_service(
            db_session,
            9999,
            description="New description"
        )
        
        # Assert
        assert result is None
    
    @pytest.mark.unit
    def test_update_with_invalid_field(self, db_session, sample_service):
        """Test that invalid fields are ignored."""
        # Arrange
        original_name = sample_service.name
        
        # Act - Try to update with invalid field
        result = service_catalog_module.update_service(
            db_session,
            sample_service.id,
            invalid_field="should be ignored",
            name="Valid Update"
        )
        
        # Assert - Valid field updated, invalid ignored
        assert result.name == "Valid Update"
        # No error should be raised for invalid field


class TestServiceCatalogDelete:
    """Test service deletion operations."""
    
    @pytest.mark.unit
    def test_delete_service(self, db_session, sample_service):
        """Test deleting a service."""
        # Arrange
        service_id = sample_service.id
        
        # Act
        success = service_catalog_module.delete_service(db_session, service_id)
        
        # Assert
        assert success is True
        
        # Verify deleted from database
        deleted = db_session.query(models.Service).filter(
            models.Service.id == service_id
        ).first()
        assert deleted is None
    
    @pytest.mark.unit
    def test_delete_nonexistent_service(self, db_session):
        """Test deleting non-existent service."""
        # Act
        success = service_catalog_module.delete_service(db_session, 9999)
        
        # Assert
        assert success is False
    
    @pytest.mark.unit
    def test_delete_does_not_affect_other_services(self, db_session):
        """Test that deleting one service doesn't affect others."""
        # Arrange - Create multiple services
        service1 = service_catalog_module.create_service(
            db_session, name="Service 1", service_type="container", host="host1"
        )
        service2 = service_catalog_module.create_service(
            db_session, name="Service 2", service_type="container", host="host2"
        )
        
        # Act - Delete service1
        service_catalog_module.delete_service(db_session, service1.id)
        
        # Assert - Service2 still exists
        remaining = service_catalog_module.get_service_by_id(
            db_session, service2.id
        )
        assert remaining is not None
        assert remaining.id == service2.id


class TestServiceCatalogEdgeCases:
    """Test edge cases and special scenarios."""
    
    @pytest.mark.unit
    def test_create_service_with_null_optional_fields(self, db_session):
        """Test creating service with explicitly null optional fields."""
        # Arrange & Act
        result = service_catalog_module.create_service(
            db_session,
            name="Minimal Service",
            service_type="container",
            host="host",
            url=None,
            description=None,
            ports=None,
            cpu=None,
            memory=None
        )
        
        # Assert
        assert result.name == "Minimal Service"
        assert result.url is None
        assert result.description is None
        assert result.ports is None
    
    @pytest.mark.unit
    def test_service_name_must_be_unique(self, db_session):
        """Test that service names must be unique (database constraint)."""
        # Arrange - Create first service
        service_catalog_module.create_service(
            db_session,
            name="nginx",
            service_type="container",
            host="host1"
        )
        
        # Act & Assert - Creating duplicate name should fail
        with pytest.raises(Exception) as exc_info:
            service_catalog_module.create_service(
                db_session,
                name="nginx",  # Same name
                service_type="container",
                host="host2"  # Different host, but name still conflicts
            )
        
        # Verify it's a uniqueness constraint error
        assert "UNIQUE constraint failed" in str(exc_info.value) or \
               "unique" in str(exc_info.value).lower()
    
    @pytest.mark.unit
    def test_update_preserves_timestamps(self, db_session, sample_service):
        """Test that updates preserve created_date and update updated_date."""
        # Arrange
        original_created = sample_service.created_date
        
        # Act
        result = service_catalog_module.update_service(
            db_session,
            sample_service.id,
            description="Updated"
        )
        
        # Assert
        assert result.created_date == original_created
        # Note: updated_date should change, but we can't test exact time
        assert result.updated_date is not None
    
    @pytest.mark.unit
    def test_get_services_by_host_case_sensitive(self, db_session):
        """Test that host filtering is case-sensitive."""
        # Arrange
        service_catalog_module.create_service(
            db_session, name="Service", service_type="container", host="Host-A"
        )
        
        # Act
        results_upper = service_catalog_module.get_services_by_host(
            db_session, "Host-A"
        )
        results_lower = service_catalog_module.get_services_by_host(
            db_session, "host-a"
        )
        
        # Assert
        assert len(results_upper) == 1
        assert len(results_lower) == 0  # Case-sensitive, no match