# Calcifer Roadmap

Future enhancements and ideas for Calcifer.

## High Priority

### Work Item Documentation Enforcement
- [ ] Add notes/documentation field that's editable in work item UI
- [ ] Require documentation before marking work item complete
- [ ] Auto-generate documentation template based on work type
- [ ] Link work item documentation to specific files in Git repo

### Git Branch Integration
- [ ] Check if branch has been merged before allowing work item closure
- [ ] Show merge status in work item UI
- [ ] Provide "Create Pull Request" button (for GitHub/GitLab)
- [ ] Auto-close work item when branch is merged

### Git Commit Workflow
- [ ] Add "Commit" button in UI that enforces CHANGES.md update
- [ ] Show uncommitted changes in work item view
- [ ] Validate CHANGES.md has entry before allowing commit
- [ ] Link commits to work items automatically

## Medium Priority

### Service Catalog Enhancements
- [ ] Link services to monitoring dashboards (Uptime Kuma, Grafana)
- [ ] Link services to documentation pages
- [ ] Require change log entry when adding/modifying services
- [ ] Auto-detect services from docker-compose files
- [ ] Service dependency graph visualization
- [ ] Health check integration (ping, HTTP status)

### Documentation
- [ ] In-app documentation editor (markdown)
- [ ] Auto-generate docs from work item completion
- [ ] Documentation templates by service type
- [ ] Search functionality across all docs
- [ ] Documentation review workflow

### Backup & Recovery
- [ ] Automated database backups
- [ ] Export/import functionality
- [ ] Backup to remote storage (S3, etc.)
- [ ] Restore from backup feature
- [ ] Configuration backup integration

## Low Priority / Future Ideas

### Integrations Framework
- [ ] Plugin system for custom integrations
- [ ] Integration marketplace/catalog
- [ ] OAuth support for third-party services
- [ ] Webhook system for automation

### Monitoring Integration
- [ ] Uptime Kuma API integration
- [ ] Grafana dashboard embedding
- [ ] Alert correlation with work items
- [ ] Incident management workflow

### Collaboration
- [ ] Multi-user support with authentication
- [ ] Role-based access control (RBAC)
- [ ] Work item assignment
- [ ] Comments/discussion threads
- [ ] Notifications (email, Slack, Discord)

### Advanced Git Features
- [ ] Compare branches
- [ ] Visual diff viewer
- [ ] Merge conflict detection
- [ ] Auto-merge for simple changes

### UI/UX
- [ ] Dark mode
- [ ] Customizable themes
- [ ] Dashboard widgets
- [ ] Mobile-responsive improvements
- [ ] Keyboard shortcuts

### Reporting & Analytics
- [ ] Work item velocity metrics
- [ ] Time tracking
- [ ] Infrastructure change frequency
- [ ] Service uptime reports

## Repository Structure Decisions

### Current State