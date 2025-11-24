# Calcifer Architecture Patterns Guide

## Overview

This guide documents the architectural patterns used in Calcifer after Phase 2 refactoring. Follow these patterns when adding new features to maintain consistency and clean separation of concerns.

---

## Core Principles

### The Three-Layer Rule

```
┌─────────────────────────────────────┐
│  HTTP/UI Layer (main.py)            │  ← Routes only, no business logic
│  - Thin wrappers                    │
│  - Parse HTTP requests              │
│  - Call module methods              │
│  - Return HTTP responses            │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  Service Layer (core/* + integrations/*) │  ← ALL business logic here
│  - Business logic                   │
│  - Validation                       │
│  - Orchestration                    │
│  - Data transformation              │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  Data Layer (models.py, database.py)│  ← Database only
│  - Database schema                  │
│  - ORM models                       │
│  - Basic queries                    │
└─────────────────────────────────────┘
```

**Golden Rule:** Routes should be 5-15 lines max. If longer, move logic to modules!

---

## Pattern 1: Routes ↔ HTML Templates

### How Routes Interact with Templates

**Routes have TWO jobs:**
1. **GET routes:** Fetch data and render templates
2. **POST routes:** Call module methods and redirect

### GET Route Pattern (Read/Display)

```python
@app.get("/resource/{id}", response_class=HTMLResponse)
async def view_resource(request: Request, resource_id: int, db: Session = Depends(get_db)):
    """View resource detail."""
    # ✅ Acceptable: Simple data fetching for display
    resource = module.get_resource(db, resource_id)
    
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")
    
    # ✅ Return template with data
    return templates.TemplateResponse("resource_detail.html", {
        "request": request,
        "resource": resource
    })
```

**Rules for GET routes:**
- ✅ Can call module `get_*()` methods
- ✅ Can call multiple modules to gather display data
- ✅ Should NOT modify data (read-only)
- ❌ NO business logic
- ❌ NO complex transformations

### POST Route Pattern (Actions)

```python
@app.post("/resource/{id}/action")
async def perform_action(
    resource_id: int,
    param1: str = Form(...),
    param2: str = Form(...),
    db: Session = Depends(get_db)
):
    """Perform action on resource."""
    # ✅ Call module method - it does ALL the work
    success, message = module.perform_action(db, resource_id, param1, param2)
    
    # ✅ Redirect based on result
    if success:
        return RedirectResponse(url=f"/success?message={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/resource/{id}?error={message}", status_code=303)
```

**Rules for POST routes:**
- ✅ Parse form data
- ✅ Call ONE module method that does the work
- ✅ Redirect based on success/failure
- ❌ NO validation (module does it)
- ❌ NO business logic
- ❌ NO database operations

### Example: Perfect Route ✅

```python
@app.post("/work/{work_id}/commit")
async def commit_changes(
    work_id: int,
    commit_message: str = Form(...),
    changes_entry: str = Form(...),
    db: Session = Depends(get_db)
):
    """Commit changes and update CHANGES.md."""
    # Just call the module method
    success, message = work_module.commit_work(
        db, work_id, commit_message, changes_entry
    )
    
    # Redirect based on result
    if success:
        return RedirectResponse(url=f"/work/{work_id}?success={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/work/{work_id}/commit?error={message}", status_code=303)
```

**Why this is perfect:**
- 12 lines total
- No business logic
- No database queries
- Just HTTP → Module → HTTP
- Easy to test
- Easy to understand

---

## Pattern 2: Core Modules

### What Are Core Modules?

**Core modules are REQUIRED for Calcifer to work.** They handle fundamental functionality.

**Location:** `src/core/`

**Current Core Modules:**
- `work_module.py` - Work item management
- `service_catalog_module.py` - Infrastructure service catalog
- `documentation_module.py` - Documentation management
- `git_module.py` - Local Git operations
- `settings_module.py` - Configuration management

### Core Module Structure

