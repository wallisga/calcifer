"""Main FastAPI application for Calcifer."""
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import markdown
from pathlib import Path

from . import models, schemas
from .database import engine, get_db, init_db
from .git_integration import GitManager

# Initialize database
models.Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Calcifer", version="1.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Git manager
git_manager = GitManager(repo_path=os.getenv("REPO_PATH", ".."))

# ============================================================================
# HTML ROUTES (UI)
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home/Control Panel page."""
    # Get active work items
    active_work = db.query(models.WorkItem).filter(
        models.WorkItem.status.in_(["planning", "in_progress"])
    ).order_by(models.WorkItem.started_date.desc()).all()
    
    # Get recent completed work
    completed_work = db.query(models.WorkItem).filter(
        models.WorkItem.status == "complete"
    ).order_by(models.WorkItem.completed_date.desc()).limit(5).all()
    
    # Get git status
    git_status = git_manager.get_status()
    
    # Get recent changes
    recent_changes = db.query(models.ChangeLog).order_by(
        models.ChangeLog.date.desc()
    ).limit(10).all()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "active_work": active_work,
        "completed_work": completed_work,
        "git_status": git_status,
        "recent_changes": recent_changes
    })

@app.get("/work/new", response_class=HTMLResponse)
async def new_work_form(request: Request):
    """Form to start new work."""
    return templates.TemplateResponse("new_work.html", {"request": request})

@app.post("/work/new")
async def create_work(
    title: str = Form(...),
    work_type: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create new work item and branch."""
    # Create work item
    work_item = models.WorkItem(
        title=title,
        work_type=work_type,
        description=description,
        status="planning"
    )
    
    # Generate branch name
    branch_name = git_manager.generate_branch_name(work_type, title)
    work_item.git_branch = branch_name
    
    # Create Git branch
    git_manager.create_branch(branch_name, checkout=True)
    
    # Initialize checklist based on work type
    if work_type == "new_service":
        work_item.checklist = [
            {"item": "Define purpose and requirements", "done": False},
            {"item": "Check resource availability", "done": False},
            {"item": "Create docker-compose.yml", "done": False},
            {"item": "Test locally", "done": False},
            {"item": "Deploy to VM", "done": False},
            {"item": "Add monitoring", "done": False},
            {"item": "Update service catalog", "done": False},
            {"item": "Document in Calcifer", "done": False}
        ]
    elif work_type == "config_change":
        work_item.checklist = [
            {"item": "Document current state", "done": False},
            {"item": "Backup configs", "done": False},
            {"item": "Make changes", "done": False},
            {"item": "Verify functionality", "done": False},
            {"item": "Update documentation", "done": False}
        ]
    else:
        work_item.checklist = [
            {"item": "Define task", "done": False},
            {"item": "Complete work", "done": False},
            {"item": "Document results", "done": False}
        ]
    
    db.add(work_item)
    db.commit()
    db.refresh(work_item)
    
    return RedirectResponse(url=f"/work/{work_item.id}", status_code=303)

@app.get("/work/{work_id}", response_class=HTMLResponse)
async def work_detail(request: Request, work_id: int, db: Session = Depends(get_db)):
    """Work item detail page."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Get associated commits
    commits = db.query(models.Commit).filter(
        models.Commit.work_item_id == work_id
    ).order_by(models.Commit.committed_date.desc()).all()
    
    return templates.TemplateResponse("work_item.html", {
        "request": request,
        "work": work_item,
        "commits": commits
    })

@app.post("/work/{work_id}/checklist/{index}")
async def toggle_checklist(work_id: int, index: int, db: Session = Depends(get_db)):
    """Toggle checklist item."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    if index < len(work_item.checklist):
        work_item.checklist[index]["done"] = not work_item.checklist[index]["done"]
        db.commit()
    
    return RedirectResponse(url=f"/work/{work_id}", status_code=303)

@app.post("/work/{work_id}/complete")
async def complete_work(work_id: int, db: Session = Depends(get_db)):
    """Mark work as complete."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    work_item.status = "complete"
    work_item.completed_date = datetime.utcnow()
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/services", response_class=HTMLResponse)
async def service_catalog(request: Request, db: Session = Depends(get_db)):
    """Service catalog page."""
    services = db.query(models.Service).order_by(models.Service.name).all()
    return templates.TemplateResponse("service_catalog.html", {
        "request": request,
        "services": services
    })

@app.get("/services/new", response_class=HTMLResponse)
async def new_service_form(request: Request):
    """Form to add new service."""
    return templates.TemplateResponse("new_service.html", {"request": request})

@app.post("/services/new")
async def create_service(
    name: str = Form(...),
    service_type: str = Form(...),
    host: str = Form(...),
    url: str = Form(""),
    description: str = Form(""),
    ports: str = Form(""),
    cpu: str = Form(""),
    memory: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create new service entry."""
    service = models.Service(
        name=name,
        service_type=service_type,
        host=host,
        url=url or None,
        description=description or None,
        ports=ports or None,
        cpu=cpu or None,
        memory=memory or None
    )
    
    db.add(service)
    db.commit()
    
    return RedirectResponse(url="/services", status_code=303)

# ============================================================================
# API ROUTES (for future automation/integrations)
# ============================================================================

@app.get("/api/work", response_model=List[schemas.WorkItemResponse])
async def list_work_items(db: Session = Depends(get_db)):
    """List all work items."""
    return db.query(models.WorkItem).all()

@app.get("/api/services", response_model=List[schemas.ServiceResponse])
async def list_services(db: Session = Depends(get_db)):
    """List all services."""
    return db.query(models.Service).all()

@app.get("/api/git/status")
async def git_status():
    """Get Git repository status."""
    return git_manager.get_status()

@app.get("/api/git/commits")
async def recent_commits(limit: int = 10):
    """Get recent commits."""
    return git_manager.get_recent_commits(limit)

# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# ============================================================================
# DOCUMENTATION ROUTES
# ============================================================================

@app.get("/docs-viewer", response_class=HTMLResponse)
async def docs_list(request: Request):
    """List all documentation files."""
    docs_path = Path(git_manager.repo_path) / "docs"
    
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
    
    # Get all markdown files
    md_files = []
    for file_path in docs_path.glob("*.md"):
        md_files.append({
            "name": file_path.name,
            "title": file_path.stem.replace("_", " ").title(),
            "path": str(file_path.relative_to(git_manager.repo_path))
        })
    
    md_files.sort(key=lambda x: x["name"])
    
    return templates.TemplateResponse("docs_list.html", {
        "request": request,
        "docs": md_files
    })

@app.get("/docs-viewer/{doc_name}", response_class=HTMLResponse)
async def view_doc(request: Request, doc_name: str):
    """View a specific documentation file."""
    docs_path = Path(git_manager.repo_path) / "docs" / doc_name
    
    if not docs_path.exists() or not doc_name.endswith(".md"):
        raise HTTPException(status_code=404, detail="Documentation not found")
    
    # Read and render markdown
    with open(docs_path, "r") as f:
        content = f.read()
    
    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(
        content,
        extensions=['fenced_code', 'tables', 'toc', 'codehilite']
    )
    
    return templates.TemplateResponse("doc_view.html", {
        "request": request,
        "doc_name": doc_name,
        "doc_title": doc_name.replace(".md", "").replace("_", " ").title(),
        "content": html_content
    })