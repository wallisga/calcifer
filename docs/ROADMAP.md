# Calcifer Roadmap

Future enhancements and ideas for Calcifer.

## Recently Completed ✅

### Phase 3: Testing & Quality ✅ (Complete - November 2025)
- ✅ Pytest infrastructure setup
- ✅ Core module unit tests (work_module: 17 tests, 88% coverage)
- ✅ Service catalog unit tests (23 tests, 100% coverage)
- ✅ Integration tests for workflows (9 tests, end-to-end validation)
- ✅ 72.63% overall coverage for core modules
- ✅ Test fixtures for Git operations and database isolation
- ✅ Documentation of testing patterns and best practices

### Phase 2 Refactoring (November 2025)
- ✅ Complete architecture refactoring (service → module pattern)
- ✅ All routes under 20 lines
- ✅ Business logic extracted to core modules
- ✅ Added convenience methods (get_dashboard_data, get_work_detail, etc.)
- ✅ Implemented missing routes (settings, git status, integrations)
- ✅ Removed deprecated code
- ✅ 100% use of module methods in routes

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

### Monitoring Integration
- ✅ Endpoint creation with work item tracking
- ✅ ICMP ping, TCP port, HTTP/HTTPS health checks
- ✅ Automatic documentation generation for endpoints
- ✅ Status tracking and history

## High Priority

### Testing Improvements
- [ ] Add pytest to work item checklists (require tests for new features)
- [ ] Set up pre-commit hooks for test execution
- [ ] Add coverage threshold enforcement (--cov-fail-under=70)
- [ ] Document testing patterns in DEVELOPMENT.md
- [ ] Add test coverage badges to README

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
- [ ] Git remote push/pull operations

### Integrations Framework
- [ ] Plugin system for custom integrations
- [ ] Integration marketplace/catalog
- [ ] OAuth support for third-party services
- [ ] Webhook system for automation
- [ ] Integration enable/disable toggles

### Monitoring Integration Enhancements
- [ ] Uptime Kuma API integration
- [ ] Grafana dashboard embedding
- [ ] Alert correlation with work items
- [ ] Incident management workflow
- [ ] WMI checks for Windows hosts
- [ ] SNMP checks for network devices

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
- [ ] Custom dashboards

### Advanced Work Item Features
- [ ] Work item templates (create from template)
- [ ] Sub-tasks / nested work items
- [ ] Work item relationships (blocks, depends on)
- [ ] Tags and labels
- [ ] Work item search and filters
- [ ] Bulk operations

## Repository Structure

### Current State ✅
```
calcifer/                  # Git repo root
├── calcifer-app/         # Application code
│   ├── src/             # Python source
│   │   ├── main.py     # HTTP routes (thin layer)
│   │   ├── core/       # Core modules (required)
│   │   │   ├── work_module.py
│   │   │   ├── service_catalog_module.py
│   │   │   ├── documentation_module.py
│   │   │   ├── git_module.py
│   │   │   └── settings_module.py
│   │   ├── integrations/  # Optional integrations
│   │   │   └── monitoring/
│   │   ├── models.py   # Database models
│   │   ├── schemas.py  # Pydantic schemas
│   │   └── database.py # DB configuration
│   ├── templates/      # HTML templates
│   ├── static/         # CSS/JS
│   ├── data/           # SQLite database (gitignored)
│   ├── tests/          # Test suite ✅ NEW
│   │   ├── unit/      # Unit tests (40 tests)
│   │   └── integration/ # Integration tests (9 tests)
│   └── requirements.txt
├── docs/                # Documentation (in repo)
│   ├── ROADMAP.md
│   ├── SETUP_GUIDE.md
│   ├── PREREQUISITES.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_PATTERNS_GUIDE.md
│   ├── TESTING.md       # ✅ NEW
│   ├── CHANGES.md      # Local changes (tracked)
│   └── ...
├── infrastructure/      # Future: Deployed configs
└── README.md
```

### Future Considerations
- Infrastructure as Code (IaC) templates
- Docker Compose templates for common stacks
- Ansible playbooks integration
- Terraform module examples
- Kubernetes manifests

## Technical Debt / Improvements

- [x] Add automated tests (pytest) ← **COMPLETE**
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Database migrations (Alembic)
- [ ] API rate limiting
- [ ] Better error handling and logging
- [ ] Performance optimization for large datasets
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Security audit and hardening

## Architecture Evolution

### Phase 1: Initial Build ✅ (Complete)
- Basic FastAPI application
- SQLite database
- Git integration
- Work item tracking
- Service catalog

### Phase 2: Refactoring ✅ (Complete - November 2025)
- Three-layer architecture (HTTP/Service/Data)
- Core vs Integration separation
- Business logic extraction to modules
- Route simplification
- Module convenience methods
- Documentation alignment

### Phase 3: Testing & Quality ✅ (Complete - November 2025)
- Pytest infrastructure
- Core module tests (72% coverage)
- Integration tests (end-to-end workflows)
- Test fixtures and utilities
- Testing documentation

### Phase 4: Advanced Features (Q1 2026)
- [ ] Multi-user support
- [ ] Authentication/authorization
- [ ] Enhanced integrations
- [ ] Advanced monitoring
- [ ] CI/CD pipeline

## Testing Metrics

**Current Status (Phase 3 Complete):**
- **Total Tests:** 49
- **Unit Tests:** 40 (work_module: 17, service_catalog_module: 23)
- **Integration Tests:** 9 (full workflow validation)
- **Overall Coverage:** 72.63%
- **Core Module Coverage:**
  - work_module.py: 88%
  - service_catalog_module.py: 100%
  - git_module.py: 61.74%
  - documentation_module.py: 52.50%
- **Test Execution Time:** 0.93 seconds

**Quality Benchmarks:**
- ✅ Exceeds industry standard (70%+)
- ✅ Fast execution (< 1 second)
- ✅ Reliable fixtures (Git isolation)
- ✅ Integration tests validate real workflows

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose new features or contribute to this roadmap.

## Documentation

For detailed architecture information:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - High-level overview
- **[ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed patterns and best practices
- **[DEVELOPER_QUICK_REFERENCE.md](DEVELOPER_QUICK_REFERENCE.md)** - Daily development cheat sheet
- **[TESTING.md](TESTING.md)** - ✅ NEW: Testing patterns and best practices

---

**Last Updated**: November 25, 2025  
**Status**: Active development, Phase 3 complete  
**Next Milestone**: Phase 4 - Advanced Features (Multi-user, CI/CD)