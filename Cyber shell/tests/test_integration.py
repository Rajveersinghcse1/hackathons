# tests/test_integration.py
"""
Integration tests for CyberShell EDR prototype.
Tests the full pipeline from data collection through detection.
"""
import unittest
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFullPipeline(unittest.TestCase):
    """Test the full detection pipeline end-to-end."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.benign_csv = self.test_dir / "scenarios" / "data" / "benign" / "sysmon_benign.csv"
        self.malicious_csv = self.test_dir / "scenarios" / "data" / "malicious-ransomware" / "sysmon_ransomware.csv"
    
    def test_scenario_data_exists(self):
        """Test that scenario data files exist."""
        self.assertTrue(self.benign_csv.exists(), f"Benign CSV not found: {self.benign_csv}")
        self.assertTrue(self.malicious_csv.exists(), f"Malicious CSV not found: {self.malicious_csv}")
    
    def test_benign_data_parseable(self):
        """Test that benign CSV can be parsed."""
        import csv
        with open(self.benign_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertGreater(len(rows), 0, "Benign CSV should have data rows")
        self.assertIn('EventID', rows[0], "CSV should have EventID column")
        self.assertIn('Image', rows[0], "CSV should have Image column")
    
    def test_malicious_data_parseable(self):
        """Test that malicious CSV can be parsed."""
        import csv
        with open(self.malicious_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertGreater(len(rows), 0, "Malicious CSV should have data rows")


class TestPrivacyIntegration(unittest.TestCase):
    """Test privacy hashing is applied correctly."""
    
    def test_username_hashing(self):
        """Test username hashing consistency."""
        from utils.privacy import PrivacyHasher
        
        hasher = PrivacyHasher(salt="test_salt")
        
        # Same input should produce same output
        hash1 = hasher.hash_username("DESKTOP\\admin")
        hash2 = hasher.hash_username("DESKTOP\\admin")
        self.assertEqual(hash1, hash2)
        
        # Different inputs should produce different outputs
        hash3 = hasher.hash_username("DESKTOP\\user")
        self.assertNotEqual(hash1, hash3)
        
        # Output should have correct prefix
        self.assertTrue(hash1.startswith("USR_"))
    
    def test_event_sanitization(self):
        """Test full event sanitization."""
        from utils.privacy import PrivacyHasher
        
        hasher = PrivacyHasher(salt="test_salt")
        
        event = {
            "username": "DOMAIN\\secretuser",
            "src_ip": "192.168.1.100",
            "command_line": "cmd.exe /c whoami",
            "process_name": "cmd.exe"
        }
        
        sanitized = hasher.sanitize_event(event)
        
        # PII should be hashed
        self.assertTrue(sanitized["username"].startswith("USR_"))
        self.assertTrue(sanitized["src_ip"].startswith("IP_"))
        
        # Non-PII should be preserved
        self.assertEqual(sanitized["command_line"], event["command_line"])
        self.assertEqual(sanitized["process_name"], event["process_name"])


class TestPlaybookIntegration(unittest.TestCase):
    """Test playbook actions in simulate mode."""
    
    def test_simulate_mode_default(self):
        """Test that simulate mode is the default."""
        from playbook.actions import PlaybookActions, ExecutionMode
        
        playbook = PlaybookActions()
        self.assertEqual(playbook.mode, ExecutionMode.SIMULATE)
    
    def test_all_actions_simulate(self):
        """Test that all actions return simulated results."""
        from playbook.actions import PlaybookActions
        
        playbook = PlaybookActions()
        
        # Test various actions
        result1 = playbook.kill_process(pid=1234)
        self.assertTrue(result1.simulated)
        self.assertIn("SIMULATED", result1.message)
        
        result2 = playbook.isolate_network()
        self.assertTrue(result2.simulated)
        
        result3 = playbook.quarantine_file("C:\\temp\\test.exe")
        self.assertTrue(result3.simulated)
        
        result4 = playbook.block_ip("192.168.1.100")
        self.assertTrue(result4.simulated)


class TestDetectionIntegration(unittest.TestCase):
    """Test detection components work together."""
    
    def test_detection_result_structure(self):
        """Test DetectionResult has all required fields."""
        from model.detect import DetectionResult
        
        result = DetectionResult(
            is_malicious=True,
            confidence=0.9,
            detection_layer=1,
            category="ransomware"
        )
        
        # Check required fields exist
        self.assertTrue(hasattr(result, 'is_malicious'))
        self.assertTrue(hasattr(result, 'confidence'))
        self.assertTrue(hasattr(result, 'detection_layer'))
        self.assertTrue(hasattr(result, 'category'))
        
        # Check to_dict works
        d = result.to_dict()
        self.assertIsInstance(d, dict)


class TestScenarioRunner(unittest.TestCase):
    """Test scenario runner components."""
    
    def test_scenarios_exist(self):
        """Test that scenario data directories exist."""
        test_dir = Path(__file__).parent.parent
        
        scenarios = [
            test_dir / "scenarios" / "data" / "benign",
            test_dir / "scenarios" / "data" / "benign-anomaly",
            test_dir / "scenarios" / "data" / "malicious-ransomware",
        ]
        
        for scenario_path in scenarios:
            self.assertTrue(scenario_path.exists(), f"Scenario path not found: {scenario_path}")


if __name__ == "__main__":
    unittest.main()
