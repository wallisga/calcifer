"""SQLAlchemy ORM models for Calcifer."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class WorkItem(Base):
    """Represents a unit of work (task/project)."""
    __tablename__ = "work_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    
    # Two-level work type system
    category = Column(String(50), nullable=False)
    action_type = Column(String(50), nullable=False)
    
    # DEPRECATED but keep for backward compatibility
    work_type = Column(String(50), nullable=True)
    
    status = Column(String(20), default="planning")
    description = Column(Text)
    git_branch = Column(String(100))
    started_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    
    # Git tracking fields
    branch_merged = Column(Boolean, default=False)
    merge_commit_sha = Column(String(40), nullable=True)
    
    # Documentation tracking
    docs_updated = Column(Boolean, default=False)
    docs_path = Column(String(200), nullable=True)
    
    # Checklist stored as JSON
    checklist = Column(JSON, default=list)
    
    # Notes/documentation
    notes = Column(Text)
    
    # Link to service (nullable - platform work items have no service)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=True)
    
    # Relationships
    commits = relationship("Commit", back_populates="work_item", cascade="all, delete-orphan")
    service = relationship("Service", back_populates="work_items")  # NEW
    
    def __repr__(self):
        return f"<WorkItem(id={self.id}, title='{self.title}', category='{self.category}', action='{self.action_type}')>"
    
    @property
    def full_type(self):
        """Get the full work type string for display."""
        action_map = {
            'new': 'New',
            'change': 'Change',
            'fix': 'Fix'
        }
        category_map = {
            'platform_feature': 'Platform Feature',
            'integration': 'Integration',
            'service': 'Service',
            'documentation': 'Document'
        }
        action = action_map.get(self.action_type, self.action_type.title())
        cat = category_map.get(self.category, self.category.replace('_', ' ').title())
        
        if self.action_type == 'new':
            return f"New {cat}"
        else:
            return f"{cat} {action}"

class Service(Base):
    """Represents a deployed service/container/VM."""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    service_type = Column(String(50), nullable=False)  # container, vm, bare_metal
    host = Column(String(100), nullable=False)  # Which VM/host it runs on
    url = Column(String(200), nullable=True)
    description = Column(Text)
    status = Column(String(20), default="active")  # active, inactive, maintenance
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)    
    
    # Technical details
    ports = Column(String(200), nullable=True)
    cpu = Column(String(20), nullable=True)
    memory = Column(String(20), nullable=True)
    
    # Relationships and dependencies (JSON list of service IDs)
    depends_on = Column(JSON, default=list)
    required_by = Column(JSON, default=list)
    
    # Documentation
    docs_url = Column(String(200), nullable=True)
    config_path = Column(String(200), nullable=True)  # Path in Git repo
    readme_path = Column(String(500))    # Path to service README
    architecture_doc = Column(Text)      # Service architecture notes    

    # Git repository settings
    git_repo_path = Column(String(500))  # e.g., "~/calcifer/wireguard-vpn-server"
    git_repo_url = Column(String(500))   # e.g., "git@github.com:user/wireguard-vpn-server.git"
    git_repo_private = Column(Boolean, default=True)
    git_provider = Column(String(50))    # "github", "gitlab", "gitea", or null
    
    # Deployment settings
    deployment_type = Column(String(50))  # "bare_metal", "docker", "kubernetes"
    docker_compose_path = Column(String(500))  # Path to docker-compose.yml if applicable
    
    # Relationships
    hosts = relationship("ServiceHost", back_populates="service", cascade="all, delete-orphan")
    config_files = relationship("ServiceConfigFile", back_populates="service", cascade="all, delete-orphan")
    work_items = relationship("WorkItem", back_populates="service")
    endpoints = relationship("Endpoint", back_populates="service")
    
    def __repr__(self):
        return f"<Service(name='{self.name}', type='{self.service_type}', host='{self.host}')>"

class ServiceHost(Base):
    """Track multiple hosts/VMs for a single service."""
    __tablename__ = "service_hosts"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    hostname = Column(String(100), nullable=False)
    ip_address = Column(String(50))
    role = Column(String(50))  # e.g., "vpn-client", "api-server", "database"
    description = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    service = relationship("Service", back_populates="hosts")
    
    def __repr__(self):
        return f"<ServiceHost(hostname='{self.hostname}', role='{self.role}', service_id={self.service_id})>"

class ServiceConfigFile(Base):
    """Track configuration files managed by a service."""
    __tablename__ = "service_config_files"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    filepath = Column(String(500), nullable=False)  # e.g., "/etc/nginx/sites-available/app"
    description = Column(Text)
    is_template = Column(Boolean, default=False)  # True if this is a template file
    git_tracked = Column(Boolean, default=True)
    secrets_file = Column(Boolean, default=False)  # True if this is .env or contains secrets
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    service = relationship("Service", back_populates="config_files")
    
    def __repr__(self):
        return f"<ServiceConfigFile(filepath='{self.filepath}', service_id={self.service_id})>"

class Commit(Base):
    """Tracks Git commits associated with work items."""
    __tablename__ = "commits"
    
    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=False)
    commit_sha = Column(String(40), nullable=False)
    commit_message = Column(Text)
    committed_date = Column(DateTime, default=datetime.utcnow)
    
    work_item = relationship("WorkItem", back_populates="commits")
    
    def __repr__(self):
        return f"<Commit(sha='{self.commit_sha[:7]}', work_item_id={self.work_item_id})>"
    
class Endpoint(Base):
    """Represents a monitored endpoint (network node, service, etc.)."""
    __tablename__ = "endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    endpoint_type = Column(String(50), nullable=False)
    target = Column(String(200), nullable=False)
    port = Column(Integer, nullable=True)
    check_interval = Column(Integer, default=60)
    
    # Status tracking
    status = Column(String(20), default="unknown")
    last_check = Column(DateTime, nullable=True)
    last_up = Column(DateTime, nullable=True)
    last_down = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0)
    
    # Metadata
    description = Column(Text, nullable=True)
    documentation_url = Column(String(200), nullable=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=True)
    
    # Link to service (nullable - some endpoints might not belong to a service)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=True)
    
    # Monitoring config (JSON for flexibility)
    monitor_config = Column(JSON, default=dict)
    
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="endpoints")
    
    def __repr__(self):
        return f"<Endpoint(name='{self.name}', type='{self.endpoint_type}', status='{self.status}')>"
    
    @property
    def is_up(self):
        return self.status == "up"
    
    @property
    def uptime_percentage(self):
        # Future: calculate from check history
        return 0.0    

class ChangeLog(Base):
    """Tracks all changes for CHANGES.md generation."""
    __tablename__ = "changelog"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    author = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    work_item_id = Column(Integer, ForeignKey("work_items.id"), nullable=True)
    category = Column(String(50), default="other")  # infrastructure, service, config, docs
    
    def __repr__(self):
        return f"<ChangeLog(date='{self.date}', description='{self.description[:50]}...')>"