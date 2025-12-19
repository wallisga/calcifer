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

class TestServiceHostManagement:
    """Test service host management operations."""
    
    @pytest.mark.unit
    def test_add_host_to_service(self, db_session, sample_service):
        """Test adding a host to a service."""
        # Arrange
        hostname = "test-host-1"
        ip_address = "192.168.1.100"
        role = "primary"
        
        # Act
        result = service_catalog_module.add_host_to_service(
            db_session,
            service_id=sample_service.id,
            hostname=hostname,
            ip_address=ip_address,
            role=role,
            description="Primary host"
        )
        
        # Assert
        assert result is not None
        assert result.hostname == hostname
        assert result.ip_address == ip_address
        assert result.role == role
        assert result.service_id == sample_service.id
    
    @pytest.mark.unit
    def test_add_multiple_hosts(self, db_session, sample_service):
        """Test adding multiple hosts to a service."""
        # Arrange & Act
        host1 = service_catalog_module.add_host_to_service(
            db_session, sample_service.id, "host1", "10.0.0.1", "server"
        )
        host2 = service_catalog_module.add_host_to_service(
            db_session, sample_service.id, "host2", "10.0.0.2", "client"
        )
        
        # Assert
        hosts = service_catalog_module.get_service_hosts(db_session, sample_service.id)
        assert len(hosts) == 2
        assert hosts[0].hostname == "host1"
        assert hosts[1].hostname == "host2"
    
    @pytest.mark.unit
    def test_add_host_to_nonexistent_service(self, db_session):
        """Test adding host to non-existent service."""
        # Act
        result = service_catalog_module.add_host_to_service(
            db_session, 9999, "hostname", "10.0.0.1"
        )
        
        # Assert
        assert result is None
    
    @pytest.mark.unit
    def test_update_host(self, db_session, sample_service):
        """Test updating a host."""
        # Arrange
        host = service_catalog_module.add_host_to_service(
            db_session, sample_service.id, "host1", "10.0.0.1"
        )
        
        # Act
        result = service_catalog_module.update_host(
            db_session,
            host.id,
            ip_address="10.0.0.2",
            role="updated-role"
        )
        
        # Assert
        assert result.ip_address == "10.0.0.2"
        assert result.role == "updated-role"
        assert result.hostname == "host1"  # Unchanged
    
    @pytest.mark.unit
    def test_delete_host(self, db_session, sample_service):
        """Test deleting a host."""
        # Arrange
        host = service_catalog_module.add_host_to_service(
            db_session, sample_service.id, "host1", "10.0.0.1"
        )
        
        # Act
        success = service_catalog_module.delete_host(db_session, host.id)
        
        # Assert
        assert success is True
        hosts = service_catalog_module.get_service_hosts(db_session, sample_service.id)
        assert len(hosts) == 0
    
    @pytest.mark.unit
    def test_delete_nonexistent_host(self, db_session):
        """Test deleting non-existent host."""
        # Act
        success = service_catalog_module.delete_host(db_session, 9999)
        
        # Assert
        assert success is False
    
    @pytest.mark.unit
    def test_delete_service_cascades_hosts(self, db_session, sample_service):
        """Test that deleting service deletes its hosts."""
        # Arrange
        service_catalog_module.add_host_to_service(
            db_session, sample_service.id, "host1", "10.0.0.1"
        )
        service_catalog_module.add_host_to_service(
            db_session, sample_service.id, "host2", "10.0.0.2"
        )
        
        # Act
        service_catalog_module.delete_service(db_session, sample_service.id)
        
        # Assert - Hosts should be deleted too
        hosts = db_session.query(models.ServiceHost).all()
        assert len(hosts) == 0


