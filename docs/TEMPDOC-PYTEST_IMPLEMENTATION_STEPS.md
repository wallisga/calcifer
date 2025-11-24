# Pytest Infrastructure Implementation Guide

## 🎯 Goal

Set up pytest with fixtures, markers, and first example tests.

**Time Estimate:** 2-3 hours

---

## 📋 Step-by-Step Implementation

### Step 1: Install pytest Dependencies (5 minutes)

Update `requirements.txt`:

```bash
cd ~/calcifer/calcifer-app
```

Add these lines to `requirements.txt`:

```
# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-mock==3.12.0
```

Install dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt

# Verify installation
pytest --version
# Should show: pytest 7.4.3
```

---

### Step 2: Create Test Directory Structure (5 minutes)

```bash
cd ~/calcifer/calcifer-app

# Create test directories
mkdir -p tests/unit/test_core
mkdir -p tests/unit/test_integrations/test_monitoring
mkdir -p tests/integration
mkdir -p tests/e2e

# Create __init__.py files
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/test_core/__init__.py
touch tests/unit/test_integrations/__init__.py
touch tests/unit/test_integrations/test_monitoring/__init__.py
touch tests/integration/__init__.py
touch tests/e2e/__init__.py
```

Verify structure:

```bash
tree tests/
# Should show:
# tests/
# ├── __init__.py
# ├── unit/
# │   ├── __init__.py
# │   ├── test_core/
# │   │   └── __init__.py
# │   └── test_integrations/
# │       ├── __init__.py
# │       └── test_monitoring/
# │           └── __init__.py
# ├── integration/
# │   └── __init__.py
# └── e2e/
#     └── __init__.py
```

---

### Step 3: Create pytest Configuration (10 minutes)

Create `pytest.ini` in `calcifer-app/`:

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Markers
markers =
    unit: Fast unit tests with mocks (< 1 second)
    integration: Tests with real dependencies (Git, DB)
    slow: Tests that take > 1 second
    e2e: End-to-end workflow tests

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings

# Coverage options (when using --cov)
[coverage:run]
source = src
omit =
    */tests/*
    */__pycache__/*
    */venv/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```

Create `.coveragerc` for detailed coverage config:

