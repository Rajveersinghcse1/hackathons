"""
CyberShell Scenarios - Scenario Runner Module
==============================================

Purpose: Run packaged demo scenarios for hackathon
Scenarios: benign, benign-anomaly, malicious-ransomware

Features:
- Replay Sysmon CSV and PCAP without live collection
- Inject events into detection pipeline
- Compute metrics against ground truth
- Safe for judges to run locally

Usage:
    python -m scenarios.runner --scenario malicious-ransomware --simulate
"""

import json
import csv
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Dict, Any, List, Optional
from dataclasses import dataclass


# Add parent to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agent.collector import UnifiedCollector, PrivacyHasher
from parser.feature_extractor import FeatureExtractor
from model.detect import HybridDetector
from playbook.actions import PlaybookActions, ExecutionMode
from metrics.compute_metrics import MetricsCalculator, MetricsReporter


# =============================================================================
# SCENARIO DEFINITIONS
# =============================================================================

@dataclass
class ScenarioConfig:
    """Configuration for a demo scenario"""
    name: str
    description: str
    sysmon_csv: str
    pcap_file: Optional[str]
    eventlog_csv: Optional[str]
    labels_csv: str
    expected_alerts: List[str]
    duration_seconds: int


SCENARIOS = {
    'benign': ScenarioConfig(
        name='benign',
        description='Normal office activity - baseline behavior',
        sysmon_csv='scenarios/data/benign/sysmon_benign.csv',
        pcap_file=None,
        eventlog_csv=None,
        labels_csv='scenarios/data/benign/labels.csv',
        expected_alerts=[],
        duration_seconds=60
    ),
    'benign-anomaly': ScenarioConfig(
        name='benign-anomaly',
        description='Unusual but legitimate behavior (software update, backup)',
        sysmon_csv='scenarios/data/benign-anomaly/sysmon_benign_anomaly.csv',
        pcap_file=None,
        eventlog_csv=None,
        labels_csv='scenarios/data/benign-anomaly/labels.csv',
        expected_alerts=['anomaly'],  # May trigger low-confidence alerts
        duration_seconds=60
    ),
    'malicious-ransomware': ScenarioConfig(
        name='malicious-ransomware',
        description='Ransomware attack with encryption and exfiltration',
        sysmon_csv='scenarios/data/malicious-ransomware/sysmon_ransomware.csv',
        pcap_file=None,
        eventlog_csv=None,
        labels_csv='scenarios/data/malicious-ransomware/labels.csv',
        expected_alerts=['ransomware', 'exfil'],
        duration_seconds=120
    ),
}


# =============================================================================
# SAMPLE DATA GENERATOR
# =============================================================================

