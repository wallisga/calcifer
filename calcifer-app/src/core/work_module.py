"""
Core Work Module

Handles work item management - the core workflow of Calcifer.
Work items represent units of work (tasks, features, fixes) that
track changes to the infrastructure.

This is CORE functionality - required for Calcifer to work.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Tuple, Optional
from .. import models
from .git_module import git_module


class WorkModule:
    """
    Core module for managing work items and their lifecycle.
    
    Work items are the foundation of Calcifer's change tracking.
    Each work item gets its own Git branch and tracks progress
    through checklists, documentation, and commits.
    """
    
    @staticmethod
    def create_work_item(
        db: Session,
        title: str,
        category: str,
        action_type: str,
        description: str = ""
    ) -> models.WorkItem:
        """
        Create a new work item with automatic branch creation and checklist.
        
        Args:
            db: Database session
            title: Work item title
            category: Category (platform_feature, integration, service, documentation)
            action_type: Action type (new, change, fix)
            description: Optional description
            
        Returns:
            Created WorkItem model instance
        """
        # Create work item
        work_item = models.WorkItem(
            title=title,
            category=category,
            action_type=action_type,
            description=description,
            status="planning"
        )
        
        # Generate branch name using git module
        branch_name = git_module.generate_branch_name(category, action_type, title)
        work_item.git_branch = branch_name
        
        # Create Git branch
        git_module.create_branch(branch_name, checkout=True)
        
        # Initialize checklist based on category and action
        work_item.checklist = WorkModule._generate_checklist(category, action_type)
        
        db.add(work_item)
        db.commit()
        db.refresh(work_item)
        
        return work_item
    
    @staticmethod
    def _generate_checklist(category: str, action_type: str) -> List[dict]:
        """
        Generate checklist items based on work type.
        
        Args:
            category: Work item category
            action_type: Action type
            
        Returns:
            List of checklist item dictionaries
        """
        checklists = {
            'platform_feature': {
                'new': [
                    {"item": "Define feature requirements and scope", "done": False},
                    {"item": "Design database schema changes (if any)", "done": False},
                    {"item": "Implement backend logic", "done": False},
                    {"item": "Create/update UI templates", "done": False},
                    {"item": "Test feature thoroughly", "done": False},
                    {"item": "Document feature in work notes", "done": False},
                    {"item": "Update user-facing documentation", "done": False}
                ],
                'change': [
                    {"item": "Document current behavior", "done": False},
                    {"item": "Implement changes", "done": False},
                    {"item": "Test changes thoroughly", "done": False},
                    {"item": "Update related documentation", "done": False},
                    {"item": "Verify no regressions", "done": False}
                ],
                'fix': [
                    {"item": "Reproduce the issue", "done": False},
                    {"item": "Identify root cause", "done": False},
                    {"item": "Implement fix", "done": False},
                    {"item": "Test fix thoroughly", "done": False},
                    {"item": "Verify issue is resolved", "done": False},
                    {"item": "Document fix for future reference", "done": False}
                ]
            },
            'integration': {
                'new': [
                    {"item": "Research integration API/requirements", "done": False},
                    {"item": "Create integration module structure", "done": False},
                    {"item": "Implement core integration logic", "done": False},
                    {"item": "Add configuration options", "done": False},
                    {"item": "Test integration end-to-end", "done": False},
                    {"item": "Document integration setup", "done": False},
                    {"item": "Add to integrations documentation", "done": False}
                ],
                'change': [
                    {"item": "Document current integration behavior", "done": False},
                    {"item": "Implement changes", "done": False},
                    {"item": "Test integration functionality", "done": False},
                    {"item": "Update integration documentation", "done": False}
                ],
                'fix': [
                    {"item": "Reproduce integration issue", "done": False},
                    {"item": "Identify root cause", "done": False},
                    {"item": "Implement fix", "done": False},
                    {"item": "Test integration thoroughly", "done": False},
                    {"item": "Document fix", "done": False}
                ]
            },
            'service': {
                'new': [
                    {"item": "Define service purpose and requirements", "done": False},
                    {"item": "Check resource availability (RAM/CPU/disk)", "done": False},
                    {"item": "Create docker-compose.yml or config files", "done": False},
                    {"item": "Test service locally", "done": False},
                    {"item": "Deploy to target VM/host", "done": False},
                    {"item": "Configure monitoring/health checks", "done": False},
                    {"item": "Add to service catalog in Calcifer", "done": False},
                    {"item": "Document service configuration", "done": False}
                ],
                'change': [
                    {"item": "Document current service configuration", "done": False},
                    {"item": "Backup existing configuration", "done": False},
                    {"item": "Make configuration changes", "done": False},
                    {"item": "Test changes", "done": False},
                    {"item": "Update service catalog entry", "done": False},
                    {"item": "Update service documentation", "done": False}
                ],
                'fix': [
                    {"item": "Identify service issue", "done": False},
                    {"item": "Check logs and diagnostics", "done": False},
                    {"item": "Implement fix", "done": False},
                    {"item": "Restart/redeploy service", "done": False},
                    {"item": "Verify service is healthy", "done": False},
                    {"item": "Document fix for future reference", "done": False}
                ]
            },
            'documentation': {
                'new': [
                    {"item": "Define documentation scope and audience", "done": False},
                    {"item": "Create document structure/outline", "done": False},
                    {"item": "Write documentation content", "done": False},
                    {"item": "Add examples and code snippets", "done": False},
                    {"item": "Review for clarity and accuracy", "done": False},
                    {"item": "Add to docs/ directory", "done": False}
                ],
                'change': [
                    {"item": "Identify sections to update", "done": False},
                    {"item": "Make documentation changes", "done": False},
                    {"item": "Update examples if needed", "done": False},
                    {"item": "Review for accuracy", "done": False}
                ]
            }
        }
        
        return checklists.get(category, {}).get(action_type, [
            {"item": "Complete the work", "done": False},
            {"item": "Document changes", "done": False}
        ])
    
    @staticmethod
    def get_work_item(db: Session, work_id: int) -> Optional[models.WorkItem]:
        """Get work item by ID."""
        return db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
    
    @staticmethod
    def get_active_work(db: Session) -> List[models.WorkItem]:
        """Get all active (planning or in_progress) work items."""
        return db.query(models.WorkItem).filter(
            models.WorkItem.status.in_(["planning", "in_progress"])
        ).order_by(models.WorkItem.started_date.desc()).all()
    
    @staticmethod
    def get_completed_work(db: Session, limit: int = 5) -> List[models.WorkItem]:
        """Get recently completed work items."""
        return db.query(models.WorkItem).filter(
            models.WorkItem.status == "complete"
        ).order_by(models.WorkItem.completed_date.desc()).limit(limit).all()
    
    @staticmethod
    def toggle_checklist_item(db: Session, work_id: int, index: int) -> bool:
        """
        Toggle a checklist item's completion status.
        
        Args:
            db: Database session
            work_id: Work item ID
            index: Checklist item index
            
        Returns:
            True if successful, False otherwise
        """
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item or index >= len(work_item.checklist):
            return False
        
        work_item.checklist[index]["done"] = not work_item.checklist[index]["done"]
        
        # Mark column as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(work_item, "checklist")
        db.commit()
        return True
    
    @staticmethod
    def update_notes(db: Session, work_id: int, notes: str) -> Optional[models.WorkItem]:
        """
        Update work item notes.
        
        Args:
            db: Database session
            work_id: Work item ID
            notes: Notes content
            
        Returns:
            Updated work item or None if not found
        """
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item:
            return None
        
        work_item.notes = notes[:2000] if notes else None
        db.commit()
        return work_item
    
    @staticmethod
    def delete_work_item(db: Session, work_id: int) -> Tuple[bool, str]:
        """
        Delete work item and its Git branch.
        
        Args:
            db: Database session
            work_id: Work item ID
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item:
            return False, "Work item not found"
        
        branch_name = work_item.git_branch
        
        try:
            # Delete Git branch if it exists
            if branch_name:
                try:
                    # Switch to main first
                    git_module.checkout_branch("main")
                    
                    # Delete local branch
                    git_module.repo.delete_head(branch_name, force=True)
                    
                    # Note: Remote branch deletion would be in git_remote integration
                        
                except Exception as e:
                    print(f"Branch deletion failed: {e}")
            
            # Delete work item from database (cascades to commits)
            db.delete(work_item)
            db.commit()
            
            return True, "Work item deleted successfully"
            
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    @staticmethod
    def validate_for_completion(work_item: models.WorkItem) -> Tuple[bool, List[str]]:
        """
        Validate work item is ready for completion.
        
        Args:
            work_item: Work item to validate
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
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
            branch_commits = git_module.get_branch_commits(work_item.git_branch)
            if not branch_commits:
                errors.append("Branch has no commits")
        
        # Check 4: CHANGES.md updated?
        if work_item.git_branch:
            if not git_module.check_changes_md_updated():
                errors.append("docs/CHANGES.md not updated in this branch")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def merge_and_complete(db: Session, work_id: int) -> Tuple[bool, str]:
        """Validate, merge branch, and complete work item."""
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item:
            return False, "Work item not found"
        
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
            branch_commits = git_module.get_branch_commits(work_item.git_branch)
            if not branch_commits:
                errors.append("Branch has no commits")
        
        # Check 4: CHANGES.md updated?
        if work_item.git_branch:
            if not git_module.check_changes_md_updated():
                errors.append("docs/CHANGES.md not updated in this branch")
        
        # If validation fails, stop here
        if errors:
            return False, " | ".join(errors)
        
        # MERGE PHASE (happens AFTER validation passes)
        if git_module.is_branch_merged(work_item.git_branch):
            # Already merged, just update status
            work_item.branch_merged = True
        else:
            # Not merged yet - do the merge now!
            success, result = git_module.merge_branch(work_item.git_branch)
            
            if not success:
                return False, f"Merge failed: {result}"
            
            # Update merge status
            work_item.branch_merged = True
            work_item.merge_commit_sha = result
        
        # COMPLETION PHASE
        work_item.status = "complete"
        work_item.completed_date = datetime.utcnow()
        db.commit()
        
        return True, "Work item completed and merged successfully!"
    
    @staticmethod
    def commit_work(
        db: Session,
        work_id: int,
        commit_message: str,
        changes_entry: str
    ) -> Tuple[bool, str]:
        """
        Commit changes with automatic CHANGES.md update.
        
        Args:
            db: Database session
            work_id: Work item ID
            commit_message: Git commit message
            changes_entry: Entry to add to CHANGES.md
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        from datetime import datetime
        from ..models import Commit, WorkItem
        from . import documentation_module
        
        # Get work item
        work_item = db.query(WorkItem).filter(WorkItem.id == work_id).first()
        if not work_item:
            return False, "Work item not found"
        
        # Validate inputs
        if not commit_message.strip():
            return False, "Commit message is required"
        
        if not changes_entry.strip():
            return False, "CHANGES.md entry is required"
        
        try:
            # Checkout the work item's branch
            if work_item.git_branch:
                git_module.checkout_branch(work_item.git_branch)
            
            # Get author info
            try:
                author = git_module.repo.config_reader().get_value("user", "name")
            except:
                author = "System"
            
            # Get work type for display
            work_type_display = work_item.full_type if hasattr(work_item, 'full_type') else "Work"
            
            # Update CHANGES.md using documentation_module
            documentation_module.append_to_changes_md(
                changes_entry,
                author,
                work_type_display
            )
            
            # Stage all changes
            git_module.repo.git.add('-A')
            
            # Commit
            commit_sha = git_module.commit(commit_message)
            
            if not commit_sha:
                return False, "Commit failed - no changes to commit or git error"
            
            # Record commit in database
            commit_record = Commit(
                work_item_id=work_id,
                commit_sha=commit_sha,
                commit_message=commit_message
            )
            db.add(commit_record)
            db.commit()
            
            return True, "Changes committed successfully!"
            
        except Exception as e:
            return False, f"Error: {str(e)}"    


# Singleton instance for easy import
work_module = WorkModule()