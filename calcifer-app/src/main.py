"""Main FastAPI application for Calcifer."""
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import json
import markdown
from pathlib import Path

from . import models, schemas
from .database import engine, get_db, init_db
from .core import (
    work_module,
    service_catalog_module,
    documentation_module,
    git_module,
    settings_module
)
from .integrations import monitoring, endpoint_module

# Initialize database
models.Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Calcifer", version="1.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    git_status = git_module.get_status()
    
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
    category: str = Form(...),
    action_type: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create new work item and branch."""
    work_item = work_module.create_work_item(
        db, title, category, action_type, description
    )
    return RedirectResponse(url=f"/work/{work_item.id}", status_code=303)

@app.get("/work/{work_id}", response_class=HTMLResponse)
async def work_detail(request: Request, work_id: int, db: Session = Depends(get_db)):
    """Work item detail page."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Get associated commits from database
    db_commits = db.query(models.Commit).filter(
        models.Commit.work_item_id == work_id
    ).order_by(models.Commit.committed_date.desc()).all()
    
    # Get commits from Git branch (newer approach - shows real branch commits)
    branch_commits = []
    if work_item.git_branch:
        branch_commits = git_module.get_branch_commits(work_item.git_branch)
    
    # Get branch merge status
    branch_merged = False
    if work_item.git_branch:
        branch_merged = git_module.is_branch_merged(work_item.git_branch)
        work_item.branch_merged = branch_merged
        db.commit()
    
    return templates.TemplateResponse("work_item.html", {
        "request": request,
        "work": work_item,
        "commits": db_commits,  # Keep for backward compatibility
        "branch_commits": branch_commits,  # New: actual branch commits
        "branch_merged": branch_merged
    })

@app.post("/work/{work_id}/checklist/{index}")
async def toggle_checklist(work_id: int, index: int, db: Session = Depends(get_db)):
    """Toggle checklist item."""
    work_module.toggle_checklist_item(db, work_id, index)
    return RedirectResponse(url=f"/work/{work_id}", status_code=303)