```python
"""
Core Module Name

Handles [domain] functionality.
This is CORE functionality - required for Calcifer to work.
"""

from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from .. import models
from .other_core_module import other_module  # ✅ Can import other core modules


class ModuleNameModule:
    """
    Core module for [domain] management.
    
    This module handles:
    - [Responsibility 1]
    - [Responsibility 2]
    - [Responsibility 3]
    """
    
    @staticmethod
    def create_something(
        db: Session,
        param1: str,
        param2: str
    ) -> models.Something:
        """
        Create something with automatic setup.
        
        Args:
            db: Database session
            param1: Description
            param2: Description
            
        Returns:
            Created model instance
        """
        # Business logic here
        # Validation here
        # Database operations here
        return created_object
    
    @staticmethod
    def update_something(
        db: Session,
        something_id: int,
        new_value: str
    ) -> Tuple[bool, str]:
        """
        Update something.
        
        Args:
            db: Database session
            something_id: ID to update
            new_value: New value
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Get from DB
        # Validate
        # Update
        # Save
        return True, "Success message"
    
    @staticmethod
    def delete_something(
        db: Session,
        something_id: int
    ) -> Tuple[bool, str]:
        """
        Delete something with cleanup.
        
        Args:
            db: Database session
            something_id: ID to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate can delete
        # Clean up related data
        # Delete
        return True, "Deleted successfully"


# Singleton instance for easy import
module_name_module = ModuleNameModule()
```

### Core Module Rules

**Can Do:**
- ✅ Use other core modules (import from `.other_module`)
- ✅ Use database models (`from .. import models`)
- ✅ Complex business logic
- ✅ Validation
- ✅ Database operations
- ✅ Call git_module for Git operations

**Cannot Do:**
- ❌ Use integrations (core must work without them)
- ❌ Use HTTP/FastAPI stuff (Request, Response, etc.)
- ❌ Return HTTP responses
- ❌ Access request objects

**Return Values:**
- `Model` - For create operations
- `Optional[Model]` - For get operations (None if not found)
- `List[Model]` - For list operations
- `Tuple[bool, str]` - For operations that can fail (success flag + message)

### Adding a Method to a Core Module

**Example: Add a method to work_module**

```python
# In src/core/work_module.py

@staticmethod
def archive_work(db: Session, work_id: int) -> Tuple[bool, str]:
    """
    Archive a completed work item.
    
    Args:
        db: Database session
        work_id: Work item ID
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Step 1: Get the work item
    work_item = db.query(models.WorkItem).filter(
        models.WorkItem.id == work_id
    ).first()
    
    if not work_item:
        return False, "Work item not found"
    
    # Step 2: Validate can archive
    if work_item.status != "complete":
        return False, "Can only archive completed work"
    
    # Step 3: Perform the action
    work_item.archived = True
    work_item.archived_date = datetime.utcnow()
    db.commit()
    
    # Step 4: Return result
    return True, "Work item archived successfully"
```

Then use in a route:

```python
@app.post("/work/{work_id}/archive")
async def archive_work(work_id: int, db: Session = Depends(get_db)):
    """Archive completed work item."""
    success, message = work_module.archive_work(db, work_id)
    
    if success:
        return RedirectResponse(url=f"/?success={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/work/{work_id}?error={message}", status_code=303)
```

---

## Pattern 3: Integration Modules

### What Are Integration Modules?

**Integration modules are OPTIONAL enhancements.** Calcifer works without them, but they add powerful features.

**Location:** `src/integrations/`

**Current Integration Modules:**
- `monitoring/` - Endpoint health checks (optional monitoring feature)

### Integration vs Core: Key Differences

| Aspect | Core Modules | Integration Modules |
|--------|--------------|---------------------|
| Required? | ✅ Yes | ❌ No (optional) |
| Location | `src/core/` | `src/integrations/` |
| Import from | `from .core import module` | `from .integrations import module` |
| Can use core? | ✅ Yes | ✅ Yes |
| Can use integrations? | ❌ No | ✅ Yes |
| Purpose | Fundamental features | Enhancements |

### Integration Module Structure

Integrations typically have TWO parts:

**1. Integration Class** - Low-level operations
**2. Module Class** - Business logic that uses core + integration

#### Example: Monitoring Integration

```
src/integrations/monitoring/
├── __init__.py                    # Exports both
├── integration.py                 # Low-level monitoring operations
└── endpoint_module.py             # Business logic (uses core modules)
```

