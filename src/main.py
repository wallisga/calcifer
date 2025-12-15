"""Main FastAPI application for Calcifer - Phase 2 Refactoring Complete."""
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import sys
import logging
import os

from .core.logging_module import setup_logging, log_startup, log_shutdown, get_logger
from . import models
from .database import engine, get_db
from .core import (
    work_module,
    service_catalog_module,
    documentation_module,
    git_module,
    settings_module
)
from .integrations.monitoring import monitoring, endpoint_module

# Initialize database
models.Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Calcifer", version="1.0.0")

# Initialize logging
log_level = getattr(logging, os.getenv('CALCIFER_LOG_LEVEL', 'INFO'))
format_json = os.getenv('LOG_FORMAT') == 'json'
setup_logging(level=log_level, format_json=format_json)
logger = get_logger('calcifer.main')


# App Lifecyle Event Handlers
@app.on_event("startup")
async def startup_event():
    """Log startup event."""
    log_startup()
    logger.info("Calcifer web interface ready at http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown event."""
    log_shutdown()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ============================================================================
# HOME / DASHBOARD ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home/Control Panel page."""
    # ✅ PHASE 1 FIX: Use module method for dashboard data
    dashboard_data = work_module.get_dashboard_data(db)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        **dashboard_data
    })

# ============================================================================
# WORK ITEM ROUTES
# ============================================================================

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
    detail_data = work_module.get_work_detail(db, work_id)
    
    if not detail_data:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    return templates.TemplateResponse("work_item.html", {
        "request": request,
        "work": detail_data["work_item"],
        "commits": detail_data["commits"],
        "branch_commits": detail_data["branch_commits"],
        "branch_merged": detail_data["branch_merged"]
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
    work_item = work_module.update_notes(db, work_id, notes)
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
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
    success, message = work_module.commit_work(
        db, work_id, commit_message, changes_entry
    )
    
    if success:
        return RedirectResponse(
            url=f"/work/{work_id}?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/work/{work_id}/commit?error={message}",
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

@app.post("/work/{work_id}/merge-and-complete")
async def merge_and_complete(work_id: int, db: Session = Depends(get_db)):
    """Validate, merge branch, and complete work item in one action."""
    success, message = work_module.merge_and_complete(db, work_id)
    
    if success:
        return RedirectResponse(url=f"/?success={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/work/{work_id}?error={message}", status_code=303)

# ============================================================================
# SERVICE CATALOG ROUTES
# ============================================================================

@app.get("/services", response_class=HTMLResponse)
async def service_catalog(request: Request, db: Session = Depends(get_db)):
    """Service catalog page."""
    # ✅ PHASE 1 FIX: Use module method instead of direct query
    services = service_catalog_module.get_all_services(db)
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
    git_repo_path: str = Form(""),
    git_repo_url: str = Form(""),
    git_repo_private: bool = Form(True),
    git_provider: str = Form(""),
    deployment_type: str = Form(""),
    docker_compose_path: str = Form(""),
    db: Session = Depends(get_db)
):
    """
    Create new service with automatic work item tracking.
    
    Work item is created automatically in the background.
    User is redirected to service detail page, not work item.
    """
    # Create service with automatic work item
    service, work_item = service_catalog_module.create_service_with_work_item(
        db,
        name=name,
        service_type=service_type,
        host=host,
        url=url or None,
        description=description or None,
        ports=ports or None,
        cpu=cpu or None,
        memory=memory or None,
        git_repo_path=git_repo_path or None,
        git_repo_url=git_repo_url or None,
        git_repo_private=git_repo_private,
        git_provider=git_provider or None,
        deployment_type=deployment_type or None,
        docker_compose_path=docker_compose_path or None
    )
    
    # Redirect to SERVICE detail page (not work item)
    return RedirectResponse(
        url=f"/services/{service.id}?success=Service created successfully. Work item #{work_item.id} tracks setup.",
        status_code=303
    )

@app.get("/services/{service_id}", response_class=HTMLResponse)
async def service_detail(
    request: Request,
    service_id: int,
    db: Session = Depends(get_db),
    success: str = None,
    error: str = None
):
    """Service detail page with tabs for hosts, configs, endpoints, work items."""
    detail = service_catalog_module.get_service_detail(db, service_id)
    
    if not detail:
        return RedirectResponse(url="/services?error=Service not found", status_code=303)
    
    return templates.TemplateResponse("service_detail.html", {
        "request": request,
        "service": detail["service"],
        "hosts": detail["hosts"],
        "config_files": detail["config_files"],
        "work_items": detail["work_items"],
        "endpoints": detail["endpoints"],
        "success": success,
        "error": error
    })

@app.post("/services/{service_id}/add-host")
async def add_host_to_service(
    service_id: int,
    hostname: str = Form(...),
    ip_address: str = Form(""),
    role: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Add a host to a service."""
    host = service_catalog_module.add_host_to_service(
        db,
        service_id=service_id,
        hostname=hostname,
        ip_address=ip_address or None,
        role=role or None,
        description=description or None
    )
    
    if not host:
        return RedirectResponse(
            url=f"/services/{service_id}?error=Failed to add host",
            status_code=303
        )
    
    return RedirectResponse(
        url=f"/services/{service_id}?success=Host added successfully",
        status_code=303
    )

@app.post("/services/{service_id}/add-config-file")
async def add_config_file_to_service(
    service_id: int,
    filepath: str = Form(...),
    description: str = Form(""),
    is_template: bool = Form(False),
    git_tracked: bool = Form(True),
    secrets_file: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Add a configuration file to track for a service."""
    config_file = service_catalog_module.add_config_file(
        db,
        service_id=service_id,
        filepath=filepath,
        description=description or None,
        is_template=is_template,
        git_tracked=git_tracked,
        secrets_file=secrets_file
    )
    
    if not config_file:
        return RedirectResponse(
            url=f"/services/{service_id}?error=Failed to add config file",
            status_code=303
        )
    
    return RedirectResponse(
        url=f"/services/{service_id}?success=Config file added successfully",
        status_code=303
    )

@app.post("/services/{service_id}/delete-host/{host_id}")
async def delete_service_host(
    service_id: int,
    host_id: int,
    db: Session = Depends(get_db)
):
    """Delete a host from a service."""
    success = service_catalog_module.delete_host(db, host_id)
    
    if success:
        return RedirectResponse(
            url=f"/services/{service_id}?success=Host deleted successfully",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/services/{service_id}?error=Host not found",
            status_code=303
        )

@app.post("/services/{service_id}/delete-config/{config_id}")
async def delete_service_config(
    service_id: int,
    config_id: int,
    db: Session = Depends(get_db)
):
    """Delete a config file from tracking."""
    success = service_catalog_module.delete_config_file(db, config_id)
    
    if success:
        return RedirectResponse(
            url=f"/services/{service_id}?success=Config file removed successfully",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/services/{service_id}?error=Config file not found",
            status_code=303
        )

# ============================================================================
# ENDPOINT ROUTES (Monitoring Integration)
# ============================================================================

@app.get("/endpoints", response_class=HTMLResponse)
async def endpoint_list(request: Request, db: Session = Depends(get_db)):
    """List all monitored endpoints."""
    # ✅ PHASE 1 FIX: Use module method instead of direct query
    endpoints = endpoint_module.get_all_endpoints(db)
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
    service_id: int = Form(None),  # NEW parameter
    db: Session = Depends(get_db)
):
    """Create new monitored endpoint with work item."""
    work_item_id, message = endpoint_module.create_endpoint_with_work_item(
        db,
        name=name,
        endpoint_type=endpoint_type,
        target=target,
        port=port,
        check_interval=check_interval,
        description=description or None,
        service_id=service_id  # NEW parameter
    )
    
    # Redirect based on whether endpoint is linked to service
    if service_id:
        return RedirectResponse(
            url=f"/services/{service_id}?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/work/{work_item_id}?success={message}",
            status_code=303
        )

@app.get("/endpoints/{endpoint_id}", response_class=HTMLResponse)
async def endpoint_detail(request: Request, endpoint_id: int, db: Session = Depends(get_db)):
    """View endpoint details and status."""
    detail_data = endpoint_module.get_endpoint_detail(db, endpoint_id)
    
    if not detail_data:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    return templates.TemplateResponse("endpoint_detail.html", {
        "request": request,
        "endpoint": detail_data["endpoint"],
        "work_item": detail_data["work_item"]
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
    """Delete endpoint."""
    success, message = endpoint_module.delete_endpoint(db, endpoint_id)
    
    if success:
        return RedirectResponse(
            url=f"/endpoints?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/endpoints/{endpoint_id}?error={message}",
            status_code=303
        )

# ============================================================================
# DOCUMENTATION ROUTES
# ============================================================================

@app.get("/docs-viewer", response_class=HTMLResponse)
async def docs_list(request: Request):
    """List all documentation files."""
    docs = documentation_module.get_all_docs()
    return templates.TemplateResponse("docs_list.html", {
        "request": request,
        "docs": docs
    })

@app.get("/docs-viewer/{doc_name}", response_class=HTMLResponse)
async def view_doc(request: Request, doc_name: str):
    """View a specific documentation file."""
    html_content = documentation_module.render_doc_html(doc_name)
    
    if not html_content:
        raise HTTPException(status_code=404, detail="Documentation not found")
    
    return templates.TemplateResponse("doc_view.html", {
        "request": request,
        "doc_name": doc_name,
        "doc_title": doc_name.replace(".md", "").replace("_", " ").title(),
        "content": html_content
    })

# ============================================================================
# SETTINGS ROUTES (✨ NEW - PHASE 1)
# ============================================================================

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Application settings page."""
    settings = settings_module.get_all()
    
    # Get Git author info
    try:
        git_author = git_module.repo.config_reader().get_value("user", "name")
    except:
        git_author = "Not configured"
    
    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "repo_path": settings_module.repo_path,
        "db_path": settings_module.db_path,
        "git_author": git_author,
        "python_version": python_version
    })

@app.post("/settings/update")
async def update_settings(db: Session = Depends(get_db)):
    """Update application settings (future implementation)."""
    # For now, just redirect back
    return RedirectResponse(url="/settings", status_code=303)

# ============================================================================
# GIT STATUS ROUTES (✨ NEW - PHASE 1)
# ============================================================================

@app.get("/git/status", response_class=HTMLResponse)
async def git_status_page(request: Request):
    """Git repository status page."""
    git_status = git_module.get_status()
    branches = git_module.get_branches()
    recent_commits = git_module.get_recent_commits(limit=20)
    
    return templates.TemplateResponse("git_status.html", {
        "request": request,
        "git_status": git_status,
        "branches": branches,
        "recent_commits": recent_commits
    })

# ============================================================================
# INTEGRATIONS ROUTES (✨ NEW - PHASE 1)
# ============================================================================

@app.get("/integrations", response_class=HTMLResponse)
async def integrations_page(request: Request):
    """Integrations management page."""
    return templates.TemplateResponse("integrations.html", {
        "request": request
    })

@app.get("/integrations/setup/{integration_name}", response_class=HTMLResponse)
async def integration_setup(request: Request, integration_name: str):
    """Setup page for a specific integration (future)."""
    # For now, redirect to main integrations page
    return RedirectResponse(url="/integrations", status_code=303)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}