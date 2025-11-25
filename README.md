# 🔥 Calcifer

**Your Infrastructure Platform for Documentation, Change Tracking, and Service Management**

Calcifer is a self-hosted web application that enforces infrastructure best practices by making documentation, change tracking, and service management part of your natural workflow.

## What is Calcifer?

Calcifer helps you maintain your homelab or infrastructure by:

- **Tracking every change** through work items with automatic Git branching
- **Enforcing documentation** before changes can be completed
- **Managing your service catalog** with detailed configuration tracking
- **Monitoring endpoints** with health checks and documentation
- **Maintaining a change log** automatically via the UI
- **Integrating with Git** to version control everything

**Philosophy:** No change without a work item. No completion without documentation. Everything in Git.

## Key Features

### Work Item Management
- Create work items that automatically create Git branches
- Context-aware checklists based on work type
- Enforce documentation and change log updates
- Merge and complete with validation

### Git Integration
- Automatic branch creation and management
- Commit directly from the UI with CHANGES.md updates
- Branch merge status tracking
- Commit history per work item

### Service Catalog
- Track all infrastructure services (VMs, containers, bare metal)
- Document configuration, resources, and dependencies
- Link services to monitoring and documentation

### Endpoint Monitoring
- ICMP, TCP, HTTP/HTTPS health checks
- Automatic documentation generation
- Status tracking and history
- Create endpoints with full work item workflow

### Documentation Management
- Markdown documentation with built-in viewer
- Auto-generate docs for services and endpoints
- Integrated change log (CHANGES.md)
- Search and browse all documentation

## Architecture

Calcifer uses a clean three-layer architecture:

```
┌─────────────────────────────────────┐
│  HTTP/UI Layer (main.py)            │
│  - Routes (thin, <20 lines)         │
│  - Request/response handling        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Service Layer                      │
│  - Core modules (required)          │
│  - Integration modules (optional)   │
│  - Business logic                   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Data Layer                         │
│  - SQLite database                  │
│  - SQLAlchemy ORM                   │
└─────────────────────────────────────┘
```

**Core Modules** (Required):
- `work_module` - Work item management
- `service_catalog_module` - Service tracking
- `documentation_module` - Docs and change logs
- `git_module` - Local Git operations
- `settings_module` - Configuration

**Integration Modules** (Optional):
- `monitoring` - Endpoint health checks

## Quick Start

### Prerequisites

- Python 3.11+
- Git
- Linux, macOS, or Windows with WSL2

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/calcifer.git
cd calcifer

# Set up Python environment
cd calcifer-app
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run Calcifer
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

### First Steps

1. Create your first work item: "Document Current Infrastructure"
2. Add services to the service catalog
3. Set up monitoring endpoints for critical systems
4. Complete your first work item (enforces documentation!)

## Project Structure

```
calcifer/
├── calcifer-app/           # Application code
│   ├── src/
│   │   ├── main.py        # HTTP routes
│   │   ├── core/          # Core modules (required)
│   │   ├── integrations/  # Integration modules (optional)
│   │   ├── models.py      # Database models
│   │   └── database.py    # Database config
│   ├── templates/         # Jinja2 HTML templates
│   ├── static/            # CSS/JS assets
│   ├── data/              # SQLite database (gitignored)
│   └── requirements.txt   # Python dependencies
│
├── docs/                  # Documentation
│   ├── SETUP_GUIDE.md              # Complete setup instructions
│   ├── PREREQUISITES.md            # System requirements
│   ├── ARCHITECTURE.md             # Architecture overview
│   ├── ARCHITECTURE_PATTERNS_GUIDE.md  # Development patterns
│   ├── DEVELOPER_QUICK_REFERENCE.md    # Daily dev reference
│   ├── DEVELOPMENT.md              # Development workflow
│   ├── ROADMAP.md                  # Future plans
│   └── CHANGES.md                  # Change log (tracked in Git)
│
└── README.md              # This file
```

## Documentation Guide

### For Users (Getting Started)

1. **[PREREQUISITES.md](docs/PREREQUISITES.md)** - System requirements and dependencies
2. **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Complete installation and setup
3. **[ROADMAP.md](docs/ROADMAP.md)** - Features and future plans

### For Developers (Contributing)

1. **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - High-level architecture overview
2. **[ARCHITECTURE_PATTERNS_GUIDE.md](docs/ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed development patterns
3. **[DEVELOPER_QUICK_REFERENCE.md](docs/DEVELOPER_QUICK_REFERENCE.md)** - Daily development cheat sheet
4. **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development workflow and setup

### Key Concepts

**Start here if you're new:**
- Read `PREREQUISITES.md` to check requirements
- Follow `SETUP_GUIDE.md` to install
- Review `ARCHITECTURE.md` to understand the system

**For developers:**
- Read `ARCHITECTURE_PATTERNS_GUIDE.md` for coding patterns
- Keep `DEVELOPER_QUICK_REFERENCE.md` handy while coding
- Follow `DEVELOPMENT.md` for workflow

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates with Bootstrap 5
- **Version Control**: Git (GitPython)
- **Deployment**: Docker Compose (planned)

## Current Status

**Version**: 2.0 (Phase 2 Complete)  
**Status**: Active Development  
**Last Updated**: November 23, 2025

### Recently Completed (Phase 2)
✅ Complete architecture refactoring  
✅ Core vs Integration separation  
✅ All routes under 20 lines  
✅ Business logic in modules  
✅ Git commit workflow with CHANGES.md enforcement  
✅ Endpoint monitoring integration  
✅ Documentation system

### Next Up (Phase 3)
🔄 Testing framework (pytest)  
🔄 CI/CD pipeline  
🔄 Enhanced integrations  

See [ROADMAP.md](docs/ROADMAP.md) for complete feature list.

## Use Cases

### Homelab Management
- Track VM configurations and changes
- Monitor critical services
- Document network architecture
- Maintain change history

### Team Infrastructure
- Enforce documentation standards
- Track service dependencies
- Monitor uptime and health
- Maintain audit trail

### Learning Platform
- Document learning experiments
- Track configuration changes
- Practice infrastructure as code
- Build a knowledge base

## Philosophy & Rules

Calcifer enforces these rules through the UI:

1. **No changes without a work item** - Every change gets tracked
2. **Branch per work item** - Automatic Git workflow
3. **Documentation required** - Can't complete without notes
4. **Change log mandatory** - CHANGES.md updated via UI
5. **Validation before merge** - All requirements checked

These rules help you maintain clean, documented infrastructure that future you will appreciate.

## Screenshots

*Coming soon - UI screenshots showing work items, service catalog, monitoring, etc.*

## Contributing

Contributions are welcome! Please:

1. Read [ARCHITECTURE_PATTERNS_GUIDE.md](docs/ARCHITECTURE_PATTERNS_GUIDE.md)
2. Follow the established patterns
3. Create a work item for your change
4. Document thoroughly
5. Submit a pull request

## License

*License to be determined*

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Create a work item in Calcifer to track it!
- **Questions**: Review the documentation first

## Acknowledgments

Calcifer is inspired by the need for enforced documentation and change tracking in infrastructure management. Named after the fire demon from Howl's Moving Castle, it keeps your infrastructure castle running smoothly.

---

**Remember**: Good documentation today saves hours of debugging tomorrow. Calcifer makes sure you never skip the documentation step. 🔥
