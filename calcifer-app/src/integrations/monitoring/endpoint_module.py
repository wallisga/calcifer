"""
Monitoring Endpoint Module

Business logic for managing monitored endpoints.
This module uses core modules (work, docs, git) to create
endpoints with full work item tracking.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Tuple, Optional
import json

# Import from CURRENT location (will update paths later)
from ...core import work_module, documentation_module, git_module
from ...models import Endpoint, WorkItem
from .integration import monitoring


class EndpointModule:
    """
    Endpoint management module.
    
    Handles the business logic for creating, managing, and checking
    monitored endpoints. Coordinates between core modules and
    monitoring integration.
    """
    
    # ========================================================================
    # ✨ NEW CONVENIENCE METHOD - PHASE 2
    # ========================================================================
    
    def get_endpoint_detail(self, db: Session, endpoint_id: int) -> Optional[dict]:
        """
        Get endpoint with related work item.
        
        Args:
            db: Database session
            endpoint_id: Endpoint ID
            
        Returns:
            Dictionary with endpoint and work item, or None if not found
        """
        endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
        
        if not endpoint:
            return None
        
        # Get associated work item
        work_item = None
        if endpoint.work_item_id:
            work_item = db.query(WorkItem).filter(
                WorkItem.id == endpoint.work_item_id
            ).first()
        
        return {
            "endpoint": endpoint,
            "work_item": work_item
        }
    
    # ========================================================================
    # ENDPOINT CREATION
    # ========================================================================
    
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
        
        This method:
        1. Creates work item with branch
        2. Creates endpoint in database
        3. Generates documentation
        4. Commits everything to git
        5. Performs initial health check
        6. Updates work item notes
        
        Args:
            db: Database session
            name: Endpoint name
            endpoint_type: Type (network, tcp, http, https)
            target: Target IP/hostname
            port: Port number (optional)
            check_interval: Check interval in seconds
            description: Optional description
            
        Returns:
            Tuple of (work_item_id, success_message)
        """
        # 1. Create work item
        work_item = work_module.create_work_item(
            db,
            title=f"Add monitoring endpoint: {name}",
            category="service",
            action_type="new",
            description=f"Create monitoring endpoint for {endpoint_type} target: {target}"
        )
        
        # 2. Create endpoint
        endpoint = Endpoint(
            name=name,
            endpoint_type=endpoint_type,
            target=target,
            port=port,
            check_interval=check_interval,
            description=description,
            work_item_id=work_item.id,
            status="unknown"
        )
        
        # 3. Generate and save documentation
        doc_content = monitoring.generate_endpoint_documentation(
            name, endpoint_type, target, port, description
        )
        doc_filename = f"endpoint-{name.lower().replace(' ', '-')}.md"
        documentation_module.create_doc(doc_filename, doc_content)
        endpoint.documentation_url = f"/docs-viewer/{doc_filename}"
        
        # 4. Create monitoring config
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
        db.refresh(endpoint)
        
        # 5. Commit to git
        self._commit_endpoint_creation(work_item, name, endpoint_type, target, doc_filename)
        
        # 6. Perform initial check
        is_up = monitoring.update_endpoint_status(endpoint, db)
        
        # 7. Update work item notes
        self._update_work_item_notes(db, work_item, endpoint, is_up, doc_filename, monitor_config)
        
        # 8. Auto-complete some checklist items
        self._update_checklist(db, work_item, is_up)
        
        success_msg = f"Endpoint created and is {'UP! ✅' if is_up else 'DOWN ❌'}"
        return work_item.id, success_msg
    
    def _commit_endpoint_creation(
        self,
        work_item: WorkItem,
        name: str,
        endpoint_type: str,
        target: str,
        doc_filename: str
    ) -> None:
        """Commit endpoint creation to git."""
        commit_message = f"Add monitoring endpoint: {name}"
        
        # Update CHANGES.md
        changes_entry = f"Add monitoring endpoint: {name} ({endpoint_type} - {target})"
        try:
            author = git_module.repo.config_reader().get_value("user", "name")
        except:
            author = "System"
        
        work_type_display = "New Service"
        documentation_module.append_to_changes_md(changes_entry, author, work_type_display)
        
        # Stage both files together
        git_module.stage_files(['docs/CHANGES.md', f'docs/{doc_filename}'])
        
        # Commit
        commit_sha = git_module.commit(commit_message)
        
        # Record commit in database
        if commit_sha:
            from ...models import Commit
            commit_record = Commit(
                work_item_id=work_item.id,
                commit_sha=commit_sha,
                commit_message=commit_message
            )
            from sqlalchemy.orm import object_session
            db = object_session(work_item)
            db.add(commit_record)
            db.commit()
    
    def _update_work_item_notes(
        self,
        db: Session,
        work_item: WorkItem,
        endpoint: Endpoint,
        is_up: bool,
        doc_filename: str,
        monitor_config: dict
    ) -> None:
        """Update work item with endpoint details."""
        notes = f"""# Endpoint: {endpoint.name}

**Type:** {endpoint.endpoint_type}
**Target:** {endpoint.target}
{f'**Port:** {endpoint.port}' if endpoint.port else ''}
**Check Interval:** {endpoint.check_interval}s
**Initial Status:** {'✅ UP' if is_up else '❌ DOWN'}

## Generated Files
- Documentation: `docs/{doc_filename}` ✅ Committed
- CHANGES.md: Updated ✅ Committed

## Configuration
```json
{json.dumps(monitor_config, indent=2)}
```

## Initial Check Results
- Performed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Status: {'UP - endpoint is reachable' if is_up else 'DOWN - endpoint is not reachable'}

## Next Steps
1. ✅ Documentation created and committed
2. ✅ Monitoring configured
3. {'✅ Endpoint verified as UP' if is_up else '❌ Investigate connectivity issue'}
4. Review the work item and mark complete when satisfied
"""
        work_item.notes = notes
        db.commit()
    
    def _update_checklist(
        self,
        db: Session,
        work_item: WorkItem,
        is_up: bool
    ) -> None:
        """Auto-complete checklist items."""
        # These steps were done automatically
        work_item.checklist[0]["done"] = True  # Define endpoint details
        work_item.checklist[1]["done"] = True  # Create documentation
        work_item.checklist[2]["done"] = True  # Configure monitoring
        work_item.checklist[3]["done"] = True  # Commit configuration
        work_item.checklist[4]["done"] = is_up  # Verify reachability (only if UP)
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(work_item, "checklist")
        db.commit()
    
    # ========================================================================
    # ENDPOINT RETRIEVAL
    # ========================================================================
    
    def get_endpoint(self, db: Session, endpoint_id: int):
        """Get endpoint by ID."""
        return db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    
    def get_all_endpoints(self, db: Session):
        """Get all endpoints."""
        return db.query(Endpoint).order_by(Endpoint.name).all()
    
    # ========================================================================
    # ENDPOINT DELETION
    # ========================================================================
    
    def delete_endpoint(self, db: Session, endpoint_id: int) -> Tuple[bool, str]:
        """Delete endpoint."""
        endpoint = self.get_endpoint(db, endpoint_id)
        if not endpoint:
            return False, "Endpoint not found"
        
        endpoint_name = endpoint.name
        db.delete(endpoint)
        db.commit()
        
        return True, f"Endpoint '{endpoint_name}' deleted successfully"


# Singleton instance
endpoint_module = EndpointModule()