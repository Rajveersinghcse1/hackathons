"""
CyberShell Model - Detection Module
=====================================

Purpose: Score feature rows using hybrid detection
Approach: Rules (Layer 1) + ML Anomaly (Layer 2)

Output per feature row:
- risk_score: 0-100 (combined score)
- alert_type: Classification of threat type
- rule_matches: Which rules triggered
- top_3_features: Most contributing features (explainability)
- evidence: Supporting data for investigation

Safety: Detection only - no automated actions
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
import joblib

# Add parent to path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from parser.feature_extractor import FeatureRow


# =============================================================================
# DETECTION RESULT STRUCTURE
# =============================================================================

@dataclass
class DetectionResult:
    """Result from hybrid detection engine"""
    # Core fields for test compatibility
    is_malicious: bool = False       # True if threat detected
    confidence: float = 0.0          # 0.0-1.0 confidence
    detection_layer: int = 0         # 1=rules, 2=ML, 0=none
    rule_name: Optional[str] = None  # Name of triggered rule
    category: str = "benign"         # Threat category
    top_features: List[str] = None   # Top contributing features
    explanation: str = ""            # Human-readable explanation
    
    # Extended fields
    timestamp: str = ""
    host_hash: str = ""
    risk_score: int = 0              # 0-100 combined score
    rule_score: int = 0              # 0-100 from rules only
    ml_score: int = 0                # 0-100 from ML only
    alert_type: str = "benign"       # Alias for category
    severity: str = "info"           # 'critical', 'high', 'medium', 'low', 'info'
    rule_matches: List[str] = None   # List of rule IDs that matched
    top_3_features: List[Dict] = None  # Top 3 contributing features with values
    evidence: Dict[str, Any] = None  # Supporting evidence
    detection_time_ms: float = 0.0   # Time taken to score
    
    def __post_init__(self):
        if self.top_features is None:
            self.top_features = []
        if self.rule_matches is None:
            self.rule_matches = []
        if self.top_3_features is None:
            self.top_3_features = []
        if self.evidence is None:
            self.evidence = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_alert(self) -> Dict[str, Any]:
        """Format as alert for UI display"""
        return {
            'id': f"{self.host_hash}_{self.timestamp}",
            'timestamp': self.timestamp,
            'host': self.host_hash,
            'type': self.alert_type,
            'severity': self.severity,
            'risk_score': self.risk_score,
            'summary': self._generate_summary(),
            'top_features': self.top_3_features,
            'rules': self.rule_matches,
        }
    
    def _generate_summary(self) -> str:
        """Generate human-readable summary"""
        summaries = {
            'ransomware': "Potential ransomware activity detected - high file write/rename rate",
            'exfil': "Possible data exfiltration - unusual outbound traffic volume",
            'c2': "Potential C2 beaconing - periodic outbound connections detected",
            'lateral': "Lateral movement indicators - unusual authentication patterns",
            'lolbin': "Living-off-the-Land technique - suspicious use of system binaries",
            'anomaly': "Behavioral anomaly - activity deviates from baseline",
            'benign': "Normal activity - no threats detected"
        }
        return self.explanation or summaries.get(self.category, "Unknown activity pattern")


# =============================================================================
# RULE DEFINITIONS
# =============================================================================

@dataclass
class DetectionRule:
    """Single detection rule definition"""
    id: str
    name: str
    description: str
    severity: str                    # critical, high, medium, low
    category: str                    # ransomware, exfil, c2, lateral, lolbin
    
    # Conditions (callable or threshold-based)
    conditions: Dict[str, Any]       # Feature thresholds or patterns
    
    def matches(self, features: FeatureRow) -> Tuple[bool, float]:
        """
        Check if rule matches feature row.
        Returns: (matched: bool, confidence: float)
        """
        matched_conditions = 0
        total_conditions = len(self.conditions)
        
        for feature_name, threshold in self.conditions.items():
            value = getattr(features, feature_name, None)
            
            if value is None:
                continue
            
            if isinstance(threshold, dict):
                # Complex condition
                if 'min' in threshold and value >= threshold['min']:
                    matched_conditions += 1
                elif 'max' in threshold and value <= threshold['max']:
                    matched_conditions += 1
                elif 'equals' in threshold and value == threshold['equals']:
                    matched_conditions += 1
                elif 'contains' in threshold and threshold['contains'] in str(value):
                    matched_conditions += 1
            else:
                # Simple threshold (greater than)
                if value >= threshold:
                    matched_conditions += 1
        
        if total_conditions == 0:
            return False, 0.0
        
        confidence = matched_conditions / total_conditions
        matched = confidence >= 0.5  # At least half conditions must match
        
        return matched, confidence


class RuleEngine:
    """
    Rule-based detection engine (Layer 1).
    
    Rules are checked in priority order:
    1. Ransomware (high priority)
    2. Exfiltration (high priority)
    3. C2/Beaconing (medium-high)
    4. Lateral Movement (medium)
    5. LOLBins (medium)
    """
    
    def __init__(self):
        self.rules = self._define_rules()
    
    def _define_rules(self) -> List[DetectionRule]:
        """Define all detection rules"""
        return [
            # === RANSOMWARE RULES (High Priority) ===
            DetectionRule(
                id="RANSOM-001",
                name="High File Write Rate",
                description="Excessive file write operations indicating possible encryption",
                severity="critical",
                category="ransomware",
                conditions={
                    'file_write_rate_1m': 50,  # >50 writes per minute
                }
            ),
            DetectionRule(
                id="RANSOM-002",
                name="Mass File Rename",
                description="Many file renames indicating ransomware extension changes",
                severity="critical",
                category="ransomware",
                conditions={
                    'file_rename_count_5m': 30,  # >30 renames in 5 min
                    'unique_extensions_written': 5,  # Multiple new extensions
                }
            ),
            DetectionRule(
                id="RANSOM-003",
                name="Ransomware Score Threshold",
                description="Combined ransomware indicators above threshold",
                severity="high",
                category="ransomware",
                conditions={
                    'ransomware_score': 0.6,  # Composite score >0.6
                }
            ),
            
            # === EXFILTRATION RULES (High Priority) ===
            DetectionRule(
                id="EXFIL-001",
                name="Large Outbound Transfer",
                description="Unusually large outbound data transfer",
                severity="high",
                category="exfil",
                conditions={
                    'outbound_bytes_5m': 50_000_000,  # >50MB in 5 min
                }
            ),
            DetectionRule(
                id="EXFIL-002",
                name="Many Unique Destinations",
                description="Connections to unusually many unique IPs",
                severity="medium",
                category="exfil",
                conditions={
                    'unique_dst_ips_1hr': 30,  # >30 unique IPs
                    'unique_dst_ports_1hr': 10,  # Multiple ports
                }
            ),
            DetectionRule(
                id="EXFIL-003",
                name="Exfil Score Threshold",
                description="Combined exfiltration indicators above threshold",
                severity="high",
                category="exfil",
                conditions={
                    'exfil_score': 0.6,
                }
            ),
            
            # === C2/BEACONING RULES (Medium-High) ===
            DetectionRule(
                id="C2-001",
                name="Periodic Connections",
                description="Regular interval connections suggesting beaconing",
                severity="high",
                category="c2",
                conditions={
                    'periodic_connection_score': 0.7,  # High regularity
                }
            ),
            DetectionRule(
                id="C2-002",
                name="DNS Tunneling Indicator",
                description="Unusual DNS query patterns",
                severity="medium",
                category="c2",
                conditions={
                    'dns_query_count_5m': 100,  # High DNS activity
                    'dns_txt_query_count': 5,   # TXT queries (tunneling)
                }
            ),
            DetectionRule(
                id="C2-003",
                name="Beacon Score Threshold",
                description="Combined C2 indicators above threshold",
                severity="high",
                category="c2",
                conditions={
                    'c2_beacon_score': 0.6,
                }
            ),
            
            # === LATERAL MOVEMENT RULES (Medium) ===
            DetectionRule(
                id="LATERAL-001",
                name="Brute Force Attempt",
                description="Multiple failed logon attempts",
                severity="high",
                category="lateral",
                conditions={
                    'failed_logons_10m': 10,
                }
            ),
            DetectionRule(
                id="LATERAL-002",
                name="Password Spray",
                description="Failed logons across multiple accounts",
                severity="high",
                category="lateral",
                conditions={
                    'unique_failed_users_1hr': 5,
                }
            ),
            DetectionRule(
                id="LATERAL-003",
                name="Unusual Remote Logons",
                description="Excessive RDP/remote logon activity",
                severity="medium",
                category="lateral",
                conditions={
                    'remote_logon_count': 10,
                }
            ),
            
            # === LOLBIN RULES (Medium) ===
            DetectionRule(
                id="LOLBIN-001",
                name="LOLBin Execution",
                description="Living-off-the-Land binary used",
                severity="medium",
                category="lolbin",
                conditions={
                    'is_lolbin': 1,
                    'cmdline_entropy': 4.0,  # High entropy command
                }
            ),
            DetectionRule(
                id="LOLBIN-002",
                name="Base64 Command",
                description="Base64 encoded command detected",
                severity="high",
                category="lolbin",
                conditions={
                    'cmdline_has_base64': 1,
                }
            ),
            DetectionRule(
                id="LOLBIN-003",
                name="Unusual Process Path",
                description="Process running from suspicious location",
                severity="medium",
                category="lolbin",
                conditions={
                    'is_unusual_path': 1,
                }
            ),
        ]
    
    def evaluate(self, features: FeatureRow) -> Tuple[List[str], int, str, str, float]:
        """
        Evaluate all rules against feature row.
        
        Returns:
            (matched_rules, rule_score, category, severity, confidence)
        """
        matched_rules = []
        max_severity = 'info'
        max_confidence = 0.0
        primary_category = 'benign'
        
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
        category_counts = {}
        
        for rule in self.rules:
            matched, confidence = rule.matches(features)
            
            if matched:
                matched_rules.append(rule.id)
                category_counts[rule.category] = category_counts.get(rule.category, 0) + 1
                
                if severity_order.get(rule.severity, 0) > severity_order.get(max_severity, 0):
                    max_severity = rule.severity
                
                if confidence > max_confidence:
                    max_confidence = confidence
        
        # Determine primary category
        if category_counts:
            primary_category = max(category_counts.items(), key=lambda x: x[1])[0]
        
        # Calculate rule score (0-100)
        # Severity-based scoring: critical=40, high=30, medium=20, low=10
        severity_scores = {'critical': 40, 'high': 30, 'medium': 20, 'low': 10}
        rule_score = min(
            sum(severity_scores.get(
                next((r.severity for r in self.rules if r.id == rule_id), 'low'),
                10
            ) for rule_id in matched_rules),
            100
        )
        
        # Minimum score if any rule matched
        if matched_rules:
            rule_score = max(rule_score, 40)
        
        return matched_rules, rule_score, primary_category, max_severity, max_confidence


# =============================================================================
# ML ANOMALY DETECTOR
# =============================================================================

class MLAnomalyDetector:
    """
    ML-based anomaly detection (Layer 2).
    Uses trained IsolationForest model.
    
    Scoring:
    - decision_function returns anomaly score (negative = anomaly)
    - Converted to 0-100 scale for UI
    """
    
    def __init__(self, model_path: str = "model/model.pkl",
                 scaler_path: str = "model/scaler.pkl",
                 config_path: str = "model/config.json"):
        self.model = None
        self.scaler = None
        self.config = None
        self.feature_names = []
        
        # Load model if exists
        self._load_model(model_path, scaler_path, config_path)
    
    def _load_model(self, model_path: str, scaler_path: str, config_path: str):
        """Load trained model and scaler"""
        model_file = Path(model_path)
        scaler_file = Path(scaler_path)
        config_file = Path(config_path)
        
        if model_file.exists():
            self.model = joblib.load(model_file)
            print(f"[INFO] Loaded model from {model_path}")
        else:
            print(f"[WARNING] No model found at {model_path}")
        
        if scaler_file.exists():
            self.scaler = joblib.load(scaler_file)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
                self.feature_names = self.config.get('feature_names', [])
    
    def score(self, features: FeatureRow) -> Tuple[int, List[Dict]]:
        """
        Score feature row with ML model.
        
        Returns:
            (ml_score: 0-100, top_features: list of contributing features)
        """
        if self.model is None:
            # Return neutral score if no model
            return 50, []
        
        # Extract ML features
        feature_vector = np.array(features.to_ml_features()).reshape(1, -1)
        
        # Scale if scaler available
        if self.scaler:
            feature_vector = self.scaler.transform(feature_vector)
        
        # Get anomaly score
        # decision_function: positive = normal, negative = anomaly
        decision_score = self.model.decision_function(feature_vector)[0]
        
        # Convert to 0-100 scale
        # Typical range is [-0.5, 0.5], map to [100, 0]
        ml_score = int(max(0, min(100, 50 - decision_score * 100)))
        
        # Get feature contributions (approximation)
        top_features = self._get_feature_contributions(features, feature_vector[0])
        
        return ml_score, top_features
    
    def _get_feature_contributions(self, features: FeatureRow, 
                                   scaled_vector: np.ndarray) -> List[Dict]:
        """
        Calculate which features contribute most to the anomaly score.
        Uses deviation from mean as proxy for contribution.
        """
        contributions = []
        feature_values = features.to_ml_features()
        feature_names = FeatureRow.feature_names()
        
        for i, (name, value, scaled) in enumerate(zip(feature_names, feature_values, scaled_vector)):
            # Deviation from 0 in scaled space indicates abnormality
            deviation = abs(scaled)
            contributions.append({
                'feature': name,
                'value': value,
                'scaled_deviation': float(deviation),
                'contribution_rank': 0  # Will be set after sorting
            })
        
        # Sort by deviation and get top 3
        contributions.sort(key=lambda x: x['scaled_deviation'], reverse=True)
        
        for i, c in enumerate(contributions[:3]):
            c['contribution_rank'] = i + 1
        
        return contributions[:3]


# =============================================================================
# HYBRID DETECTOR (Main Class)
# =============================================================================

class HybridDetector:
    """
    Combined rule-based and ML detection.
    
    Detection flow:
    1. Rules evaluate feature row → rule_score, matched_rules
    2. ML evaluates feature row → ml_score, top_features
    3. Combine scores with weighting
    4. Generate final DetectionResult
    
    Usage:
        detector = HybridDetector()
        result = detector.detect(feature_row)
        if result.risk_score > 70:
            alert(result)
    """
    
    def __init__(self, model_path: str = "model/model.pkl",
                 rule_weight: float = 0.6,
                 ml_weight: float = 0.4,
                 enable_explainability: bool = True,
                 enable_mitre_mapping: bool = True):
        """
        Args:
            model_path: Path to trained ML model
            rule_weight: Weight for rule-based score (0-1)
            ml_weight: Weight for ML score (0-1)
            enable_explainability: Enable SHAP-based explanations
            enable_mitre_mapping: Enable MITRE ATT&CK threat intelligence
        """
        self.rule_engine = RuleEngine()
        self.ml_detector = MLAnomalyDetector(model_path)
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight
        self.enable_explainability = enable_explainability
        self.enable_mitre_mapping = enable_mitre_mapping
        
        # Initialize SHAP explainer if enabled
        self.shap_explainer = None
        if enable_explainability:
            try:
                from model.explainability import SHAPExplainer, LocalInterpretability
                if self.ml_detector.model:
                    # Get feature names from ML detector config or use defaults
                    feature_names = self.ml_detector.feature_names if self.ml_detector.feature_names else None
                    self.shap_explainer = SHAPExplainer(self.ml_detector.model, feature_names)
                    self.local_interpreter = LocalInterpretability()
                    print("[INFO] SHAP explainability enabled")
            except ImportError:
                print("[WARNING] SHAP not available - install with: pip install shap")
                self.enable_explainability = False
            except Exception as e:
                print(f"[WARNING] SHAP initialization failed: {e}")
                self.enable_explainability = False
        
        # Initialize MITRE mapper if enabled
        self.mitre_mapper = None
        if enable_mitre_mapping:
            try:
                from model.threat_intelligence import MITREMapper
                self.mitre_mapper = MITREMapper
                print("[INFO] MITRE ATT&CK mapping enabled")
            except ImportError:
                print("[WARNING] MITRE module not available")
                self.enable_mitre_mapping = False
    
    def detect(self, features: FeatureRow) -> DetectionResult:
        """
        Run hybrid detection on feature row.
        
        Returns:
            DetectionResult with scores, classification, and explainability
        """
        import time
        start_time = time.time()
        
        # Layer 1: Rule-based detection
        matched_rules, rule_score, category, severity, rule_confidence = \
            self.rule_engine.evaluate(features)
        
        # Layer 2: ML anomaly detection
        ml_score, top_features = self.ml_detector.score(features)
        
        # Combine scores
        combined_score = int(
            rule_score * self.rule_weight + 
            ml_score * self.ml_weight
        )
        
        # Adjust category based on ML if rules didn't match
        alert_type = category
        if category == 'benign' and ml_score > 70:
            alert_type = 'anomaly'
        
        # Adjust severity based on combined score
        if combined_score >= 80:
            severity = 'critical'
        elif combined_score >= 60:
            severity = max(severity, 'high', key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x, 0))
        elif combined_score >= 40:
            severity = max(severity, 'medium', key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x, 0))
        
        # Calculate final confidence
        confidence = max(rule_confidence, ml_score / 100)
        
        # Build evidence
        evidence = {
            'process': features.process_name,
            'parent': features.parent_process,
            'cmdline_entropy': features.cmdline_entropy,
            'network_summary': {
                'outbound_bytes_5m': features.outbound_bytes_5m,
                'unique_destinations': features.unique_dst_ips_1hr,
            },
            'file_summary': {
                'write_rate': features.file_write_rate_1m,
                'renames': features.file_rename_count_5m,
            },
            'auth_summary': {
                'failed_logons': features.failed_logons_10m,
            }
        }
        
        detection_time = (time.time() - start_time) * 1000  # ms
        
        # Create base detection result
        result = DetectionResult(
            timestamp=features.timestamp,
            host_hash=features.host_hash,
            risk_score=combined_score,
            rule_score=rule_score,
            ml_score=ml_score,
            alert_type=alert_type,
            category=alert_type,
            severity=severity,
            confidence=confidence,
            is_malicious=(combined_score >= 50),
            detection_layer=(1 if matched_rules else 2 if ml_score > 50 else 0),
            rule_name=matched_rules[0] if matched_rules else None,
            rule_matches=matched_rules,
            top_3_features=top_features,
            evidence=evidence,
            detection_time_ms=round(detection_time, 2)
        )
        
        # === ENHANCEMENT 1: SHAP EXPLAINABILITY ===
        if self.enable_explainability and self.shap_explainer and combined_score >= 40:
            try:
                # Get SHAP explanation for this detection
                feature_vector = np.array(features.to_ml_features()).reshape(1, -1)
                if self.ml_detector.scaler:
                    feature_vector = self.ml_detector.scaler.transform(feature_vector)
                
                shap_result = self.shap_explainer.explain_single(
                    feature_vector[0],
                    feature_names=self.ml_detector.feature_names or [f"feature_{i}" for i in range(len(feature_vector[0]))]
                )
                
                # Generate natural language explanation
                nl_explanation = self.local_interpreter.generate_explanation(
                    shap_result, 
                    alert_type
                )
                
                # Attach to result
                result.explanation = nl_explanation
                result.evidence['shap_values'] = {
                    'base_value': float(shap_result.base_value),
                    'prediction': float(shap_result.prediction),
                    'top_positive_features': [
                        {'feature': f, 'contribution': float(c)} 
                        for f, c in shap_result.top_positive_features[:5]
                    ],
                    'top_negative_features': [
                        {'feature': f, 'contribution': float(c)} 
                        for f, c in shap_result.top_negative_features[:3]
                    ]
                }
            except Exception as e:
                print(f"[WARNING] SHAP explanation failed: {e}")
        
        # === ENHANCEMENT 2: MITRE ATT&CK MAPPING ===
        if self.enable_mitre_mapping and self.mitre_mapper and combined_score >= 40:
            try:
                mitre_intel = self.mitre_mapper.enrich_detection(result)
                result.evidence['mitre_attack'] = mitre_intel.to_dict()
                result.evidence['kill_chain_phase'] = mitre_intel.kill_chain_phase
                result.evidence['recommended_actions'] = mitre_intel.recommended_actions
                
                # Update explanation with MITRE context if not already set
                if not result.explanation:
                    technique = mitre_intel.primary_technique
                    result.explanation = f"Detected {technique.technique_name} (MITRE {technique.technique_id}). {mitre_intel.severity_justification}"
            except Exception as e:
                print(f"[WARNING] MITRE mapping failed: {e}")
        
        return result
    
    def detect_batch(self, feature_rows: List[FeatureRow]) -> List[DetectionResult]:
        """Detect on multiple feature rows"""
        return [self.detect(row) for row in feature_rows]


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Detector")
    parser.add_argument("--input", required=True,
                        help="Input features JSONL file")
    parser.add_argument("--output", default="detections.jsonl",
                        help="Output detections JSONL file")
    parser.add_argument("--model", default="model/model.pkl",
                        help="Path to trained model")
    parser.add_argument("--threshold", type=int, default=50,
                        help="Alert threshold (0-100)")
    
    args = parser.parse_args()
    
    detector = HybridDetector(model_path=args.model)
    
    alerts = 0
    total = 0
    
    with open(args.input, 'r') as f_in, open(args.output, 'w') as f_out:
        for line in f_in:
            row_data = json.loads(line)
            features = FeatureRow(**row_data)
            
            result = detector.detect(features)
            total += 1
            
            f_out.write(json.dumps(result.to_dict()) + '\n')
            
            if result.risk_score >= args.threshold:
                alerts += 1
                print(f"[ALERT] {result.severity.upper()}: {result.alert_type} "
                      f"(score={result.risk_score}) - {result.host_hash}")
    
    print(f"\n[INFO] Processed {total} feature rows, generated {alerts} alerts")


if __name__ == "__main__":
    main()
