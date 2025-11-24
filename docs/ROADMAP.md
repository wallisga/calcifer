# Calcifer Roadmap

Future enhancements and ideas for Calcifer.

## Recently Completed ✅

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

### Testing Framework
- [ ] Add pytest infrastructure
- [ ] Unit tests for core modules
- [ ] Integration tests for routes
- [ ] Mock Git operations for testing
- [ ] CI/CD pipeline setup

### Backup & Recovery
- [ ] Automated database backups
- [ ] Export/import functionality
- [ ] Backup to remote storage (S3, etc.)
- [ ] Restore from backup feature
- [ ] Configuration backup integration

## Medium Priority

### Logging & Observability Integration
**Status:** Foundation Complete, Integration Planned  
**Purpose:** Centralized log aggregation and monitoring

**Foundation Complete (Phase 3a):**
- ✅ Structured logging to stdout
- ✅ Module-level loggers
- ✅ JSON format support
- ✅ Container-friendly output

**Integration Features (Planned):**
- [ ] Grafana Loki integration
  - [ ] Promtail sidecar for log collection
  - [ ] Loki server setup
  - [ ] Grafana dashboards for log viewing
  - [ ] Log-based alerting
- [ ] Log retention policies
  - [ ] Automatic log rotation
  - [ ] Archive old logs to S3/object storage
  - [ ] Configurable retention periods
- [ ] Advanced log filtering
  - [ ] Filter by module
  - [ ] Filter by log level
  - [ ] Search across all logs
  - [ ] Correlation with work items
- [ ] Log-based metrics
  - [ ] Error rate tracking
  - [ ] Performance metrics from logs
  - [ ] Work item completion timing
  - [ ] Git operation duration

**Alternative Options:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- CloudWatch (if running on AWS)
- Papertrail (hosted solution)
- Self-hosted Graylog

**Prerequisites:**
- [ ] Logging foundation (✅ Complete)
- [ ] Docker deployment
- [ ] Monitoring infrastructure

---

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
│   └── requirements.txt
├── docs/                # Documentation (in repo)
│   ├── ROADMAP.md
│   ├── SETUP_GUIDE.md
│   ├── PREREQUISITES.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_PATTERNS_GUIDE.md
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

- [ ] Add automated tests (pytest) ← **HIGH PRIORITY**
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

### Phase 3: Testing & Quality (Next - December 2025)
- [ ] Pytest infrastructure
- [ ] Core module tests
- [ ] Integration tests
- [ ] CI/CD pipeline
- [ ] Code coverage reporting

### Phase 4: Advanced Features (Q1 2026)
- [ ] Multi-user support
- [ ] Authentication/authorization
- [ ] Enhanced integrations
- [ ] Advanced monitoring

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose new features or contribute to this roadmap.

## Documentation

For detailed architecture information:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - High-level overview
- **[ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed patterns and best practices
- **[DEVELOPER_QUICK_REFERENCE.md](DEVELOPER_QUICK_REFERENCE.md)** - Daily development cheat sheet

---

**Last Updated**: November 23, 2025  
**Status**: Active development, Phase 2 complete  
**Next Milestone**: Phase 3 - Testing Framework