```ini
[run]
source = src
omit =
    */tests/*
    */__pycache__/*
    */venv/*
    */logging_config.py

[report]
precision = 2
show_missing = True
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

### Step 4: Create conftest.py with Fixtures (20 minutes)

Create `tests/conftest.py`:

```python
"""
Pytest Configuration and Shared Fixtures

Fixtures defined here are available to all tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import git

from src.database import Base
from src import models


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db_engine():
    """
    Create in-memory SQLite database engine.
    
    Scope: function (new database for each test)
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create database session for tests.
    
    Automatically rolls back changes after each test.
    """
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_work_item(db_session):
    """Create a sample work item for testing."""
    work = models.WorkItem(
        title="Test Work Item",
        category="service",
        action_type="new",
        description="Test description",
        git_branch="service/new/test-work-20251124",
        status="planning",
        checklist=[
            {"item": "Task 1", "done": False},
            {"item": "Task 2", "done": False},
            {"item": "Task 3", "done": False}
        ]
    )
    db_session.add(work)
    db_session.commit()
    db_session.refresh(work)
    return work


@pytest.fixture
def sample_service(db_session):
    """Create a sample service for testing."""
    service = models.Service(
        name="Test Service",
        service_type="container",
        host="test-host",
        url="http://test.local",
        description="Test service description",
        status="active"
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


@pytest.fixture
def sample_endpoint(db_session):
    """Create a sample endpoint for testing."""
    endpoint = models.Endpoint(
        name="Test Endpoint",
        endpoint_type="network",
        target="127.0.0.1",
        check_interval=60,
        status="unknown"
    )
    db_session.add(endpoint)
    db_session.commit()
    db_session.refresh(endpoint)
    return endpoint


# ============================================================================
# GIT FIXTURES
# ============================================================================

@pytest.fixture
def temp_git_repo(tmp_path):
    """
    Create temporary Git repository for testing.
    
    Automatically cleaned up after test.
    """
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize repo
    repo = git.Repo.init(repo_path)
    
    # Configure repo
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
    
    # Create initial commit
    readme = repo_path / "README.md"
    readme.write_text("# Test Repo\n")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")
    
    # Create docs directory with CHANGES.md
    docs_path = repo_path / "docs"
    docs_path.mkdir()
    changes = docs_path / "CHANGES.md"
    changes.write_text("# Change Log\n\nAll changes logged here.\n\n")
    repo.index.add(["docs/CHANGES.md"])
    repo.index.commit("Add CHANGES.md")
    
    yield repo_path
    
    # Cleanup handled automatically by tmp_path


@pytest.fixture
def mock_git(monkeypatch):
    """
    Mock Git module for unit tests.
    
    Prevents actual Git operations during unit tests.
    """
    mock = MagicMock()
    
    # Configure mock methods
    mock.create_branch.return_value = True
    mock.checkout_branch.return_value = True
    mock.get_branches.return_value = ["main", "test-branch"]
    mock.get_current_branch.return_value = "main"
    mock.get_status.return_value = {
        "branch": "main",
        "is_dirty": False,
        "untracked_files": [],
        "modified_files": [],
        "staged_files": []
    }
    mock.stage_files.return_value = True
    mock.commit.return_value = "abc123def456"
    mock.is_branch_merged.return_value = False
    mock.merge_branch.return_value = (True, "merged_sha")
    mock.generate_branch_name.return_value = "test/branch/name-20251124"
    mock.get_branch_commits.return_value = []
    
    # Replace git_module with mock
    monkeypatch.setattr('src.core.work_module.git_module', mock)
    
    return mock


# ============================================================================
# INTEGRATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_monitoring(monkeypatch):
    """Mock monitoring integration for unit tests."""
    mock = MagicMock()
    
    # Configure mock methods
    mock.check_endpoint.return_value = (True, None)
    mock.update_endpoint_status.return_value = True
    mock.generate_endpoint_documentation.return_value = "# Test Doc\n"
    
    # Replace monitoring with mock
    monkeypatch.setattr(
        'src.integrations.monitoring.endpoint_module.monitoring',
        mock
    )
    
    return mock


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "unit: Fast unit tests with mocks"
    )
    config.addinivalue_line(
        "markers",
        "integration: Tests with real dependencies"
    )
```

---

### Step 5: Create First Example Tests (30 minutes)

#### Example 1: Test work_module.py

Create `tests/unit/test_core/test_work_module.py`:

```python
"""
Unit tests for work_module.

