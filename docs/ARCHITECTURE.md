# Calcifer Architecture (v2.0 - Refactored)

## Overview

Calcifer now uses a clean three-layer architecture:

```
┌─────────────────────────────────────────┐
│         HTTP/UI Layer (main.py)         │
│  - Routing                              │
│  - Request/Response handling            │
│  - Template rendering                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Service Layer (core/*)             │
│  - Business logic                       │
│  - Validation                           │
│  - Orchestration                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│     Data Layer (models.py, database.py) │
│  - Database operations                  │
│  - ORM models                           │
│  - Schema validation                    │
└─────────────────────────────────────────┘
```

## Directory Structure

```
calcifer-app/
├── src/
│   ├── main.py                    # HTTP routing (thin layer)
│   │
│   ├── core/                      # Business logic services
│   │   ├── __init__.py
│   │   ├── work_service.py        # Work item operations
│   │   ├── service_catalog_service.py  # Service catalog
│   │   ├── documentation_service.py    # Doc management
│   │   ├── endpoint_service.py    # Monitoring endpoints
│   │   └── git_service.py         # Git wrapper
│   │
│   ├── integrations/              # External integrations
│   │   ├── __init__.py
│   │   ├── git.py                 # Git operations
│   │   └── monitoring.py          # Health checks
│   │
│   ├── models.py                  # SQLAlchemy models
│   ├── schemas.py                 # Pydantic schemas
│   └── database.py                # DB configuration
│
├── templates/                     # Jinja2 templates
├── static/                        # CSS/JS assets
└── data/                          # SQLite database
```

## Layer Responsibilities

### 1. HTTP/UI Layer (main.py)

**Responsibilities:**
- Define FastAPI routes
- Parse HTTP requests
- Validate form data
- Call service methods
- Return HTTP responses
- Render templates

**What NOT to do:**
- ❌ Business logic
- ❌ Database queries (except simple gets)
- ❌ Complex validation
- ❌ Git operations

**Example:**
```python
@app.post("/work/new")
async def create_work(
    title: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    # Just call the service
    work_item = work_service.create_work_item(db, title, category, ...)
    return RedirectResponse(url=f"/work/{work_item.id}")
```

### 2. Service Layer (core/*)

**Responsibilities:**
- Business logic
- Validation
- Orchestration (calling multiple operations)
- Error handling
- Data transformation

**What NOT to do:**
- ❌ HTTP concerns (requests, responses)
- ❌ Template rendering
- ❌ URL routing

**Example:**
```python
class WorkService:
    def create_work_item(self, db, title, category, action_type, description):
        # Business logic here
        work_item = models.WorkItem(...)
        branch_name = self._generate_branch_name(...)
        git_manager.create_branch(branch_name)
        work_item.checklist = self._generate_checklist(...)
        db.add(work_item)
        db.commit()
        return work_item
```

### 3. Data Layer (models.py, database.py)

**Responsibilities:**
- Database schema
- ORM models
- Basic queries
- Relationships

**What NOT to do:**
- ❌ Business logic
- ❌ Complex validation
- ❌ External integrations

## Service Descriptions

### WorkService (`core/work_service.py`)

**Purpose:** Manage work item lifecycle

**Key Methods:**
- `create_work_item()` - Create with branch and checklist
- `get_work_item()` - Fetch by ID
- `get_active_work()` - Get in-progress items
- `toggle_checklist_item()` - Update checklist
- `update_notes()` - Save documentation
- `commit_work()` - Commit changes with CHANGES.md
- `validate_for_completion()` - Check if ready to complete
- `merge_and_complete()` - Merge and mark done
- `delete_work_item()` - Remove work and branch

**Dependencies:**
- Git integration (for branches)
- Documentation service (for CHANGES.md)

### ServiceCatalogService (`core/service_catalog_service.py`)

**Purpose:** Manage service catalog

**Key Methods:**
- `create_service()` - Add new service
- `update_service()` - Modify service
- `delete_service()` - Remove service
- `get_all_services()` - List all
- `get_service_by_id()` - Fetch by ID
- `get_services_by_host()` - Filter by host
- `get_services_by_type()` - Filter by type

**Dependencies:** None (pure data operations)

### DocumentationService (`core/documentation_service.py`)

**Purpose:** Manage documentation files

**Key Methods:**
- `get_all_docs()` - List markdown files
- `get_doc_content()` - Read raw markdown
- `render_doc_html()` - Convert to HTML
- `append_to_changes_md()` - Update changelog
- `create_doc()` - Create new doc file

**Dependencies:** None (filesystem operations)

### EndpointService (`core/endpoint_service.py`)

**Purpose:** Manage monitored endpoints

**Key Methods:**
- `create_endpoint_with_work_item()` - Full setup
- `get_endpoint()` - Fetch by ID
- `get_all_endpoints()` - List all
- `check_endpoint_now()` - Manual check
- `delete_endpoint()` - Remove endpoint

**Dependencies:**
- Git integration (for work item branch)
- Monitoring integration (for health checks)
- Documentation service (for endpoint docs)

### GitService (`core/git_service.py`)

**Purpose:** Wrapper for Git operations

**Key Methods:**
- `get_status()` - Repository status
- `get_branches()` - List branches
- `get_recent_commits()` - Commit history
- `is_branch_merged()` - Check merge status
- `create_branch()` - Make new branch
- `merge_branch()` - Merge to main

**Dependencies:** Git integration singleton

## Integration Layer

### Git Integration (`integrations/git.py`)

**Purpose:** Low-level Git operations using GitPython

**Key Components:**
- `GitManager` class - Handles all Git operations
- `git_manager` singleton - Global instance

