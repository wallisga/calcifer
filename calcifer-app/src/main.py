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
    category: str = Form(...),
    action_type: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create new work item and branch."""
    # Create work item
    work_item = models.WorkItem(
        title=title,
        category=category,
        action_type=action_type,
        description=description,
        status="planning"
    )
    
    # Generate branch name using category and action
    branch_prefix = f"{category}/{action_type}"
    sanitized_title = title.lower().replace(" ", "-")
    sanitized_title = "".join(c for c in sanitized_title if c.isalnum() or c == "-")
    sanitized_title = sanitized_title[:30]
    date_str = datetime.now().strftime("%Y%m%d")
    branch_name = f"{branch_prefix}/{sanitized_title}-{date_str}"
    
    work_item.git_branch = branch_name
    
    # Create Git branch
    git_manager.create_branch(branch_name, checkout=True)
    
    # Initialize checklist based on category and action
    if category == "platform_feature":
        if action_type == "new":
            work_item.checklist = [
                {"item": "Define feature requirements and scope", "done": False},
                {"item": "Design database schema changes (if any)", "done": False},
                {"item": "Implement backend logic", "done": False},
                {"item": "Create/update UI templates", "done": False},
                {"item": "Test feature thoroughly", "done": False},
                {"item": "Document feature in work notes", "done": False},
                {"item": "Update user-facing documentation", "done": False}
            ]
        elif action_type == "change":
            work_item.checklist = [
                {"item": "Document current behavior", "done": False},
                {"item": "Implement changes", "done": False},
                {"item": "Test changes thoroughly", "done": False},
                {"item": "Update related documentation", "done": False},
                {"item": "Verify no regressions", "done": False}
            ]
        else:  # fix
            work_item.checklist = [
                {"item": "Reproduce the issue", "done": False},
                {"item": "Identify root cause", "done": False},
                {"item": "Implement fix", "done": False},
                {"item": "Test fix thoroughly", "done": False},
                {"item": "Verify issue is resolved", "done": False},
                {"item": "Document fix for future reference", "done": False}
            ]
    
    elif category == "integration":
        if action_type == "new":
            work_item.checklist = [
                {"item": "Research integration API/requirements", "done": False},
                {"item": "Create integration module structure", "done": False},
                {"item": "Implement core integration logic", "done": False},
                {"item": "Add configuration options", "done": False},
                {"item": "Test integration end-to-end", "done": False},
                {"item": "Document integration setup", "done": False},
                {"item": "Add to INTEGRATIONS.md doc (if exists)", "done": False}
            ]
        elif action_type == "change":
            work_item.checklist = [
                {"item": "Document current integration behavior", "done": False},
                {"item": "Implement changes", "done": False},
                {"item": "Test integration functionality", "done": False},
                {"item": "Update integration documentation", "done": False}
            ]
        else:  # fix
            work_item.checklist = [
                {"item": "Reproduce integration issue", "done": False},
                {"item": "Identify root cause", "done": False},
                {"item": "Implement fix", "done": False},
                {"item": "Test integration thoroughly", "done": False},
                {"item": "Document fix", "done": False}
            ]
    
    elif category == "service":
        if action_type == "new":
            work_item.checklist = [
                {"item": "Define service purpose and requirements", "done": False},
                {"item": "Check resource availability (RAM/CPU/disk)", "done": False},
                {"item": "Create docker-compose.yml or config files", "done": False},
                {"item": "Test service locally", "done": False},
                {"item": "Deploy to target VM/host", "done": False},
                {"item": "Configure monitoring/health checks", "done": False},
                {"item": "Add to service catalog in Calcifer", "done": False},
                {"item": "Document service configuration", "done": False}
            ]
        elif action_type == "change":
            work_item.checklist = [
                {"item": "Document current service configuration", "done": False},
                {"item": "Backup existing configuration", "done": False},
                {"item": "Make configuration changes", "done": False},
                {"item": "Test changes", "done": False},
                {"item": "Update service catalog entry", "done": False},
                {"item": "Update service documentation", "done": False}
            ]
        else:  # fix
            work_item.checklist = [
                {"item": "Identify service issue", "done": False},
                {"item": "Check logs and diagnostics", "done": False},
                {"item": "Implement fix", "done": False},
                {"item": "Restart/redeploy service", "done": False},
                {"item": "Verify service is healthy", "done": False},
                {"item": "Document fix for future reference", "done": False}
            ]
    
    elif category == "documentation":
        if action_type == "new":
            work_item.checklist = [
                {"item": "Define documentation scope and audience", "done": False},
                {"item": "Create document structure/outline", "done": False},
                {"item": "Write documentation content", "done": False},
                {"item": "Add examples and code snippets", "done": False},
                {"item": "Review for clarity and accuracy", "done": False},
                {"item": "Add to docs/ directory", "done": False}
            ]
        else:  # change (no "fix" for docs)
            work_item.checklist = [
                {"item": "Identify sections to update", "done": False},
                {"item": "Make documentation changes", "done": False},
                {"item": "Update examples if needed", "done": False},
                {"item": "Review for accuracy", "done": False}
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
    
    # Get associated commits from database
    db_commits = db.query(models.Commit).filter(
        models.Commit.work_item_id == work_id
    ).order_by(models.Commit.committed_date.desc()).all()
    
    # Get commits from Git branch (newer approach - shows real branch commits)
    branch_commits = []
    if work_item.git_branch:
        branch_commits = git_manager.get_branch_commits(work_item.git_branch)
    
    # Get branch merge status
    branch_merged = False
    if work_item.git_branch:
        branch_merged = git_manager.is_branch_merged(work_item.git_branch)
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
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    if index < len(work_item.checklist):
        work_item.checklist[index]["done"] = not work_item.checklist[index]["done"]
        # Mark the column as modified so SQLAlchemy saves it
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(work_item, "checklist")
        db.commit()
    
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
    git_status = git_manager.get_status()
    
    # Get author info
    try:
        author_name = git_manager.repo.config_reader().get_value("user", "name")
        author_email = git_manager.repo.config_reader().get_value("user", "email")
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
            git_manager.checkout_branch(work_item.git_branch)
        
        # Update CHANGES.md
        from datetime import datetime
        changes_path = os.path.join(git_manager.repo_path, "docs", "CHANGES.md")
        
# Prepare new entry with proper formatting
        today = datetime.now().strftime('%Y-%m-%d')
        author = git_manager.repo.config_reader().get_value("user", "name")
        
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
        git_manager.repo.git.add('-A')
        
        # Commit
        commit_sha = git_manager.commit(commit_message)
        
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
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    branch_name = work_item.git_branch
    
    try:
        # Delete Git branch if it exists
        if branch_name:
            try:
                # Switch to main first
                git_manager.checkout_branch("main")
                
                # Delete local branch
                git_manager.repo.delete_head(branch_name, force=True)
                
                # Try to delete remote branch (if it exists)
                try:
                    git_manager.repo.git.push('origin', '--delete', branch_name)
                except:
                    pass  # Remote branch might not exist, that's ok
                    
            except Exception as e:
                # Branch deletion failed, but continue with work item deletion
                print(f"Branch deletion failed: {e}")
        
        # Delete work item from database (cascades to commits)
        db.delete(work_item)
        db.commit()
        
        return RedirectResponse(
            url="/?success=Work item deleted successfully",
            status_code=303
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"/work/{work_id}?error=Delete failed: {str(e)}",
            status_code=303
        )    

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
    if git_manager.is_branch_merged(work_item.git_branch):
        work_item.branch_merged = True
        db.commit()
        return RedirectResponse(
            url=f"/work/{work_id}?success=Branch already merged",
            status_code=303
        )
    
    # VALIDATION: Check if CHANGES.md was updated
    if not git_manager.check_changes_md_updated():
        return RedirectResponse(
            url=f"/work/{work_id}?error=Cannot merge: docs/CHANGES.md not updated in this branch",
            status_code=303
        )
    
    # VALIDATION: Check if branch has commits
    branch_commits = git_manager.get_branch_commits(work_item.git_branch)
    if not branch_commits:
        return RedirectResponse(
            url=f"/work/{work_id}?error=Cannot merge: branch has no commits",
            status_code=303
        )
    
    # Attempt merge
    success, result = git_manager.merge_branch(work_item.git_branch)
    
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
    work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # VALIDATION PHASE
    errors = []
    
    # Check 1: All checklist items completed?
    incomplete_items = [item for item in work_item.checklist if not item.get("done", False)]
    if incomplete_items:
        errors.append(f"{len(incomplete_items)} checklist item(s) not completed")
    
    # Check 2: Branch exists?
    if not work_item.git_branch:
        errors.append("No Git branch associated with this work item")
    
    # Check 3: Branch has commits?
    if work_item.git_branch:
        branch_commits = git_manager.get_branch_commits(work_item.git_branch)
        if not branch_commits:
            errors.append("Branch has no commits")
    
    # Check 4: CHANGES.md updated?
    if work_item.git_branch:
        if not git_manager.check_changes_md_updated():
            errors.append("docs/CHANGES.md not updated in this branch")
    
    # If validation fails, stop here
    if errors:
        error_msg = " | ".join(errors)
        return RedirectResponse(
            url=f"/work/{work_id}?error={error_msg}",
            status_code=303
        )
    
    # MERGE PHASE
    # Check if already merged
    if git_manager.is_branch_merged(work_item.git_branch):
        work_item.branch_merged = True
    else:
        # Attempt merge
        success, result = git_manager.merge_branch(work_item.git_branch)
        
        if not success:
            return RedirectResponse(
                url=f"/work/{work_id}?error=Merge failed: {result}",
                status_code=303
            )
        
        # Update merge status
        work_item.branch_merged = True
        work_item.merge_commit_sha = result
    
    # COMPLETION PHASE
    work_item.status = "complete"
    work_item.completed_date = datetime.utcnow()
    db.commit()
    
    return RedirectResponse(
        url="/?success=Work item completed and merged successfully!",
        status_code=303
    )    

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
    """Create endpoint with monitoring, docs, and work item."""
    
    # 1. Create work item
    work_item = models.WorkItem(
        title=f"Add monitoring endpoint: {name}",
        category="service",
        action_type="new",
        description=f"Create monitoring endpoint for {endpoint_type} target: {target}",
        status="planning"
    )
    
    # Generate branch
    branch_name = f"service/new/endpoint-{name.lower().replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}"
    work_item.git_branch = branch_name
    git_manager.create_branch(branch_name, checkout=True)
    
    # Checklist for endpoint creation
    work_item.checklist = [
        {"item": "Define endpoint details (done by wizard)", "done": True},
        {"item": "Create documentation (done automatically)", "done": True},
        {"item": "Configure monitoring check (done automatically)", "done": True},
        {"item": "Verify endpoint is reachable", "done": False},  # Will be set based on check
        {"item": "Review and commit endpoint configuration", "done": False}
    ]
    
    db.add(work_item)
    db.commit()
    db.refresh(work_item)
    
    # 2. Create endpoint entry
    endpoint = models.Endpoint(
        name=name,
        endpoint_type=endpoint_type,
        target=target,
        port=port,
        check_interval=check_interval,
        description=description,
        work_item_id=work_item.id,
        status="unknown"  # Will be checked after setup
    )
    
    # 3. Generate documentation
    doc_content = generate_endpoint_documentation(name, endpoint_type, target, port, description)
    doc_filename = f"endpoint-{name.lower().replace(' ', '-')}.md"
    doc_path = os.path.join(git_manager.repo_path, "docs", doc_filename)
    
    # Create docs directory if doesn't exist
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    endpoint.documentation_url = f"/docs-viewer/{doc_filename}"
    
    # 4. Generate monitoring config (placeholder for now)
    monitor_config = {
        "check_type": endpoint_type,
        "target": target,
        "port": port,
        "interval": check_interval,
        "timeout": 5,
        "retries": 3
    }
    endpoint.monitor_config = monitor_config
    
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)  # ADD THIS
    
    # 5. Add files to git
    git_manager.stage_files([f"docs/{doc_filename}"])
    
    # 5.5. PERFORM INITIAL CHECK
    is_up = perform_endpoint_check(endpoint)
    endpoint.last_check = datetime.utcnow()
    if is_up:
        endpoint.status = "up"
        endpoint.last_up = datetime.utcnow()
        endpoint.consecutive_failures = 0
    else:
        endpoint.status = "down"
        endpoint.last_down = datetime.utcnow()
        endpoint.consecutive_failures = 1
    db.commit()
    
    # 6. Update work item notes
    work_item.notes = f"""# Endpoint: {name}

