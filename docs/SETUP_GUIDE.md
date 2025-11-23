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

## Part 1: WSL2 Setup (Windows)

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
mkdir -p calcifer-app/{src,templates,static/{css,js},data}
mkdir -p infrastructure/{docker-compose/{apps,platform},configs,scripts}
mkdir -p docs
mkdir -p .vscode
```

### Step 3: Create Files

**IMPORTANT:** You need to create these files BEFORE proceeding to Python setup. Copy the content from each artifact (shown at the end of the previous conversation) into these files.

**Core Application Files (Create These First):**

```bash
# Create empty __init__.py
touch calcifer-app/src/__init__.py

# Create static placeholders
touch calcifer-app/static/css/.gitkeep
touch calcifer-app/static/js/.gitkeep
```

**Essential Files to Create Now (copy from artifacts):**

1. **calcifer-app/requirements.txt** - [From artifact: `idp_requirements`]
   ```bash
   nano calcifer-app/requirements.txt
   # Copy content from artifact, save with Ctrl+X, Y, Enter
   ```

2. **docs/CHANGES.md**
   ```bash
   cat > docs/CHANGES.md << 'EOF'
# Change Log

All infrastructure changes are logged here.

## 2024-11-22 - Initial Setup
- Created Calcifer application
- Set up repository structure
- Configured development environment
EOF
   ```

3. **.gitignore**
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

**Option A - Manual File Creation (Recommended for Learning):**

Create each file by copying from the artifacts listed below:
- `calcifer-app/src/database.py` - [From artifact: `idp_database`]
- `calcifer-app/src/models.py` - [From artifact: `idp_models`]
- `calcifer-app/src/schemas.py` - [From artifact: `idp_schemas`]
- `calcifer-app/src/git_integration.py` - [From artifact: `idp_git_integration`]
- `calcifer-app/src/main.py` - [From artifact: `idp_main_app`]
- All template files in `calcifer-app/templates/`
- VS Code settings in `.vscode/`

**Option B - Quick Start Script (Faster):**

If you want to speed this up, I can provide a script that creates all files at once. Let me know if you'd prefer this approach.

**Verification Before Continuing:**

```bash
# Verify these files exist before moving to Part 3:
ls calcifer-app/requirements.txt
ls calcifer-app/src/database.py
ls calcifer-app/src/main.py
ls docs/CHANGES.md
ls .gitignore

# If any are missing, create them before continuing!
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
# Should print: 0.109.0
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
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

**Option B - From Windows Browser:**
1. Open browser
2. Go to: `http://localhost:8000`
3. You should see the Calcifer dashboard! 🔥

---

## Part 5: Initial Testing Checklist

Test each feature:

- [ ] Home page loads (http://localhost:8000)
- [ ] Click "Start New Work" - form appears
- [ ] Create a test work item:
  - Title: "Test Calcifer Setup"
  - Type: "Troubleshooting"
  - Description: "Testing the Calcifer application"
- [ ] Verify work item appears on home page
- [ ] Click on work item - detail page loads
- [ ] Toggle checklist items - they save and persist
- [ ] Add notes in the notes section - saves correctly
- [ ] Click "Commit Changes" button:
  - Shows current Git status
  - Fill out commit message and CHANGES.md entry
  - Commits successfully
- [ ] Verify commit appears in work item commit list
- [ ] Complete all checklist items
- [ ] Click "Merge & Complete":
  - Validates all requirements
  - Merges branch to main
  - Completes work item
  - Redirects to home with success message
- [ ] Go to Services page - empty state shows
- [ ] Click "Add Service" - form appears
- [ ] Create test service:
  - Name: "Calcifer"
  - Type: "container"
  - Host: "localhost"
  - URL: "http://localhost:8000"
- [ ] Verify service appears in catalog
- [ ] Click "Docs" in navbar
- [ ] See PREREQUISITES.md, SETUP_GUIDE.md, CHANGES.md, ROADMAP.md
- [ ] Click to view rendered documentation

---

## Part 6: Commit Initial Setup

Once everything works:

```bash
# Make sure you're in the calcifer root directory
cd ~/calcifer

# Stage all files
git add .

# Create initial commit
git commit -m "Initial Calcifer setup - application structure and configuration"

# Check status
git status
# Should show: "nothing to commit, working tree clean"
```

---

## Part 7: Using VS Code Tasks (Optional but Recommended)

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac), then:

1. **Setup Python Virtual Environment**
   - Type: "Run Task"
   - Select: "Setup Python Virtual Environment"
   - This automates Part 3

2. **Run Calcifer (Development)**
   - Type: "Run Task"
   - Select: "Run Calcifer (Development)"
   - This starts the server