Tests work item creation, updates, and lifecycle management.
"""

import pytest
from src.core import work_module
from src import models


class TestWorkModuleCreate:
    """Test work item creation."""
    
    @pytest.mark.unit
    def test_create_work_item_basic(self, db_session, mock_git):
        """Test basic work item creation."""
        # Arrange
        title = "Test Feature"
        category = "service"
        action_type = "new"
        description = "Test description"
        
        # Act
        result = work_module.create_work_item(
            db_session, title, category, action_type, description
        )
        
        # Assert
        assert result is not None
        assert result.title == title
        assert result.category == category
        assert result.action_type == action_type
        assert result.description == description
        assert result.status == "planning"
        assert result.git_branch is not None
        assert len(result.checklist) > 0
        
        # Verify Git operations called
        mock_git.create_branch.assert_called_once()
    
    @pytest.mark.unit
    def test_create_generates_checklist(self, db_session, mock_git):
        """Test that checklist is generated based on work type."""
        # Act
        result = work_module.create_work_item(
            db_session, "Test", "service", "new"
        )
        
        # Assert
        assert len(result.checklist) > 0
        assert all("item" in item for item in result.checklist)
        assert all("done" in item for item in result.checklist)
        assert all(item["done"] is False for item in result.checklist)
    
    @pytest.mark.unit
    def test_create_different_categories(self, db_session, mock_git):
        """Test creation with different categories."""
        categories = ["platform_feature", "integration", "service", "documentation"]
        
        for category in categories:
            work = work_module.create_work_item(
                db_session, f"Test {category}", category, "new"
            )
            assert work.category == category
            assert work.checklist  # Has checklist


class TestWorkModuleRetrieve:
    """Test work item retrieval."""
    
    @pytest.mark.unit
    def test_get_work_item_success(self, db_session, sample_work_item):
        """Test retrieving existing work item."""
        # Act
        result = work_module.get_work_item(db_session, sample_work_item.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_work_item.id
        assert result.title == sample_work_item.title
    
    @pytest.mark.unit
    def test_get_work_item_not_found(self, db_session):
        """Test retrieving non-existent work item."""
        # Act
        result = work_module.get_work_item(db_session, 9999)
        
        # Assert
        assert result is None


class TestWorkModuleUpdate:
    """Test work item updates."""
    
    @pytest.mark.unit
    def test_toggle_checklist_item(self, db_session, sample_work_item):
        """Test toggling checklist item."""
        # Arrange
        initial_state = sample_work_item.checklist[0]["done"]
        
        # Act
        success = work_module.toggle_checklist_item(
            db_session, sample_work_item.id, 0
        )
        
        # Assert
        assert success is True
        db_session.refresh(sample_work_item)
        assert sample_work_item.checklist[0]["done"] == (not initial_state)
    
    @pytest.mark.unit
    def test_update_notes(self, db_session, sample_work_item):
        """Test updating work item notes."""
        # Arrange
        new_notes = "These are updated notes"
        
        # Act
        result = work_module.update_notes(
            db_session, sample_work_item.id, new_notes
        )
        
        # Assert
        assert result is not None
        assert result.notes == new_notes


class TestWorkModuleDelete:
    """Test work item deletion."""
    
    @pytest.mark.unit
    def test_delete_work_item(self, db_session, sample_work_item, mock_git):
        """Test deleting work item."""
        # Arrange
        work_id = sample_work_item.id
        
        # Act
        success, message = work_module.delete_work_item(db_session, work_id)
        
        # Assert
        assert success is True
        
        # Verify deleted from database
        deleted = db_session.query(models.WorkItem).filter(
            models.WorkItem.id == work_id
        ).first()
        assert deleted is None
```

#### Example 2: Test git_module.py

Create `tests/unit/test_core/test_git_module.py`:

```python
"""
Unit tests for git_module.

