# tests/test_privacy.py
"""
Unit tests for utils/privacy.py
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.privacy import PrivacyHasher


class TestPrivacyHasher(unittest.TestCase):
    """Tests for PrivacyHasher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hasher = PrivacyHasher()
    
    def test_initialization(self):
        """Test hasher initializes correctly."""
        self.assertIsNotNone(self.hasher)
    
    def test_hash_username(self):
        """Test username hashing."""
        username = "DESKTOP\\testuser"
        hashed = self.hasher.hash_username(username)
        self.assertNotEqual(hashed, username)
        self.assertTrue(hashed.startswith("USR_"))
    
    def test_hash_username_consistency(self):
        """Test same username always produces same hash."""
        username = "DESKTOP\\admin"
        hash1 = self.hasher.hash_username(username)
        hash2 = self.hasher.hash_username(username)
        self.assertEqual(hash1, hash2)
    
    def test_hash_ip(self):
        """Test IP address hashing."""
        ip = "192.168.1.100"
        hashed = self.hasher.hash_ip(ip)
        self.assertNotEqual(hashed, ip)
        self.assertTrue(hashed.startswith("IP_"))
    
    def test_hash_hostname(self):
        """Test hostname hashing."""
        hostname = "DESKTOP-ABC123"
        hashed = self.hasher.hash_hostname(hostname)
        self.assertNotEqual(hashed, hostname)
        self.assertTrue(hashed.startswith("HOST_"))
    
    def test_sanitize_event(self):
        """Test full event sanitization."""
        event = {
            "username": "DOMAIN\\secretuser",
            "src_ip": "10.0.0.50",
            "dst_ip": "8.8.8.8",
            "hostname": "WORKSTATION-01",
            "command_line": "cmd.exe /c whoami"
        }
        sanitized = self.hasher.sanitize_event(event)
        
        # Check PII is hashed
        self.assertTrue(sanitized["username"].startswith("USR_"))
        self.assertTrue(sanitized["src_ip"].startswith("IP_"))
        self.assertTrue(sanitized["hostname"].startswith("HOST_"))
        
        # Check non-PII is preserved
        self.assertEqual(sanitized["command_line"], event["command_line"])
    
    def test_empty_values_handled(self):
        """Test empty/None values don't crash."""
        self.assertEqual(self.hasher.hash_username(""), "USR_EMPTY")
        self.assertEqual(self.hasher.hash_username(None), "USR_NONE")


class TestPrivacyHasherDifferentSalts(unittest.TestCase):
    """Tests for PrivacyHasher with different salts."""
    
    def test_different_salts_produce_different_hashes(self):
        """Test that different salts produce different hashes."""
        hasher1 = PrivacyHasher(salt="salt1")
        hasher2 = PrivacyHasher(salt="salt2")
        
        username = "testuser"
        hash1 = hasher1.hash_username(username)
        hash2 = hasher2.hash_username(username)
        
        self.assertNotEqual(hash1, hash2)


if __name__ == "__main__":
    unittest.main()
