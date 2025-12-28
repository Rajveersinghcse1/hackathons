# CyberShell Privacy Policy

**Version:** 1.0  
**Last Updated:** December 1, 2025  
**Purpose:** Hackathon Demonstration Only

---

## 1. Overview

CyberShell is an AI-based endpoint detection prototype designed for security research and demonstration purposes. This document explains what data is collected, how it is processed, and how to disable collection.

## 2. Data Collection Scope

### 2.1 What We Collect

| Data Type | Collected | Anonymized | Purpose |
|-----------|-----------|------------|---------|
| Process names | ✅ Yes | ❌ No | Threat detection |
| Process command lines | ✅ Yes | ⚠️ Partial* | LOLBin detection |
| Parent-child process relationships | ✅ Yes | ❌ No | Behavior chains |
| Network flow metadata | ✅ Yes | ✅ Yes | Exfil detection |
| File write rates (aggregate) | ✅ Yes | ✅ Yes | Ransomware detection |
| Windows Event Log metadata | ✅ Yes | ✅ Yes | Logon analysis |
| DNS query domains | ✅ Yes | ⚠️ Partial* | C2 detection |

*Partial anonymization: Sensitive patterns are detected but not logged in full.

### 2.2 What We DO NOT Collect

| Data Type | Status | Reason |
|-----------|--------|--------|
| Keystrokes | ❌ Never | Privacy violation |
| Clipboard contents | ❌ Never | Privacy violation |
| Email content | ❌ Never | Privacy violation |
| File contents | ❌ Never | Privacy violation |
| Screen captures | ❌ Never | Privacy violation |
| Browser history | ❌ Never | Privacy violation |
| Personal documents | ❌ Never | Privacy violation |
| Chat/messaging data | ❌ Never | Privacy violation |

## 3. Anonymization Methods

### 3.1 Identifier Hashing

All personally identifiable information is hashed before storage:

```python
# Example: How we anonymize
import hashlib

def hash_identifier(value: str, salt: str) -> str:
    """One-way hash with salt - cannot be reversed without salt"""
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:16]

# Usage
username = "john.doe"           # Original
hashed = hash_identifier(username, SECRET_SALT)  # "a3f2b1c9d8e7f6a5"
```

### 3.2 What Gets Hashed

- **Usernames**: `DOMAIN\user` → `hash_abc123`
- **Hostnames**: `WORKSTATION-01` → `host_def456`
- **IP Addresses**: `192.168.1.100` → `ip_ghi789`
- **MAC Addresses**: `AA:BB:CC:DD:EE:FF` → `mac_jkl012`

### 3.3 Salt Storage

The anonymization salt is stored in `.cybershell_salt` (not committed to git).
Without this salt, hashes cannot be reversed.

## 4. Data Storage

### 4.1 Storage Locations

| Data | Location | Retention |
|------|----------|-----------|
| Feature rows | `data/features/` | Session only |
| Alerts | `data/alerts/` | Session only |
| Models | `model/model.pkl` | Persistent |
| Hash mappings | `.hash_mapping.json` | Local only |

### 4.2 No Cloud Transmission

CyberShell operates **entirely offline**. No data is transmitted to:
- Cloud services
- External APIs
- Remote servers
- Third parties

## 5. Simulation Mode

### 5.1 Default Behavior

CyberShell runs in `--simulate` mode by default:

```powershell
# Default - all actions are print-only
python -m ui.streamlit_app

# Explicit simulation
python -m ui.streamlit_app --simulate
```

### 5.2 Execute Mode (VM Only)

Real containment actions require explicit confirmation:

```powershell
# Requires --execute AND --vm flags
# Will prompt for confirmation before any action
python -m playbook.actions --execute --vm
```

### 5.3 Containment Actions

| Action | Simulate Mode | Execute Mode |
|--------|--------------|--------------|
| Isolate host | Prints command | Requires VM + confirm |
| Block process | Prints command | Requires VM + confirm |
| Forensic capture | Prints command | Requires VM + confirm |
| Network block | Prints command | Requires VM + confirm |

## 6. Disabling Collection

### 6.1 Full Disable

To run with no live data collection:

```powershell
# Use replay sandbox - only packaged demo data
python -m scenarios.runner --replay-sandbox
```

### 6.2 Selective Disable

In `config/settings.yaml`:

```yaml
collection:
  sysmon: false      # Disable Sysmon collection
  pcap: false        # Disable PCAP collection
  wmi: false         # Disable WMI queries
  eventlog: false    # Disable Event Log reading
```

### 6.3 Anonymization Only

To enable maximum anonymization:

```yaml
privacy:
  hash_all_identifiers: true
  strip_command_args: true
  aggregate_only: true  # Only aggregate metrics, no raw events
```

## 7. Replay Sandbox Mode

For judges and demonstrations, the replay sandbox:

1. **Uses only packaged scenario data** - no live collection
2. **Cannot access host telemetry** - isolation guaranteed
3. **Fully reproducible** - same inputs produce same outputs

```powershell
# Enter replay sandbox
python -m scenarios.runner --scenario malicious-ransomware --replay-sandbox
```

## 8. Data Subject Rights

Even though this is a prototype, we respect:

- **Right to know**: This document explains all collection
- **Right to delete**: Delete `data/` folder to remove all session data
- **Right to disable**: Use `--replay-sandbox` or config options
- **Right to portability**: All data is in standard CSV/JSON formats

## 9. Security Measures

| Measure | Implementation |
|---------|----------------|
| Encryption at rest | Optional, via `--encrypt-data` flag |
| Access control | OS-level file permissions |
| Audit logging | All access logged to `logs/audit.log` |
| No persistence | Session data cleared on exit (default) |

## 10. Contact

For questions about this privacy policy:
- **Project**: CyberShell Hackathon Prototype
- **Purpose**: Educational / Research demonstration
- **Scope**: Local execution only

---

## Appendix A: Feature List with Privacy Impact

| Feature | Raw Data | Privacy Impact | Mitigation |
|---------|----------|----------------|------------|
| `timestamp` | Event time | Low | None needed |
| `host_hash` | Hostname | Medium | SHA-256 hash |
| `process_name` | Process name | Low | None needed |
| `parent_process` | Parent name | Low | None needed |
| `cmdline_entropy` | Entropy score | Low | Score only, not content |
| `outbound_bytes_5m` | Byte count | Low | Aggregate only |
| `unique_dst_ips_1hr` | Count | Low | Count only, IPs hashed |
| `file_write_rate` | Writes/sec | Low | Rate only |
| `failed_logons_10m` | Count | Low | Count only, users hashed |

## Appendix B: Compliance Notes

This prototype is designed for educational demonstration. For production use:

- Consult legal counsel for jurisdiction-specific requirements
- Implement proper consent mechanisms
- Add data retention policies
- Consider GDPR/CCPA compliance if applicable
- Conduct privacy impact assessment
