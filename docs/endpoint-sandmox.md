# Endpoint: sandmox

## Overview

**Type:** NETWORK  
**Target:** `10.66.33.111`  
**Status:** Monitored by Calcifer

Bare metal running Proxmox VE 8 for sandbox purposes. Hosts various VMs and has domain-joined access to shared resources on the network.

## Monitoring Configuration

This endpoint is monitored for availability.

**Check Type:** network  
**Check Method:** Ping (ICMP)

## Access Information

**Target:** `10.66.33.111`

## Troubleshooting

### Endpoint is Down

1. **Check network connectivity:**
```bash
   ping 10.66.33.111
```

2. **Check specific port (if applicable):**
```bash
   nc -zv 10.66.33.111
```

3. **Check firewall rules:**
   - Verify firewall allows traffic from monitoring server
   - Check iptables/firewalld rules

4. **Verify service is running:**
   - Check if the target service/device is online
   - Review service logs

## History

- **Created:** 2025-11-23
- **Purpose:** Monitor availability of sandmox

## Related

- Endpoint configuration in Calcifer
- Service catalog entry