**Used by:**
- WorkService (branch creation, merging)
- EndpointService (committing endpoint setup)
- GitService (wrapper layer)

### Monitoring Integration (`integrations/monitoring.py`)

**Purpose:** Health checking for endpoints

**Key Components:**
- `MonitoringIntegration` class - Health check methods
- `monitoring` singleton - Global instance

**Check Types:**
- Network (ICMP ping)
- TCP (port connectivity)
- HTTP/HTTPS (web requests)

**Used by:**
- EndpointService (initial checks, manual checks)

## Data Flow Examples

### Creating a Work Item

```
User submits form
    ↓
main.py: POST /work/new
    ↓
work_service.create_work_item(db, title, category, ...)
    ├─→ Generate branch name
    ├─→ git_manager.create_branch()
    ├─→ Generate checklist (business logic)
    ├─→ Create WorkItem model
    └─→ Save to database
    ↓
Return work_item
    ↓
main.py: Redirect to /work/{id}
```

### Committing Work

```
User submits commit form
    ↓
main.py: POST /work/{id}/commit
    ↓
work_service.commit_work(db, work_id, message, changes_entry)
    ├─→ Get work item from DB
    ├─→ Validate inputs
    ├─→ git_manager.checkout_branch()
    ├─→ docs.append_to_changes_md()
    ├─→ git_manager.stage_files()
    ├─→ git_manager.commit()
    └─→ Save commit to database
    ↓
Return (success, message)
    ↓
main.py: Redirect with success message
```

### Creating Monitored Endpoint

```
User submits endpoint form
    ↓
main.py: POST /endpoints/new
    ↓
endpoint_service.create_endpoint_with_work_item(db, name, type, ...)
    ├─→ Create WorkItem with branch
    ├─→ Create Endpoint model
    ├─→ docs.create_doc() - Generate endpoint docs
    ├─→ git_manager.stage_files()
    ├─→ docs.append_to_changes_md()
    ├─→ git_manager.commit()
    ├─→ monitoring.update_endpoint_status() - Initial check
    └─→ Update work item notes
    ↓
Return (work_item_id, success_message)
    ↓
main.py: Redirect to work item
```

## Benefits of This Architecture

### 1. **Testability**
Services can be tested without HTTP:
```python
def test_work_creation():
    service = WorkService()
    work = service.create_work_item(mock_db, "Test", "service", "new")
    assert work.status == "planning"
```

### 2. **Reusability**
Services can be used outside web context:
```python
# CLI tool
from src.core import WorkService
service = WorkService()
work = service.create_work_item(db, ...)
```

### 3. **Maintainability**
- Each service focuses on one domain
- Easy to find relevant code
- Changes isolated to specific services

### 4. **Clear Dependencies**
```
main.py
  ↓
core services
  ↓
integrations
  ↓
database
```

### 5. **Easy Mocking**
Mock services in tests:
```python
@patch('src.core.work_service.git_manager')
def test_without_git(mock_git):
    service = WorkService()
    # Test without actual Git operations
```

## Anti-Patterns to Avoid

### ❌ Business Logic in Routes
```python
# BAD
@app.post("/work/new")
async def create_work(title: str = Form(...)):
    # Generate branch name here
    # Create checklist here
    # This belongs in WorkService!
```

### ❌ HTTP Concerns in Services
```python
# BAD
class WorkService:
    def create_work_item(self, request: Request):
        # Services shouldn't know about HTTP
```

### ❌ Direct Database in Routes
```python
# BAD
@app.get("/work/{id}")
async def work_detail(work_id: int, db: Session):
    work = db.query(WorkItem).filter(...).first()
    # Use work_service.get_work_item() instead
```

### ❌ Mixing Concerns in Services
```python
# BAD
class WorkService:
    def create_work_item_and_send_email(self):
        # Do one thing per method
        # Split into create_work_item() and notify()
```

## Future Enhancements

### Phase 2: Data Domain
Move data layer to separate package:
```
src/
├── data/
│   ├── models.py
│   ├── schemas.py
│   └── database.py
```

### Phase 3: Event System
Decouple services with events:
```python
# When work item created
events.publish('work.created', work_item)

# Listeners
@events.on('work.created')
def send_notification(work_item):
    # Send Slack notification
```

### Phase 4: Plugin System
Load integrations dynamically:
```python
# Load enabled integrations
integrations = load_enabled_integrations()
for integration in integrations:
    integration.initialize(app)
```

## Comparison: Old vs New

### Lines of Code

| File | Old | New | Change |
|------|-----|-----|--------|
| main.py | 1000+ | ~300 | -70% |
| Business logic | In main.py | In services | Organized |
| **Total complexity** | High | Low | ✅ Better |

### Responsibilities

| Layer | Old | New |
|-------|-----|-----|
| main.py | Routes + Logic + Validation | Routes only |
| Services | None | Business logic |
| Models | Data only | Data only |

### Testability

| Aspect | Old | New |
|--------|-----|-----|
| Unit testing | Hard (requires FastAPI) | Easy (pure Python) |
| Mocking | Complex | Simple |
| Coverage | Low | High potential |

## Migration Checklist

When adding new features:

- [ ] Define route in main.py (thin layer)
- [ ] Implement logic in appropriate service
- [ ] Keep services independent of HTTP
- [ ] Use dependency injection where needed
- [ ] Add type hints to service methods
- [ ] Document service methods with docstrings
- [ ] Consider adding tests (future)

## Conclusion

This architecture provides:
- **Clarity**: Easy to understand where code lives
- **Maintainability**: Changes isolated to services
- **Testability**: Services can be tested independently
- **Scalability**: Easy to add new features
- **Flexibility**: Services reusable outside web context

The refactoring maintains 100% backward compatibility while providing a much cleaner foundation for future development.