# Calcifer Integrations

This directory contains integrations that extend Calcifer's functionality with external tools and services.

## Core Integrations

### Git (`git.py`)
**Status:** ✅ Active (Core Integration)  
**Purpose:** Git operations and version control

**Features:**
- Branch management (create, checkout, merge)
- Commit operations with author tracking
- Branch status and merge detection
- CHANGES.md validation
- Repository status queries

**Usage:**
```python
from integrations import git_manager

# Create and checkout branch
git_manager.create_branch("feature/my-feature", checkout=True)

# Get repository status
status = git_manager.get_status()

# Check if branch is merged
is_merged = git_manager.is_branch_merged("feature/my-feature")

# Commit changes
commit_sha = git_manager.commit("Add new feature")
```

---

### Monitoring (`monitoring.py`)
**Status:** ✅ Active  
**Purpose:** Synthetic monitoring and endpoint health checks

**Features:**
- ICMP ping checks
- TCP port connectivity
- HTTP/HTTPS availability
- Automatic status tracking
- Documentation generation

**Usage:**
```python
from integrations import monitoring

# Check endpoint
is_up, error = monitoring.check_endpoint(endpoint)

# Update endpoint status in database
is_up = monitoring.update_endpoint_status(endpoint, db)
```

**Future Enhancements:**
- WMI checks for Windows hosts
- SNMP checks for network devices
- Custom application instrumentation
- Integration with Uptime Kuma API

---

## Future Integrations

### Uptime Kuma
**Status:** 📋 Planned  
**Purpose:** Integration with Uptime Kuma monitoring platform

**Features:**
- Sync endpoints to Uptime Kuma
- Pull monitoring data from Uptime Kuma
- Unified status display

---

### Grafana
**Status:** 📋 Planned  
**Purpose:** Dashboard and metrics visualization

**Features:**
- Embed Grafana dashboards in Calcifer
- Link services to Grafana panels
- Unified monitoring view

---

### Notifications
**Status:** 📋 Planned  
**Purpose:** Alert delivery via multiple channels

**Features:**
- Slack notifications
- Discord webhooks
- Email alerts
- Work item notifications

---

### Backups
**Status:** 📋 Planned  
**Purpose:** Automated backup management

**Features:**
- Database backups
- Configuration backups
- Remote storage (S3, etc.)
- Restore capabilities

---

## Integration Guidelines

### Structure

Each integration should be self-contained in its own file:
```python
class SomeIntegration:
    """Integration description."""
    
    def __init__(self, config: dict = None):
        """Initialize with optional configuration."""
        pass
    
    def check_connectivity(self) -> bool:
        """Test if integration is working."""
        pass
    
    # Integration-specific methods
```

### Configuration

Integrations should accept configuration via:
1. Constructor arguments
2. Environment variables
3. Database settings (future)

### Error Handling

All integrations must handle errors gracefully and return meaningful error messages.

### Documentation

Each integration must have:
- Docstrings for all public methods
- Usage examples
- Configuration documentation

### Singleton Pattern

For stateless integrations, provide a singleton instance:
```python
class MyIntegration:
    # ... methods ...

# Singleton for convenience
my_integration = MyIntegration()
```

## Adding New Integrations

1. Create new file in `integrations/` directory
2. Implement integration class
3. Add singleton instance if stateless
4. Export in `__init__.py`
5. Update this README
6. Add usage examples in docstrings
7. Create work item in Calcifer to track implementation