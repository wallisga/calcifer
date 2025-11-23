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
    
    # NEW: Two-level work type system
    category = Column(String(50), nullable=False)  # platform_feature, integration, service, documentation
    action_type = Column(String(50), nullable=False)  # new, change, fix
    
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
    
    # Relationships
    commits = relationship("Commit", back_populates="work_item", cascade="all, delete-orphan")
    
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
    
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Service(name='{self.name}', type='{self.service_type}', host='{self.host}')>"

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