class SampleDataGenerator:
    """
    Generate sample scenario data for demos.
    Creates Sysmon CSV, PCAP descriptions, and ground truth labels.
    """
    
    def __init__(self, output_dir: str = "scenarios/data"):
        self.output_dir = Path(output_dir)
        self.hasher = PrivacyHasher()
    
    def generate_all_scenarios(self):
        """Generate sample data for all scenarios"""
        self.generate_benign_scenario()
        self.generate_benign_anomaly_scenario()
        self.generate_ransomware_scenario()
    
    def generate_benign_scenario(self):
        """Generate normal office activity data"""
        scenario_dir = self.output_dir / "benign"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        
        # Sysmon CSV - normal processes
        sysmon_data = [
            ['EventID', 'TimeCreated', 'Image', 'CommandLine', 'ParentImage', 'User', 
             'ProcessId', 'ParentProcessId', 'DestinationIp', 'DestinationPort', 'TargetFilename'],
            # Normal browser activity
            [1, '2024-01-15 09:00:00', 'C:\\Program Files\\Chrome\\chrome.exe', 
             '"chrome.exe" --profile-directory=Default', 'C:\\Windows\\explorer.exe', 
             'DOMAIN\\user1', 1234, 5678, '', '', ''],
            # Normal Office
            [1, '2024-01-15 09:05:00', 'C:\\Program Files\\Microsoft Office\\WINWORD.EXE',
             '"WINWORD.EXE" /n', 'C:\\Windows\\explorer.exe',
             'DOMAIN\\user1', 2345, 5678, '', '', ''],
            # Normal network - HTTPS
            [3, '2024-01-15 09:10:00', 'C:\\Program Files\\Chrome\\chrome.exe',
             '', '', 'DOMAIN\\user1', 1234, 0, '172.217.14.99', '443', ''],
            # Normal file save
            [11, '2024-01-15 09:15:00', 'C:\\Program Files\\Microsoft Office\\WINWORD.EXE',
             '', '', 'DOMAIN\\user1', 2345, 0, '', '', 
             'C:\\Users\\user1\\Documents\\report.docx'],
        ]
        
        self._write_csv(scenario_dir / "sysmon.csv", sysmon_data)
        
        # Event log - successful logons
        eventlog_data = [
            ['EventID', 'TimeCreated', 'TargetUserName', 'LogonType', 'IpAddress'],
            [4624, '2024-01-15 08:55:00', 'user1', 2, ''],  # Interactive logon
        ]
        self._write_csv(scenario_dir / "eventlog.csv", eventlog_data)
        
        # Labels - all benign
        labels_data = [
            ['timestamp', 'host_hash', 'is_malicious', 'attack_type', 'attack_start_time'],
            ['2024-01-15T09:00:00', 'host_demo1', 'false', 'benign', ''],
            ['2024-01-15T09:10:00', 'host_demo1', 'false', 'benign', ''],
        ]
        self._write_csv(scenario_dir / "labels.csv", labels_data)
        
        # PCAP description (placeholder - actual PCAP would need binary generation)
        self._write_text(scenario_dir / "traffic_description.txt", """
        PCAP Summary: Benign Scenario
        =============================
        Duration: 60 seconds
        Protocols: HTTPS (443), DNS (53)
        Destinations: Google, Microsoft CDN
        Bytes: ~500KB total
        Pattern: Normal browsing, no anomalies
        
        To replay with tcpreplay:
        tcpreplay -i eth0 traffic.pcap
        """)
        
        print(f"[INFO] Generated benign scenario in {scenario_dir}")
    
    def generate_benign_anomaly_scenario(self):
        """Generate unusual but legitimate activity"""
        scenario_dir = self.output_dir / "benign-anomaly"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        
        # Sysmon CSV - legitimate but unusual
        sysmon_data = [
            ['EventID', 'TimeCreated', 'Image', 'CommandLine', 'ParentImage', 'User',
             'ProcessId', 'ParentProcessId', 'DestinationIp', 'DestinationPort', 'TargetFilename'],
            # Software update with high file writes (legitimate)
            [1, '2024-01-15 10:00:00', 'C:\\Windows\\System32\\msiexec.exe',
             'msiexec.exe /i update.msi /quiet', 'C:\\Windows\\System32\\services.exe',
             'SYSTEM', 3456, 789, '', '', ''],
            # Many file operations (update installing)
            [11, '2024-01-15 10:01:00', 'C:\\Windows\\System32\\msiexec.exe',
             '', '', 'SYSTEM', 3456, 0, '', '',
             'C:\\Program Files\\App\\file1.dll'],
            [11, '2024-01-15 10:01:01', 'C:\\Windows\\System32\\msiexec.exe',
             '', '', 'SYSTEM', 3456, 0, '', '',
             'C:\\Program Files\\App\\file2.dll'],
            # ... (would have many more file writes)
            # Large backup upload (legitimate)
            [3, '2024-01-15 10:30:00', 'C:\\Program Files\\Backup\\backup.exe',
             '', '', 'DOMAIN\\admin', 4567, 0, '52.184.80.100', '443', ''],
        ]
        
        self._write_csv(scenario_dir / "sysmon.csv", sysmon_data)
        
        # Labels - benign but may trigger low alerts
        labels_data = [
            ['timestamp', 'host_hash', 'is_malicious', 'attack_type', 'attack_start_time'],
            ['2024-01-15T10:00:00', 'host_demo2', 'false', 'benign', ''],
            ['2024-01-15T10:30:00', 'host_demo2', 'false', 'benign', ''],
        ]
        self._write_csv(scenario_dir / "labels.csv", labels_data)
        self._write_csv(scenario_dir / "eventlog.csv", [
            ['EventID', 'TimeCreated', 'TargetUserName', 'LogonType', 'IpAddress'],
        ])
        
        print(f"[INFO] Generated benign-anomaly scenario in {scenario_dir}")
    
    def generate_ransomware_scenario(self):
        """Generate ransomware attack data"""
        scenario_dir = self.output_dir / "malicious-ransomware"
        scenario_dir.mkdir(parents=True, exist_ok=True)
        
        # Sysmon CSV - ransomware behavior
        sysmon_data = [
            ['EventID', 'TimeCreated', 'Image', 'CommandLine', 'ParentImage', 'User',
             'ProcessId', 'ParentProcessId', 'DestinationIp', 'DestinationPort', 'TargetFilename'],
            # Initial access - phishing document
            [1, '2024-01-15 14:00:00', 'C:\\Program Files\\Microsoft Office\\WINWORD.EXE',
             '"WINWORD.EXE" invoice.docm', 'C:\\Windows\\explorer.exe',
             'DOMAIN\\victim', 5001, 5678, '', '', ''],
            # Macro spawns PowerShell (LOLBin)
            [1, '2024-01-15 14:00:30', 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
             'powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkA',
             'C:\\Program Files\\Microsoft Office\\WINWORD.EXE',
             'DOMAIN\\victim', 5002, 5001, '', '', ''],
            # C2 callback
            [3, '2024-01-15 14:01:00', 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
             '', '', 'DOMAIN\\victim', 5002, 0, '185.220.101.45', '443', ''],
            # Ransomware payload dropped
            [11, '2024-01-15 14:01:30', 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
             '', '', 'DOMAIN\\victim', 5002, 0, '', '',
             'C:\\Users\\victim\\AppData\\Local\\Temp\\update.exe'],
            # Ransomware execution
            [1, '2024-01-15 14:02:00', 'C:\\Users\\victim\\AppData\\Local\\Temp\\update.exe',
             'update.exe', 'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe',
             'DOMAIN\\victim', 5003, 5002, '', '', ''],
            # Mass encryption - many file operations
            [11, '2024-01-15 14:02:10', 'C:\\Users\\victim\\AppData\\Local\\Temp\\update.exe',
             '', '', 'DOMAIN\\victim', 5003, 0, '', '',
             'C:\\Users\\victim\\Documents\\report.docx.encrypted'],
            [11, '2024-01-15 14:02:11', 'C:\\Users\\victim\\AppData\\Local\\Temp\\update.exe',
             '', '', 'DOMAIN\\victim', 5003, 0, '', '',
             'C:\\Users\\victim\\Documents\\budget.xlsx.encrypted'],
            [11, '2024-01-15 14:02:12', 'C:\\Users\\victim\\AppData\\Local\\Temp\\update.exe',
             '', '', 'DOMAIN\\victim', 5003, 0, '', '',
             'C:\\Users\\victim\\Documents\\presentation.pptx.encrypted'],
            # Data exfiltration
            [3, '2024-01-15 14:05:00', 'C:\\Users\\victim\\AppData\\Local\\Temp\\update.exe',
             '', '', 'DOMAIN\\victim', 5003, 0, '91.234.99.42', '443', ''],
        ]
        
        self._write_csv(scenario_dir / "sysmon.csv", sysmon_data)
        
        # Event log - may show lateral movement attempts
        eventlog_data = [
            ['EventID', 'TimeCreated', 'TargetUserName', 'LogonType', 'IpAddress'],
            [4624, '2024-01-15 13:55:00', 'victim', 2, ''],
            [4625, '2024-01-15 14:10:00', 'admin', 3, '192.168.1.50'],  # Failed lateral
            [4625, '2024-01-15 14:10:05', 'administrator', 3, '192.168.1.50'],
        ]
        self._write_csv(scenario_dir / "eventlog.csv", eventlog_data)
        
        # Labels - malicious with attack timing
        labels_data = [
            ['timestamp', 'host_hash', 'is_malicious', 'attack_type', 'attack_start_time'],
            ['2024-01-15T14:00:00', 'host_victim', 'false', 'benign', ''],
            ['2024-01-15T14:00:30', 'host_victim', 'true', 'lolbin', '2024-01-15T14:00:30'],
            ['2024-01-15T14:01:00', 'host_victim', 'true', 'c2', '2024-01-15T14:00:30'],
            ['2024-01-15T14:02:00', 'host_victim', 'true', 'ransomware', '2024-01-15T14:02:00'],
            ['2024-01-15T14:05:00', 'host_victim', 'true', 'exfil', '2024-01-15T14:02:00'],
        ]
        self._write_csv(scenario_dir / "labels.csv", labels_data)
        
        print(f"[INFO] Generated malicious-ransomware scenario in {scenario_dir}")
    
    def _write_csv(self, path: Path, data: List[List]):
        """Write CSV file"""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    
    def _write_text(self, path: Path, content: str):
        """Write text file"""
        path.write_text(content.strip())


