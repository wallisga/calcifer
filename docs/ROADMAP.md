# Calcifer Roadmap

Future enhancements and ideas for Calcifer.

## Recently Completed ✅

### Work Item Documentation Enforcement
- ✅ Added editable notes field (2000 char limit) in work item UI
- ✅ Required documentation before marking work item complete
- ✅ Auto-generate documentation template based on work type (via checklists)

### Git Branch Integration
- ✅ Check if branch has been merged before allowing work item closure
- ✅ Show merge status in work item UI
- ✅ Show commit list from branch in work item view
- ✅ Merge & Complete button (validates and merges in one action)

### Git Commit Workflow
- ✅ Added "Commit Changes" button in UI that enforces CHANGES.md update
- ✅ Show uncommitted changes in commit form
- ✅ Validate CHANGES.md has entry before allowing merge
- ✅ Link commits to work items automatically
- ✅ Automatic CHANGES.md entry creation via UI

### Work Item Management
- ✅ Delete work items with automatic branch cleanup
- ✅ SQLAlchemy JSON column fix (checklist persistence)
- ✅ Enhanced checklists by work type
- ✅ Validation before merge and completion

## High Priority

### Service Catalog Enhancements
- [ ] Link services to monitoring dashboards (Uptime Kuma, Grafana)
- [ ] Link services to documentation pages
- [ ] Require change log entry when adding/modifying services
- [ ] Auto-detect services from docker-compose files
- [ ] Service dependency graph visualization
- [ ] Health check integration (ping, HTTP status)

### Documentation
- [ ] In-app documentation editor (markdown) for new docs
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

## Medium Priority

### Advanced Git Features
- [ ] Compare branches visually
- [ ] Visual diff viewer
- [ ] Merge conflict detection and resolution
- [ ] Create Pull Request button (for GitHub/GitLab integrations)

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

## Low Priority / Future Ideas

### UI/UX
- [ ] Dark mode
- [ ] Customizable themes (beyond current red theme)
- [ ] Dashboard widgets (customizable home page)
- [ ] Mobile-responsive improvements
- [ ] Keyboard shortcuts
- [ ] Drag-and-drop checklist reordering

### Reporting & Analytics
- [ ] Work item velocity metrics
- [ ] Time tracking per work item
- [ ] Infrastructure change frequency graphs
- [ ] Service uptime reports
- [ ] Burndown charts

### Advanced Work Item Features
- [ ] Work item templates (create from template)
- [ ] Sub-tasks / nested work items
- [ ] Work item relationships (blocks, depends on)
- [ ] Tags and labels
- [ ] Work item search and filters

## Repository Structure

### Current State ✅
```
calcifer/                  # Git repo root
├── calcifer-app/         # Application code
│   ├── src/             # Python source
│   ├── templates/       # HTML templates
│   ├── data/            # SQLite database (gitignored)
│   └── requirements.txt
├── docs/                 # Documentation (in repo)
│   ├── ROADMAP.md
│   ├── SETUP_GUIDE.md
│   ├── PREREQUISITES.md
│   ├── CHANGES.md       # Local changes (tracked in private repo)
│   └── ...
├── infrastructure/       # Future: Deployed configs
└── README.md
```

### Future Considerations
- Infrastructure as Code (IaC) templates
- Docker Compose templates for common stacks
- Ansible playbooks integration
- Terraform module examples

## Technical Debt / Improvements

- [ ] Add automated tests (pytest)
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Database migrations (Alembic)
- [ ] API rate limiting
- [ ] Better error handling and logging
- [ ] Performance optimization for large datasets
- [ ] Add API documentation (Swagger/OpenAPI)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose new features or contribute to this roadmap.

---

**Last Updated**: 2024-11-22
**Status**: Active development, private repo phase