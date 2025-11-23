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
    work_type = Column(String(50), nullable=False)  # new_service, config_change, new_vm, troubleshooting
    status = Column(String(20), default="planning")  # planning, in_progress, complete, cancelled
    description = Column(Text)
    git_branch = Column(String(100))
    started_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    
    # Checklist stored as JSON
    checklist = Column(JSON, default=list)
    
    # Notes/documentation
    notes = Column(Text)
    
    # Relationships
    commits = relationship("Commit", back_populates="work_item", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkItem(id={self.id}, title='{self.title}', status='{self.status}')>"

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