# Development Setup

Guide for setting up Calcifer for local development.

## Prerequisites

See [PREREQUISITES.md](PREREQUISITES.md) for system requirements.

**Quick checklist:**
- Python 3.11+
- Git
- VS Code (recommended)

## Setup from Git Clone

### 1. Clone Repository
```bash
git clone git@github.com:yourusername/calcifer.git
cd calcifer
```

### 2. Set Up Python Environment
```bash
cd calcifer-app
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Initialize Local Documentation

The repo includes template documentation, but local changes are git-ignored:
```bash
cd ..
# docs/CHANGES.md will be created automatically by Calcifer
# You can also create it manually:
cat > docs/CHANGES.md << 'EOF'
# Change Log

## $(date +%Y-%m-%d) - $(git config user.name)
- Initial local setup
EOF
```

### 4. Run Calcifer
```bash
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open: http://localhost:8000

### 5. Make Initial Commit (If Needed)

If this is a fresh repo without commits:
```bash
cd ~/calcifer
git add .
git commit -m "Initial setup"
```

## Development Workflow

### Using VS Code

Open the repository in VS Code:
```bash
code ~/calcifer
```

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (for Python intellisense)
- GitLens (for Git integration)

**VS Code Tasks:**

Press `Ctrl+Shift+P` → "Run Task":
- "Run Calcifer (Development)" - Starts the server
- "Open Calcifer Dashboard" - Opens browser

### File Structure
```
calcifer/
├── calcifer-app/           # Application code
│   ├── src/               # Python source
│   │   ├── main.py       # FastAPI routes
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # API schemas
│   │   └── ...
│   ├── templates/        # HTML templates
│   ├── static/           # CSS/JS (currently minimal)
│   ├── data/             # SQLite database (git-ignored)
│   └── requirements.txt  # Python dependencies
├── docs/                 # Documentation
├── infrastructure/       # Deployment configs (future)
└── README.md
```

### Making Changes

1. **Create work item in Calcifer UI** → auto-creates branch
2. **Make code changes**
3. **Test locally**
4. **Update docs/CHANGES.md** (Calcifer will remind you)
5. **Commit and push**

### Database

Calcifer uses SQLite stored in `calcifer-app/data/calcifer.db`.

**To inspect:**
```bash
cd calcifer-app
sqlite3 data/calcifer.db

.tables
SELECT * FROM work_items;
.quit
```

**To reset (fresh start):**
```bash
rm -f calcifer-app/data/calcifer.db
# Restart Calcifer - database will be recreated
```

## Common Issues

### Port 8000 in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Import errors
```bash
cd calcifer-app
source venv/bin/activate
pip install -r requirements.txt
```

### Database errors
```bash
rm -f calcifer-app/data/calcifer.db
# Restart - fresh database
```

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Check [ROADMAP.md](ROADMAP.md) for planned features
- Start building! 🔥