**integration.py** - Low-level:
```python
"""
Monitoring Integration

Provides synthetic monitoring and endpoint health checking.
This is an OPTIONAL integration - Calcifer works without it.
"""

class MonitoringIntegration:
    """Low-level health check operations."""
    
    def check_endpoint(self, endpoint) -> Tuple[bool, Optional[str]]:
        """Perform health check on an endpoint."""
        # Low-level check logic
        # Network operations
        # No database
        # No core module dependencies
        return is_up, error_message
    
    @staticmethod
    def generate_endpoint_documentation(name, type, target, port, description) -> str:
        """Generate markdown documentation for an endpoint."""
        # Pure function - no dependencies
        return markdown_content


# Singleton
monitoring = MonitoringIntegration()
```

**endpoint_module.py** - Business logic:
```python
"""
Monitoring Endpoint Module

Business logic for managing monitored endpoints.
Uses core modules (work, docs, git) to create endpoints with full tracking.
"""

from ...core import work_module, documentation_module, git_module
from ...models import Endpoint
from .integration import monitoring


class EndpointModule:
    """Endpoint management with work item tracking."""
    
    def create_endpoint_with_work_item(
        self,
        db: Session,
        name: str,
        endpoint_type: str,
        target: str,
        port: Optional[int],
        check_interval: int,
        description: Optional[str]
    ) -> Tuple[int, str]:
        """
        Create endpoint with full work item workflow.
        
        This orchestrates multiple core modules + monitoring integration.
        """
        # 1. Use work_module to create work item
        work_item = work_module.create_work_item(...)
        
        # 2. Create endpoint in database
        endpoint = Endpoint(...)
        
        # 3. Use monitoring integration to generate docs
        doc_content = monitoring.generate_endpoint_documentation(...)
        
        # 4. Use documentation_module to save docs
        documentation_module.create_doc(doc_filename, doc_content)
        
        # 5. Use git_module to commit
        git_module.stage_files([...])
        git_module.commit(...)
        
        # 6. Use monitoring integration to check endpoint
        is_up = monitoring.update_endpoint_status(endpoint, db)
        
        return work_item.id, success_message


# Singleton
endpoint_module = EndpointModule()
```

**__init__.py** - Exports:
```python
"""
Monitoring Integration Module
"""

from .integration import MonitoringIntegration, monitoring
from .endpoint_module import EndpointModule, endpoint_module

__all__ = [
    'MonitoringIntegration',
    'monitoring',
    'EndpointModule',
    'endpoint_module',
]
```

### Integration Module Rules

**Integration Class (integration.py):**
- ✅ Low-level operations (health checks, API calls)
- ✅ Pure functions where possible
- ✅ Minimal dependencies
- ❌ No core module usage
- ❌ No database operations
- ❌ Keep it focused and simple

**Module Class (endpoint_module.py):**
- ✅ Use core modules freely (composition pattern)
- ✅ Orchestrate workflows
- ✅ Database operations
- ✅ Can use integration class
- ❌ No HTTP concerns

### Adding a New Integration

**Example: Add Slack notifications**

**Step 1: Create directory structure**
```
src/integrations/notifications/
├── __init__.py
├── integration.py        # Slack API client
└── notification_module.py  # Business logic
```

**Step 2: Create integration.py**
```python
"""
Notifications Integration

Send notifications via various channels.
This is OPTIONAL - Calcifer works without it.
"""

import requests


class NotificationsIntegration:
    """Low-level notification sending."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
    
    def send_slack_message(self, message: str) -> bool:
        """Send message to Slack."""
        if not self.webhook_url:
            return False
        
        try:
            response = requests.post(self.webhook_url, json={"text": message})
            return response.status_code == 200
        except:
            return False


# Singleton
notifications = NotificationsIntegration()
```

**Step 3: Create notification_module.py**
```python
"""
Notification Module

Business logic for notifications.
Uses core modules to determine what to notify about.
"""

from ...core import work_module
from .integration import notifications


class NotificationModule:
    """Notification business logic."""
    
    def notify_work_complete(self, db: Session, work_id: int) -> bool:
        """Send notification when work is completed."""
        # Use core module to get work item
        work_item = work_module.get_work_item(db, work_id)
        
        if not work_item or work_item.status != "complete":
            return False
        
        # Format message
        message = f"✅ Work completed: {work_item.title}"
        
        # Use integration to send
        return notifications.send_slack_message(message)


# Singleton
notification_module = NotificationModule()
```

