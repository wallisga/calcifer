# Developer Tools & Utilities

This document covers optional development tools and scripts that enhance the Calcifer development workflow.

---

## Git Sync Tool

**Purpose:** Safely synchronize your local repository with remote changes when working across multiple machines.

**Location:** `tools/git-sync.sh`

**Use Case:**
- Working on multiple development machines (work laptop + home desktop)
- Pulling latest changes before starting new work
- Avoiding merge conflicts from out-of-sync branches

### Installation

```bash
# One-time setup
cd ~/calcifer
mkdir -p tools
# Copy git-sync.sh to tools/
chmod +x tools/git-sync.sh

# (Optional) Add to PATH for global use
ln -s ~/calcifer/tools/git-sync.sh ~/bin/git-sync
```

### Usage

```bash
# From calcifer directory
cd ~/calcifer
./tools/git-sync.sh          # Sync main branch
./tools/git-sync.sh develop  # Sync specific branch

# If installed to PATH
git-sync                      # Use from anywhere
```

### What It Does

1. ✅ Checks if you're in a git repository
2. ✅ Warns if you have uncommitted changes (won't overwrite)
3. ✅ Fetches latest from remote
4. ✅ Shows what commits would be pulled
5. ✅ Asks for confirmation before pulling
6. ✅ Only pulls if fast-forward is possible (safe)
7. ❌ Aborts if branches have diverged (prevents conflicts)

### Safety Features

- **Never overwrites uncommitted work**
- **Shows preview before pulling**
- **Requires confirmation**
- **Only fast-forwards** (no merge commits unless necessary)
- **Detects conflicts before they happen**

### Example Output

**When up to date:**
```
=== Git Sync Tool ===
Branch: main

Fetching from remote...
✓ Already up to date!
```

**When updates available:**
```
=== Git Sync Tool ===
Branch: main

Fetching from remote...
✓ Can fast-forward

Changes that will be pulled:
a1b2c3d Update service catalog module
e4f5g6h Add monitoring endpoint tests

Pull these changes? (Y/n):
```

**When branches diverged:**
```
✗ Branches have diverged!

Your commits not on remote:
h7i8j9k Working on feature X

Remote commits you don't have:
a1b2c3d Update from other machine

Cannot auto-sync - manual merge required
```

### Integration with Calcifer Workflow

**Recommended daily workflow when using multiple machines:**

1. **Start of day:**
   ```bash
   cd ~/calcifer
   ./tools/git-sync.sh    # Pull latest changes
   ```

2. **Work in Calcifer:**
   - Create work items in UI
   - Calcifer auto-creates feature branches
   - Make your changes
   - Commit via Calcifer UI

3. **After merging work items:**
   ```bash
   git checkout main
   ./tools/git-sync.sh    # Sync main with remote
   ```

4. **End of day:**
   ```bash
   git push origin main   # Push your merged work
   ```

---

## IDE Integration (Planned)

**Status:** 🔄 Planned for Phase 5

### Concept: IDE Tools Integration

Instead of treating IDE setup as a "service" in the service catalog, Calcifer will provide **integration modules** for different IDEs that install development utilities.

**Approach:**
- Integration (not a service) - keeps service catalog focused on infrastructure
- Install scripts per IDE (VS Code, JetBrains, Vim, etc.)
- Each integration can install:
  - Editor extensions/plugins
  - Workspace settings
  - Development scripts (like git-sync)
  - Code snippets
  - Debugging configurations

### VS Code Integration (Planned)

**What it will provide:**

**Workspace Settings:**
- Python path configuration
- Pylance settings
- Git integration preferences
- File associations

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "eamodio.gitlens",
    "ms-vscode-remote.remote-wsl"
  ]
}
```

**Tasks:**
- Run Calcifer server
- Run tests
- Format code
- Lint code

**Launch Configurations:**
- Debug Calcifer server
- Debug tests
- Attach to running process

**Code Snippets:**
- Module method templates
- Route templates
- Test templates

### Implementation Plan

**Phase 5 Work Items:**

1. **Create IDE Integration Framework**
   - Add `src/integrations/ide/` directory
   - Create base IDE integration class
   - Install/uninstall script framework

2. **VS Code Integration**
   - Create `.vscode/` templates
   - Install script: `tools/setup-vscode.sh`
   - Workspace settings generator
   - Extension installer

3. **JetBrains Integration (PyCharm)** (Future)
   - `.idea/` templates
   - Run configurations
   - Code style settings

4. **Vim/Neovim Integration** (Future)
   - LSP configuration
   - Plugin recommendations
   - Key bindings

### Why Integration vs Service?

**Service Catalog is for:**
- Infrastructure components (VMs, containers, networks)
- Deployed applications
- Monitored endpoints
- Things with uptime/health checks

**Integrations are for:**
- Development tools
- Optional enhancements
- IDE configurations
- Local development utilities

**Decision:** IDE tooling is an **integration**, not a service.

---

## Current Developer Tools

### Available Now

| Tool | Location | Purpose |
|------|----------|---------|
| git-sync.sh | `tools/git-sync.sh` | Safe multi-machine sync |

### Planned (Phase 5)

| Tool | Status | Purpose |
|------|--------|---------|
| setup-vscode.sh | 🔄 Planned | Install VS Code workspace |
| setup-pycharm.sh | 🔄 Planned | Install PyCharm config |
| dev-env-check.sh | 🔄 Planned | Verify dev environment |
| test-runner.sh | 🔄 Planned | Run tests with coverage |

---

## Contributing New Tools

When adding developer tools:

1. **Add to `tools/` directory**
   ```bash
   tools/
   ├── git-sync.sh
   ├── setup-vscode.sh      # New tool
   └── README.md            # Tools index
   ```

2. **Make it executable**
   ```bash
   chmod +x tools/new-tool.sh
   ```

3. **Document in this file**
   - Add section above
   - Explain purpose, usage, examples

4. **Add to DEVELOPMENT.md if workflow-critical**
   - Reference from "Multi-Machine Workflow"
   - Keep DEVELOPMENT.md focused on workflow

5. **Create work item**
   - Title: "Add [tool name] developer utility"
   - Category: "platform_feature"
   - Action: "new"
   - Document in work item notes

---

## Future Enhancements

### Planned Tools

**Development:**
- Pre-commit hooks installer
- Code formatter wrapper (black, isort)
- Test runner with coverage reports
- Database migration helper

**Deployment:**
- Docker Compose validator
- Environment variable checker
- Service health checker
- Backup script generator

**Documentation:**
- Markdown linter
- Doc generator from code
- Change log validator
- README updater

---

**Last Updated:** December 6, 2025  
**Status:** Active - git-sync.sh available  
**Next:** IDE integration framework (Phase 5)