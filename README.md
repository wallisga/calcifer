# Calcifer

Infrastructure platform powering your continuously changing systems

## 📚 Documentation

- **[Prerequisites](docs/PREREQUISITES.md)** - System requirements and dependencies (READ FIRST)
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete step-by-step setup instructions
- **[Roadmap](docs/ROADMAP.md)** - Current and planned features
- **[Change Log](docs/CHANGES.md)** - All infrastructure changes

## Quick Start

### Before You Begin
Review [docs/PREREQUISITES.md](docs/PREREQUISITES.md) to ensure you have:
- Git installed and configured
- Python 3.11+
- VS Code (with WSL extension if on Windows)
- WSL2 with Ubuntu 22.04 (Windows only)

### Local Development

1. Set up Python environment:
```bash
   cd calcifer-app
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

2. Run the application:
```bash
   uvicorn src.main:app --reload
```

3. Open browser: http://localhost:8000

### Using VS Code

1. Open this folder in VS Code
2. Press `Ctrl+Shift+P` → "Run Task" → "Setup Python Virtual Environment"
3. Press `Ctrl+Shift+P` → "Run Task" → "Run Calcifer (Development)"
4. Press `Ctrl+Shift+P` → "Run Task" → "Open Calcifer Dashboard"

### Using Docker
```bash
cd calcifer-app
docker-compose up -d
```

Access at: http://localhost:8000

## Repository Structure
```
calcifer/
├── calcifer-app/         # Calcifer application
│   ├── src/             # FastAPI application code
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # CSS/JS assets
│   └── data/            # SQLite database (gitignored)
├── infrastructure/       # Deployed infrastructure configs
│   ├── docker-compose/  # Docker Compose stacks
│   ├── configs/         # Configuration files
│   └── scripts/         # Automation scripts
├── docs/                # Documentation and change logs
└── .vscode/             # VS Code workspace settings
```

## Workflow

1. **Start New Work**: Use Calcifer dashboard to create work item
2. **Work on Branch**: Automatic Git branch creation
3. **Commit Changes**: Use UI button to commit with CHANGES.md
4. **Complete Checklist**: Track progress with built-in checklists
5. **Merge & Complete**: One button validates, merges, and closes work

## Features

- 🔥 **Work Item Tracking** - Never lose track of what you're working on
- 📋 **Service Catalog** - Central registry of all deployed services
- 🌿 **Git Integration** - Automatic branch management and merge workflow
- 📝 **Enforced Documentation** - CHANGES.md updated via UI
- 📊 **Built-in Docs Viewer** - Renders markdown beautifully
- ✅ **Smart Checklists** - Task-specific guidance by work type
- 💾 **Commit from UI** - Stage changes and update docs in one click
- 🗑️ **Branch Cleanup** - Delete work items and branches together

## Current Status

**Phase**: Private development
**Version**: 1.0.0-alpha
**Database**: SQLite (stored in `calcifer-app/data/`)

## Links

- Calcifer Dashboard: http://localhost:8000
- Documentation: http://localhost:8000/docs-viewer
- Proxmox: https://proxmox-ip:8006 (when deployed)
- Portainer: http://services-ip:9000 (when deployed)

## Future Plans

See [docs/ROADMAP.md](docs/ROADMAP.md) for upcoming features including:
- Service monitoring integration
- Backup automation
- Multi-user support
- Advanced reporting

## License

MIT (or your choice when going public)