**Step 4: Export in __init__.py**
```python
from .integration import notifications
from .notification_module import notification_module

__all__ = ['notifications', 'notification_module']
```

**Step 5: Use in main.py**
```python
from .integrations import notifications, notification_module

@app.post("/work/{work_id}/merge-and-complete")
async def merge_and_complete(work_id: int, db: Session = Depends(get_db)):
    success, message = work_module.merge_and_complete(db, work_id)
    
    if success:
        # Optional: Send notification if integration is enabled
        notification_module.notify_work_complete(db, work_id)
        
        return RedirectResponse(url=f"/?success={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/work/{work_id}?error={message}", status_code=303)
```

---

## Pattern 4: Database Operations

### Where Database Queries Belong

**✅ YES - In Modules:**
```python
# In work_module.py
@staticmethod
def get_work_item(db: Session, work_id: int) -> Optional[models.WorkItem]:
    """Get work item by ID."""
    return db.query(models.WorkItem).filter(
        models.WorkItem.id == work_id
    ).first()
```

**❌ NO - Not in Routes:**
```python
# In main.py - DON'T DO THIS!
@app.get("/work/{work_id}")
async def work_detail(work_id: int, db: Session = Depends(get_db)):
    # ❌ Direct database query in route
    work_item = db.query(models.WorkItem).filter(
        models.WorkItem.id == work_id
    ).first()
```

### Exception: Simple Display Queries

**Acceptable in GET routes for display only:**
```python
@app.get("/work/{work_id}")
async def work_detail(request: Request, work_id: int, db: Session = Depends(get_db)):
    # ✅ Simple fetch for display is OK
    work_item = db.query(models.WorkItem).filter(
        models.WorkItem.id == work_id
    ).first()
    
    if not work_item:
        raise HTTPException(status_code=404)
    
    # ✅ Just rendering, no business logic
    return templates.TemplateResponse("work_item.html", {
        "request": request,
        "work": work_item
    })
```

**Better approach (more consistent):**
```python
@app.get("/work/{work_id}")
async def work_detail(request: Request, work_id: int, db: Session = Depends(get_db)):
    # ✅ Use module method for consistency
    work_item = work_module.get_work_item(db, work_id)
    
    if not work_item:
        raise HTTPException(status_code=404)
    
    return templates.TemplateResponse("work_item.html", {
        "request": request,
        "work": work_item
    })
```

### Database Operations Rules

| Operation | Where | Why |
|-----------|-------|-----|
| Simple SELECT for display | Route (acceptable) | Just fetching data to show |
| SELECT with joins | Module | Getting complex |
| INSERT/UPDATE/DELETE | Module (always) | Business logic |
| Validation before save | Module (always) | Business logic |
| Multiple queries | Module (always) | Orchestration |

---

## Pattern 5: Return Values & Error Handling

### Module Return Types

**For operations that can fail:**
```python
Tuple[bool, str]  # (success flag, message)

# Example
def do_something(db: Session, id: int) -> Tuple[bool, str]:
    if error:
        return False, "Error message for user"
    
    # do work
    
    return True, "Success message for user"
```

**For object retrieval:**
```python
Optional[Model]  # Model or None if not found

# Example
def get_something(db: Session, id: int) -> Optional[models.Something]:
    return db.query(models.Something).filter(
        models.Something.id == id
    ).first()
```

**For creation:**
```python
Model  # Return the created object

# Example
def create_something(db: Session, name: str) -> models.Something:
    obj = models.Something(name=name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
```

**For lists:**
```python
List[Model]  # Can be empty list

# Example
def get_all_things(db: Session) -> List[models.Thing]:
    return db.query(models.Thing).all()
```

### Route Error Handling Pattern

