# Calcifer Architecture

## Overview

Calcifer is designed with a clear separation between **Core Features** (essential to its purpose) and **Integrations** (optional enhancements).

```
┌──────────────────────────────────────┐
│         Calcifer Platform            │
├──────────────────────────────────────┤
│  Core Features (Required)            │
│  - Work Items                        │
│  - Services Catalog                  │
│  - Documentation                     │
├──────────────────────────────────────┤
│  Integrations (Optional)             │
│  - Git (branch management)           │
│  - Monitoring (health checks)        │
│  - [Future: Notifications, Backups]  │
└──────────────────────────────────────┘
```

## Core Features

### 1. Work Items (`src/core/work_items.py`)

**Purpose**: Track infrastructure work and enforce workflow discipline.

**Key Functionality**:
- Create work items with category and action type
- Manage dynamic checklists based on work type
- Track notes and documentation
- Validate completion requirements
- Enforce documentation before closing work

**Why Core**: This is Calcifer's primary value - preventing "forgotten documentation" and tracking infrastructure changes.

### 2. Services (`src/core/services.py`)

**Purpose**: Maintain a catalog of all deployed services.

**Key Functionality**:
- Register services (containers, VMs, bare metal)
- Track service dependencies
- Document service configurations
- Link to monitoring and documentation

**Why Core**: Knowing what's deployed where is fundamental to infrastructure management.

### 3. Documentation (`src/core/documentation.py`)

**Purpose**: Centralized documentation management.

**Key Functionality**:
- Discover markdown files in `docs/`
- Render markdown as HTML
- Manage CHANGES.md automatically
- Generate documentation templates

**Why Core**: Documentation is the main output of Calcifer's workflow.

## Integrations

### 1. Git (`src/integrations/git.py`)

**Purpose**: Automatic Git operations for infrastructure as code.

**Key Functionality**:
- Create branches for work items
- Stage and commit changes
- Merge branches with validation
- Track commit history
- Enforce CHANGES.md updates

**Why Integration**: Calcifer can work without Git (manual branch management), but Git integration automates the workflow.

**Can Be Disabled**: Yes - work items can be tracked without Git branches.

### 2. Monitoring (`src/integrations/monitoring.py`)

**Purpose**: Synthetic monitoring of network endpoints.

**Key Functionality**:
- ICMP ping checks
- TCP port connectivity
- HTTP/HTTPS availability
- Status tracking and history

**Why Integration**: Monitoring is useful but not required for tracking work or managing services. You could use external tools like Uptime Kuma instead.

**Can Be Disabled**: Yes - endpoints feature can be hidden if not used.

## Directory Structure

```
calcifer-app/
├── src/
│   ├── core/                  # Core features (required)
│   │   ├── __init__.py
│   │   ├── work_items.py     # Work item management
│   │   ├── services.py       # Service catalog
│   │   └── documentation.py  # Doc management
│   │
│   ├── integrations/          # Optional integrations
│   │   ├── __init__.py
│   │   ├── git.py            # Git operations
│   │   └── monitoring.py     # Health checks
│   │
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # DB configuration
│   └── main.py               # FastAPI application
│
├── templates/                 # Jinja2 templates
├── static/                    # CSS/JS assets
├── data/                      # SQLite database (gitignored)
└── requirements.txt           # Python dependencies
```

## Data Flow

### Creating a Work Item

```
User Request (UI/API)
    ↓
FastAPI Route (/work/new)
    ↓
WorkItemsCore.create_work_item()
    ├─→ Generate checklist template
    └─→ [Optional] GitIntegration.create_branch()
    ↓
Database (SQLAlchemy)
    ↓
Redirect to work item detail page
```

### Completing Work Item

```
User clicks "Merge & Complete"
    ↓
FastAPI Route (/work/{id}/merge-and-complete)
    ↓
WorkItemsCore.validate_for_completion()
    ├─→ Check all checklist items done
    ├─→ Check notes exist
    └─→ [Optional] Check Git branch merged
    ↓
[If Git enabled] GitIntegration.merge_branch()
    ↓
WorkItemsCore.complete_work_item()
    ↓
Update database, redirect to home
```

## Integration Points

### How Core Uses Integrations

```python
# Core modules accept integrations as optional dependencies
from src.core.work_items import WorkItemsCore
from src.integrations.git import GitIntegration

# With Git integration
git = GitIntegration()
work_items = WorkItemsCore(git_integration=git)

# Without Git integration
work_items = WorkItemsCore()  # Still works, no branches created
```

### Future Integration Pattern

```python
# Example: Adding Slack notifications
class SlackIntegration:
    def check_connectivity(self) -> bool:
        """Test if integration is working."""
        pass
    
    def send_notification(self, message: str) -> bool:
        """Send notification."""
        pass

# Use in core
notifications = SlackIntegration() if SLACK_ENABLED else None
if notifications:
    notifications.send_notification("Work item completed!")
```

## UI Architecture

### Navigation Structure

```
┌────────────────────────────────────────────────────┐
│ 🔥 Calcifer  [New Work] [Services] [Docs] | [Monitoring] [Git] │
│              └─────── Core ────────┘   └─ Integrations ─┘ │
└────────────────────────────────────────────────────┘
```

