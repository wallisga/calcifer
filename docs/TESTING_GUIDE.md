# Calcifer Testing Patterns Guide

## Overview

This document defines testing patterns for Calcifer. Follow these patterns when writing tests to ensure consistency and quality.

---

## Testing Philosophy

**Core Principles:**
1. **Fast Feedback** - Unit tests should run in < 1 second
2. **Isolated Tests** - No dependencies between tests
3. **Clear Intent** - Test names describe what's being tested
4. **Minimal Mocking** - Mock only external dependencies
5. **Real Scenarios** - Integration tests use real components

---

## Test Directory Structure

```
calcifer-app/
├── src/                        # Application code
│   ├── core/
│   ├── integrations/
│   └── main.py
│
└── tests/                      # All tests here
    ├── __init__.py
    ├── conftest.py            # Shared fixtures
    │
    ├── unit/                  # Fast, isolated tests
    │   ├── __init__.py
    │   ├── test_core/         # Core module tests
    │   │   ├── test_work_module.py
    │   │   ├── test_git_module.py
    │   │   ├── test_documentation_module.py
    │   │   ├── test_service_catalog_module.py
    │   │   └── test_settings_module.py
    │   └── test_integrations/ # Integration unit tests
    │       └── test_monitoring/
    │           ├── test_integration.py
    │           └── test_endpoint_module.py
    │
    ├── integration/           # Tests with real dependencies
    │   ├── __init__.py
    │   ├── test_work_workflow.py
    │   ├── test_git_operations.py
    │   └── test_endpoint_creation.py
    │
    └── e2e/                   # End-to-end tests (future)
        ├── __init__.py
        └── test_complete_workflows.py
```

---

## Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Fast test with mocks."""
    pass

@pytest.mark.integration
def test_with_real_dependencies():
    """Test with real Git, database."""
    pass

@pytest.mark.slow
def test_expensive_operation():
    """Test that takes > 1 second."""
    pass

@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test of complete feature."""
    pass
```

**Run specific tests:**
```bash
# Fast tests only (pre-commit)
pytest -m unit

# Unit + integration (pre-push)
pytest -m "unit or integration"

# All tests (CI)
pytest

# Skip slow tests
pytest -m "not slow"
```

---

## Pattern 1: Core Module Unit Tests

### Template

```python
"""
Unit tests for core module.

Tests business logic in isolation using mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core import module_name
from src import models


class TestModuleCreate:
    """Test create operations."""
    
    @pytest.mark.unit
    def test_create_basic(self, db_session, mock_git):
        """Test basic creation."""
        # Arrange
        param = "test_value"
        
        # Act
        result = module_name.create_something(db_session, param)
        
        # Assert
        assert result is not None
        assert result.param == param
        mock_git.create_branch.assert_called_once()
    
    @pytest.mark.unit
    def test_create_with_validation_error(self, db_session, mock_git):
        """Test creation with invalid input."""
        # Arrange
        invalid_param = ""
        
        # Act
        success, message = module_name.create_something(db_session, invalid_param)
        
        # Assert
        assert success is False
        assert "required" in message.lower()
        mock_git.create_branch.assert_not_called()


class TestModuleUpdate:
    """Test update operations."""
    
    @pytest.mark.unit
    def test_update_success(self, db_session, sample_object):
        """Test successful update."""
        # Arrange
        new_value = "updated"
        
        # Act
        success, message = module_name.update_something(
            db_session, sample_object.id, new_value
        )
        
        # Assert
        assert success is True
        assert sample_object.value == new_value
    
    @pytest.mark.unit
    def test_update_not_found(self, db_session):
        """Test update with non-existent ID."""
        # Act
        success, message = module_name.update_something(db_session, 9999, "value")
        
        # Assert
        assert success is False
        assert "not found" in message.lower()


class TestModuleDelete:
    """Test delete operations."""
    
    @pytest.mark.unit
    def test_delete_success(self, db_session, sample_object, mock_git):
        """Test successful deletion."""
        # Act
        success, message = module_name.delete_something(db_session, sample_object.id)
        
        # Assert
        assert success is True
        # Verify object removed from DB
        deleted = db_session.query(models.Something).filter(
            models.Something.id == sample_object.id
        ).first()
        assert deleted is None
```

---

## Pattern 2: Integration Module Tests

### Template

```python
"""
Unit tests for integration module.

Mock external systems, test integration logic.
"""

import pytest
from unittest.mock import Mock, patch
from src.integrations.integration_name import integration