```python
@app.post("/resource/action")
async def perform_action(param: str = Form(...), db: Session = Depends(get_db)):
    """Perform action."""
    success, message = module.perform_action(db, param)
    
    if success:
        return RedirectResponse(
            url=f"/success-page?success={message}",
            status_code=303
        )
    else:
        return RedirectResponse(
            url=f"/failure-page?error={message}",
            status_code=303
        )
```

**Key points:**
- ✅ Module returns success flag + user-friendly message
- ✅ Route just redirects with the message
- ✅ Use `?success=` for success messages
- ✅ Use `?error=` for error messages
- ✅ Templates show these messages to user

---

## Pattern 6: Logging in Modules

### Overview

All modules use centralized logging for observability and debugging. This pattern ensures consistent log output across the application.

### The Logging Architecture

```
Application Startup (main.py)
    ↓
setup_logging() - Configure once
    ↓
All modules get_logger('module.name')
    ↓
Structured output to stdout
    ↓
Ready for log aggregation
```

---

### Core Module Logging Pattern

**Template:**
```python
"""
Module Name Module

Description of module functionality.
This is CORE functionality - required for Calcifer to work.
"""

from sqlalchemy.orm import Session
from typing import Tuple
from .logging_module import get_logger
from .. import models

# Create module-level logger
logger = get_logger('calcifer.core.module_name')


class ModuleNameModule:
    """Module description."""
    
    @staticmethod
    def do_something(db: Session, param: str) -> Tuple[bool, str]:
        """
        Do something with logging.
        
        Args:
            db: Database session
            param: Parameter
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Starting operation with param: {param}")
        
        try:
            # Validation with debug logging
            if not param:
                logger.warning("Empty parameter provided, using default")
                param = "default"
            
            # Operation
            result = perform_operation(param)
            
            # Success logging
            logger.info(f"Operation completed successfully: {result}")
            return True, "Success"
            
        except Exception as e:
            # Error logging with stack trace
            logger.error(f"Operation failed: {e}", exc_info=True)
            return False, str(e)


# Singleton
module_name_module = ModuleNameModule()
```

---

### Integration Module Logging Pattern

**Template:**
```python
"""
Integration Name Integration

Optional integration for extended functionality.
"""

from ...core.logging_module import get_logger

# Create integration-level logger
logger = get_logger('calcifer.integrations.integration_name')


class IntegrationClass:
    """Integration description."""
    
    def __init__(self):
        logger.info("Initializing integration")
        self.ready = False
    
    def check_connectivity(self) -> bool:
        """Test integration connectivity."""
        logger.debug("Checking integration connectivity")
        
        try:
            # Test connection
            result = test_connection()
            
            if result:
                logger.info("Integration connectivity verified")
                self.ready = True
            else:
                logger.warning("Integration connectivity check failed")
                self.ready = False
            
            return result
        except Exception as e:
            logger.error(f"Integration connectivity error: {e}", exc_info=True)
            return False


# Singleton
integration = IntegrationClass()
```

---

### Route Logging Pattern

**Routes should NOT have loggers** - they're too thin. Logging happens in modules.

**Exception:** You can add request/response logging at the app level:

```python
# In main.py

from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {duration:.3f}s with status {response.status_code}"
    )
    
    return response
```

---

### Logging Levels Decision Tree

```
Is it operational information?
├─ YES → Are you debugging?
│  ├─ YES → logger.debug()
│  └─ NO  → logger.info()
│
└─ NO  → Is it a problem?
   ├─ YES → Can the app continue?
   │  ├─ YES → Is it unexpected?
   │  │  ├─ YES → logger.warning()
   │  │  └─ NO  → logger.error(exc_info=True)
   │  └─ NO  → logger.critical()
   │
   └─ NO  → Don't log it
```

**Examples:**

```python
# DEBUG - Detailed flow information
logger.debug(f"Generated branch name: {branch_name}")
logger.debug(f"Processing {len(items)} checklist items")

# INFO - Important operational events
logger.info("Work item created successfully")
logger.info(f"Branch merged: {branch_name} → main")

# WARNING - Unexpected but handled
logger.warning("Branch already exists, reusing")
logger.warning("CHANGES.md entry truncated to 500 chars")

# ERROR - Problems that need attention
logger.error("Failed to create Git branch", exc_info=True)
logger.error(f"Database operation failed: {e}", exc_info=True)

# CRITICAL - Application cannot continue
logger.critical("Database file is corrupted")
logger.critical("Git repository not found")
```

