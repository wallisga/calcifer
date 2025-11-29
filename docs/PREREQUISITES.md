# Prerequisites & Dependencies

This document lists all requirements for setting up and running Calcifer.

## System Requirements

### Hardware
- **Minimum**: 2GB RAM, 2 CPU cores, 10GB disk space
- **Recommended**: 4GB RAM, 4 CPU cores, 20GB disk space
- Applies to: Development machine and any VM running Calcifer

### Operating Systems

**Development Machine (where you'll build/test):**
- **Windows 10/11** (version 1903 or higher) - for WSL support
  - OR **Linux** (Ubuntu 20.04+, Debian 11+, any modern distro)
  - OR **macOS** (10.15+)

**Deployment Target (Proxmox VMs):**
- **Debian 11 or 12** (recommended)
- **Ubuntu 22.04 LTS** (alternative)

---

## Required Software

### 1. Git

**Purpose**: Version control for all infrastructure code and documentation

**Installation:**

**Windows (via WSL):**
```bash
sudo apt install git
```

**Linux:**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

**Verification:**
```bash
git --version
# Should show: git version 2.x.x
```

**Configuration Required:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

---

### 2. Git Hosting Account (Optional but Recommended)

**Purpose**: Remote backup and collaboration

**Options:**
- **GitHub** (https://github.com) - Free tier includes unlimited private repos
- **GitLab** (https://gitlab.com) - Free tier, can also self-host
- **Gitea** (self-hosted) - Lightweight option

**Recommendation**: Start with GitHub free tier, migrate to self-hosted Gitea later if desired.

**Account Setup:**
1. Create account at chosen provider
2. Generate SSH key (if not already done):
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   cat ~/.ssh/id_ed25519.pub  # Copy this
   ```
3. Add SSH key to your Git provider account settings

---

### 3. Python 3.10+

**Purpose**: Calcifer application runtime

**Tested Versions**:
- ✅ **Python 3.10** (Ubuntu 22.04 default)
- ✅ **Python 3.11** (Recommended)
- ✅ **Python 3.12** (Should work, not extensively tested)

**Minimum Version**: Python 3.10

**Why 3.10+?**
- FastAPI 0.109+ requires Python 3.8+
- Pydantic 2.x requires Python 3.8+
- SQLAlchemy 2.x requires Python 3.7+
- **Tested on Python 3.10** (Ubuntu 22.04 default)
- Modern Python features and performance improvements

**Note**: While dependencies technically support Python 3.8+, Calcifer is developed and tested on Python 3.10+. Earlier versions may work but are not officially supported.

---

**Installation:**

**Ubuntu 22.04 (Recommended):**
```bash
# Python 3.10 comes pre-installed
python3 --version
# Should show: Python 3.10.x

# Install venv and pip
sudo apt install python3.10-venv python3-pip -y
```

**Ubuntu 20.04:**
```bash
# Python 3.8 comes pre-installed
# For Python 3.10 or 3.11, add deadsnakes PPA:
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip -y
# OR
sudo apt install python3.11 python3.11-venv python3-pip -y
```

**macOS:**
```bash
brew install python@3.10
# OR
brew install python@3.11
```

**Verification:**
```bash
python3 --version
# Should show: Python 3.10.x or 3.11.x

# Verify venv module exists
python3 -m venv --help
# Should show venv help, not an error
```

---

### 4. Visual Studio Code

**Purpose**: Primary development environment with WSL integration

**Version**: Latest stable (1.80+)

**Download**: https://code.visualstudio.com/

**Required Extensions:**
- **WSL** (ms-vscode-remote.remote-wsl) - For Windows users
- **Python** (ms-python.python) - Recommended
- **GitLens** (eamodio.gitlens) - Optional but helpful

**Installation:**
1. Download and install VS Code
2. Open VS Code
3. Press `Ctrl+Shift+X` to open Extensions
4. Search and install: "WSL" (if on Windows)
5. Search and install: "Python"

**Verification:**
- Open VS Code
- Bottom-left corner should show a status indicator
- Press `Ctrl+Shift+P` and type "WSL" - you should see WSL commands

---

### 5. WSL (Windows Only)

**Purpose**: Run Linux environment natively on Windows

**Version**: WSL 1 or WSL 2 (both work)

**Requirements:**
- Windows 10 version 1903+ or Windows 11
- Virtualization enabled in BIOS (for WSL 2 only)
- Administrator access

**Installation:**

**For WSL 2** (with virtualization):
```powershell
# In PowerShell as Administrator
wsl --install -d Ubuntu-22.04
```

**For WSL 1** (without virtualization):
```powershell
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Restart computer
shutdown /r /t 5

# Install Ubuntu
wsl --install -d Ubuntu-22.04
# OR download manually from: https://aka.ms/wslubuntu2204
```

**Verification:**
```powershell
wsl --list --verbose
# Should show Ubuntu-22.04 with VERSION 1 or 2
```

**Post-Install:**
- Create username (lowercase, no spaces)
- Set password (save in password manager!)
- **Verify you're not root**: Run `whoami` - should show your username, NOT "root"

**Note**: Calcifer works perfectly on both WSL 1 and WSL 2. WSL 2 offers better performance but requires virtualization support.

---

### 6. Docker & Docker Compose (For Deployment)

**Purpose**: Container runtime for deploying Calcifer and services

**Note**: Not needed for initial local development, only for deployment to VMs

**Installation (on Debian/Ubuntu VM):**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify
docker --version
docker compose version
```

---

## Optional Dependencies

### 7. Windows Terminal (Windows Only)

**Purpose**: Better terminal experience than default Command Prompt

**Recommendation**: Highly recommended for Windows users

**Installation:**
- Microsoft Store: Search "Windows Terminal"
- Or download from: https://github.com/microsoft/terminal/releases

---

### 8. KeePass or Password Manager

**Purpose**: Securely store passwords and SSH keys

**Recommendation**: Use a password manager for WSL passwords, SSH keys, and API tokens

---

## Python Package Dependencies

See `requirements.txt` for complete list. Key dependencies:

| Package | Version | Min Python | Purpose |
|---------|---------|------------|---------|
| FastAPI | 0.109.0 | 3.8+ | Web framework |
| Uvicorn | 0.27.0 | 3.8+ | ASGI server |
| SQLAlchemy | 2.0.25 | 3.7+ | ORM |
| Pydantic | 2.5.3 | 3.8+ | Data validation |
| GitPython | 3.1.41 | 3.7+ | Git integration |
| Jinja2 | 3.1.3 | 3.7+ | Templates |

**All dependencies support Python 3.8+**

**Calcifer is tested on Python 3.10+** for optimal compatibility and performance.

---

## Tested Configurations

### ✅ **Officially Tested** (Development Environment)

| OS | Python | Status |
|----|--------|--------|
| Ubuntu 22.04 (WSL 1) | 3.10.x | ✅ Primary |
| Ubuntu 22.04 (WSL 1) | 3.11.x | ✅ Tested |
| Ubuntu 22.04 (WSL 2) | 3.10.x | ✅ Tested |

### 🔄 **Should Work** (Not Extensively Tested)

| OS | Python | Status |
|----|--------|--------|
| Ubuntu 20.04 | 3.8.x | 🔄 Supported by dependencies |
| Ubuntu 20.04 | 3.10.x | 🔄 Should work |
| Debian 11 | 3.9.x | 🔄 Should work |
| macOS 10.15+ | 3.10+ | 🔄 Should work |

### ❌ **Not Supported**

| OS | Python | Reason |
|----|--------|--------|
| Ubuntu 16.04 | 3.5.x | Too old, dependencies incompatible |
| Ubuntu 18.04 | 3.6.x | Python too old |
| Any OS | < 3.8 | Dependencies require 3.8+ |

---

## Network Requirements

### Ports Used

**Local Development:**
- `8000` - Calcifer web interface (http://localhost:8000)

**Future Deployment:**
- `8000` - Calcifer on services VM
- `9000` - Portainer (Docker management UI)
- `51820/udp` - WireGuard VPN
- Various - Your application containers

**Firewall Notes:**
- WSL uses network bridge - may need Windows Firewall rules for WSL 1
- Proxmox VMs need appropriate firewall rules

---

## Storage Requirements

**Development Machine:**
- `~100MB` - Calcifer application and dependencies
- `~50MB` - Git repository (will grow over time)
- `~500MB` - VS Code and extensions
- `~1GB` - Docker images (if testing locally)

**Proxmox VM (when deployed):**
- `10GB` - VM disk minimum
- `20GB` - VM disk recommended

---

## Platform Support Matrix

### Current Status

| Platform | Python | WSL | Status |
|----------|--------|-----|--------|
| Windows 10/11 | 3.10+ | WSL 1/2 | ✅ Primary Development |
| Linux | 3.10+ | N/A | ✅ Deployment Target |
| macOS | 3.10+ | N/A | 🔄 Should Work |

### Future Testing Roadmap

As the project matures, additional platforms and Python versions will be tested:

**Phase 4**: 
- Ubuntu 22.04 + Python 3.10/3.11 (current)
- Debian 12 deployment testing

**Phase 5+**:
- Python 3.12 compatibility testing
- macOS development environment testing
- Additional Linux distributions
- Older Python versions (3.8, 3.9) verification

---

## Next Steps

Once all prerequisites are met, proceed to:
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development workflow and patterns

---

## Additional Reading

After setup, review these to understand the architecture:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
- **[ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed development patterns
- **[DEVELOPER_QUICK_REFERENCE.md](DEVELOPER_QUICK_REFERENCE.md)** - Daily development cheat sheet

---

## Troubleshooting Prerequisites

### WSL Issues
- Check Windows version: `winver` (must be 1903+)
- Check virtualization (WSL 2 only): `systeminfo` and look for "Hyper-V"
- Enable in BIOS if needed (for WSL 2)

### Python Version Issues
```bash
# Ubuntu 22.04 - Python 3.10 is default
python3 --version

# For older Ubuntu versions, use deadsnakes PPA
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv -y
```

### Git SSH Key Issues
```bash
# Test SSH connection to GitHub
ssh -T git@github.com
# Should show: "Hi username! You've successfully authenticated"
```

### VS Code Can't Find WSL
- Restart VS Code
- Restart WSL: `wsl --shutdown` then restart Ubuntu
- Reinstall WSL extension

---

**Last Updated:** November 2025  
**Tested On:** Ubuntu 22.04 LTS (WSL 1) with Python 3.10  
**Version:** Calcifer v2.0 (Phase 3 Complete)