@app.post("/work/{work_id}/notes")
async def update_notes(
    work_id: int, 
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    """Update work item notes."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Limit to 2000 characters
    work_item.notes = notes[:2000] if notes else None
    db.commit()
    
    return RedirectResponse(url=f"/work/{work_id}", status_code=303)

@app.get("/work/{work_id}/commit", response_class=HTMLResponse)
async def commit_form(request: Request, work_id: int, db: Session = Depends(get_db)):
    """Show form to commit changes with CHANGES.md update."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Get current git status
    git_status = git_module.get_status()
    
    # Get author info
    try:
        author_name = git_module.repo.config_reader().get_value("user", "name")
        author_email = git_module.repo.config_reader().get_value("user", "email")
    except:
        author_name = "Unknown"
        author_email = ""
    
    return templates.TemplateResponse("commit_form.html", {
        "request": request,
        "work": work_item,
        "git_status": git_status,
        "author_name": author_name,
        "author_email": author_email
    })

@app.post("/work/{work_id}/commit")
async def commit_changes(
    work_id: int,
    commit_message: str = Form(...),
    changes_entry: str = Form(...),
    db: Session = Depends(get_db)
):
    """Commit changes and update CHANGES.md."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Validation
    if not commit_message.strip():
        return RedirectResponse(
            url=f"/work/{work_id}/commit?error=Commit message is required",
            status_code=303
        )
    
    if not changes_entry.strip():
        return RedirectResponse(
            url=f"/work/{work_id}/commit?error=CHANGES.md entry is required",
            status_code=303
        )
    
    try:
        # Make sure we're on the right branch
        if work_item.git_branch:
            git_module.checkout_branch(work_item.git_branch)
        
        # Update CHANGES.md
        from datetime import datetime
        changes_path = os.path.join(git_module.repo_path, "docs", "CHANGES.md")
        
# Prepare new entry with proper formatting
        today = datetime.now().strftime('%Y-%m-%d')
        author = git_module.repo.config_reader().get_value("user", "name")
        
        # Get work type for the entry
        work_type_display = work_item.full_type if hasattr(work_item, 'full_type') else work_item.work_type
        
        # Format: ## YYYY-MM-DD - Author - Work Type
        # - Change description
        new_entry = f"## {today} - {author} - {work_type_display}\n- {changes_entry}\n"
        
        # Read current content
        with open(changes_path, 'r') as f:
            lines = f.readlines()
        
        # Find where to insert (after the header, before first ## entry)
        insert_index = len(lines)  # Default to end
        for i, line in enumerate(lines):
            if i > 0 and line.startswith('## '):  # Skip file header
                insert_index = i
                break
        
        # Insert with proper spacing
        lines.insert(insert_index, '\n')
        lines.insert(insert_index + 1, new_entry)
        
        # Write updated CHANGES.md
        with open(changes_path, 'w') as f:
            f.writelines(lines)
        
        # Stage all changes
        git_module.repo.git.add('-A')
        
        # Commit
        commit_sha = git_module.commit(commit_message)
        
        if commit_sha:
            # Record commit in database
            commit_record = models.Commit(
                work_item_id=work_id,
                commit_sha=commit_sha,
                commit_message=commit_message
            )
            db.add(commit_record)
            db.commit()
            
            return RedirectResponse(
                url=f"/work/{work_id}?success=Changes committed successfully!",
                status_code=303
            )
        else:
            return RedirectResponse(
                url=f"/work/{work_id}/commit?error=Commit failed",
                status_code=303
            )
            
    except Exception as e:
        return RedirectResponse(
            url=f"/work/{work_id}/commit?error=Error: {str(e)}",
            status_code=303
        )
    
@app.post("/work/{work_id}/delete")
async def delete_work_item(work_id: int, db: Session = Depends(get_db)):
    """Delete work item and its Git branch."""
    success, message = work_module.delete_work_item(db, work_id)
    
    if success:
        return RedirectResponse(url="/?success=Work item deleted successfully", status_code=303)
    else:
        return RedirectResponse(url=f"/?error={message}", status_code=303)

@app.post("/work/{work_id}/complete")
async def complete_work(work_id: int, db: Session = Depends(get_db)):
    """Mark work as complete - simple validation only."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Validation checks
    errors = []
    
    # Check 1: All checklist items completed?
    incomplete_items = [item for item in work_item.checklist if not item.get("done", False)]
    if incomplete_items:
        errors.append(f"{len(incomplete_items)} checklist item(s) not completed")
    
    # Check 2: Branch merged?
    if work_item.git_branch and not work_item.branch_merged:
        errors.append("Branch not yet merged to main")
    
    # If there are validation errors, show them
    if errors:
        error_msg = " | ".join(errors)
        return RedirectResponse(
            url=f"/work/{work_id}?error={error_msg}", 
            status_code=303
        )
    
    # All checks passed - mark complete
    work_item.status = "complete"
    work_item.completed_date = datetime.utcnow()
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/work/{work_id}/merge")
async def merge_work_branch(work_id: int, db: Session = Depends(get_db)):
    """Merge work item branch to main - with validation."""
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    if not work_item.git_branch:
        return RedirectResponse(
            url=f"/work/{work_id}?error=No branch associated with this work item",
            status_code=303
        )
    
    # Check if already merged
    if git_module.is_branch_merged(work_item.git_branch):
        work_item.branch_merged = True
        db.commit()
        return RedirectResponse(
            url=f"/work/{work_id}?success=Branch already merged",
            status_code=303
        )
    
    # VALIDATION: Check if CHANGES.md was updated
    if not git_module.check_changes_md_updated():
        return RedirectResponse(
            url=f"/work/{work_id}?error=Cannot merge: docs/CHANGES.md not updated in this branch",
            status_code=303
        )
    
    # VALIDATION: Check if branch has commits
    branch_commits = git_module.get_branch_commits(work_item.git_branch)
    if not branch_commits:
        return RedirectResponse(
            url=f"/work/{work_id}?error=Cannot merge: branch has no commits",
            status_code=303
        )
    
    # Attempt merge
    success, result = git_module.merge_branch(work_item.git_branch)
    
    if success:
        # Update work item
        work_item.branch_merged = True
        work_item.merge_commit_sha = result
        db.commit()
        
        return RedirectResponse(
            url=f"/work/{work_id}?success=Branch merged successfully! You can now mark work complete.",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/work/{work_id}?error=Merge failed: {result}",
            status_code=303
        )
    
@app.post("/work/{work_id}/merge-and-complete")
async def merge_and_complete(work_id: int, db: Session = Depends(get_db)):
    """Validate, merge branch, and complete work item in one action."""
    success, message = work_module.merge_and_complete(db, work_id)
    
    if success:
        return RedirectResponse(url=f"/?success={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/work/{work_id}?error={message}", status_code=303)

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
    service_catalog_module.create_service(
        db, name, service_type, host,
        url or None, description or None,
        ports or None, cpu or None, memory or None
    )
    return RedirectResponse(url="/services", status_code=303)

# ============================================================================
# ENDPOINT ROUTES (Monitoring)
# ============================================================================

@app.get("/endpoints", response_class=HTMLResponse)
async def endpoint_list(request: Request, db: Session = Depends(get_db)):
    """List all monitored endpoints."""
    endpoints = db.query(models.Endpoint).order_by(models.Endpoint.name).all()
    return templates.TemplateResponse("endpoint_list.html", {
        "request": request,
        "endpoints": endpoints
    })

@app.get("/endpoints/new", response_class=HTMLResponse)
async def endpoint_wizard(request: Request):
    """Wizard to create new monitored endpoint."""
    return templates.TemplateResponse("endpoint_wizard.html", {
        "request": request
    })

@app.post("/endpoints/new")
async def create_endpoint(
    name: str = Form(...),
    endpoint_type: str = Form(...),
    target: str = Form(...),
    port: int = Form(None),
    check_interval: int = Form(60),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create new monitored endpoint."""
    work_id, success_msg = endpoint_module.create_endpoint_with_work_item(
        db, name, endpoint_type, target, port, check_interval, description
    )
    
    return RedirectResponse(
        url=f"/work/{work_id}?success={success_msg}",
        status_code=303
    )

@app.get("/endpoints/{endpoint_id}", response_class=HTMLResponse)
async def endpoint_detail(request: Request, endpoint_id: int, db: Session = Depends(get_db)):
    """View endpoint details and status."""
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    # Get associated work item
    work_item = None
    if endpoint.work_item_id:
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == endpoint.work_item_id).first()
    
    return templates.TemplateResponse("endpoint_detail.html", {
        "request": request,
        "endpoint": endpoint,
        "work_item": work_item
    })

@app.post("/endpoints/{endpoint_id}/check")
async def check_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    """Manually trigger endpoint check."""
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    # Use monitoring integration
    is_up = monitoring.update_endpoint_status(endpoint, db)
    
    return RedirectResponse(url=f"/endpoints/{endpoint_id}", status_code=303)

@app.post("/endpoints/{endpoint_id}/delete")
async def delete_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    """Delete endpoint and optionally its work item."""
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    endpoint_name = endpoint.name
    work_item_id = endpoint.work_item_id
    
    # Delete endpoint from database
    db.delete(endpoint)
    db.commit()
    
    # Optionally delete documentation file
    # (keeping it for now - can be useful for audit trail)
    
    return RedirectResponse(
        url=f"/endpoints?success=Endpoint '{endpoint_name}' deleted successfully",
        status_code=303
    )

# Helper functions

def generate_endpoint_documentation(name, endpoint_type, target, port, description):
    """
    Generate endpoint documentation using monitoring integration.
    
    DEPRECATED: Use MonitoringIntegration.generate_endpoint_documentation() directly.
    Kept for backward compatibility.
    """
    return MonitoringIntegration.generate_endpoint_documentation(
        name, endpoint_type, target, port, description
    )

def perform_endpoint_check(endpoint) -> bool:
    """
    Perform endpoint check using monitoring integration.
    
    DEPRECATED: Use monitoring.check_endpoint() directly.
    Kept for backward compatibility.
    """
    is_up, error_msg = monitoring.check_endpoint(endpoint)
    return is_up

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
    return git_module.get_status()

@app.get("/api/git/commits")
async def recent_commits(limit: int = 10):
    """Get recent commits."""
    return git_module.get_recent_commits(limit)

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
    docs_path = Path(git_module.repo_path) / "docs"
    
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
    
    # Get all markdown files
    md_files = []
    for file_path in docs_path.glob("*.md"):
        md_files.append({
            "name": file_path.name,
            "title": file_path.stem.replace("_", " ").title(),
            "path": str(file_path.relative_to(git_module.repo_path))
        })
    
    md_files.sort(key=lambda x: x["name"])
    
    return templates.TemplateResponse("docs_list.html", {
        "request": request,
        "docs": md_files
    })

@app.get("/docs-viewer/{doc_name}", response_class=HTMLResponse)
async def view_doc(request: Request, doc_name: str):
    """View a specific documentation file."""
    docs_path = Path(git_module.repo_path) / "docs" / doc_name
    
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