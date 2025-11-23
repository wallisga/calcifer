# Endpoint: storage

## Overview

**Type:** NETWORK  
**Target:** `10.66.33.11`  
**Status:** Monitored by Calcifer

Bare metal storage endpoint that hosts a RAID 10 server with samba serving files to domain-joined users.

## Monitoring Configuration

This endpoint is monitored for availability.

**Check Type:** network  
**Check Method:** Ping (ICMP)

## Access Information

**Target:** `10.66.33.11`

## Troubleshooting

### Endpoint is Down

1. **Check network connectivity:**
```bash
   ping 10.66.33.11
```

2. **Check specific port (if applicable):**
```bash
   nc -zv 10.66.33.11
```

3. **Check firewall rules:**
   - Verify firewall allows traffic from monitoring server
   - Check iptables/firewalld rules

4. **Verify service is running:**
   - Check if the target service/device is online
   - Review service logs

## History

- **Created:** 2025-11-23
- **Purpose:** Monitor availability of storage

## Related

- Endpoint configuration in Calcifer
- Service catalog entry
