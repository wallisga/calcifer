"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Work Item Schemas
class WorkItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    work_type: str = Field(..., pattern="^(new_service|config_change|new_vm|troubleshooting)$")
    description: Optional[str] = None

class WorkItemUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    checklist: Optional[List[dict]] = None
    completed_date: Optional[datetime] = None

class WorkItemResponse(BaseModel):
    id: int
    title: str
    work_type: str
    status: str
    description: Optional[str]
    git_branch: Optional[str]
    started_date: datetime
    completed_date: Optional[datetime]
    checklist: List[dict]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

# Service Schemas
# Service Schemas
class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    service_type: str = Field(..., pattern="^(container|vm|bare_metal)$")
    host: str = Field(..., min_length=1, max_length=100)
    url: Optional[str] = None
    description: Optional[str] = None
    ports: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    depends_on: Optional[List[int]] = []
    required_by: Optional[List[int]] = []
    config_path: Optional[str] = None
    git_repo_path: Optional[str] = None
    git_repo_url: Optional[str] = None
    git_repo_private: bool = True
    git_provider: Optional[str] = None
    deployment_type: Optional[str] = None
    docker_compose_path: Optional[str] = None
    readme_path: Optional[str] = None
    architecture_doc: Optional[str] = None

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    service_type: Optional[str] = None
    host: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    ports: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    depends_on: Optional[List[int]] = None
    required_by: Optional[List[int]] = None
    config_path: Optional[str] = None
    git_repo_path: Optional[str] = None
    git_repo_url: Optional[str] = None
    git_repo_private: Optional[bool] = None
    git_provider: Optional[str] = None
    deployment_type: Optional[str] = None
    docker_compose_path: Optional[str] = None
    readme_path: Optional[str] = None
    architecture_doc: Optional[str] = None

class ServiceResponse(BaseModel):
    id: int
    name: str
    service_type: str
    host: str
    url: Optional[str]
    description: Optional[str]
    status: str
    ports: Optional[str]
    cpu: Optional[str]
    memory: Optional[str]
    depends_on: List[int]
    required_by: List[int]
    config_path: Optional[str]
    git_repo_path: Optional[str]
    git_repo_url: Optional[str]
    git_repo_private: bool
    git_provider: Optional[str]
    deployment_type: Optional[str]
    docker_compose_path: Optional[str]
    readme_path: Optional[str]
    architecture_doc: Optional[str]
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

# Change Log Schemas
class ChangeLogCreate(BaseModel):
    description: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    work_item_id: Optional[int] = None
    category: str = Field(default="other", pattern="^(infrastructure|service|config|docs|other)$")

class ChangeLogResponse(BaseModel):
    id: int
    date: datetime
    author: str
    description: str
    work_item_id: Optional[int]
    category: str
    
    class Config:
        from_attributes = True