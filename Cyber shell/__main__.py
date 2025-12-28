# CyberShell Main Entry Point
# ============================
# Unified CLI for all CyberShell operations

"""
CyberShell - AI-Based Endpoint Detection Prototype
===================================================

Usage:
    python -m cybershell collect --sysmon data/sysmon.csv
    python -m cybershell detect --input features.jsonl
    python -m cybershell scenario --name malicious-ransomware
    python -m cybershell ui --simulate
    python -m cybershell metrics --scenario-dir scenarios/data/

All commands default to simulate mode for safety.
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="CyberShell - AI-Based Endpoint Detection",
        epilog="For hackathon demo, use: python __main__.py scenario --name malicious-ransomware"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect telemetry data')
    collect_parser.add_argument('--sysmon', help='Sysmon CSV file')
    collect_parser.add_argument('--pcap', help='PCAP file')
    collect_parser.add_argument('--output', default='events.jsonl', help='Output file')
    
    # Detect command  
    detect_parser = subparsers.add_parser('detect', help='Run detection engine')
    detect_parser.add_argument('--input', required=True, help='Input features JSONL')
    detect_parser.add_argument('--output', default='detections.jsonl', help='Output file')
    detect_parser.add_argument('--threshold', type=int, default=50, help='Alert threshold')
    
    # Scenario command
    scenario_parser = subparsers.add_parser('scenario', help='Run demo scenario')
    scenario_parser.add_argument('--name', default='malicious-ransomware',
                                 choices=['benign', 'benign-anomaly', 'malicious-ransomware', 'all'],
                                 help='Scenario name')
    scenario_parser.add_argument('--simulate', action='store_true', default=True,
                                 help='Simulate mode (default)')
    scenario_parser.add_argument('--generate-data', action='store_true',
                                 help='Generate sample data')
    
    # UI command
    ui_parser = subparsers.add_parser('ui', help='Launch Streamlit dashboard')
    ui_parser.add_argument('--simulate', action='store_true', default=True,
                          help='Simulate mode (default)')
    ui_parser.add_argument('--port', type=int, default=8501, help='Port number')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Compute detection metrics')
    metrics_parser.add_argument('--scenario-dir', help='Scenario data directory')
    metrics_parser.add_argument('--detections', help='Detections JSONL file')
    metrics_parser.add_argument('--labels', help='Labels CSV file')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train ML model')
    train_parser.add_argument('--data', required=True, help='Training data')
    train_parser.add_argument('--output', default='model/model.pkl', help='Model output path')
    
    args = parser.parse_args()
    
    if args.command == 'collect':
        from agent.collector import main as collector_main
        sys.argv = ['collector', '--sysmon-csv', args.sysmon, '--output', args.output]
        collector_main()
        
    elif args.command == 'detect':
        from model.detect import main as detect_main
        sys.argv = ['detect', '--input', args.input, '--output', args.output, 
                   '--threshold', str(args.threshold)]
        detect_main()
        
    elif args.command == 'scenario':
        from scenarios.runner import main as scenario_main
        if args.generate_data:
            sys.argv = ['runner', '--generate-data']
        else:
            sys.argv = ['runner', '--scenario', args.name]
            if args.simulate:
                sys.argv.append('--simulate')
        scenario_main()
        
    elif args.command == 'ui':
        import subprocess
        cmd = ['streamlit', 'run', 'ui/streamlit_app.py', '--',
               '--simulate' if args.simulate else '']
        subprocess.run(cmd)
        
    elif args.command == 'metrics':
        from metrics.compute_metrics import main as metrics_main
        sys.argv = ['metrics']
        if args.scenario_dir:
            sys.argv.extend(['--scenario-dir', args.scenario_dir])
        elif args.detections and args.labels:
            sys.argv.extend(['--detections', args.detections, '--labels', args.labels])
        metrics_main()
        
    elif args.command == 'train':
        from model.train_model import main as train_main
        sys.argv = ['train', '--data', args.data, '--model', args.output]
        train_main()
        
    else:
        parser.print_help()
        print("\n[TIP] Quick start: python __main__.py scenario --name malicious-ransomware")


if __name__ == "__main__":
    main()