# =============================================================================
# SCENARIO RUNNER
# =============================================================================

class ScenarioRunner:
    """
    Runs packaged scenarios through the detection pipeline.
    
    Pipeline:
    1. Load scenario data (Sysmon CSV)
    2. Collect events via SysmonCollector
    3. Extract features via FeatureExtractor
    4. Run detection via HybridDetector
    5. Compare results to ground truth labels
    6. Report metrics
    """
    
    def __init__(self, simulate: bool = True):
        self.simulate = simulate
        self.detector = None
        self.playbook = PlaybookActions(
            mode=ExecutionMode.SIMULATE if simulate else ExecutionMode.EXECUTE_VM
        )
    
    def run_scenario(self, scenario_name: str, 
                     interactive: bool = False) -> Dict[str, Any]:
        """
        Run a single scenario.
        
        Args:
            scenario_name: Name of scenario to run
            interactive: If True, pause for user input at alerts
            
        Returns:
            Results dictionary with detections and metrics
        """
        if scenario_name not in SCENARIOS:
            available = ', '.join(SCENARIOS.keys())
            raise ValueError(f"Unknown scenario: {scenario_name}. Available: {available}")
        
        config = SCENARIOS[scenario_name]
        
        print("\n" + "=" * 60)
        print(f"RUNNING SCENARIO: {config.name}")
        print("=" * 60)
        print(f"Description: {config.description}")
        print(f"Expected alerts: {config.expected_alerts}")
        print(f"Mode: {'SIMULATE' if self.simulate else 'EXECUTE'}")
        print("=" * 60 + "\n")
        
        # Check if data exists
        sysmon_path = Path(config.sysmon_csv)
        if not sysmon_path.exists():
            print(f"[ERROR] Sysmon CSV not found: {config.sysmon_csv}")
            return {'error': f'Missing data file: {config.sysmon_csv}'}
        
        # Initialize detector
        self.detector = HybridDetector()
        
        # Create hasher for collection
        hasher = PrivacyHasher()
        
        # Collect events from CSV
        print("[1/4] Collecting events from scenario data...")
        from agent.collector import SysmonCollector
        collector = SysmonCollector(hasher, csv_path=sysmon_path)
        
        events = list(collector.collect())
        print(f"   Collected {len(events)} events")
        
        if len(events) == 0:
            print("[WARNING] No events collected from CSV")
        
        # Extract features
        print("[2/4] Extracting features...")
        extractor = FeatureExtractor(aggregation_window=5)  # 5-second window for demos
        
        feature_rows = []
        for event in events:
            # Get host hash from event
            host_hash = getattr(event, 'user_hash', None) or 'host_unknown'
            row = extractor.process(event, host_hash)
            if row:
                feature_rows.append(row)
        
        # Flush remaining
        final_row = extractor.flush('host_unknown')
        if final_row:
            feature_rows.append(final_row)
        
        print(f"   Extracted {len(feature_rows)} feature rows")
        
        # Run detection
        print("[3/4] Running hybrid detection...")
        detections = []
        
        for row in feature_rows:
            result = self.detector.detect(row)
            det_dict = result.to_dict()
            # Add timestamp and host for metrics matching
            det_dict['timestamp'] = datetime.now().isoformat()
            det_dict['host_hash'] = getattr(row, 'host_hash', 'host_unknown')
            detections.append(det_dict)
            
            if result.risk_score >= 50:
                print(f"   [ALERT] {result.alert_type.upper()} "
                      f"(score={result.risk_score}, rules={result.rule_matches})")
                
                if interactive:
                    input("   Press Enter to continue...")
        
        # Save detections
        output_dir = Path(f"scenarios/output/{scenario_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "detections.jsonl", 'w') as f:
            for det in detections:
                f.write(json.dumps(det) + '\n')
        
        # Compute metrics
        print("[4/4] Computing metrics...")
        labels_path = Path(config.labels_csv)
        
        if labels_path.exists():
            try:
                calculator = MetricsCalculator(threshold=50)
                labels = calculator.load_ground_truth(str(labels_path))
                metrics = calculator.compute_all_metrics(detections, labels)
                MetricsReporter.print_summary(metrics)
                MetricsReporter.save_csv(metrics, str(output_dir / "metrics.csv"))
                metrics_dict = metrics.to_dict()
            except Exception as e:
                print(f"   [WARNING] Metrics computation failed: {e}")
                metrics_dict = None
        else:
            print("   [WARNING] No labels file - skipping metrics")
            metrics_dict = None
        
        print(f"\n[OK] Scenario '{scenario_name}' completed")
        print(f"   Results saved to: {output_dir}")
        
        return {
            'scenario': scenario_name,
            'events': len(events),
            'feature_rows': len(feature_rows),
            'detections': detections,
            'metrics': metrics_dict
        }
    
    def run_all_scenarios(self) -> Dict[str, Dict]:
        """Run all available scenarios"""
        results = {}
        
        for name in SCENARIOS:
            try:
                results[name] = self.run_scenario(name)
            except Exception as e:
                print(f"[ERROR] Scenario {name} failed: {e}")
                results[name] = {'error': str(e)}
        
        return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CyberShell Scenario Runner",
        epilog="Run packaged demo scenarios through the detection pipeline"
    )
    
    parser.add_argument("--scenario", 
                        choices=list(SCENARIOS.keys()) + ['all'],
                        default="malicious-ransomware",
                        help="Scenario to run (default: malicious-ransomware)")
    
    parser.add_argument("--simulate", action="store_true", default=True,
                        help="Simulate mode - no real actions (default)")
    
    parser.add_argument("--interactive", action="store_true",
                        help="Pause at each alert for user input")
    
    parser.add_argument("--list", action="store_true",
                        help="List available scenarios")
    
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable Scenarios:")
        print("-" * 40)
        for name, config in SCENARIOS.items():
            print(f"  {name}: {config.description}")
        return
    
    runner = ScenarioRunner(simulate=args.simulate)
    
    if args.scenario == 'all':
        results = runner.run_all_scenarios()
        
        print("\n" + "=" * 60)
        print("ALL SCENARIOS SUMMARY")
        print("=" * 60)
        for name, result in results.items():
            if 'error' in result:
                print(f"  [FAIL] {name}: {result['error']}")
            else:
                metrics = result.get('metrics') or {}
                tpr = metrics.get('tpr', 0)
                fpr = metrics.get('fpr', 0)
                if isinstance(tpr, (int, float)) and isinstance(fpr, (int, float)):
                    print(f"  [OK] {name}: TPR={tpr:.2%}, FPR={fpr:.2%}")
                else:
                    print(f"  [OK] {name}: Completed (no metrics)")
    else:
        runner.run_scenario(args.scenario, interactive=args.interactive)


if __name__ == "__main__":
    main()
