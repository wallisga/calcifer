# Development Guide

This guide covers the development workflow for contributing to Calcifer.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Development Environment](#development-environment)
3. [File Structure](#file-structure)
4. [Development Workflow](#development-workflow)
5. [Multi-Machine Workflow](#multi-machine-workflow)
6. [Testing](#testing)
7. [Code Style](#code-style)
8. [Architecture Patterns](#architecture-patterns)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- See [PREREQUISITES.md](PREREQUISITES.md)

### 1. Clone Repository
```bash
cd ~
git clone git@github.com:yourusername/calcifer.git
cd calcifer
```

### 2. Set Up Python Environment
```bash
cd calcifer-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Git
```bash
git config user.name "Your Name"
git config user.email "your@email.com"
```

### 4. Run Calcifer
```bash
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open: http://localhost:8000

### 5. Make Initial Commit (If Needed)

If this is a fresh repo without commits:
```bash
cd ~/calcifer
git add .
git commit -m "Initial setup"
```

---

## Development Environment

### Using VS Code

Open the repository in VS Code:
```bash
code ~/calcifer
```

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (for Python intellisense)
- GitLens (for Git integration)

**VS Code Tasks:**

Press `Ctrl+Shift+P` → "Run Task":
- "Run Calcifer (Development)" - Starts the server
- "Open Calcifer Dashboard" - Opens browser

---

## File Structure

```
calcifer/
├── calcifer-app/           # Application code
│   ├── src/               # Python source
│   │   ├── main.py       # FastAPI routes (thin layer, <20 lines each)
│   │   │
│   │   ├── core/         # Core modules (REQUIRED)
│   │   │   ├── __init__.py
│   │   │   ├── work_module.py              # Work item management
│   │   │   ├── service_catalog_module.py   # Service catalog
│   │   │   ├── documentation_module.py     # Documentation management
│   │   │   ├── git_module.py               # Local Git operations
│   │   │   └── settings_module.py          # Configuration
│   │   │
│   │   ├── integrations/  # Optional integrations
│   │   │   ├── __init__.py
│   │   │   └── monitoring/
│   │   │       ├── integration.py          # Low-level health checks
│   │   │       └── endpoint_module.py      # Business logic
│   │   │
│   │   ├── models.py     # Database models (SQLAlchemy)
│   │   ├── schemas.py    # API schemas (Pydantic)
│   │   └── database.py   # DB configuration
│   │
│   ├── templates/        # Jinja2 HTML templates
│   ├── static/           # CSS/JS (currently minimal)
│   ├── data/             # SQLite database (git-ignored)
│   ├── tests/            # Test suite
│   │   ├── unit/        # Unit tests
│   │   └── integration/ # Integration tests
│   └── requirements.txt  # Python dependencies
│
├── docs/                 # Documentation
│   ├── ROADMAP.md
│   ├── SETUP_GUIDE.md
│   ├── PREREQUISITES.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_PATTERNS_GUIDE.md  # ← Key reference!
│   ├── DEVELOPER_QUICK_REFERENCE.md    # ← Keep this handy!
│   ├── DEVELOPMENT.md    # ← You are here
│   ├── TESTING.md
│   ├── TOOLS.md          # Developer utilities
│   └── CHANGES.md        # Change log (tracked in Git)
│
├── tools/                # Developer scripts
│   └── git-sync.sh      # Multi-machine sync tool
│
└── README.md            # Project overview
```

---

## Development Workflow

### Making Changes

**ALWAYS use Calcifer's UI to manage work:**

1. **Create Work Item**
   - Go to http://localhost:8000
   - Click "New Work"
   - Fill out form (title, category, action type, description)
   - Calcifer auto-creates Git branch

2. **Work on Changes**
   - Edit code in your editor
   - Calcifer is on the feature branch
   - Make your changes

3. **Commit via Calcifer UI**
   - Click "Commit Changes" in work item
   - See current Git status
   - Enter commit message
   - **IMPORTANT:** Add CHANGES.md entry
   - Commit

4. **Complete Checklist**
   - Toggle checklist items as you complete them
   - Add notes documenting your work

5. **Merge & Complete**
   - Click "Merge & Complete" button
   - Calcifer validates:
     - All checklist items complete
     - Notes added
     - CHANGES.md has entry
     - Commits made
   - Merges to main
   - Marks work item complete

### Architecture Rules

**Phase 2 Pattern:**

```
HTTP Layer (main.py)
  ↓ calls
Core Modules (business logic)
  ↓ calls
Integrations (optional features)
  ↓ uses
Database (models + queries)
```

**Key Rules:**
- Routes in `main.py` should be < 20 lines
- Business logic goes in core modules
- Direct database queries only in modules, not routes
- Integrations are optional features

See [ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md) for details.

---

## Multi-Machine Workflow

### Scenario: Working on Multiple Machines

**Example:** Development laptop at work + desktop at home

### Setup (One-Time Per Machine)

**On each machine:**

1. **Clone repository**
   ```bash
   cd ~
   git clone git@github.com:yourusername/calcifer.git
   cd calcifer
   ```

2. **Set up environment**
   ```bash
   cd calcifer-app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install git-sync tool** (recommended)
   ```bash
   chmod +x tools/git-sync.sh
   ```

### Daily Workflow

**Machine A (e.g., work laptop):**

```bash
# Morning - Start of day
cd ~/calcifer
./tools/git-sync.sh              # Pull latest changes safely

# Start Calcifer
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload

# Create work item in UI, make changes, commit via UI

# After merging work item
git checkout main
git push origin main             # Push to GitHub

# End of day - you're done!
```

**Machine B (e.g., home desktop):**

```bash
# Evening - Start of session
cd ~/calcifer
./tools/git-sync.sh              # Gets work from Machine A

# Start Calcifer
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload

# Continue work or start new work items

# After merging work item
git checkout main
git push origin main             # Push to GitHub
```

### Git Sync Tool

**What it does:**
- Safely fetches latest changes
- Shows what would be pulled
- Only pulls if safe (fast-forward)
- Warns about uncommitted changes
- Aborts if conflicts detected

**Usage:**
```bash
cd ~/calcifer
./tools/git-sync.sh         # Sync main branch
./tools/git-sync.sh develop # Sync specific branch
```

See [TOOLS.md](TOOLS.md) for detailed git-sync documentation.

### Handling Uncommitted Work

**Scenario:** You have uncommitted changes on Machine A, need to switch to Machine B

**Option 1: Commit your work via Calcifer**
```bash
# Best practice - use Calcifer UI to commit
# Then push and sync on other machine
```

**Option 2: Git stash (manual)**
```bash
# On Machine A
git stash
git push origin main

# On Machine B
git pull origin main
# Work on Machine B

# Back on Machine A later
git pull origin main
git stash pop
```

**Option 3: Temporary branch (manual)**
```bash
# On Machine A
git checkout -b temp-work-in-progress
git add .
git commit -m "WIP: Save work"
git push origin temp-work-in-progress

# On Machine B
git fetch origin
git checkout temp-work-in-progress
# Continue work
```

### Best Practices

**DO:**
- ✅ Use git-sync.sh before starting work each day
- ✅ Push main after merging work items
- ✅ Create work items for all changes
- ✅ Commit frequently via Calcifer UI

**DON'T:**
- ❌ Make changes directly on main without work item
- ❌ Force push (`git push -f`)
- ❌ Work on same feature branch on both machines simultaneously
- ❌ Forget to push after merging work items

### Troubleshooting Multi-Machine

**"Branches have diverged"**
```bash
# You and remote both have different commits
# Options:

# 1. Merge (keeps both sets of changes)
git pull origin main

# 2. Rebase (puts your changes on top)
git rebase origin/main

# 3. Reset (discards local commits - careful!)
git reset --hard origin/main
```

**"Uncommitted changes would be overwritten"**
```bash
# You have local changes not committed
# Use Calcifer UI to commit them first, or:
git stash              # Save changes temporarily
./tools/git-sync.sh    # Sync
git stash pop          # Restore changes
```

**"Remote contains work you don't have"**
```bash
# Normal! Just sync:
./tools/git-sync.sh    # Pulls changes safely
```

---

## Testing

### Running Tests

```bash
cd calcifer-app
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_work_module.py -v

# Run specific test
pytest tests/unit/test_work_module.py::test_create_work_item -v
```

### Test Structure

```
tests/
├── unit/                    # Unit tests (modules in isolation)
│   ├── test_work_module.py
│   └── test_service_catalog_module.py
│
├── integration/             # Integration tests (full workflows)
│   └── test_work_flows.py
│
├── conftest.py             # Shared fixtures
└── __init__.py
```

### Writing Tests

See [TESTING.md](TESTING.md) for comprehensive testing guide.

**Quick example:**
```python
def test_create_work_item(db_session, temp_git_repo):
    """Test creating a work item."""
    work = work_module.create_work_item(
        db_session,
        title="Test Work",
        category="service",
        action_type="new"
    )
    
    assert work.title == "Test Work"
    assert work.status == "planning"
    assert work.branch_name is not None
```

---

## Code Style

### Python Style Guide

**Follow:**
- PEP 8 (Python Enhancement Proposal 8)
- Type hints where appropriate
- Docstrings for all public methods

**Example:**
```python
def create_work_item(
    db: Session,
    title: str,
    category: str,
    action_type: str
) -> models.WorkItem:
    """
    Create a new work item with Git branch.
    
    Args:
        db: Database session
        title: Work item title
        category: Category (service, platform_feature, infrastructure)
        action_type: Action (new, change, fix, deprecate)
        
    Returns:
        Created WorkItem instance
    """
    # Implementation here
```

### Module Pattern

**All business logic in modules:**
```python
# ✅ GOOD - Logic in module
class WorkModule:
    @staticmethod
    def create_work_item(db: Session, ...) -> models.WorkItem:
        # Business logic here
        
# ✅ GOOD - Thin route
@app.post("/work/new")
async def create_work(title: str = Form(...), db: Session = Depends(get_db)):
    work_item = work_module.create_work_item(db, title, ...)
    return RedirectResponse(...)

# ❌ BAD - Logic in route
@app.post("/work/new")
async def create_work(...):
    # Generate branch name here
    # Create checklist here
    # Save to database here
    # This should be in WorkModule!
```

---

## Architecture Patterns

### Key Documents

**Must read before contributing:**
1. [ARCHITECTURE.md](ARCHITECTURE.md) - High-level overview
2. [ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md) - Detailed patterns
3. [DEVELOPER_QUICK_REFERENCE.md](DEVELOPER_QUICK_REFERENCE.md) - Quick reference

### Quick Architecture Overview

**3-Layer Pattern:**

```
┌─────────────────────────────────┐
│  HTTP Layer (main.py)           │  ← Thin routes, < 20 lines
│  - Receive requests             │
│  - Call modules                 │
│  - Return responses             │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Service Layer (core/*)         │  ← Business logic
│  - Validation                   │
│  - Orchestration                │
│  - Business rules               │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Data Layer (models.py)         │  ← Database operations
│  - Database schema              │
│  - ORM models                   │
│  - Queries                      │
└─────────────────────────────────┘
```

**Core vs Integrations:**
- **Core** = Required for Calcifer to work (work items, git, docs)
- **Integrations** = Optional features (monitoring, external APIs)

---

## Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Ensure __init__.py files exist
ls calcifer-app/src/core/__init__.py
ls calcifer-app/src/integrations/__init__.py

# Reinstall dependencies
cd calcifer-app
pip install -r requirements.txt
```

**Port 8000 already in use**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

**Database errors**
```bash
# Delete and recreate database
rm -f calcifer-app/data/calcifer.db
# Restart app - database recreates automatically
```

**Git operations failing**
```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## Additional Resources

### Internal Documentation
- [TOOLS.md](TOOLS.md) - Developer utilities and scripts
- [TESTING.md](TESTING.md) - Testing patterns and best practices
- [ROADMAP.md](ROADMAP.md) - Future features and plans

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [GitPython](https://gitpython.readthedocs.io/)
- [Pytest](https://docs.pytest.org/)

---

**Last Updated:** December 6, 2025  
**Version:** Calcifer v2.0 (Phase 3 Complete)  
**Next Milestone:** Phase 4 - Production Deployment