class TestServiceConfigFileManagement:
    """Test service config file management operations."""
    
    @pytest.mark.unit
    def test_add_config_file(self, db_session, sample_service):
        """Test adding a config file to a service."""
        # Arrange
        filepath = "/etc/nginx/sites-available/app"
        description = "Nginx configuration"
        
        # Act
        result = service_catalog_module.add_config_file(
            db_session,
            service_id=sample_service.id,
            filepath=filepath,
            description=description,
            git_tracked=True,
            secrets_file=False
        )
        
        # Assert
        assert result is not None
        assert result.filepath == filepath
        assert result.description == description
        assert result.git_tracked is True
        assert result.secrets_file is False
        assert result.service_id == sample_service.id
    
    @pytest.mark.unit
    def test_add_secrets_file(self, db_session, sample_service):
        """Test adding a secrets file."""
        # Arrange & Act
        result = service_catalog_module.add_config_file(
            db_session,
            sample_service.id,
            filepath="/opt/service/.env",
            description="Environment variables",
            git_tracked=False,
            secrets_file=True
        )
        
        # Assert
        assert result.secrets_file is True
        assert result.git_tracked is False
    
    @pytest.mark.unit
    def test_add_multiple_config_files(self, db_session, sample_service):
        """Test adding multiple config files."""
        # Arrange & Act
        service_catalog_module.add_config_file(
            db_session, sample_service.id, "/etc/nginx/nginx.conf"
        )
        service_catalog_module.add_config_file(
            db_session, sample_service.id, "/etc/nginx/sites-available/app"
        )
        service_catalog_module.add_config_file(
            db_session, sample_service.id, "/opt/app/.env", secrets_file=True
        )
        
        # Assert
        config_files = service_catalog_module.get_service_config_files(
            db_session, sample_service.id
        )
        assert len(config_files) == 3
    
    @pytest.mark.unit
    def test_add_config_file_to_nonexistent_service(self, db_session):
        """Test adding config file to non-existent service."""
        # Act
        result = service_catalog_module.add_config_file(
            db_session, 9999, "/path/to/config"
        )
        
        # Assert
        assert result is None
    
    @pytest.mark.unit
    def test_update_config_file(self, db_session, sample_service):
        """Test updating a config file."""
        # Arrange
        config_file = service_catalog_module.add_config_file(
            db_session, sample_service.id, "/etc/config", git_tracked=True
        )
        
        # Act
        result = service_catalog_module.update_config_file(
            db_session,
            config_file.id,
            description="Updated description",
            secrets_file=True
        )
        
        # Assert
        assert result.description == "Updated description"
        assert result.secrets_file is True
        assert result.filepath == "/etc/config"  # Unchanged
    
    @pytest.mark.unit
    def test_delete_config_file(self, db_session, sample_service):
        """Test deleting a config file."""
        # Arrange
        config_file = service_catalog_module.add_config_file(
            db_session, sample_service.id, "/etc/config"
        )
        
        # Act
        success = service_catalog_module.delete_config_file(db_session, config_file.id)
        
        # Assert
        assert success is True
        files = service_catalog_module.get_service_config_files(
            db_session, sample_service.id
        )
        assert len(files) == 0
    
    @pytest.mark.unit
    def test_delete_service_cascades_config_files(self, db_session, sample_service):
        """Test that deleting service deletes its config files."""
        # Arrange
        service_catalog_module.add_config_file(
            db_session, sample_service.id, "/etc/config1"
        )
        service_catalog_module.add_config_file(
            db_session, sample_service.id, "/etc/config2"
        )
        
        # Act
        service_catalog_module.delete_service(db_session, sample_service.id)
        
        # Assert - Config files should be deleted too
        files = db_session.query(models.ServiceConfigFile).all()
        assert len(files) == 0


class TestEnhancedServiceCreation:
    """Test service creation with new fields."""
    
    @pytest.mark.unit
    def test_create_service_with_git_repo(self, db_session):
        """Test creating service with Git repository settings."""
        # Arrange & Act
        service = service_catalog_module.create_service(
            db_session,
            name="WireGuard VPN Server",
            service_type="bare_metal",
            host="linode",
            git_repo_path="~/calcifer/wireguard-vpn-server",
            git_repo_url="git@github.com:user/wireguard-vpn-server.git",
            git_repo_private=True,
            git_provider="github"
        )
        
        # Assert
        assert service.git_repo_path == "~/calcifer/wireguard-vpn-server"
        assert service.git_repo_url == "git@github.com:user/wireguard-vpn-server.git"
        assert service.git_repo_private is True
        assert service.git_provider == "github"
    
    @pytest.mark.unit
    def test_create_service_with_deployment_type(self, db_session):
        """Test creating service with deployment settings."""
        # Arrange & Act
        service = service_catalog_module.create_service(
            db_session,
            name="FastAPI App",
            service_type="container",
            host="localhost",
            deployment_type="docker",
            docker_compose_path="~/calcifer/fastapi-app/docker-compose.yml"
        )
        
        # Assert
        assert service.deployment_type == "docker"
        assert service.docker_compose_path == "~/calcifer/fastapi-app/docker-compose.yml"
    
    @pytest.mark.unit
    def test_create_service_with_documentation(self, db_session):
        """Test creating service with documentation fields."""
        # Arrange & Act
        service = service_catalog_module.create_service(
            db_session,
            name="Service",
            service_type="vm",
            host="proxmox",
            readme_path="~/calcifer/service/docs/README.md",
            architecture_doc="Multi-tier architecture with load balancer"
        )
        
        # Assert
        assert service.readme_path == "~/calcifer/service/docs/README.md"
        assert "Multi-tier" in service.architecture_doc        