---

### Anti-Patterns to Avoid

#### ❌ Anti-Pattern 1: Logging in Routes

```python
# BAD - Don't do this
@app.post("/resource/action")
async def action_route(param: str = Form(...)):
    logger.info(f"Route called with {param}")  # ❌ Too noisy
    result = module.do_action(param)
    logger.info(f"Route completed")  # ❌ Redundant
    return RedirectResponse(...)
```

**Why it's bad:**
- Routes should be thin
- Module already logs the operation
- HTTP middleware can log requests

**Better:**
```python
# GOOD - Module handles logging
@app.post("/resource/action")
async def action_route(param: str = Form(...)):
    result = module.do_action(param)  # Module logs internally
    return RedirectResponse(...)
```

---

#### ❌ Anti-Pattern 2: Logging Sensitive Data

```python
# BAD - Don't log sensitive data
logger.info(f"User logged in with password: {password}")  # ❌ Security issue
logger.debug(f"API token: {token}")  # ❌ Credentials exposed
```

**Better:**
```python
# GOOD - Log without sensitive data
logger.info(f"User logged in: {username}")
logger.debug("API authentication successful")
```

---

#### ❌ Anti-Pattern 3: Excessive Debug Logging

```python
# BAD - Too much noise
def process_items(items):
    for item in items:
        logger.debug(f"Item {item.id}")  # ❌ 1000 items = 1000 logs
        logger.debug(f"Processing: {item.name}")
        logger.debug(f"Status: {item.status}")
        # ... more processing
```

**Better:**
```python
# GOOD - Summary logging
def process_items(items):
    logger.info(f"Processing {len(items)} items")
    
    for item in items:
        # Process silently unless error
        try:
            process_item(item)
        except Exception as e:
            logger.error(f"Failed to process item {item.id}: {e}")
    
    logger.info("All items processed successfully")
```

---

#### ❌ Anti-Pattern 4: Not Using exc_info

```python
# BAD - No stack trace
try:
    result = dangerous_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")  # ❌ No context
    return False, str(e)
```

**Better:**
```python
# GOOD - Full stack trace
try:
    result = dangerous_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)  # ✅ Stack trace
    return False, str(e)
```

---

### Testing with Logging

When writing tests, you can verify logs:

```python
import logging
import pytest

def test_operation_logs_success(db_session, caplog):
    """Test successful operation logs correctly."""
    with caplog.at_level(logging.INFO):
        result = module.do_something(db_session, "test")
    
    assert "Operation completed successfully" in caplog.text
    assert result is True

def test_operation_logs_error(db_session, caplog):
    """Test error operation logs with stack trace."""
    with caplog.at_level(logging.ERROR):
        result = module.do_something(db_session, "invalid")
    
    assert "Operation failed" in caplog.text
    assert result is False
```

---

### Production Considerations

#### Environment-Based Configuration

```python
# main.py
import os
import logging

# Set log level from environment
log_level_name = os.getenv('CALCIFER_LOG_LEVEL', 'INFO')
log_level = getattr(logging, log_level_name.upper())

# JSON format for production log aggregation
format_json = os.getenv('CALCIFER_LOG_FORMAT') == 'json'

setup_logging(level=log_level, format_json=format_json)
```

#### Docker Configuration

