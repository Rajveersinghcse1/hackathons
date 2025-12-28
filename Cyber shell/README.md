# CyberShell - AI-Based Endpoint Detection Prototype

> **Hackathon-Ready | Windows-Safe | Privacy-First**

A hybrid rule-based + ML anomaly detection system for Windows endpoints.
Operates entirely in userland with read-only collection by default.

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CYBERSHELL ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        DATA SOURCES (Read-Only)                       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  [Sysmon EVTX/CSV]  [PCAP Files]  [WMI Queries]  [Event Logs]        │   │
│  │       ↓                  ↓             ↓              ↓               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      AGENT / COLLECTOR LAYER                          │   │
│  │                      (agent/collector.py)                             │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  • SysmonCollector: Parse EVTX/CSV exports                           │   │
│  │  • PcapCollector: Offline PCAP parsing (scapy/dpkt)                  │   │
│  │  • WMICollector: Process enumeration via WMI                         │   │
│  │  • EventLogCollector: Windows Security/System events                 │   │
│  │  ────────────────────────────────────────────────────────────────    │   │
│  │  Privacy: Hash usernames/IPs before forwarding                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    PARSER / FEATURE EXTRACTOR                         │   │
│  │                   (parser/feature_extractor.py)                       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  Raw Events → Feature Rows:                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐     │   │
│  │  │ timestamp | host_hash | process | parent | cmdline_entropy │     │   │
│  │  │ outbound_bytes_5m | unique_dst_ips_1hr | file_write_rate   │     │   │
│  │  │ failed_logons_10m | dns_query_count | beacon_score         │     │   │
│  │  └─────────────────────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      DETECTION ENGINE (Hybrid)                        │   │
│  │                        (model/detect.py)                              │   │
│  ├─────────────────────────────┬────────────────────────────────────────┤   │
│  │     LAYER 1: RULES          │       LAYER 2: ML ANOMALY              │   │
│  │  ──────────────────────     │    ────────────────────────            │   │
│  │  • Ransomware patterns      │    • IsolationForest model             │   │
│  │  • Exfil thresholds         │    • Anomaly scoring (0-100)           │   │
│  │  • LOLBins signatures       │    • Feature contribution              │   │
│  │  • C2 beacon detection      │    • Explainability (top-3)            │   │
│  │  • Credential abuse         │                                        │   │
│  ├─────────────────────────────┴────────────────────────────────────────┤   │
│  │  Output: risk_score (0-100), alert_type, top_3_features, evidence    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                    ┌───────────────┼───────────────┐                        │
│                    ▼               ▼               ▼                        │
│  ┌────────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐    │
│  │   STREAMLIT UI     │ │ PLAYBOOK RUNNER │ │   METRICS RECORDER      │    │
│  │ (ui/streamlit_app) │ │ (playbook/      │ │  (metrics/compute_      │    │
│  │                    │ │  actions.py)    │ │   metrics.py)           │    │
│  ├────────────────────┤ ├─────────────────┤ ├─────────────────────────┤    │
│  │ • Alerts feed      │ │ --simulate mode │ │ • TPR, FPR, Precision   │    │
│  │ • Evidence viewer  │ │ • isolate_host  │ │ • Recall, MTTD          │    │
│  │ • Triage buttons   │ │ • forensic_cap  │ │ • Alert reduction ratio │    │
│  │ • Metrics display  │ │ • block_process │ │ • CSV report output     │    │
│  │ • Simulate badge   │ │ (prints only)   │ │                         │    │
│  └────────────────────┘ └─────────────────┘ └─────────────────────────┘    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        SCENARIO RUNNER                                │   │
│  │                     (scenarios/runner.py)                             │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  Packaged Scenarios:                                                  │   │
│  │  1. BENIGN: Normal office activity (baseline)                        │   │
│  │  2. BENIGN-ANOMALY: Unusual but legitimate behavior                  │   │
│  │  3. MALICIOUS-RANSOMWARE: Encryption + exfil patterns                │   │
│  │  ────────────────────────────────────────────────────────────────    │   │
│  │  Replay: tcpreplay PCAP + inject Sysmon CSV without live collection  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

SAFETY FLAGS:
  --simulate (DEFAULT): All containment actions print-only
  --execute --vm: Real actions, requires VM confirmation
  --replay-sandbox: Use packaged data, no live telemetry
```

## 🚀 Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Run in replay sandbox mode (safe for demo)
python -m scenarios.runner --scenario malicious-ransomware --simulate

# Launch UI
streamlit run ui/streamlit_app.py -- --simulate --replay-sandbox

# Compute metrics
python -m metrics.compute_metrics --scenario-dir scenarios/data/
```

## 📁 Project Structure

```
cybershell/
├── agent/                  # Data collection (read-only)
│   ├── __init__.py
│   └── collector.py
├── parser/                 # Feature extraction
│   ├── __init__.py
│   └── feature_extractor.py
├── model/                  # ML models
│   ├── __init__.py
│   ├── train_model.py
│   ├── detect.py
│   ├── rules.py
│   └── model.pkl
├── ui/                     # Streamlit dashboard
│   ├── __init__.py
│   └── streamlit_app.py
├── playbook/               # Response actions
│   ├── __init__.py
│   └── actions.py
├── metrics/                # Performance measurement
│   ├── __init__.py
│   └── compute_metrics.py
├── scenarios/              # Demo scenarios
│   ├── __init__.py
│   ├── runner.py
│   └── data/
│       ├── benign/
│       ├── benign-anomaly/
│       └── malicious-ransomware/
├── utils/                  # Shared utilities
│   ├── __init__.py
│   ├── privacy.py
│   └── config.py
├── tests/                  # Unit tests
├── privacy_policy.md
├── requirements.txt
└── README.md
```

## 🔒 Safety & Privacy

- **Simulate by default**: All containment actions are print-only
- **Hashed identifiers**: Usernames and IPs are SHA-256 hashed
- **No PII collection**: No keystrokes, clipboard, or email content
- **Replay sandbox**: Demo without touching live system data

See [privacy_policy.md](privacy_policy.md) for full details.

## 📊 Detection Priorities

| Priority | Threat | Key Features |
|----------|--------|--------------|
| 🔴 High | Ransomware | file_write_rate, rename_count, unusual_path |
| 🔴 High | Exfiltration | outbound_bytes_5m, unique_dst_ips |
| 🟠 Med-High | C2/Beaconing | periodic_flows, dns_anomaly |
| 🟡 Medium | Credential Abuse | failed_logons, new_admin |
| 🟡 Medium | LOLBins | cmdline_entropy, base64_patterns |

## 📜 License

MIT License - Hackathon Demo Only