class TestIntegrationConnectivity:
    """Test integration connectivity checks."""
    
    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_connectivity_success(self, mock_subprocess):
        """Test successful connectivity check."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0)
        
        # Act
        result = integration.check_connectivity()
        
        # Assert
        assert result is True
        mock_subprocess.assert_called_once()
    
    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_connectivity_failure(self, mock_subprocess):
        """Test failed connectivity check."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=1)
        
        # Act
        result = integration.check_connectivity()
        
        # Assert
        assert result is False


class TestIntegrationOperations:
    """Test integration operations."""
    
    @pytest.mark.unit
    def test_operation_with_mock(self, mock_external_api):
        """Test operation with mocked external API."""
        # Arrange
        mock_external_api.get.return_value = {"status": "ok"}
        
        # Act
        result = integration.fetch_data()
        
        # Assert
        assert result["status"] == "ok"
        mock_external_api.get.assert_called_once()
```

---

## Pattern 3: Integration Tests (Real Dependencies)

### Template

```python
"""
Integration tests with real dependencies.

Uses real Git, real database, but isolated environment.
"""

import pytest
from src.core import work_module, git_module
from src import models


class TestWorkItemLifecycle:
    """Test complete work item workflow."""
    
    @pytest.mark.integration
    def test_create_commit_complete_workflow(self, db_session, temp_git_repo):
        """Test full work item lifecycle with real Git."""
        # Create work item
        work = work_module.create_work_item(
            db_session,
            title="Test Feature",
            category="service",
            action_type="new",
            description="Test"
        )
        
        # Verify in database
        assert work.id is not None
        db_work = db_session.query(models.WorkItem).filter(
            models.WorkItem.id == work.id
        ).first()
        assert db_work is not None
        
        # Verify Git branch created
        assert work.git_branch in git_module.get_branches()
        
        # Complete checklist
        for i in range(len(work.checklist)):
            success = work_module.toggle_checklist_item(db_session, work.id, i)
            assert success is True
        
        # Verify all items checked
        db_session.refresh(work)
        assert all(item["done"] for item in work.checklist)
        
        # Merge and complete
        success, message = work_module.merge_and_complete(db_session, work.id)
        assert success is True
        
        # Verify completed
        db_session.refresh(work)
        assert work.status == "complete"
        assert work.completed_date is not None
    
    @pytest.mark.integration
    def test_git_operations_real_repo(self, temp_git_repo):
        """Test Git operations with real repository."""
        # Create branch
        success = git_module.create_branch("test-branch", checkout=True)
        assert success is True
        
        # Verify current branch
        assert git_module.get_current_branch() == "test-branch"
        
        # Get branches
        branches = git_module.get_branches()
        assert "test-branch" in branches
        assert "main" in branches
```

---

## Pattern 4: Testing with Logging

### Template

```python
"""Test that operations log correctly."""

import pytest
import logging


class TestLogging:
    """Test logging behavior."""
    
    @pytest.mark.unit
    def test_operation_logs_success(self, db_session, caplog):
        """Test successful operation logs info message."""
        with caplog.at_level(logging.INFO):
            result = module.do_something(db_session, "test")
        
        assert "Operation completed successfully" in caplog.text
        assert result is True
    
    @pytest.mark.unit
    def test_operation_logs_error(self, db_session, caplog):
        """Test error operation logs error with stack trace."""
        with caplog.at_level(logging.ERROR):
            result = module.do_something(db_session, "invalid")
        
        assert "Operation failed" in caplog.text
        # Verify stack trace included
        assert "Traceback" in caplog.text
        assert result is False
```

---

## Common Fixtures (conftest.py)

### Database Fixtures

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src import models


@pytest.fixture
def db_engine():
    """Create in-memory database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create database session for tests."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_work_item(db_session):
    """Create a sample work item for testing."""
    work = models.WorkItem(
        title="Test Work",
        category="service",
        action_type="new",
        git_branch="test/branch",
        status="planning",
        checklist=[
            {"item": "Task 1", "done": False},
            {"item": "Task 2", "done": False}
        ]
    )
    db_session.add(work)
    db_session.commit()
    db_session.refresh(work)
    return work
```

### Git Fixtures

```python
import pytest
import tempfile
import shutil
from pathlib import Path
import git


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create temporary Git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize repo
    repo = git.Repo.init(repo_path)
    
    # Create initial commit
    readme = repo_path / "README.md"
    readme.write_text("# Test Repo\n")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")
    
    # Create docs directory
    docs_path = repo_path / "docs"
    docs_path.mkdir()
    changes = docs_path / "CHANGES.md"
    changes.write_text("# Change Log\n")
    repo.index.add(["docs/CHANGES.md"])
    repo.index.commit("Add CHANGES.md")
    
    yield repo_path
    
    # Cleanup handled by tmp_path


@pytest.fixture
def mock_git(monkeypatch):
    """Mock Git operations for unit tests."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.create_branch.return_value = True
    mock.checkout_branch.return_value = True
    mock.get_branches.return_value = ["main", "test-branch"]
    mock.get_current_branch.return_value = "main"
    
    monkeypatch.setattr('src.core.git_module.git_module', mock)
    return mock
```

