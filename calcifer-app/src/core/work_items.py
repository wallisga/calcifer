"""Work Item Service - Business logic for work item operations."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Tuple, Optional
from .. import models
from ..integrations import git_manager


class WorkService:
    """Service for managing work items and their lifecycle."""
    
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
        
        # Generate branch name
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
        work_item.checklist = WorkService._generate_checklist(category, action_type)
        
        db.add(work_item)
        db.commit()
        db.refresh(work_item)
        
        return work_item
    
    @staticmethod
    def _generate_checklist(category: str, action_type: str) -> List[dict]:
        """Generate checklist items based on work type."""
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
                    {"item": "Add to INTEGRATIONS.md doc (if exists)", "done": False}
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
    def toggle_checklist_item(db: Session, work_id: int, index: int) -> bool:
        """Toggle a checklist item's completion status."""
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
        """Update work item notes."""
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item:
            return None
        
        work_item.notes = notes[:2000] if notes else None
        db.commit()
        return work_item
    
    @staticmethod
    def delete_work_item(db: Session, work_id: int) -> Tuple[bool, str]:
        """Delete work item and its Git branch."""
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item:
            return False, "Work item not found"
        
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
                        pass  # Remote branch might not exist
                        
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
        """Validate work item is ready for completion."""
        errors = []
        
        # Check 1: All checklist items completed?
        incomplete_items = [item for item in work_item.checklist if not item.get("done", False)]
        if incomplete_items:
            errors.append(f"{len(incomplete_items)} checklist item(s) not completed")
        
        # Check 2: Branch merged?
        if work_item.git_branch and not work_item.branch_merged:
            errors.append("Branch not yet merged to main")
        
        # Check 3: Branch has commits?
        if work_item.git_branch:
            branch_commits = git_manager.get_branch_commits(work_item.git_branch)
            if not branch_commits:
                errors.append("Branch has no commits")
        
        # Check 4: CHANGES.md updated?
        if work_item.git_branch:
            if not git_manager.check_changes_md_updated():
                errors.append("docs/CHANGES.md not updated in this branch")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def merge_and_complete(db: Session, work_id: int) -> Tuple[bool, str]:
        """Validate, merge branch, and complete work item."""
        work_item = db.query(models.WorkItem).filter(models.WorkItem.id == work_id).first()
        if not work_item:
            return False, "Work item not found"
        
        # Validation phase
        is_valid, errors = WorkService.validate_for_completion(work_item)
        if not is_valid:
            return False, " | ".join(errors)
        
        # Merge phase
        if git_manager.is_branch_merged(work_item.git_branch):
            work_item.branch_merged = True
        else:
            success, result = git_manager.merge_branch(work_item.git_branch)
            if not success:
                return False, f"Merge failed: {result}"
            
            work_item.branch_merged = True
            work_item.merge_commit_sha = result
        
        # Completion phase
        work_item.status = "complete"
        work_item.completed_date = datetime.utcnow()
        db.commit()
        
        return True, "Work item completed and merged successfully!"