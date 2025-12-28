# tests/test_detect.py
"""
Unit tests for model/detect.py
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.detect import HybridDetector, RuleEngine, DetectionResult


class TestRuleEngine(unittest.TestCase):
    """Tests for RuleEngine (Layer 1)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = RuleEngine()
    
    def test_initialization(self):
        """Test rule engine initializes correctly."""
        self.assertIsNotNone(self.engine)
        self.assertGreater(len(self.engine.rules), 0)


class TestHybridDetector(unittest.TestCase):
    """Tests for HybridDetector (Layer 1 + Layer 2)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = HybridDetector(model_path="nonexistent.pkl")
    
    def test_initialization(self):
        """Test detector initializes correctly."""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.rule_engine)


class TestDetectionResult(unittest.TestCase):
    """Tests for DetectionResult dataclass."""
    
    def test_result_creation(self):
        """Test creating a DetectionResult."""
        result = DetectionResult(
            is_malicious=True,
            confidence=0.95,
            detection_layer=1,
            rule_name="RANSOMWARE_FILE_EXTENSION",
            category="ransomware",
            top_features=["has_encryption_ext", "rapid_file_changes"],
            explanation="Detected encrypted file extensions"
        )
        self.assertTrue(result.is_malicious)
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.detection_layer, 1)
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = DetectionResult(
            is_malicious=True,
            confidence=0.85,
            detection_layer=2,
            rule_name=None,
            category="anomaly",
            top_features=["entropy_cmdline", "cmd_length"],
            explanation="ML anomaly detected"
        )
        d = result.to_dict()
        self.assertIn("is_malicious", d)
        self.assertIn("confidence", d)


if __name__ == "__main__":
    unittest.main()
