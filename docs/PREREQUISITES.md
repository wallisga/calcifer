# Prerequisites & Dependencies

This document lists all requirements for setting up and running Calcifer.

## System Requirements

### Hardware
- **Minimum**: 2GB RAM, 2 CPU cores, 10GB disk space
- **Recommended**: 4GB RAM, 4 CPU cores, 20GB disk space
- Applies to: Development machine and any VM running Calcifer

### Operating Systems

**Development Machine (where you'll build/test):**
- **Windows 10/11** (version 1903 or higher) - for WSL2 support
  - OR **Linux** (Ubuntu 20.04+, Debian 11+, any modern distro)
  - OR **macOS** (10.15+)

**Deployment Target (Proxmox VMs):**
- **Debian 11 or 12** (recommended)
- **Ubuntu 22.04 LTS** (alternative)

## Required Software

### 1. Git

**Purpose**: Version control for all infrastructure code and documentation

**Installation:**

**Windows (via WSL2):**
```bash
# Already included in WSL setup
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
```

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

### 3. Python 3.11+

**Purpose**: Calcifer application runtime

**Installation:**

**Windows (via WSL2):**
```bash
sudo apt install python3.11 python3-pip python3-venv
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt install python3.11 python3-pip python3-venv
```

**macOS:**
```bash
brew install python@3.11
```

**Verification:**
```bash
python3 --version
# Should show: Python 3.11.x
```

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

### 5. WSL2 (Windows Only)

**Purpose**: Run Linux environment natively on Windows

**Requirements:**
- Windows 10 version 1903+ or Windows 11
- Virtualization enabled in BIOS/UEFI
- Administrator access

**Installation:**
```powershell
# In PowerShell as Administrator
wsl --install -d Ubuntu-22.04
```

**Verification:**
```powershell
wsl --list --verbose
# Should show: Ubuntu-22.04 running WSL version 2
```

**Post-Install:**
- Set username (lowercase, no spaces) - **IMPORTANT: Do NOT skip this step!**
- Set password (save in KeePass!)
- **Verify you're not root**: Run `whoami` - should show your username, NOT "root"

**Common Issue - Logged in as Root:**

If `whoami` shows `root` instead of your username:

1. Create a regular user:
   ```bash
   # While logged in as root
   adduser yourusername
   usermod -aG sudo yourusername
   ```

2. In PowerShell (as Administrator):
   ```powershell
   wsl --shutdown
   wsl --set-default-user yourusername
   ```

3. Reopen Ubuntu terminal and verify `whoami` shows your username

See SETUP_GUIDE.md Troubleshooting section for detailed instructions.

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

## Optional Dependencies

### 7. Windows Terminal (Windows Only)

**Purpose**: Better terminal experience than default Command Prompt

**Recommendation**: Highly recommended for Windows users

**Installation:**
- Microsoft Store: Search "Windows Terminal"
- Or download from: https://github.com/microsoft/terminal/releases

### 8. KeePass or Password Manager

**Purpose**: Secure storage for credentials

**Options:**
- **KeePass** (existing)
- **Vaultwarden** (will set up later in Calcifer stack)
- **Bitwarden** (cloud option)

**For now**: Use your existing KeePass database

## Dependency Checklist

Before starting setup, verify you have:

- [ ] Windows 10/11 (version 1903+) OR Linux/macOS
- [ ] Git installed and configured
- [ ] Git hosting account created (GitHub/GitLab) OR plan to use local-only
- [ ] SSH key generated and added to Git host (if using remote)
- [ ] Python 3.11+ installed
- [ ] Visual Studio Code installed
- [ ] WSL extension installed in VS Code (Windows only)
- [ ] WSL2 with Ubuntu 22.04 installed (Windows only)
- [ ] Administrator/sudo access on your machine
- [ ] Password manager (KeePass) set up

## Version Information

Document your versions for troubleshooting:

```bash
# Run these commands and save output
echo "=== System Info ==="
uname -a

echo "=== Git ==="
git --version

echo "=== Python ==="
python3 --version

echo "=== VS Code ==="
code --version

echo "=== WSL (Windows only) ==="
wsl --version
```

**Save this output** in Calcifer as a work item note or in a `docs/SYSTEM_INFO.md` file.

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
- WSL2 uses network bridge - may need Windows Firewall rules
- Proxmox VMs need appropriate firewall rules

## Storage Requirements

**Development Machine:**
- `~100MB` - Calcifer application and dependencies
- `~50MB` - Git repository (will grow over time)
- `~500MB` - VS Code and extensions
- `~1GB` - Docker images (if testing locally)

**Proxmox VM (when deployed):**
- `10GB` - VM disk minimum
- `20GB` - VM disk recommended

## Next Steps

Once all prerequisites are met, proceed to:
- `docs/SETUP_GUIDE.md` - Complete setup instructions

## Troubleshooting Prerequisites

### WSL2 Not Available
- Check Windows version: `winver` (must be 1903+)
- Check virtualization: `systeminfo` and look for "Hyper-V"
- Enable in BIOS if needed

### Python 3.11 Not Found
```bash
# Ubuntu/Debian - add deadsnakes PPA
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
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