- **Core features**: Standard nav items (white text)
- **Separator**: Visual divider between core and integrations
- **Integrations**: Blue left border indicator

### Template Hierarchy

```
base.html (navigation, styles)
    ├─→ home.html (dashboard)
    ├─→ work_item.html (work details)
    ├─→ service_catalog.html (services list)
    ├─→ docs_list.html (documentation)
    ├─→ endpoint_list.html (monitoring)
    └─→ git_status.html (git integration)
```

## Database Schema

### Core Tables

1. **work_items**: Track infrastructure work
   - Essential fields: id, title, category, action_type, status
   - Git fields: git_branch, branch_merged (nullable)
   - Documentation: notes, checklist

2. **services**: Service catalog
   - Essential fields: id, name, service_type, host
   - Optional: ports, cpu, memory, dependencies

3. **commits**: Commit tracking (optional, only if Git enabled)
   - Links commits to work items

4. **endpoints**: Monitoring targets (optional, only if Monitoring enabled)
   - Links endpoints to work items

### Schema Evolution

- Core tables are always created
- Integration tables (commits, endpoints) only needed if integrations used
- Future: Feature flags to disable unused tables

## Configuration

### Environment Variables

```bash
# Core
DB_PATH=./data/calcifer.db           # SQLite database location
REPO_PATH=..                         # Repository root (for docs)

# Git Integration (optional)
GIT_ENABLED=true                     # Enable Git integration
GIT_AUTO_COMMIT=true                 # Auto-commit on work completion

# Monitoring Integration (optional)
MONITORING_ENABLED=true              # Enable monitoring features
MONITORING_INTERVAL=60               # Default check interval (seconds)
```

### Feature Flags (Future)

```python
class Config:
    # Core features (always enabled)
    CORE_WORK_ITEMS = True
    CORE_SERVICES = True
    CORE_DOCS = True
    
    # Integrations (can be disabled)
    INTEGRATION_GIT = os.getenv("GIT_ENABLED", "true").lower() == "true"
    INTEGRATION_MONITORING = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
```

## Design Principles

### 1. Separation of Concerns
- Core modules don't depend on integrations
- Integrations can optionally depend on core
- Clear interfaces between layers

### 2. Graceful Degradation
- If Git integration fails, work items still work
- If monitoring is disabled, rest of Calcifer works fine
- Core functionality never breaks due to integration issues

### 3. Easy Extension
- New integrations follow same pattern
- Add to `src/integrations/`
- Register in `__init__.py`
- Use in `main.py` routes as needed

### 4. Progressive Enhancement
- Start with core features
- Add integrations as needed
- No forced dependencies on external services

## Testing Strategy

### Unit Tests (Future)

```python
# Test core modules independently
def test_work_item_creation():
    core = WorkItemsCore()  # No integrations
    work = core.create_work_item(...)
    assert work.status == "planning"

# Test with integration
def test_work_item_with_git():
    git = GitIntegration()
    core = WorkItemsCore(git_integration=git)
    work = core.create_work_item(...)
    assert work.git_branch is not None
```

### Integration Tests

```python
# Test full workflow
def test_complete_workflow():
    # Setup
    git = GitIntegration()
    core = WorkItemsCore(git_integration=git)
    
    # Create work
    work = core.create_work_item(...)
    
    # Complete checklist
    core.toggle_checklist_item(work.id, 0)
    
    # Add notes
    core.update_notes(work.id, "Documentation")
    
    # Complete
    success, error = core.complete_work_item(work.id)
    assert success
```

## Future Enhancements

### Planned Integrations

1. **Uptime Kuma** - Pull monitoring data from existing tool
2. **Grafana** - Embed dashboards in service views
3. **Notifications** - Slack/Discord/Email alerts
4. **Backups** - Automated database and config backups
5. **LDAP/OAuth** - User authentication

### Core Enhancements

1. **Multi-user support** - User accounts and permissions
2. **Advanced search** - Full-text search across work items and docs
3. **Templates** - Predefined work item templates
4. **Tags** - Flexible categorization beyond category/action

### Architecture Improvements

1. **Plugin system** - Load integrations dynamically
2. **API authentication** - Secure API access
3. **Event system** - Pub/sub for integration communication
4. **Config management** - UI for enabling/disabling features

## Migration Guide

### From Old Structure

1. **Move git_integration.py** → `src/integrations/git.py`
2. **Extract core logic** from main.py → core modules
3. **Update imports** in main.py
4. **Update templates** to use new base.html
5. **Test all routes** work with new structure

### Breaking Changes

- None - this is a refactoring, not an API change
- Database schema unchanged
- All routes remain the same
- Templates maintain same names

## Conclusion

This architecture makes Calcifer:
- **Easier to understand** - Clear core vs optional
- **Easier to maintain** - Related code grouped together
- **Easier to extend** - Simple integration pattern
- **More robust** - Core works even if integrations fail

The separation of core and integrations reflects Calcifer's philosophy: enforce good infrastructure practices (core), with optional automation to make it easier (integrations).