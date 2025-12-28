# tests/test_collector.py
"""
Unit tests for agent/collector.py
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.collector import UnifiedCollector, SysmonCollector, WMICollector, PrivacyHasher


class TestSysmonCollector(unittest.TestCase):
    """Tests for SysmonCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hasher = PrivacyHasher(salt="test_salt")
        self.collector = SysmonCollector(self.hasher)
    
    def test_initialization(self):
        """Test collector initializes correctly."""
        self.assertIsNotNone(self.collector)
    
    def test_is_not_available_without_file(self):
        """Test is_available returns False without a file."""
        self.assertFalse(self.collector.is_available())


class TestWMICollector(unittest.TestCase):
    """Tests for WMICollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.hasher = PrivacyHasher(salt="test_salt")
        self.collector = WMICollector(self.hasher, live_mode=False)
    
    def test_initialization(self):
        """Test collector initializes correctly."""
        self.assertIsNotNone(self.collector)
    
    def test_is_not_available_without_live_mode(self):
        """Test WMI collector not available without live mode."""
        self.assertFalse(self.collector.is_available())


class TestUnifiedCollector(unittest.TestCase):
    """Tests for UnifiedCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = UnifiedCollector()
    
    def test_initialization(self):
        """Test unified collector initializes correctly."""
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.hasher)
    
    def test_collect_returns_generator(self):
        """Test that collect_all returns a generator."""
        result = self.collector.collect_all()
        self.assertIsNotNone(result)
    
    def test_get_stats(self):
        """Test get_stats returns dictionary."""
        stats = self.collector.get_stats()
        self.assertIsInstance(stats, dict)


if __name__ == "__main__":
    unittest.main()