**Type:** {endpoint_type}
**Target:** {target}
{'**Port:** ' + str(port) if port else ''}
**Check Interval:** {check_interval}s
**Initial Status:** {'✅ UP' if is_up else '❌ DOWN'}

## Generated Files
- Documentation: `docs/{doc_filename}`
- Monitoring config: Stored in database

## Configuration
```json
{json.dumps(monitor_config, indent=2)}
```

## Initial Check Results
- Performed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Status: {'UP - endpoint is reachable' if is_up else 'DOWN - endpoint is not reachable'}

## Next Steps
1. Review documentation
2. Commit changes
3. {'Investigate connectivity issue' if not is_up else 'Verify monitoring configuration'}
4. Merge and complete
"""
    
    # Auto-complete checklist items that wizard already did
    work_item.checklist[0]["done"] = True  # Define endpoint details
    work_item.checklist[1]["done"] = True  # Create documentation
    work_item.checklist[2]["done"] = True  # Configure monitoring check
    work_item.checklist[3]["done"] = is_up  # Verify endpoint is reachable (only if UP)
    # checklist[4] stays False - user needs to commit
    
    db.commit()
    
    # 7. Redirect to work item
    status_msg = "Endpoint created and is UP! ✅" if is_up else "Endpoint created but is DOWN ❌ - check connectivity"
    return RedirectResponse(url=f"/work/{work_item.id}?success={status_msg}", status_code=303)

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
    
    # Perform check based on endpoint type
    is_up = perform_endpoint_check(endpoint)
    
    # Update status
    endpoint.last_check = datetime.utcnow()
    if is_up:
        endpoint.status = "up"
        endpoint.last_up = datetime.utcnow()
        endpoint.consecutive_failures = 0
    else:
        endpoint.status = "down"
        endpoint.last_down = datetime.utcnow()
        endpoint.consecutive_failures += 1
    
    db.commit()
    
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
    """Generate markdown documentation for endpoint."""
    port_section = f"\n**Port:** {port}" if port else ""
    
    return f"""# Endpoint: {name}

