# Change Log

All changes are logged here. These are auto-generated using the Merge & Complete feature.












## 2025-11-23 - Gavin Wallis - Platform Feature Fix
- Test
## 2025-11-23 - Gavin Wallis - Document Change
- New patterns for Calcifer include Core Features and Integration Features. This may require an update to the work types.
Document new data flow from UI to route to DB via core/integration service business logic
Core features can leverage integration features as a non-breaking enhancement.
Integration features are inherently extensions and are dependent on at least one core feature 

## 2025-11-23 - Gavin Wallis - New Platform Feature
- Add core services and settings and integration creation
## 2025-11-23 - Gavin Wallis - Platform Feature Change
- Docs and services are core while git and monitoring is integration for now.
## 2025-11-23 - Gavin Wallis - New Platform Feature
- Monitoring features are now being managed in the Integrations domain. This included the deprecation of endpoint features in main.
## 2025-11-23 - Gavin Wallis - Document Change
- Delete sandmox endpoint document
## 2025-11-23 - Gavin Wallis - New Service
- Add monitoring endpoint: storage (network - 10.66.33.11)
## 2025-11-23 - Gavin Wallis - New Service
- This will be logged as an endpoint change but handles how changes are updated in the endpoint wizard feature.
## 2025-11-23 - Gavin Wallis - New Platform Feature
- Ensure endpoints are automatically checked after creation.
Update checklist
## 2025-11-23 - Gavin Wallis - New Platform Feature
- Add endpoint model
Add endpoint wizard page
Add Endpoint Landing page
Add Endpoint Detail page
## 2025-11-23 - Gavin Wallis - Platform Feature Changes
- Change the work item attributes to include category and type for improved Change Log formatting.
## 2025-11-23 - Gavin Wallis - Documentation Changes
- Update Roadmap Docs
- Update README
- Update Setup Guide
## 2025-11-23 - Gavin Wallis - Platform Feature Changes
- New Feature - Deletion of Completed Items
## 2025-11-23 - Gavin Wallis - New Platform Features
- Added new commit feature that adds changes to docs
- Add feature to delete work items that are stale.
## 2025-11-22 - Gavin Wallis - Bug Fixes
- Fixed checklist items not persisting (SQLAlchemy JSON column issue)
## 2024-11-22 - Feature Enhancements
- Enhanced work item completion with validation
- Added Git branch status tracking
- Improved checklist templates by work type
- Fixed database location (now in data/ directory)
- Added editable notes field (2000 char limit)
- Added commit list view in work items
- Added merge and complete button in UI
- Improved validation messages
## 2025-11-22 - Initial Setup
- Created Calcifer application
- Set up repository structure
- Configured development environment