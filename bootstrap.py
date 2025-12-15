"""
Bootstrap Calcifer Self-Management

This script:
1. Creates .calcifer/ directory in calcifer-app
2. Initializes metadata files
3. Registers calcifer-app as a service in its own catalog
4. Creates self-monitoring endpoint

Run this ONCE after completing Work Item 3.
"""

from src.database import SessionLocal
from src.core import service_catalog_module, service_metadata_module
from src.integrations.monitoring import endpoint_module
import os

def bootstrap_calcifer():
    db = SessionLocal()
    
    try:
        print("=== Bootstrapping Calcifer Self-Management ===\n")
        
        # Get current directory
        calcifer_app_path = os.path.expanduser("~/calcifer/calcifer-app")
        
        # Step 1: Initialize .calcifer/ directory
        print("Step 1: Initializing .calcifer/ metadata directory...")
        service_metadata_module.initialize_metadata_files(
            calcifer_app_path,
            "calcifer-app"
        )
        print("✅ .calcifer/ directory created with metadata files\n")
        
        # Step 2: Check if calcifer-app service already exists
        print("Step 2: Checking if calcifer-app service exists...")
        existing = db.query(models.Service).filter(
            models.Service.name == "calcifer-app"
        ).first()
        
        if existing:
            print(f"✅ calcifer-app service already exists (ID: {existing.id})\n")
            calcifer_service = existing
        else:
            # Step 3: Register calcifer-app as a service
            print("Step 3: Registering calcifer-app as a service...")
            calcifer_service, work_item = service_catalog_module.create_service_with_work_item(
                db,
                name="calcifer-app",
                service_type="container",  # or "bare_metal" depending on deployment
                host="localhost",
                description="Calcifer infrastructure management platform",
                url="http://localhost:8000",
                ports="8000:8000",
                git_repo_path=calcifer_app_path,
                git_repo_url="git@github.com:YOUR_USERNAME/calcifer-app.git",  # Update this!
                git_repo_private=True,
                git_provider="github",
                deployment_type="docker",  # or "bare_metal"
                docker_compose_path=f"{calcifer_app_path}/docker-compose.yml"
            )
            print(f"✅ calcifer-app registered as service (ID: {calcifer_service.id})")
            print(f"✅ Work item created (ID: {work_item.id})\n")
        
        # Step 4: Create self-monitoring endpoint
        print("Step 4: Creating self-monitoring endpoint...")
        existing_endpoint = db.query(models.Endpoint).filter(
            models.Endpoint.name == "Calcifer Health Check"
        ).first()
        
        if existing_endpoint:
            print(f"✅ Health check endpoint already exists (ID: {existing_endpoint.id})\n")
        else:
            work_item_id, message = endpoint_module.create_endpoint_with_work_item(
                db,
                name="Calcifer Health Check",
                endpoint_type="http",
                target="localhost",
                port=8000,
                check_interval=60,
                description="Monitors Calcifer's own health endpoint",
                service_id=calcifer_service.id
            )
            print(f"✅ {message}")
            print(f"✅ Endpoint work item created (ID: {work_item_id})\n")
        
        print("=== Bootstrap Complete ===")
        print("\nCalcifer is now managing itself!")
        print(f"- Service ID: {calcifer_service.id}")
        print(f"- Metadata: {calcifer_app_path}/.calcifer/")
        print(f"- View in UI: http://localhost:8000/services/{calcifer_service.id}")
        print("\nNext steps:")
        print("1. Complete the bootstrap work items in Calcifer UI")
        print("2. Verify .calcifer/ directory committed to Git")
        print("3. Check service detail page shows endpoints and work items")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Import here to avoid issues
    from src import models
    bootstrap_calcifer()