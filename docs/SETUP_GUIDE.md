# Calcifer - Complete Setup Guide

This guide will walk you through setting up Calcifer, your infrastructure platform, from scratch.

## Before You Begin

**READ FIRST**: Review `docs/PREREQUISITES.md` to ensure you have all required software and accounts.

**Quick Checklist:**
- [ ] Windows 10/11 (1903+) OR Linux/macOS
- [ ] Git installed and configured
- [ ] Git account (GitHub/GitLab) - optional but recommended
- [ ] Python 3.11+ installed
- [ ] Visual Studio Code with WSL extension (Windows)
- [ ] WSL2 with Ubuntu 22.04 (Windows only)

If anything is missing, complete the prerequisites first.

---

## Part 1: WSL2 Setup (Windows Only)


### Step 1: Install WSL2

```powershell
# Open PowerShell as Administrator
wsl --install -d Ubuntu-22.04
```

**After installation:**
- System will restart
- Ubuntu terminal will open automatically
- Create username (lowercase, no spaces)
- Create password (save in KeePass!)

### Step 2: Launch WSL2

**Method 1 - Windows Terminal (Recommended):**
1. Press `Windows Key` → Search "Terminal"
2. Click dropdown arrow (˅) next to the + tab
3. Select "Ubuntu-22.04"

**Method 2 - Direct:**
1. Press `Windows Key` → Type "Ubuntu"
2. Click "Ubuntu 22.04" app

**Method 3 - Command Line:**
```powershell
wsl
```

**IMPORTANT - Verify You're Not Root:**

After launching, check:
```bash
whoami
# Should show your username (like 'gavin'), NOT 'root'
```

If it shows `root`, see the Troubleshooting section at the end of this guide.

### Step 3: Update Ubuntu

Once inside Ubuntu terminal:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git python3.11 python3-pip python3-venv curl wget nano vim
```

### Step 4: Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

### Step 5: Install VS Code WSL Extension

1. Open VS Code on Windows
2. Install extension: "WSL" (ms-vscode-remote.remote-wsl)
3. Restart VS Code

### Step 6: Open WSL in VS Code

In Ubuntu terminal:

```bash
# Create your workspace directory
mkdir -p ~/calcifer
cd ~/calcifer

# Open in VS Code
code .
```

This will:
- Install VS Code Server in WSL
- Open VS Code connected to WSL
- You'll see "WSL: Ubuntu-22.04" in bottom-left corner

### Step 7: Verify Setup

In VS Code terminal (should automatically be WSL Ubuntu):

```bash
# Check Python version
python3 --version  # Should show 3.11.x

# Check Git
git --version

# Check current directory
pwd  # Should be /home/yourusername/calcifer
```

**✅ Checkpoint: Screenshot your VS Code showing WSL connection and terminal working**

---

## Part 2: Create Repository

### Step 1: Initialize Git Repository

In VS Code terminal (WSL Ubuntu):

```bash
# Should be in ~/calcifer
git init
```

### Step 2: Create Directory Structure

```bash
mkdir -p calcifer-app/{src/{core,integrations/monitoring},templates,static/{css,js},data}
mkdir -p infrastructure/{docker-compose/{apps,platform},configs,scripts}
mkdir -p docs
mkdir -p .vscode
```

**Note:** This creates the Phase 2 architecture structure with `core/` and `integrations/` directories.

### Step 3: Create Essential Files

**Core Python Files:**

```bash
# Create __init__.py files for Python packages
touch calcifer-app/src/__init__.py
touch calcifer-app/src/core/__init__.py
touch calcifer-app/src/integrations/__init__.py
touch calcifer-app/src/integrations/monitoring/__init__.py

# Create static placeholders
touch calcifer-app/static/css/.gitkeep
touch calcifer-app/static/js/.gitkeep
```

**Create .gitignore:**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDEs
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
.idea/

# Database
*.db
*.sqlite
*.sqlite3
calcifer-app/data/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Secrets
*credentials*
*secrets*
!*-example.*
EOF
```

**Create Initial CHANGES.md:**

```bash
cat > docs/CHANGES.md << 'EOF'
# Change Log

All infrastructure changes are logged here.

## 2025-11-23 - Initial Setup
- Created Calcifer application
- Set up Phase 2 architecture (core modules + integrations)
- Configured development environment
EOF
```

### Step 4: Copy Application Files

You'll need to copy the complete Calcifer application files. These are available from:
- Your previous Calcifer installation
- Or from the project repository

**Required files to copy:**
- `calcifer-app/requirements.txt`
- `calcifer-app/src/database.py`
- `calcifer-app/src/models.py`
- `calcifer-app/src/schemas.py`
- `calcifer-app/src/main.py`
- All files in `calcifer-app/src/core/`
- All files in `calcifer-app/src/integrations/`
- All template files in `calcifer-app/templates/`

**Verification:**