3. **Open Calcifer Dashboard**
   - Type: "Run Task"
   - Select: "Open Calcifer Dashboard"
   - This opens browser automatically

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
- Best practice is to use regular user with sudo when needed

**Solution:**

**Step 1: Create a regular user (if you don't have one)**

While logged in as root in WSL:
```bash
# Create user (replace 'gavin' with your desired username - lowercase, no spaces)
adduser gavin

# Follow prompts:
# - Set password (save in KeePass!)
# - Press Enter through the rest (optional info)

# Add user to sudo group (required for admin tasks)
usermod -aG sudo gavin

# Verify user exists
id gavin
# Should show: uid=1000(gavin) gid=1000(gavin) groups=1000(gavin),27(sudo)
```

**Step 2: Set as default user**

In **PowerShell as Administrator**, try these commands in order until one works:

```powershell
# First, shut down WSL
wsl --shutdown

# Check your distribution name
wsl --list --verbose
# Note the exact name (e.g., "Ubuntu-22.04", "Ubuntu", etc.)

# Try method 1:
wsl --set-default-user gavin

# If that fails, try method 2 (MOST LIKELY TO WORK):
wsl --manage Ubuntu-22.04 --set-default-user gavin

# If that fails, try method 3:
ubuntu2204 config --default-user gavin

# If that fails, try method 4:
ubuntu config --default-user gavin

# If that fails, try method 5:
ubuntu.exe config --default-user gavin
```

**Step 3: Restart everything**

```powershell
# In PowerShell
wsl --shutdown

# Wait 10 seconds, then open Ubuntu app directly
# (NOT through VS Code yet)
```

**Step 4: Verify**

In Ubuntu terminal:
```bash
whoami
# Should show: gavin (or your username)

echo $HOME
# Should show: /home/gavin

# Test sudo access
sudo whoami
# Enter your password
# Should show: root
```

**Step 5: Fix VS Code (if still showing root)**

If VS Code still connects as root:

1. Close VS Code completely
2. Press `Windows Key + R`, type: `%APPDATA%\Code\User\settings.json`, press Enter
3. Look for: `"remote.WSL.defaultUser": "root"`
4. Change to: `"remote.WSL.defaultUser": "gavin"` (or remove the line)
5. Save and close
6. Open VS Code, connect to WSL
7. Verify: Terminal should now show `gavin@...`

**Step 6: Reconfigure Git as your user**

```bash
# Run these as your regular user (NOT root)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main

# Verify
git config --global --list
```

**Step 7: Regenerate SSH key as your user**

If you created SSH key as root, regenerate:

```bash
# Check current SSH keys
ls -la ~/.ssh/

# If empty or you want to regenerate
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for default location
# Set passphrase (optional but recommended)

# Display public key
cat ~/.ssh/id_ed25519.pub
# Copy this entire output
```

Add to GitHub: https://github.com/settings/keys → "New SSH Key"

**Nuclear Option (if nothing works):**

```powershell
# In PowerShell as Administrator
# WARNING: This deletes your WSL installation
wsl --unregister Ubuntu-22.04

# Reinstall
wsl --install -d Ubuntu-22.04
# This time, it WILL prompt you to create a user
# Create your user when prompted
```

---

### Issue: "Module not found" errors

**Solution:**
```bash
cd calcifer-app
source venv/bin/activate
pip install -r requirements.txt
```

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

### Issue: Database errors

**Solution:**
```bash
# Delete database and restart
rm -f calcifer-app/data/calcifer.db
# Restart application - database will be recreated
```

### Issue: Git operations failing

**Solution:**
```bash
# Make sure Git is configured
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

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

1. **Document Your Current Infrastructure**
   - Use Calcifer to create work item: "Document Current Infrastructure"
   - Add each existing VM to service catalog
   - Document configurations

2. **Deploy Calcifer to Proxmox VM**
   - Create work item: "Deploy Calcifer to services VM"
   - Use Docker Compose deployment
   - Access from your network

3. **Start Your Roadmap**
   - VPN migration
   - File sharing setup
   - Monitoring implementation

---

## Summary - What You Should Have Now

- ✅ WSL2 with Ubuntu 22.04
- ✅ Git configured
- ✅ VS Code with WSL extension
- ✅ Python 3.11 virtual environment
- ✅ Calcifer application running locally
- ✅ Tested all features
- ✅ Initial commit in Git

**You're ready to start using Calcifer!** 🔥

Calcifer will now enforce your workflow:
- No more forgotten documentation
- Automatic Git branch management
- Service catalog stays current
- Change log updated automatically

---

## Questions?

If you encounter issues not covered here, document them in Calcifer as a new work item titled "Calcifer Setup Issues" - this becomes part of your knowledge base!