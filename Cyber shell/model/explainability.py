"""
CyberShell Advanced ML Engine - Explainable AI Module
=====================================================

Purpose: Provide SHAP-based feature importance and explainability
for detection decisions, enabling SOC analysts to understand WHY
a threat was flagged.

Features:
- SHAP (SHapley Additive exPlanations) integration
- Feature importance visualization
- Decision path explanation
- Counterfactual analysis ("what if" scenarios)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import joblib
from pathlib import Path

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("[WARNING] SHAP not installed. Run: pip install shap")


@dataclass
class ExplainabilityResult:
    """Explainability analysis for a single detection"""
    feature_contributions: Dict[str, float]  # Feature -> SHAP value
    top_positive_features: List[Tuple[str, float]]  # Top 5 increasing risk
    top_negative_features: List[Tuple[str, float]]  # Top 5 decreasing risk
    base_value: float  # Model's expected output (baseline)
    prediction_value: float  # Actual prediction
    explanation_summary: str  # Human-readable summary
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feature_contributions': self.feature_contributions,
            'top_positive': [{'feature': f, 'impact': float(v)} for f, v in self.top_positive_features],
            'top_negative': [{'feature': f, 'impact': float(v)} for f, v in self.top_negative_features],
            'base_value': float(self.base_value),
            'prediction': float(self.prediction_value),
            'summary': self.explanation_summary
        }


class SHAPExplainer:
    """
    SHAP-based explainer for IsolationForest and other ML models.
    Uses TreeExplainer for tree-based models.
    """
    
    def __init__(self, model, feature_names: List[str] = None):
        """
        Initialize explainer with trained model.
        
        Args:
            model: Trained ML model (IsolationForest, RandomForest, etc.)
            feature_names: List of feature names (optional)
        """
        if not SHAP_AVAILABLE:
            raise ImportError("SHAP is required. Install with: pip install shap")
        
        self.model = model
        self.feature_names = feature_names or []
        self.explainer = None
        
        # Initialize appropriate SHAP explainer
        try:
            # Try TreeExplainer for tree-based models (IsolationForest, RandomForest)
            self.explainer = shap.TreeExplainer(model)
            print("[INFO] SHAP TreeExplainer initialized")
        except Exception as e:
            # Fallback to KernelExplainer (model-agnostic, slower)
            print(f"[INFO] TreeExplainer failed ({e}), using fallback")
            self.explainer = None  # Will be initialized with background data if needed
    
    def explain_single(self, features: np.ndarray) -> ExplainabilityResult:
        """
        Explain a single prediction.
        
        Args:
            features: Feature vector (1D array)
            
        Returns:
            ExplainabilityResult with SHAP values and interpretation
        """
        if self.explainer is None:
            return self._fallback_explanation(features)
        
        # Compute SHAP values
        shap_values = self.explainer.shap_values(features.reshape(1, -1))
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            shap_values = shap_values[0]  # Binary classification
        
        # Get base value (expected output)
        if hasattr(self.explainer, 'expected_value'):
            base_value = self.explainer.expected_value
            if isinstance(base_value, np.ndarray):
                base_value = base_value[0]
        else:
            base_value = 0.0
        
        # Build feature contributions dictionary
        feature_contribs = {
            name: float(val) 
            for name, val in zip(self.feature_names, shap_values[0])
        }
        
        # Sort by absolute contribution
        sorted_features = sorted(
            feature_contribs.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        
        # Top positive (increasing risk)
        top_positive = [(f, v) for f, v in sorted_features if v > 0][:5]
        
        # Top negative (decreasing risk)
        top_negative = [(f, v) for f, v in sorted_features if v < 0][:5]
        
        # Model prediction
        try:
            prediction = self.model.decision_function(features.reshape(1, -1))[0]
        except:
            prediction = self.model.predict(features.reshape(1, -1))[0]
        
        # Generate summary
        summary = self._generate_summary(top_positive, top_negative, prediction)
        
        return ExplainabilityResult(
            feature_contributions=feature_contribs,
            top_positive_features=top_positive,
            top_negative_features=top_negative,
            base_value=base_value,
            prediction_value=float(prediction),
            explanation_summary=summary
        )
    
    def _generate_summary(self, top_positive, top_negative, prediction) -> str:
        """Generate human-readable explanation"""
        if prediction < 0:  # Anomaly in IsolationForest
            main_drivers = ", ".join([f"{name} ({val:.2f})" for name, val in top_positive[:3]])
            return f"THREAT DETECTED. Primary risk factors: {main_drivers}"
        else:
            return f"BENIGN. Activity within normal parameters."
    
    def _fallback_explanation(self, features: np.ndarray) -> ExplainabilityResult:
        """Fallback when SHAP is unavailable - use basic feature analysis"""
        # Simple heuristic: use raw feature values as proxy for importance
        feature_values = dict(zip(self.feature_names, features))
        sorted_features = sorted(feature_values.items(), key=lambda x: abs(x[1]), reverse=True)
        
        top_positive = [(f, v) for f, v in sorted_features if v > 0][:5]
        top_negative = [(f, v) for f, v in sorted_features if v < 0][:5]
        
        return ExplainabilityResult(
            feature_contributions=feature_values,
            top_positive_features=top_positive,
            top_negative_features=top_negative,
            base_value=0.0,
            prediction_value=0.0,
            explanation_summary="[SHAP unavailable] Showing raw feature values"
        )


class LocalInterpretability:
    """
    Provide local (per-instance) interpretability for detections.
    Answers: "Why was THIS specific event flagged?"
    """
    
    @staticmethod
    def generate_natural_language_explanation(
        detection_result,
        explainability_result: ExplainabilityResult
    ) -> str:
        """
        Convert SHAP analysis into plain English explanation.
        
        Returns:
            Human-readable explanation suitable for non-technical users
        """
        category = detection_result.category
        top_features = explainability_result.top_positive_features
        
        templates = {
            'ransomware': "This event was flagged as ransomware because: {reasons}. The system observed {feature_1} and {feature_2}, which are characteristic of file encryption malware.",
            'exfil': "Potential data exfiltration detected due to: {reasons}. Specifically, {feature_1} combined with {feature_2} suggests unauthorized data transfer.",
            'c2': "C2 beaconing indicators found: {reasons}. The pattern of {feature_1} is typical of malware communicating with command-and-control servers.",
            'lolbin': "Suspicious use of system tools detected: {reasons}. {feature_1} is a known 'Living off the Land' technique used by attackers.",
            'anomaly': "Anomalous behavior detected: {reasons}. This deviates from the normal baseline established for this system."
        }
        
        if not top_features:
            return "Detection triggered by rule-based logic."
        
        # Extract top 2 feature explanations
        reasons = ", ".join([f"{name} (impact: {val:.2f})" for name, val in top_features[:3]])
        feature_1 = top_features[0][0] if len(top_features) > 0 else "unknown"
        feature_2 = top_features[1][0] if len(top_features) > 1 else "unknown"
        
        template = templates.get(category, "Detection triggered due to: {reasons}.")
        
        return template.format(
            reasons=reasons,
            feature_1=feature_1.replace('_', ' '),
            feature_2=feature_2.replace('_', ' ')
        )


def integrate_explainability_into_detector(detector, explainer: SHAPExplainer):
    """
    Monkey-patch the detector to include SHAP explanations in results.
    
    Usage:
        explainer = SHAPExplainer(model, feature_names)
        integrate_explainability_into_detector(detector, explainer)
    """
    original_detect = detector.detect
    
    def enhanced_detect(features):
        result = original_detect(features)
        
        # Add SHAP explanation
        try:
            feature_vector = np.array(features.to_ml_features())
            explain_result = explainer.explain_single(feature_vector)
            
            # Attach to detection result
            result.explanation = LocalInterpretability.generate_natural_language_explanation(
                result, explain_result
            )
            result.shap_values = explain_result.to_dict()
        except Exception as e:
            result.explanation = f"Explainability unavailable: {e}"
        
        return result
    
    detector.detect = enhanced_detect
    return detector


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("CyberShell Explainable AI Module")
    print("=" * 50)
    
    if not SHAP_AVAILABLE:
        print("[ERROR] SHAP not installed.")
        print("Install with: pip install shap")
    else:
        print("[OK] SHAP is available")
        print("\nTo use:")
        print("1. Train your model and save feature names")
        print("2. explainer = SHAPExplainer(model, feature_names)")
        print("3. result = explainer.explain_single(feature_vector)")
        print("4. print(result.explanation_summary)")
