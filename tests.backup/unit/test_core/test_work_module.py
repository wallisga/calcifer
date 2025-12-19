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
    def test_create_generates_correct_checklist_for_service(self, db_session, mock_git):
        """Test that service/new generates service-specific checklist."""
        # Act
        result = work_module.create_work_item(
            db_session, "Test Service", "service", "new"
        )
        
        # Assert
        assert len(result.checklist) > 0
        # Check for service-specific items
        checklist_text = str(result.checklist)
        assert "service" in checklist_text.lower() or "deploy" in checklist_text.lower()
    
    @pytest.mark.unit
    def test_create_different_categories(self, db_session, mock_git):
        """Test creation with different categories."""
        categories = ["platform_feature", "integration", "service", "documentation"]
        
        for category in categories:
            work = work_module.create_work_item(
                db_session, f"Test {category}", category, "new"
            )
            assert work.category == category
            assert len(work.checklist) > 0  # Has checklist
            
            # Verify persisted to database
            db_work = db_session.query(models.WorkItem).filter(
                models.WorkItem.id == work.id
            ).first()
            assert db_work is not None
    
    @pytest.mark.unit
    def test_create_generates_unique_branch_names(self, db_session, mock_git):
        """Test that branch names are assigned to work items."""
        # Arrange & Act
        work1 = work_module.create_work_item(
            db_session,
            title="Feature A",
            category="platform_feature",
            action_type="new"
        )
        
        work2 = work_module.create_work_item(
            db_session,
            title="Feature B",
            category="service",
            action_type="fix"
        )
        
        # Assert - just verify branches were set, don't test format
        assert work1.git_branch is not None
        assert work2.git_branch is not None
        assert work1.git_branch != work2.git_branch
        
        # Note: Branch name format testing belongs in integration tests
        # where we test the real git_module behavior


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
    
    @pytest.mark.unit
    def test_get_active_work(self, db_session, sample_work_item):
        """Test retrieving active work items."""
        # Act
        results = work_module.get_active_work(db_session)
        
        # Assert
        assert len(results) >= 1
        assert sample_work_item.id in [w.id for w in results]
    
    @pytest.mark.unit
    def test_get_completed_work(self, db_session, sample_work_item):
        """Test retrieving completed work items."""
        # Arrange - Complete the work item
        sample_work_item.status = "complete"
        from datetime import datetime
        sample_work_item.completed_date = datetime.utcnow()
        db_session.commit()
        
        # Act
        results = work_module.get_completed_work(db_session, limit=5)
        
        # Assert
        assert len(results) >= 1
        assert sample_work_item.id in [w.id for w in results]


class TestWorkModuleUpdate:
    """Test work item updates."""
    
    @pytest.mark.unit
    def test_toggle_checklist_item(self, db_session, sample_work_item):
        """Test toggling checklist item from False to True."""
        # Arrange
        assert sample_work_item.checklist[0]["done"] is False
        
        # Act
        success = work_module.toggle_checklist_item(
            db_session, sample_work_item.id, 0
        )
        
        # Assert
        assert success is True
        db_session.refresh(sample_work_item)
        assert sample_work_item.checklist[0]["done"] is True
    
    @pytest.mark.unit
    def test_toggle_checklist_item_twice(self, db_session, sample_work_item):
        """Test toggling checklist item back and forth."""
        # Act - Toggle twice
        work_module.toggle_checklist_item(db_session, sample_work_item.id, 0)
        work_module.toggle_checklist_item(db_session, sample_work_item.id, 0)
        
        # Assert - Should be back to False
        db_session.refresh(sample_work_item)
        assert sample_work_item.checklist[0]["done"] is False
    
    @pytest.mark.unit
    def test_toggle_invalid_index(self, db_session, sample_work_item):
        """Test toggling with invalid index."""
        # Act
        success = work_module.toggle_checklist_item(
            db_session, sample_work_item.id, 999
        )
        
        # Assert
        assert success is False
    
    @pytest.mark.unit
    def test_update_notes(self, db_session, sample_work_item):
        """Test updating work item notes."""
        # Arrange
        new_notes = "These are updated notes with important information"
        
        # Act
        result = work_module.update_notes(
            db_session, sample_work_item.id, new_notes
        )
        
        # Assert
        assert result is not None
        assert result.notes == new_notes
        
        # Verify persistence
        db_session.refresh(sample_work_item)
        assert sample_work_item.notes == new_notes
    
    @pytest.mark.unit
    def test_update_notes_truncates_long_text(self, db_session, sample_work_item):
        """Test that notes are truncated to 2000 characters."""
        # Arrange
        long_notes = "x" * 3000  # 3000 characters
        
        # Act
        result = work_module.update_notes(
            db_session, sample_work_item.id, long_notes
        )
        
        # Assert
        assert len(result.notes) == 2000


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
        assert "success" in message.lower()
        
        # Verify deleted from database
        deleted = db_session.query(models.WorkItem).filter(
            models.WorkItem.id == work_id
        ).first()
        assert deleted is None
    
    @pytest.mark.unit
    def test_delete_nonexistent_work_item(self, db_session, mock_git):
        """Test deleting non-existent work item."""
        # Act
        success, message = work_module.delete_work_item(db_session, 9999)
        
        # Assert
        assert success is False
        assert "not found" in message.lower()


class TestWorkModuleValidation:
    """Test work item validation."""
    
    @pytest.mark.unit
    def test_validate_for_completion_all_checks_pass(self, db_session, sample_work_item, mock_git):
        """Test validation when all requirements met."""
        # Arrange - Complete all checklist items
        for item in sample_work_item.checklist:
            item["done"] = True
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(sample_work_item, "checklist")
        db_session.commit()
        
        # Mock git to show commits exist
        mock_git.get_branch_commits.return_value = [{"sha": "abc123"}]
        mock_git.check_changes_md_updated.return_value = True
        
        # Act
        is_valid, errors = work_module.validate_for_completion(sample_work_item)
        
        # Assert
        assert is_valid is True
        assert len(errors) == 0
    
    @pytest.mark.unit
    def test_validate_incomplete_checklist(self, db_session, sample_work_item, mock_git):
        """Test validation with incomplete checklist."""
        # Arrange - Leave checklist incomplete
        mock_git.get_branch_commits.return_value = [{"sha": "abc123"}]
        
        # Act
        is_valid, errors = work_module.validate_for_completion(sample_work_item)
        
        # Assert
        assert is_valid is False
        assert len(errors) > 0
        assert any("checklist" in err.lower() for err in errors)