Tests Git operations with mocked Git library.
"""

import pytest
from unittest.mock import Mock, patch
from src.core import git_module


class TestGitModuleBranches:
    """Test branch operations."""
    
    @pytest.mark.unit
    @patch('src.core.git_module.git.Repo')
    def test_create_branch_success(self, mock_repo_class):
        """Test successful branch creation."""
        # Arrange
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_branch = Mock()
        mock_repo.create_head.return_value = mock_branch
        
        manager = git_module.GitModule()
        
        # Act
        result = manager.create_branch("test-branch", checkout=True)
        
        # Assert
        assert result is True
        mock_repo.create_head.assert_called_once_with("test-branch")
        mock_branch.checkout.assert_called_once()
    
    @pytest.mark.unit
    def test_generate_branch_name(self):
        """Test branch name generation."""
        # Arrange
        manager = git_module.GitModule()
        
        # Act
        result = manager.generate_branch_name(
            "service", "new", "Test Feature"
        )
        
        # Assert
        assert result.startswith("service/new/")
        assert "test-feature" in result
        assert len(result) <= 100  # Reasonable length
```

---

### Step 6: Run Tests (10 minutes)

```bash
cd ~/calcifer/calcifer-app
source venv/bin/activate

# Run all tests
pytest

# Expected output:
# ============================= test session starts ==============================
# collected X items
#
# tests/unit/test_core/test_work_module.py::TestWorkModuleCreate::test_create_work_item_basic PASSED
# tests/unit/test_core/test_work_module.py::TestWorkModuleCreate::test_create_generates_checklist PASSED
# ...
# ============================== X passed in Y.YYs ===============================

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# View HTML coverage report
# Open: calcifer-app/htmlcov/index.html
```

---

### Step 7: Add pytest.ini to .gitignore Updates

Update `.gitignore` to exclude test artifacts:

```bash
# Add to .gitignore
echo "" >> .gitignore
echo "# Testing" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo "htmlcov/" >> .gitignore
echo ".coverage" >> .gitignore
echo "coverage.xml" >> .gitignore
```

---

### Step 8: Create Test Running Scripts (10 minutes)

Create `scripts/run_tests.sh`:

```bash
#!/bin/bash
# Run Calcifer tests

set -e

cd "$(dirname "$0")/../calcifer-app"

# Activate venv
source venv/bin/activate

# Parse arguments
COVERAGE=false
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --cov|--coverage)
            COVERAGE=true
            shift
            ;;
        --unit)
            MARKERS="-m unit"
            shift
            ;;
        --integration)
            MARKERS="-m integration"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--coverage] [--unit] [--integration]"
            exit 1
            ;;
    esac
done

# Run tests
if [ "$COVERAGE" = true ]; then
    pytest $MARKERS --cov=src --cov-report=html --cov-report=term
else
    pytest $MARKERS
fi
```

Make it executable:

```bash
chmod +x scripts/run_tests.sh
```

Usage:

```bash
# Run all tests
./scripts/run_tests.sh

# Run with coverage
./scripts/run_tests.sh --coverage

# Run unit tests only
./scripts/run_tests.sh --unit

# Run unit tests with coverage
./scripts/run_tests.sh --unit --coverage
```

---

### Step 9: Update VS Code Tasks (Optional)

Add to `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run All Tests",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/run_tests.sh",
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Run Unit Tests",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/run_tests.sh --unit",
            "group": "test"
        },
        {
            "label": "Run Tests with Coverage",
            "type": "shell",
            "command": "${workspaceFolder}/scripts/run_tests.sh --coverage",
            "group": "test"
        }
    ]
}
```

---

## ✅ Verification Checklist

- [ ] pytest installed (`pytest --version` works)
- [ ] Test directory structure created
- [ ] pytest.ini created and configured
- [ ] conftest.py with fixtures created
- [ ] At least 2 test files created
- [ ] Tests run successfully (`pytest` passes)
- [ ] Coverage report generated (`pytest --cov`)
- [ ] Test scripts created and executable
- [ ] .gitignore updated for test artifacts

---

## 🎉 Success Criteria

When done, you should be able to:

```bash
# Run all tests
pytest
# ✅ Passes with multiple tests

# Run unit tests only
pytest -m unit
# ✅ Runs fast (< 5 seconds)

# Check coverage
pytest --cov=src --cov-report=term
# ✅ Shows coverage percentage

# Run specific test
pytest tests/unit/test_core/test_work_module.py::TestWorkModuleCreate::test_create_work_item_basic
# ✅ Runs single test
```

---

## 📚 Next Steps

After pytest infrastructure is working:

1. **Add more tests** - Cover remaining core modules
2. **Add integration tests** - Test with real Git
3. **Setup git hooks** - Run tests pre-commit
4. **Add to CI/CD** - GitHub Actions
5. **Track coverage** - Aim for 75%+

---

## 🚨 Common Issues

### Issue: Import errors

```bash
# Solution: Install in editable mode
pip install -e .
```

### Issue: Tests can't find fixtures

```bash
# Solution: Ensure conftest.py is in tests/ root
ls tests/conftest.py
```

### Issue: Database fixtures fail

```python
# Solution: Ensure Base imported correctly
from src.database import Base
```

---

Ready to implement? Let me know when you want to start! 🔥