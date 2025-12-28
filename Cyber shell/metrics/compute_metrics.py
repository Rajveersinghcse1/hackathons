"""
CyberShell Metrics - Performance Measurement Module
====================================================

Purpose: Compute detection quality metrics
Metrics: TPR, FPR, Precision, Recall, F1, MTTD, Alert Reduction

Input: Detection results + ground truth labels
Output: Metrics CSV report

Usage:
    python -m metrics.compute_metrics --detections detections.jsonl --labels labels.csv
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class MetricsResult:
    """Complete metrics output"""
    # Basic classification metrics
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    
    # Derived metrics
    tpr: float                       # True Positive Rate (Recall/Sensitivity)
    fpr: float                       # False Positive Rate
    precision: float                 # Precision (PPV)
    recall: float                    # Recall (same as TPR)
    f1_score: float                  # F1 Score
    accuracy: float                  # Overall accuracy
    
    # Time metrics
    mttd_seconds: float              # Mean Time to Detect
    mttd_human: str                  # Human-readable MTTD
    
    # Alert quality metrics
    raw_alerts: int                  # Alerts from rules alone
    hybrid_alerts: int               # Alerts from hybrid system
    alert_reduction_pct: float       # Reduction percentage
    
    # Per-category metrics
    category_metrics: Dict[str, Dict[str, float]]
    
    # Metadata
    total_samples: int
    threshold_used: int
    evaluation_time: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_csv_row(self) -> Dict[str, Any]:
        """Flatten for CSV output"""
        row = {
            'timestamp': self.evaluation_time,
            'total_samples': self.total_samples,
            'threshold': self.threshold_used,
            'TP': self.true_positives,
            'FP': self.false_positives,
            'TN': self.true_negatives,
            'FN': self.false_negatives,
            'TPR': round(self.tpr, 4),
            'FPR': round(self.fpr, 4),
            'Precision': round(self.precision, 4),
            'Recall': round(self.recall, 4),
            'F1': round(self.f1_score, 4),
            'Accuracy': round(self.accuracy, 4),
            'MTTD_seconds': round(self.mttd_seconds, 2),
            'Raw_Alerts': self.raw_alerts,
            'Hybrid_Alerts': self.hybrid_alerts,
            'Alert_Reduction_Pct': round(self.alert_reduction_pct, 2),
        }
        return row


@dataclass
class GroundTruthLabel:
    """Ground truth for a single sample"""
    timestamp: str
    host_hash: str
    is_malicious: bool               # True = malicious, False = benign
    attack_type: str                 # 'ransomware', 'exfil', 'c2', 'benign', etc.
    attack_start_time: Optional[str] # When attack started (for MTTD)


# =============================================================================
# METRICS CALCULATOR
# =============================================================================

class MetricsCalculator:
    """
    Computes detection quality metrics.
    
    Ground Truth Format (CSV):
        timestamp,host_hash,is_malicious,attack_type,attack_start_time
        2024-01-01T10:00:00,host_abc,true,ransomware,2024-01-01T09:55:00
        2024-01-01T10:05:00,host_def,false,benign,
    
    Detection Format (JSONL):
        {"timestamp": "...", "host_hash": "...", "risk_score": 75, ...}
    """
    
    def __init__(self, threshold: int = 50):
        """
        Args:
            threshold: Risk score threshold for alerting (0-100)
        """
        self.threshold = threshold
        
    def load_ground_truth(self, labels_path: str) -> List[GroundTruthLabel]:
        """Load ground truth labels from CSV"""
        labels = []
        
        with open(labels_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                labels.append(GroundTruthLabel(
                    timestamp=row['timestamp'],
                    host_hash=row['host_hash'],
                    is_malicious=row['is_malicious'].lower() == 'true',
                    attack_type=row.get('attack_type', 'unknown'),
                    attack_start_time=row.get('attack_start_time') or None
                ))
        
        return labels
    
    def load_detections(self, detections_path: str) -> List[Dict[str, Any]]:
        """Load detection results from JSONL"""
        detections = []
        
        with open(detections_path, 'r') as f:
            for line in f:
                detections.append(json.loads(line))
        
        return detections
    
    def match_detections_to_labels(self, detections: List[Dict], 
                                   labels: List[GroundTruthLabel],
                                   time_window_seconds: int = 300
                                   ) -> List[Tuple[Dict, Optional[GroundTruthLabel]]]:
        """
        Match detections to ground truth labels based on timestamp and host.
        
        Args:
            time_window_seconds: How close timestamps must be to match
        """
        matched = []
        
        for detection in detections:
            det_time = datetime.fromisoformat(detection['timestamp'].replace('Z', ''))
            det_host = detection['host_hash']
            
            best_match = None
            best_delta = timedelta(seconds=time_window_seconds + 1)
            
            for label in labels:
                label_time = datetime.fromisoformat(label.timestamp.replace('Z', ''))
                
                if label.host_hash == det_host:
                    delta = abs(det_time - label_time)
                    if delta < best_delta:
                        best_delta = delta
                        best_match = label
            
            if best_delta.total_seconds() <= time_window_seconds:
                matched.append((detection, best_match))
            else:
                matched.append((detection, None))
        
        return matched
    
    def compute_basic_metrics(self, detections: List[Dict],
                             labels: List[GroundTruthLabel]) -> Dict[str, int]:
        """Compute TP, FP, TN, FN"""
        matched = self.match_detections_to_labels(detections, labels)
        
        tp = fp = tn = fn = 0
        
        for detection, label in matched:
            predicted_positive = detection['risk_score'] >= self.threshold
            actual_positive = label.is_malicious if label else False
            
            if predicted_positive and actual_positive:
                tp += 1
            elif predicted_positive and not actual_positive:
                fp += 1
            elif not predicted_positive and not actual_positive:
                tn += 1
            elif not predicted_positive and actual_positive:
                fn += 1
        
        return {'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn}
    
    def compute_mttd(self, detections: List[Dict],
                    labels: List[GroundTruthLabel]) -> float:
        """
        Compute Mean Time to Detect.
        
        MTTD = average(first_detection_time - attack_start_time)
        Only computed for true positives with known attack start times.
        """
        detection_times = []
        
        matched = self.match_detections_to_labels(detections, labels)
        
        for detection, label in matched:
            if label and label.is_malicious and label.attack_start_time:
                if detection['risk_score'] >= self.threshold:
                    det_time = datetime.fromisoformat(detection['timestamp'].replace('Z', ''))
                    attack_start = datetime.fromisoformat(label.attack_start_time.replace('Z', ''))
                    
                    if det_time >= attack_start:
                        ttd = (det_time - attack_start).total_seconds()
                        detection_times.append(ttd)
        
        if detection_times:
            return sum(detection_times) / len(detection_times)
        return 0.0
    
    def compute_alert_reduction(self, detections: List[Dict]) -> Tuple[int, int, float]:
        """
        Compute alert reduction from rules-only to hybrid.
        
        Returns:
            (raw_alerts, hybrid_alerts, reduction_percentage)
        """
        # Rules-only alerts: count by rule_score threshold
        raw_alerts = sum(1 for d in detections if d.get('rule_score', 0) >= self.threshold)
        
        # Hybrid alerts: count by combined risk_score threshold
        hybrid_alerts = sum(1 for d in detections if d['risk_score'] >= self.threshold)
        
        if raw_alerts > 0:
            reduction_pct = ((raw_alerts - hybrid_alerts) / raw_alerts) * 100
        else:
            reduction_pct = 0.0
        
        return raw_alerts, hybrid_alerts, reduction_pct
    
    def compute_category_metrics(self, detections: List[Dict],
                                 labels: List[GroundTruthLabel]) -> Dict[str, Dict[str, float]]:
        """Compute metrics per attack category"""
        categories = defaultdict(lambda: {'TP': 0, 'FP': 0, 'FN': 0})
        
        matched = self.match_detections_to_labels(detections, labels)
        
        for detection, label in matched:
            if label is None:
                continue
            
            category = label.attack_type
            predicted_positive = detection['risk_score'] >= self.threshold
            actual_positive = label.is_malicious
            
            if predicted_positive and actual_positive:
                categories[category]['TP'] += 1
            elif predicted_positive and not actual_positive:
                # For FP, use predicted category
                pred_category = detection.get('alert_type', 'unknown')
                categories[pred_category]['FP'] += 1
            elif not predicted_positive and actual_positive:
                categories[category]['FN'] += 1
        
        # Calculate per-category precision/recall
        result = {}
        for category, counts in categories.items():
            tp = counts['TP']
            fp = counts['FP']
            fn = counts['FN']
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            result[category] = {
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4),
                'tp': tp,
                'fp': fp,
                'fn': fn
            }
        
        return result
    
    def compute_all_metrics(self, detections: List[Dict],
                           labels: List[GroundTruthLabel]) -> MetricsResult:
        """Compute all metrics and return result object"""
        
        # Basic counts
        basic = self.compute_basic_metrics(detections, labels)
        tp, fp, tn, fn = basic['TP'], basic['FP'], basic['TN'], basic['FN']
        
        # Derived metrics
        total = tp + fp + tn + fn
        
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tpr
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / total if total > 0 else 0.0
        
        # MTTD
        mttd = self.compute_mttd(detections, labels)
        mttd_human = self._format_duration(mttd)
        
        # Alert reduction
        raw_alerts, hybrid_alerts, reduction_pct = self.compute_alert_reduction(detections)
        
        # Category metrics
        category_metrics = self.compute_category_metrics(detections, labels)
        
        return MetricsResult(
            true_positives=tp,
            false_positives=fp,
            true_negatives=tn,
            false_negatives=fn,
            tpr=tpr,
            fpr=fpr,
            precision=precision,
            recall=recall,
            f1_score=f1,
            accuracy=accuracy,
            mttd_seconds=mttd,
            mttd_human=mttd_human,
            raw_alerts=raw_alerts,
            hybrid_alerts=hybrid_alerts,
            alert_reduction_pct=reduction_pct,
            category_metrics=category_metrics,
            total_samples=len(detections),
            threshold_used=self.threshold,
            evaluation_time=datetime.now().isoformat()
        )
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds as human-readable duration"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class MetricsReporter:
    """Generate various report formats"""
    
    @staticmethod
    def print_summary(metrics: MetricsResult):
        """Print human-readable summary to console"""
        print("\n" + "=" * 60)
        print("📊 CYBERSHELL DETECTION METRICS REPORT")
        print("=" * 60)
        
        print(f"\n📈 Overall Performance (threshold={metrics.threshold_used}):")
        print(f"   Total Samples: {metrics.total_samples}")
        print(f"   TP: {metrics.true_positives} | FP: {metrics.false_positives} | "
              f"TN: {metrics.true_negatives} | FN: {metrics.false_negatives}")
        
        print(f"\n📉 Detection Rates:")
        print(f"   TPR (Recall):    {metrics.tpr:.2%}")
        print(f"   FPR:             {metrics.fpr:.2%}")
        print(f"   Precision:       {metrics.precision:.2%}")
        print(f"   F1 Score:        {metrics.f1_score:.2%}")
        print(f"   Accuracy:        {metrics.accuracy:.2%}")
        
        print(f"\n⏱️  Time to Detect:")
        print(f"   MTTD: {metrics.mttd_human}")
        
        print(f"\n🔔 Alert Quality:")
        print(f"   Raw Rules Alerts:    {metrics.raw_alerts}")
        print(f"   Hybrid Alerts:       {metrics.hybrid_alerts}")
        print(f"   Alert Reduction:     {metrics.alert_reduction_pct:.1f}%")
        
        if metrics.category_metrics:
            print(f"\n📂 Per-Category Performance:")
            for category, cm in metrics.category_metrics.items():
                print(f"   {category:15} | P: {cm['precision']:.2f} | "
                      f"R: {cm['recall']:.2f} | F1: {cm['f1']:.2f}")
        
        print("\n" + "=" * 60)
    
    @staticmethod
    def save_csv(metrics: MetricsResult, path: str):
        """Save metrics to CSV"""
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(metrics.to_csv_row().keys()))
            writer.writeheader()
            writer.writerow(metrics.to_csv_row())
        print(f"[INFO] Metrics saved to {path}")
    
    @staticmethod
    def save_json(metrics: MetricsResult, path: str):
        """Save full metrics to JSON"""
        with open(path, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        print(f"[INFO] Full metrics saved to {path}")


# =============================================================================
# SCENARIO EVALUATOR
# =============================================================================

class ScenarioEvaluator:
    """
    Evaluate detection performance across packaged scenarios.
    
    Each scenario has:
    - Input data (Sysmon CSV, PCAP)
    - Ground truth labels
    - Expected detection type
    """
    
    def __init__(self, scenarios_dir: str = "scenarios/data"):
        self.scenarios_dir = Path(scenarios_dir)
        self.calculator = MetricsCalculator()
    
    def evaluate_scenario(self, scenario_name: str) -> Optional[MetricsResult]:
        """Evaluate single scenario"""
        scenario_path = self.scenarios_dir / scenario_name
        
        if not scenario_path.exists():
            print(f"[ERROR] Scenario not found: {scenario_name}")
            return None
        
        # Load detections and labels
        detections_path = scenario_path / "detections.jsonl"
        labels_path = scenario_path / "labels.csv"
        
        if not detections_path.exists() or not labels_path.exists():
            print(f"[ERROR] Missing files for scenario: {scenario_name}")
            return None
        
        detections = self.calculator.load_detections(str(detections_path))
        labels = self.calculator.load_ground_truth(str(labels_path))
        
        return self.calculator.compute_all_metrics(detections, labels)
    
    def evaluate_all_scenarios(self) -> Dict[str, MetricsResult]:
        """Evaluate all scenarios in directory"""
        results = {}
        
        for scenario_dir in self.scenarios_dir.iterdir():
            if scenario_dir.is_dir():
                result = self.evaluate_scenario(scenario_dir.name)
                if result:
                    results[scenario_dir.name] = result
        
        return results
    
    def generate_comparison_report(self, results: Dict[str, MetricsResult],
                                   output_path: str = "scenario_comparison.csv"):
        """Generate comparison CSV across scenarios"""
        rows = []
        
        for scenario_name, metrics in results.items():
            row = metrics.to_csv_row()
            row['scenario'] = scenario_name
            rows.append(row)
        
        if rows:
            with open(output_path, 'w', newline='') as f:
                fieldnames = ['scenario'] + list(rows[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"[INFO] Comparison report saved to {output_path}")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Metrics Calculator")
    parser.add_argument("--detections", help="Path to detections JSONL file")
    parser.add_argument("--labels", help="Path to ground truth labels CSV")
    parser.add_argument("--threshold", type=int, default=50,
                        help="Alert threshold (0-100)")
    parser.add_argument("--output-csv", default="metrics_report.csv",
                        help="Output CSV path")
    parser.add_argument("--output-json", default="metrics_report.json",
                        help="Output JSON path")
    parser.add_argument("--scenario-dir", help="Evaluate all scenarios in directory")
    
    args = parser.parse_args()
    
    if args.scenario_dir:
        # Evaluate all scenarios
        evaluator = ScenarioEvaluator(args.scenario_dir)
        results = evaluator.evaluate_all_scenarios()
        
        for name, metrics in results.items():
            print(f"\n📁 Scenario: {name}")
            MetricsReporter.print_summary(metrics)
        
        evaluator.generate_comparison_report(results)
    
    elif args.detections and args.labels:
        # Evaluate single detection file
        calculator = MetricsCalculator(threshold=args.threshold)
        
        detections = calculator.load_detections(args.detections)
        labels = calculator.load_ground_truth(args.labels)
        
        metrics = calculator.compute_all_metrics(detections, labels)
        
        MetricsReporter.print_summary(metrics)
        MetricsReporter.save_csv(metrics, args.output_csv)
        MetricsReporter.save_json(metrics, args.output_json)
    
    else:
        # Demo with synthetic data
        print("[INFO] Running with demo data...")
        
        # Create synthetic detection data
        demo_detections = [
            {"timestamp": "2024-01-01T10:00:00", "host_hash": "host_a", 
             "risk_score": 85, "rule_score": 80, "alert_type": "ransomware"},
            {"timestamp": "2024-01-01T10:05:00", "host_hash": "host_b",
             "risk_score": 45, "rule_score": 40, "alert_type": "benign"},
            {"timestamp": "2024-01-01T10:10:00", "host_hash": "host_c",
             "risk_score": 75, "rule_score": 70, "alert_type": "exfil"},
        ]
        
        demo_labels = [
            GroundTruthLabel("2024-01-01T10:00:00", "host_a", True, "ransomware", "2024-01-01T09:55:00"),
            GroundTruthLabel("2024-01-01T10:05:00", "host_b", False, "benign", None),
            GroundTruthLabel("2024-01-01T10:10:00", "host_c", True, "exfil", "2024-01-01T10:05:00"),
        ]
        
        calculator = MetricsCalculator(threshold=50)
        metrics = calculator.compute_all_metrics(demo_detections, demo_labels)
        
        MetricsReporter.print_summary(metrics)


if __name__ == "__main__":
    main()
