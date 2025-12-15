"""
Test script for Work Item 3: Service-Linked Work Items & Metadata
"""

from src.database import SessionLocal
from src.core import (
    service_catalog_module,
    work_module,
    service_metadata_module,
    git_module
)
from src import models
import os

def test_work_item_3():
    db = SessionLocal()
    
    try:
        print("=== Testing Work Item 3 Implementation ===\n")
        
        # Test 1: Create service with Git repo
        print("Test 1: Creating service with Git repository...")
        test_repo_path = os.path.expanduser("~/calcifer/test-service-wi3")
        
        service, work_item = service_catalog_module.create_service_with_work_item(
            db,
            name="Test Service WI3",
            service_type="container",
            host="localhost",
            description="Test service for Work Item 3",
            git_repo_path=test_repo_path,
            git_provider="github"
        )
        print(f"✅ Service created: {service.name} (ID: {service.id})")
        print(f"✅ Work item created: #{work_item.id}")
        print(f"✅ Work item linked to service: {work_item.service_id == service.id}")
        print()
        
        # Test 2: Verify .calcifer/ directory created
        print("Test 2: Verifying .calcifer/ metadata directory...")
        calcifer_dir = os.path.join(test_repo_path, ".calcifer")
        assert os.path.exists(calcifer_dir), ".calcifer/ not created"
        assert os.path.exists(os.path.join(calcifer_dir, "endpoints.json")), "endpoints.json not created"
        assert os.path.exists(os.path.join(calcifer_dir, "integrations.json")), "integrations.json not created"
        assert os.path.exists(os.path.join(calcifer_dir, "metadata.json")), "metadata.json not created"
        print("✅ .calcifer/ directory exists")
        print("✅ All metadata files created")
        print()
        
        # Test 3: Create service-linked work item
        print("Test 3: Creating service-linked work item...")
        service_work_item = work_module.create_work_item(
            db,
            title="Configure Test Service",
            category="service",
            action_type="change",
            description="Test service-linked work item",
            service_id=service.id
        )
        print(f"✅ Service-linked work item created: #{service_work_item.id}")
        print(f"✅ Linked to service: {service_work_item.service_id == service.id}")
        print()
        
        # Test 4: Verify Git branch in service repo
        print("Test 4: Verifying Git branch in service repository...")
        repo_status = git_module.get_repo_status(test_repo_path)
        assert repo_status["initialized"], "Service repo not initialized"
        print(f"✅ Service repo initialized")
        print(f"   Current branch: {repo_status.get('current_branch')}")
        print()
        
        # Test 5: Get service detail with work items
        print("Test 5: Getting service detail with work items...")
        detail = service_catalog_module.get_service_detail(db, service.id)
        assert len(detail['work_items']) >= 2, "Should have at least 2 work items"
        print(f"✅ Service has {len(detail['work_items'])} work items")
        for wi in detail['work_items']:
            print(f"   - #{wi.id}: {wi.title}")
        print()
        
        # Test 6: Load integration settings
        print("Test 6: Loading integration settings...")
        settings = service_metadata_module.load_integration_settings(test_repo_path)
        assert "monitoring_enabled" in settings, "Missing monitoring_enabled"
        print(f"✅ Integration settings loaded")
        print(f"   Monitoring enabled: {settings.get('monitoring_enabled')}")
        print()
        
        # Test 7: Clean up
        print("Test 7: Cleaning up test data...")
        # Delete work items
        work_module.delete_work_item(db, work_item.id)
        work_module.delete_work_item(db, service_work_item.id)
        # Delete service
        service_catalog_module.delete_service(db, service.id)
        # Remove test repo directory
        import shutil
        if os.path.exists(test_repo_path):
            shutil.rmtree(test_repo_path)
        print("✅ Test data cleaned up")
        print()
        
        print("=== All Tests Passed! ===")
        print("\nNext steps:")
        print("1. Run bootstrap script: python bootstrap_calcifer.py")
        print("2. Start Calcifer and view service detail pages")
        print("3. Create endpoints linked to services")
        print("4. Verify work items show in service detail")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_work_item_3()