## Overview

**Type:** {endpoint_type.upper()}  
**Target:** `{target}`{port_section}  
**Status:** Monitored by Calcifer

{description if description else ''}

## Monitoring Configuration

This endpoint is monitored for availability.

**Check Type:** {endpoint_type}  
**Check Method:** {'Ping (ICMP)' if endpoint_type == 'network' else 'TCP connection' if endpoint_type == 'tcp' else 'HTTP request'}

## Access Information

**Target:** `{target}`{port_section}

## Troubleshooting

### Endpoint is Down

1. **Check network connectivity:**
```bash
   ping {target}
```

2. **Check specific port (if applicable):**
```bash
   {'telnet ' + target + ' ' + str(port) if port else 'nc -zv ' + target}
```

3. **Check firewall rules:**
   - Verify firewall allows traffic from monitoring server
   - Check iptables/firewalld rules

4. **Verify service is running:**
   - Check if the target service/device is online
   - Review service logs

## History

- **Created:** {datetime.now().strftime('%Y-%m-%d')}
- **Purpose:** Monitor availability of {name}

## Related

- Endpoint configuration in Calcifer
- Service catalog entry
"""

def perform_endpoint_check(endpoint: models.Endpoint) -> bool:
    """
    Perform actual connectivity check based on endpoint type.
    
    Returns True if endpoint is up, False if down.
    """
    import subprocess
    import socket
    
    try:
        if endpoint.endpoint_type == "network":
            # Ping check
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', endpoint.target],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        
        elif endpoint.endpoint_type == "tcp":
            # TCP port check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((endpoint.target, endpoint.port))
            sock.close()
            return result == 0
        
        elif endpoint.endpoint_type == "http" or endpoint.endpoint_type == "https":
            # HTTP check
            import urllib.request
            protocol = "https" if endpoint.endpoint_type == "https" else "http"
            port_part = f":{endpoint.port}" if endpoint.port else ""
            url = f"{protocol}://{endpoint.target}{port_part}"
            
            req = urllib.request.Request(url, method='GET')
            response = urllib.request.urlopen(req, timeout=5)
            return response.status < 400
        
        else:
            # Unknown type, assume down
            return False
            
    except Exception as e:
        print(f"Endpoint check failed for {endpoint.name}: {e}")
        return False

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