```yaml
# docker-compose.yml
services:
  calcifer:
    environment:
      - CALCIFER_LOG_LEVEL=INFO
      - CALCIFER_LOG_FORMAT=json
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

### Checklist: Adding Logging to New Modules

When creating a new module:

- [ ] Import logging: `from .logging_module import get_logger`
- [ ] Create logger: `logger = get_logger('calcifer.core.module_name')`
- [ ] Log operation start: `logger.info("Starting operation")`
- [ ] Log success: `logger.info("Operation completed")`
- [ ] Log errors: `logger.error("Error", exc_info=True)`
- [ ] Use appropriate levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Don't log sensitive data
- [ ] Test that logs appear correctly

---

### Summary: Logging Golden Rules

1. **One Setup:** Call `setup_logging()` once in main.py
2. **Module Loggers:** Each module gets its own logger
3. **Appropriate Levels:** DEBUG < INFO < WARNING < ERROR < CRITICAL
4. **Include Context:** Use exc_info=True for errors
5. **No Sensitive Data:** Never log passwords, tokens, keys
6. **Structured Output:** Ready for log aggregation
7. **Test Logs:** Verify important operations log correctly

---

## Checklist: Adding New Functionality

### ✅ Adding a New Feature

**Step 1: Decide - Core or Integration?**
- [ ] Is it required for Calcifer to work? → Core module
- [ ] Is it an optional enhancement? → Integration module

**Step 2: Create/Update Module**
- [ ] Add method to appropriate module
- [ ] Method does ALL business logic
- [ ] Method does ALL validation
- [ ] Method does ALL database operations
- [ ] Method returns appropriate type (Model, Tuple[bool, str], etc.)
- [ ] Add docstring with Args and Returns

**Step 3: Create Route**
- [ ] GET route: Fetch data, render template
- [ ] POST route: Parse form, call module, redirect
- [ ] Route is 5-15 lines max
- [ ] NO business logic in route
- [ ] NO database queries in route (except simple display)

**Step 4: Create Template**
- [ ] Template receives data from route
- [ ] Template displays success/error messages
- [ ] Template has forms that POST to routes

**Step 5: Test**
- [ ] Test the workflow end-to-end
- [ ] Test error cases
- [ ] Verify business logic in module works
- [ ] Verify route just coordinates

---

## Anti-Patterns to Avoid

### ❌ Business Logic in Routes

**Bad:**
```python
@app.post("/work/new")
async def create_work(title: str = Form(...), db: Session = Depends(get_db)):
    # ❌ Validation in route
    if not title or len(title) < 3:
        return RedirectResponse(url="/?error=Title too short", status_code=303)
    
    # ❌ Business logic in route
    branch_name = f"feature/{title.lower().replace(' ', '-')}"
    
    # ❌ Database operations in route
    work = models.WorkItem(title=title, git_branch=branch_name)
    db.add(work)
    db.commit()
    
    return RedirectResponse(url=f"/work/{work.id}", status_code=303)
```

**Good:**
```python
@app.post("/work/new")
async def create_work(title: str = Form(...), db: Session = Depends(get_db)):
    # ✅ Just call module
    work = work_module.create_work_item(db, title)
    return RedirectResponse(url=f"/work/{work.id}", status_code=303)
```

### ❌ HTTP Concerns in Modules

**Bad:**
```python
# In module - DON'T DO THIS!
def create_something(request: Request, db: Session):
    title = request.form.get("title")  # ❌ HTTP concerns
    # ...
    return RedirectResponse(url="...")  # ❌ HTTP response
```

**Good:**
```python
# In module
def create_something(db: Session, title: str) -> models.Something:
    # ✅ Pure business logic
    # ✅ Returns model object
    return created_object
```

### ❌ Core Modules Using Integrations

**Bad:**
```python
# In core/work_module.py - DON'T DO THIS!
from ..integrations import notifications  # ❌ Core using integration

def complete_work(db: Session, work_id: int):
    # Complete the work
    notifications.send_slack_message("Work done!")  # ❌ Optional feature in core
```

**Good:**
```python
# In main.py route
success, message = work_module.complete_work(db, work_id)
if success:
    # ✅ Route optionally uses integration
    notification_module.notify_work_complete(db, work_id)
```

---

## Summary

### The Golden Rules

1. **Routes are thin** - 5-15 lines, no business logic
2. **Modules are thick** - All business logic, validation, database
3. **Core can't use integrations** - Must work standalone
4. **Integrations can use core** - Composition pattern
5. **Return Tuple[bool, str]** - For operations that can fail
6. **Methods are static** - Use @staticmethod, access via singleton

### Quick Reference

**When adding a feature, ask:**
- Is this required? → Core module
- Is this optional? → Integration module
- Does route do business logic? → Move to module!
- Does module return HTTP response? → Return data instead!
- Can I test the module without running the server? → Yes = good architecture!

---

This pattern documentation ensures Calcifer stays clean, maintainable, and easy to extend! 🔥