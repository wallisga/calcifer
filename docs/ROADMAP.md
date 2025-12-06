# Calcifer Roadmap

Future enhancements and ideas for Calcifer.

---

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
- ✅ Core vs Integration separation
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

### Developer Tools
- ✅ Git sync tool for multi-machine development
- ✅ TOOLS.md documentation
- ✅ Multi-machine workflow documentation

---

## Phase 4: Production Deployment & Multi-Service Management (Current - Q1 2026)

**Goal:** Deploy Calcifer to production and enable management of multiple services

**Status:** 🔄 In Progress

### 4a: Foundation & Structure
- [ ] Repository restructure (monorepo with independent Git per service)
- [ ] Update git_module for multi-repo support
- [ ] Service model enhancements (git_repo_path, docs_path, deployed_version)
- [ ] Link work items to specific services
- [ ] Service-specific Git operations

### 4b: Deployment & Production
- [ ] Deploy Calcifer to Proxmox VM (10.66.33.112:8000)
- [ ] Docker Compose deployment configuration
- [ ] Reverse proxy setup (Nginx/Caddy)
- [ ] Automated backup system
- [ ] Service deployment tracking

### 4c: Service Management
- [ ] Service creation automation (from templates)
- [ ] Deploy WireGuard VPN as first managed service
- [ ] Service health monitoring integration
- [ ] Service dependency tracking
- [ ] Per-service CHANGES.md management

---

## Phase 5: IDE Integration & Developer Experience (Q2 2026)

**Goal:** Provide seamless IDE integration and developer tooling

**Status:** 🔄 Planned

### IDE Integration Framework
- [ ] Create `src/integrations/ide/` framework
- [ ] Base IDE integration class
- [ ] Install/uninstall script system
- [ ] Integration discovery and registration

### VS Code Integration
- [ ] `.vscode/` template generator
- [ ] Workspace settings auto-configuration
- [ ] Recommended extensions installer
- [ ] Task definitions (run server, run tests, format)
- [ ] Launch configurations (debug server, debug tests)
- [ ] Code snippets (module templates, route templates, test templates)
- [ ] Install script: `tools/setup-vscode.sh`

### PyCharm Integration
- [ ] `.idea/` template generator
- [ ] Run configurations
- [ ] Code style settings
- [ ] Install script: `tools/setup-pycharm.sh`

### Development Tools Expansion
- [ ] Pre-commit hooks installer
- [ ] Code formatter wrapper (black, isort)
- [ ] Linter configuration (flake8, pylint)
- [ ] Development environment validator
- [ ] Test runner with coverage reports

**Note:** IDE tooling will be implemented as **integrations**, not services in the service catalog. This keeps the service catalog focused on infrastructure while providing optional developer enhancements.

---

## High Priority

### Testing Improvements
- [ ] Add pytest to work item checklists (require tests for new features)
- [ ] Set up pre-commit hooks for test execution
- [ ] Add coverage threshold enforcement (--cov-fail-under=70)
- [ ] Add test coverage badges to README
- [ ] Improve git_module and documentation_module coverage (currently 61%, 52%)

### Service Catalog Enhancements
- [x] Link services to Git repositories (Phase 4)
- [ ] Link services to monitoring dashboards (Uptime Kuma, Grafana)
- [ ] Auto-detect services from docker-compose files
- [ ] Service dependency graph visualization
- [ ] Service deployment history tracking
- [ ] Health check integration from monitoring

### Documentation
- [x] Developer tools documentation (TOOLS.md)
- [x] Multi-machine workflow documentation
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

---

## Medium Priority

### Advanced Git Features
- [ ] Compare branches visually
- [ ] Visual diff viewer
- [ ] Merge conflict detection and resolution
- [ ] Create Pull Request button (for GitHub/GitLab integrations)
- [ ] Git remote push/pull operations from UI

### Integrations Framework
- [x] IDE integration framework (Phase 5)
- [ ] Plugin system for custom integrations
- [ ] Integration marketplace/catalog
- [ ] OAuth support for third-party services
- [ ] Webhook system for automation
- [ ] Integration enable/disable toggles in UI

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
- [ ] Comments/discussion threads on work items
- [ ] Notifications (email, Slack, Discord)
- [ ] Real-time collaboration features