```bash
# Verify these files exist
ls calcifer-app/requirements.txt
ls calcifer-app/src/main.py
ls calcifer-app/src/core/work_module.py
ls calcifer-app/src/integrations/monitoring/integration.py
ls docs/CHANGES.md
ls .gitignore

# If any are missing, copy them before continuing!
```

---

## Part 3: Set Up Python Environment

### Step 1: Create Virtual Environment

```bash
cd calcifer-app
python3 -m venv venv
```

### Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:** All packages installed successfully

### Step 4: Verify Installation

```bash
python -c "import fastapi; print(fastapi.__version__)"
# Should print: 0.109.0 or similar

python -c "import sqlalchemy; print('SQLAlchemy OK')"
# Should print: SQLAlchemy OK
```

---

## Part 4: Run Calcifer Locally (First Time)

### Step 1: Ensure You're in calcifer-app Directory

```bash
cd ~/calcifer/calcifer-app
source venv/bin/activate  # If not already activated
```

### Step 2: Set Environment Variables (Optional)

```bash
export DB_PATH="./data/calcifer.db"
export REPO_PATH=".."
```

### Step 3: Run the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4: Test the Application

**Option A - From WSL:**
```bash
curl http://localhost:8000
# Should return HTML
```

**Option B - From Windows Browser:**
1. Open browser
2. Go to: `http://localhost:8000`
3. You should see the Calcifer dashboard! 🔥

---

## Part 5: Feature Exploration Checklist

Test each feature to understand the workflow:

### Work Item Management
- [ ] Home page loads (http://localhost:8000)
- [ ] Click "New Work" in navbar
- [ ] Create a test work item:
  - Title: "Test Calcifer Setup"
  - Category: "Platform Feature"
  - Action Type: "New"
  - Description: "Testing the Calcifer application"
- [ ] Verify work item appears on home page
- [ ] Click on work item - detail page loads
- [ ] Notice the Git branch was auto-created

### Checklist & Notes
- [ ] Toggle checklist items - they save and persist
- [ ] Add notes in the notes section (bottom of page)
- [ ] Notes save correctly (up to 2000 characters)

### Git Commit Workflow
- [ ] Make a small change (edit notes again)
- [ ] Click "Commit Changes" button
- [ ] See current Git status displayed
- [ ] Fill out:
  - Commit message: "Test commit from new setup"
  - CHANGES.md entry: "Testing commit workflow"
- [ ] Click "Commit Changes"
- [ ] Verify commit appears in work item commit list

### Work Completion
- [ ] Complete all checklist items (check them off)
- [ ] Click "Merge & Complete" button
- [ ] See validation (all requirements must be met)
- [ ] Work item merges to main branch
- [ ] Work item marked as complete
- [ ] Redirects to home with success message

### Service Catalog
- [ ] Click "Services" in navbar
- [ ] See empty state (no services yet)
- [ ] Click "Add Service"
- [ ] Create test service:
  - Name: "Calcifer"
  - Type: "container"
  - Host: "localhost"
  - URL: "http://localhost:8000"
- [ ] Verify service appears in catalog

### Monitoring (Integration Feature)
- [ ] Click "Monitoring" in navbar (right side)
- [ ] See endpoint list (empty)
- [ ] Click "Add Endpoint"
- [ ] Create test endpoint:
  - Name: "router"
  - Type: "network"
  - Target: "10.66.33.1" (or your router IP)
  - Check interval: 60
- [ ] Endpoint created with work item
- [ ] Documentation auto-generated
- [ ] Initial health check performed

### Documentation Viewer
- [ ] Click "Docs" in navbar
- [ ] See list of documentation files
- [ ] Click on "PREREQUISITES.md"
- [ ] Markdown renders as HTML
- [ ] See "SETUP_GUIDE.md", "ARCHITECTURE.md", etc.

### Settings & Git Status
- [ ] Click "Settings" in navbar (right side)
- [ ] See application settings displayed
- [ ] Click "Git" in navbar (right side)
- [ ] See Git repository status
- [ ] See list of branches
- [ ] See recent commits

---

## Part 6: Commit Initial Setup

Once everything works:

```bash
# Make sure you're in the calcifer root directory
cd ~/calcifer

# Stage all files
git add .

# Create initial commit
git commit -m "Initial Calcifer setup - Phase 2 architecture"

# Check status
git status
# Should show: "nothing to commit, working tree clean"

# See what you've created
git log --oneline
# Should show your initial commit
```

---

## Part 7: Using VS Code Tasks (Optional but Recommended)

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac), then:

1. **Run Calcifer (Development)**
   - Type: "Run Task"
   - Select: "Run Calcifer (Development)"
   - This starts the server

2. **Open Calcifer Dashboard**
   - Type: "Run Task"
   - Select: "Open Calcifer Dashboard"
   - This opens browser automatically

---

## Understanding the Architecture

Now that Calcifer is running, review these documents to understand how it works:

1. **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - High-level overview of the 3-layer architecture
2. **[ARCHITECTURE_PATTERNS_GUIDE.md](../docs/ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed patterns for development
3. **[DEVELOPER_QUICK_REFERENCE.md](../docs/DEVELOPER_QUICK_REFERENCE.md)** - Daily cheat sheet

**Key Concepts:**
- **Core Modules** (`src/core/`) - Required functionality (work items, docs, git, etc.)
- **Integration Modules** (`src/integrations/`) - Optional enhancements (monitoring, etc.)
- **Routes** (`src/main.py`) - Thin HTTP layer, just calls modules
- **Models** (`src/models.py`) - Database schema

---

## Troubleshooting

### Issue: Logged in as root instead of regular user

**Symptoms:**
- `whoami` shows `root`
- Terminal prompt shows `root@...`
- Home directory is `/root` instead of `/home/username`

**This is a problem because:**
- Security risk (root has unlimited access)
- File permission issues
- Git commits have wrong ownership

**Solution:**

**Step 1: Create a regular user (if you don't have one)**

```bash
# While logged in as root in WSL
adduser gavin  # Replace 'gavin' with your username
usermod -aG sudo gavin
```

**Step 2: Set as default user**

In PowerShell as Administrator:

```powershell
wsl --shutdown
wsl --manage Ubuntu-22.04 --set-default-user gavin
```

**Step 3: Verify**

```bash
whoami  # Should show: gavin
echo $HOME  # Should show: /home/gavin
```

See [PREREQUISITES.md](PREREQUISITES.md) for complete troubleshooting steps.

---

### Issue: "Module not found" errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'core'
```

**Solution:**

1. Verify directory structure:
```bash
ls calcifer-app/src/core/
# Should show: __init__.py, work_module.py, etc.
```

2. Ensure __init__.py exists:
```bash
touch calcifer-app/src/core/__init__.py
```

3. Reinstall dependencies:
```bash
cd calcifer-app
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn src.main:app --reload --port 8001
```

---

### Issue: Database errors

**Solution:**
```bash
# Delete database and restart
rm -f calcifer-app/data/calcifer.db
# Restart application - database will be recreated
```

---

### Issue: Git operations failing

**Solution:**
```bash
# Make sure Git is configured
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Verify
git config --global --list
```

---

### Issue: Can't access from Windows browser

**Solution:**
```bash
# Check firewall - WSL2 uses network bridge
# In PowerShell (as Admin):
New-NetFirewallRule -DisplayName "WSL2 Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

## Next Steps

Once Calcifer is working locally:

### 1. Document Your Current Infrastructure
- Create work item: "Document Current Infrastructure"
- Add each VM to service catalog
- Add monitoring endpoints for critical infrastructure
- Document configurations in work item notes

### 2. Learn the Development Workflow
- Read [DEVELOPMENT.md](DEVELOPMENT.md)
- Review [ARCHITECTURE_PATTERNS_GUIDE.md](../docs/ARCHITECTURE_PATTERNS_GUIDE.md)
- Practice creating work items
- Practice the commit workflow

### 3. Explore Advanced Features
- Try creating different work item types
- Experiment with monitoring endpoints
- Set up Git remote (GitHub/GitLab)
- Review the Settings page

### 4. Deploy to Production (Future)
- Create work item: "Deploy Calcifer to Proxmox VM"
- Set up Docker Compose deployment
- Configure reverse proxy
- Set up automated backups

### 5. Start Your Roadmap
- Review [ROADMAP.md](../docs/ROADMAP.md)
- Prioritize features you need
- Create work items for each task
- Let Calcifer guide your workflow

---

## Summary - What You Should Have Now

- ✅ WSL2 with Ubuntu 22.04 (Windows) or Linux/macOS terminal
- ✅ Git configured with your identity
- ✅ VS Code with WSL extension (Windows)
- ✅ Python 3.11 virtual environment
- ✅ Calcifer application running locally
- ✅ Phase 2 architecture (core modules + integrations)
- ✅ All features tested and working
- ✅ Initial commit in Git
- ✅ Understanding of the workflow

**You're ready to use Calcifer!** 🔥

### Calcifer Will Help You:
- Never forget to document changes
- Manage Git branches automatically
- Keep service catalog current
- Update change log automatically
- Enforce best practices through the UI

---

## Questions or Issues?

If you encounter problems not covered here:

1. Check [DEVELOPMENT.md](DEVELOPMENT.md) for development-specific issues
2. Review [ARCHITECTURE_PATTERNS_GUIDE.md](../docs/ARCHITECTURE_PATTERNS_GUIDE.md) for code patterns
3. Create a work item in Calcifer: "Troubleshoot [Your Issue]"
4. Document the issue and solution in the work item notes
5. This becomes part of your knowledge base!

---

**Last Updated:** November 23, 2025  
**For:** Calcifer v2.0 (Phase 2 Architecture Complete)  
**Next Milestone:** Phase 3 - Testing Framework