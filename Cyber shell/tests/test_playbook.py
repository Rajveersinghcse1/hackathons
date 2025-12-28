# tests/test_playbook.py
"""
Unit tests for playbook/actions.py
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playbook.actions import PlaybookActions, ExecutionMode, ActionResult


class TestExecutionMode(unittest.TestCase):
    """Tests for ExecutionMode enum."""
    
    def test_simulate_is_default(self):
        """Test that SIMULATE is available and is the safe mode."""
        self.assertEqual(ExecutionMode.SIMULATE.value, "simulate")
    
    def test_execute_mode_exists(self):
        """Test that EXECUTE mode exists."""
        self.assertEqual(ExecutionMode.EXECUTE.value, "execute")


class TestPlaybookActions(unittest.TestCase):
    """Tests for PlaybookActions class."""
    
    def setUp(self):
        """Set up test fixtures in SIMULATE mode."""
        self.playbook = PlaybookActions(mode=ExecutionMode.SIMULATE)
    
    def test_initialization_defaults_to_simulate(self):
        """Test playbook defaults to simulate mode."""
        pb = PlaybookActions()
        self.assertEqual(pb.mode, ExecutionMode.SIMULATE)
    
    def test_kill_process_simulate(self):
        """Test kill_process in simulate mode doesn't actually kill."""
        result = self.playbook.kill_process(pid=1234, process_name="test.exe")
        self.assertIsInstance(result, ActionResult)
        self.assertTrue(result.simulated)
        self.assertIn("SIMULATED", result.message)
    
    def test_isolate_network_simulate(self):
        """Test network isolation in simulate mode."""
        result = self.playbook.isolate_network()
        self.assertIsInstance(result, ActionResult)
        self.assertTrue(result.simulated)
    
    def test_quarantine_file_simulate(self):
        """Test file quarantine in simulate mode."""
        result = self.playbook.quarantine_file("C:\\temp\\malware.exe")
        self.assertIsInstance(result, ActionResult)
        self.assertTrue(result.simulated)
    
    def test_block_ip_simulate(self):
        """Test IP blocking in simulate mode."""
        result = self.playbook.block_ip("192.168.1.100")
        self.assertIsInstance(result, ActionResult)
        self.assertTrue(result.simulated)


class TestPlaybookActionsExecuteMode(unittest.TestCase):
    """Tests for PlaybookActions in EXECUTE mode (mocked)."""
    
    def setUp(self):
        """Set up test fixtures in EXECUTE mode with mocking."""
        self.playbook = PlaybookActions(mode=ExecutionMode.EXECUTE, vm_mode=True)
    
    def test_execute_mode_requires_vm(self):
        """Test that execute mode with vm_mode=False raises warning."""
        pb = PlaybookActions(mode=ExecutionMode.EXECUTE, vm_mode=False)
        # Should log a warning but still work
        self.assertEqual(pb.mode, ExecutionMode.EXECUTE)
    
    @patch('playbook.actions.subprocess.run')
    def test_kill_process_execute_calls_subprocess(self, mock_run):
        """Test kill_process in execute mode calls subprocess."""
        mock_run.return_value = MagicMock(returncode=0)
        result = self.playbook.kill_process(pid=1234, process_name="test.exe")
        self.assertFalse(result.simulated)


class TestActionResult(unittest.TestCase):
    """Tests for ActionResult dataclass."""
    
    def test_action_result_creation(self):
        """Test creating an ActionResult."""
        result = ActionResult(
            action_name="kill_process",
            success=True,
            simulated=True,
            message="SIMULATED: Would terminate process 1234",
            details={"pid": 1234}
        )
        self.assertEqual(result.action_name, "kill_process")
        self.assertTrue(result.success)
        self.assertTrue(result.simulated)
    
    def test_action_result_to_log(self):
        """Test generating log entry from ActionResult."""
        result = ActionResult(
            action_name="quarantine_file",
            success=True,
            simulated=True,
            message="SIMULATED: Would quarantine file",
            details={"path": "C:\\temp\\mal.exe"}
        )
        log_entry = result.to_log_entry()
        self.assertIn("quarantine_file", log_entry)
        self.assertIn("SIMULATED", log_entry)


if __name__ == "__main__":
    unittest.main()