---

## Low Priority / Future Ideas

### UI/UX
- [ ] Dark mode
- [ ] Customizable themes (beyond current red theme)
- [ ] Dashboard widgets (customizable home page)
- [ ] Mobile-responsive improvements
- [ ] Keyboard shortcuts
- [ ] Drag-and-drop checklist reordering
- [ ] Inline editing for work item fields

### Reporting & Analytics
- [ ] Work item velocity metrics
- [ ] Time tracking per work item
- [ ] Infrastructure change frequency graphs
- [ ] Service uptime reports
- [ ] Burndown charts
- [ ] Custom dashboards
- [ ] Export reports (PDF, CSV)

### Advanced Work Item Features
- [ ] Work item templates (create from template)
- [ ] Sub-tasks / nested work items
- [ ] Work item relationships (blocks, depends on)
- [ ] Tags and labels
- [ ] Work item search and advanced filters
- [ ] Bulk operations on work items
- [ ] Work item cloning

### Technical Debt / Improvements
- [ ] API rate limiting
- [ ] Better error handling and logging
- [ ] Performance optimization for large datasets
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Security audit and hardening
- [ ] Database migrations (Alembic)
- [ ] Move to PostgreSQL option (keep SQLite default)

---

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

### Phase 4: Production Deployment 🔄 (Current - Q1 2026)
- Multi-service management
- Repository restructuring
- Service-linked work items
- Production deployment
- Service automation

### Phase 5: IDE Integration 🔄 (Planned - Q2 2026)
- IDE integration framework
- VS Code integration
- PyCharm integration
- Developer tools expansion
- Enhanced developer experience

### Phase 6: Multi-User & Collaboration (Q3 2026)
- Authentication/authorization
- Multi-user support
- RBAC (Role-Based Access Control)
- Comments and discussions
- Notifications
- CI/CD pipeline integration

---

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

**Phase 4 Goals:**
- Increase git_module coverage to 75%+
- Increase documentation_module coverage to 70%+
- Add service-linking integration tests
- Maintain < 1 second execution time

---

## Repository Structure

### Current State (Phase 3) ✅
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
│   ├── ROADMAP.md      # This file
│   ├── SETUP_GUIDE.md
│   ├── PREREQUISITES.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_PATTERNS_GUIDE.md
│   ├── DEVELOPER_QUICK_REFERENCE.md
│   ├── DEVELOPMENT.md  # Updated for multi-machine workflow
│   ├── TESTING.md
│   ├── TOOLS.md        # ✅ NEW Developer utilities
│   ├── CHANGES.md      # Local changes (tracked)
│   └── ...
├── tools/               # ✅ NEW Developer scripts
│   └── git-sync.sh     # Multi-machine sync tool
└── README.md
```

### Future (Phase 4) - Monorepo Structure
```
~/calcifer/                      # Root directory (no .git)
├── calcifer-app/               # Calcifer service
│   ├── .git/                  # Independent Git repo
│   ├── docs/                  # Service-specific docs
│   ├── src/
│   └── ...
├── wireguard-vpn/             # VPN service (example)
│   ├── .git/                  # Independent Git repo
│   ├── docs/                  # Service-specific docs
│   └── docker-compose.yml
├── customer-portal/           # App service (example)
│   ├── .git/                  # Independent Git repo
│   ├── docs/                  # Service-specific docs
│   └── ...
└── infrastructure/            # Shared infrastructure configs
    ├── terraform/
    ├── ansible/
    └── docker-compose/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose new features or contribute to this roadmap.

## Documentation

For detailed architecture information:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - High-level overview
- **[ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed patterns and best practices
- **[DEVELOPER_QUICK_REFERENCE.md](DEVELOPER_QUICK_REFERENCE.md)** - Daily development cheat sheet
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development workflow and multi-machine setup
- **[TESTING.md](TESTING.md)** - Testing patterns and best practices
- **[TOOLS.md](TOOLS.md)** - Developer utilities and scripts

---

**Last Updated**: December 6, 2025  
**Status**: Active development, Phase 4 starting  
**Current Milestone**: Repository restructure and production deployment  
**Next Milestone**: IDE integration framework (Phase 5)