### Integration Fixtures

```python
@pytest.fixture
def mock_monitoring():
    """Mock monitoring integration."""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.check_endpoint.return_value = (True, None)
    mock.update_endpoint_status.return_value = True
    return mock
```

---

## Naming Conventions

### Test Files
- **Pattern:** `test_{module_name}.py`
- **Example:** `test_work_module.py`

### Test Classes
- **Pattern:** `Test{Module}{Operation}`
- **Example:** `TestWorkModuleCreate`, `TestGitModuleMerge`

### Test Functions
- **Pattern:** `test_{operation}_{condition}`
- **Example:** `test_create_work_item_success`, `test_delete_not_found`

---

## Assertion Patterns

### Success Cases
```python
# Basic assertions
assert result is True
assert result is not None
assert len(items) == 5

# Object assertions
assert work.title == "Test"
assert work.status == "complete"
assert work.git_branch.startswith("service/")

# Collection assertions
assert "main" in branches
assert all(item["done"] for item in checklist)
```

### Error Cases
```python
# Boolean return
success, message = module.operation()
assert success is False
assert "error" in message.lower()

# Exception raising
with pytest.raises(ValueError):
    module.invalid_operation()

with pytest.raises(ValueError, match="required"):
    module.operation(None)
```

### Database Assertions
```python
# Verify object created
obj = db_session.query(Model).filter(Model.id == id).first()
assert obj is not None

# Verify object deleted
obj = db_session.query(Model).filter(Model.id == id).first()
assert obj is None

# Verify count
count = db_session.query(Model).count()
assert count == 5
```

---

## Test Organization

### Arrange-Act-Assert Pattern

Always use AAA pattern:

```python
def test_something():
    # Arrange - Set up test data
    param = "test"
    expected = "result"
    
    # Act - Execute the operation
    result = module.operation(param)
    
    # Assert - Verify the result
    assert result == expected
```

### One Assertion Per Test (Guideline)

**Preferred:**
```python
def test_work_item_has_title():
    work = create_work_item("Test")
    assert work.title == "Test"

def test_work_item_has_branch():
    work = create_work_item("Test")
    assert work.git_branch is not None
```

**Acceptable (related assertions):**
```python
def test_work_item_creation():
    work = create_work_item("Test")
    assert work.title == "Test"
    assert work.status == "planning"
    assert work.git_branch is not None
```

---

## Running Tests

### Local Development

```bash
cd ~/calcifer/calcifer-app

# All tests
pytest

# Fast tests only
pytest -m unit

# Specific module
pytest tests/unit/test_core/test_work_module.py

# Specific test
pytest tests/unit/test_core/test_work_module.py::TestWorkModuleCreate::test_create_basic

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Pre-Commit Hook

```bash
# Run fast tests before commit
pytest -m unit --quiet

# If tests pass, commit proceeds
# If tests fail, commit blocked
```

### CI Pipeline

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=xml --cov-report=term
```

---

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Core Modules | 80%+ | TBD |
| Integration Modules | 70%+ | TBD |
| Routes | 60%+ | TBD |
| Overall | 75%+ | TBD |

---

## Troubleshooting Tests

### Tests Can't Import Modules

```bash
# Ensure you're in the right directory
cd calcifer-app

# Install in editable mode
pip install -e .
```

### Database Errors

```python
# Use fresh session for each test
@pytest.fixture
def db_session(db_engine):
    session = SessionLocal()
    yield session
    session.rollback()  # Rollback changes
    session.close()
```

### Git Errors

```python
# Use isolated temp directory
@pytest.fixture
def temp_git_repo(tmp_path):
    # tmp_path is automatically cleaned up
    repo_path = tmp_path / "repo"
    # ... setup repo
    return repo_path
```

---

## Next Steps

1. **Read this document thoroughly**
2. **Review examples in test files**
3. **Write your first test**
4. **Run tests and verify**
5. **Add tests to CI/CD pipeline**

---

## References

- pytest documentation: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- pytest markers: https://docs.pytest.org/en/stable/mark.html
- Coverage.py: https://coverage.readthedocs.io/

---

**Remember:** Tests are documentation. Write tests that clearly show how modules should be used.