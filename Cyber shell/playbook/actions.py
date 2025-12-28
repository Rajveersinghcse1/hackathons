"""
CyberShell Playbook - Response Actions Module
==============================================

Purpose: Implement containment and response actions
Safety: ALL ACTIONS SIMULATE BY DEFAULT

Modes:
- --simulate (DEFAULT): Print commands, take no action
- --execute --vm: Run commands, ONLY in VM environment

Actions available:
1. isolate_host: Disable network adapter (simulate)
2. block_process: Terminate suspicious process (simulate)
3. forensic_capture: Collect memory/disk artifacts (simulate)
4. block_network: Add firewall rule (simulate)
5. quarantine_file: Move file to quarantine (simulate)

CRITICAL: Real execution requires:
1. --execute flag
2. --vm flag (must be running in VM)
3. Interactive confirmation prompt
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess


# =============================================================================
# SAFETY FLAGS
# =============================================================================

class ExecutionMode(Enum):
    """Execution mode for playbook actions"""
    SIMULATE = "simulate"      # Print only, no action (default)
    EXECUTE = "execute"        # Real action (only with vm_mode=True)
    EXECUTE_VM = "execute_vm"  # Real action, VM only (deprecated alias)


@dataclass
class ActionResult:
    """Result of a playbook action"""
    action_name: str           # Name of the action performed
    success: bool              # Whether action succeeded
    simulated: bool            # True if this was a simulation
    message: str               # Human-readable message
    details: Dict[str, Any] = None  # Additional details
    
    # Legacy fields for backward compatibility
    action_id: str = ""
    action_type: str = ""
    target: str = ""
    mode: str = ""
    command: str = ""
    timestamp: str = ""
    requires_admin: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_log_entry(self) -> str:
        """Format as a log entry string"""
        status = "SIMULATED" if self.simulated else "EXECUTED"
        return f"[{status}] {self.action_name}: {self.message}"


class SafetyChecker:
    """
    Validates execution safety before running real commands.
    
    Checks:
    1. --execute flag present
    2. --vm flag present
    3. Running inside VM (checks common VM indicators)
    4. User confirmation obtained
    """
    
    VM_INDICATORS = [
        # Registry keys that indicate VM
        r"HKLM\SOFTWARE\VMware",
        r"HKLM\SOFTWARE\Oracle\VirtualBox",
        r"HKLM\HARDWARE\ACPI\DSDT\VBOX__",
        # Process names
        "vmtoolsd.exe", "VBoxService.exe", "vmwaretray.exe",
    ]
    
    @staticmethod
    def check_vm_environment() -> bool:
        """
        Detect if running inside a VM.
        Returns True if VM indicators found.
        """
        # Check for VM-related processes
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq vmtoolsd.exe"],
                capture_output=True, text=True
            )
            if "vmtoolsd.exe" in result.stdout:
                return True
        except:
            pass
        
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq VBoxService.exe"],
                capture_output=True, text=True
            )
            if "VBoxService.exe" in result.stdout:
                return True
        except:
            pass
        
        # Check environment variable
        if os.environ.get("CYBERSHELL_VM_MODE") == "1":
            return True
        
        return False
    
    @staticmethod
    def confirm_action(action_description: str) -> bool:
        """
        Interactive confirmation for dangerous actions.
        """
        print("\n" + "=" * 60)
        print("⚠️  WARNING: REAL ACTION REQUESTED")
        print("=" * 60)
        print(f"\nAction: {action_description}")
        print("\nThis will execute a REAL system command.")
        print("Only proceed if you are in a controlled VM environment.")
        
        response = input("\nType 'CONFIRM' to proceed: ")
        return response.strip() == "CONFIRM"
    
    @staticmethod
    def validate_execution(execute_flag: bool, vm_flag: bool,
                          action_description: str) -> tuple[bool, str]:
        """
        Full validation for real execution.
        
        Returns:
            (allowed: bool, reason: str)
        """
        if not execute_flag:
            return False, "Execute mode not enabled (--simulate is default)"
        
        if not vm_flag:
            return False, "VM mode not enabled (--vm required)"
        
        if not SafetyChecker.check_vm_environment():
            return False, "VM environment not detected (set CYBERSHELL_VM_MODE=1 to override)"
        
        if not SafetyChecker.confirm_action(action_description):
            return False, "User did not confirm action"
        
        return True, "All safety checks passed"


# =============================================================================
# PLAYBOOK ACTIONS
# =============================================================================

class PlaybookActions:
    """
    Safe implementations of response actions.
    
    Each action:
    1. Generates the command that WOULD be run
    2. In simulate mode: prints command and returns
    3. In execute mode: runs full safety checks, then executes
    
    Usage:
        playbook = PlaybookActions(mode=ExecutionMode.SIMULATE)
        result = playbook.kill_process(pid=1234, process_name="test.exe")
        print(result.message)
    """
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.SIMULATE,
                 vm_mode: bool = False):
        self.mode = mode
        self.vm_mode = vm_mode
        self.action_log: List[ActionResult] = []
        
        # Warn if execute mode without VM
        if mode == ExecutionMode.EXECUTE and not vm_mode:
            print("[WARNING] Execute mode enabled without VM flag - be careful!")
    
    def _create_result(self, action_name: str, target: str, command: str,
                       success: bool = True, message: str = "",
                       details: Dict[str, Any] = None) -> ActionResult:
        """Create a standardized ActionResult"""
        simulated = (self.mode == ExecutionMode.SIMULATE)
        
        if simulated:
            message = f"SIMULATED: Would {action_name.replace('_', ' ')} - {command}"
        
        return ActionResult(
            action_name=action_name,
            success=success,
            simulated=simulated,
            message=message,
            details=details or {},
            action_id=f"{action_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            action_type=action_name,
            target=target,
            mode=self.mode.value,
            command=command,
            timestamp=datetime.now().isoformat(),
            requires_admin=True
        )
        
    def _execute_or_simulate(self, action_name: str, target: str,
                            command: str, description: str,
                            requires_admin: bool = True) -> ActionResult:
        """
        Core method: either simulate or execute with safety checks.
        """
        details = {"command": command, "target": target}
        
        if self.mode == ExecutionMode.SIMULATE:
            # Simulate mode: just print
            message = f"SIMULATED: Would execute: {command}"
            print(f"\n{'='*60}")
            print(f"🔸 SIMULATED ACTION: {action_name}")
            print(f"{'='*60}")
            print(f"Target: {target}")
            print(f"Command: {command}")
            print(f"Requires Admin: {requires_admin}")
            print(f"{'='*60}\n")
            
            return self._create_result(action_name, target, command, True, message, details)
            
        else:
            # Execute mode: full safety checks
            vm_flag = self.vm_mode
            
            allowed, reason = SafetyChecker.validate_execution(
                True, vm_flag, description
            )
            
            if not allowed:
                message = f"[BLOCKED] {reason}"
                print(f"\n❌ Action blocked: {reason}")
                return self._create_result(action_name, target, command, False, message, details)
            else:
                # Actually execute
                try:
                    print(f"\n🔴 EXECUTING: {command}")
                    subprocess.run(command, shell=True, check=True)
                    message = f"[EXECUTED] {command}"
                    print(f"✅ Action completed successfully")
                    result = self._create_result(action_name, target, command, True, message, details)
                    result.simulated = False
                    self.action_log.append(result)
                    return result
                except subprocess.CalledProcessError as e:
                    message = f"[FAILED] {str(e)}"
                    print(f"❌ Action failed: {e}")
                    return self._create_result(action_name, target, command, False, message, details)
    
    # =========================================================================
    # ACTION: KILL PROCESS (alias for block_process)
    # =========================================================================
    
    def kill_process(self, pid: int = None, process_name: str = None) -> ActionResult:
        """
        Terminate a suspicious process.
        
        Windows command: taskkill /F /PID 1234
        """
        if pid:
            command = f'taskkill /F /PID {pid}'
            target = f"PID {pid}"
        elif process_name:
            command = f'taskkill /F /IM "{process_name}"'
            target = process_name
        else:
            return self._create_result("kill_process", "unknown", "", False, 
                                       "No PID or process name provided")
        
        description = f"Terminate process: {target}"
        details = {"pid": pid, "process_name": process_name}
        
        return self._execute_or_simulate(
            action_name="kill_process",
            target=target,
            command=command,
            description=description,
            requires_admin=True
        )
    
    # =========================================================================
    # ACTION: ISOLATE NETWORK
    # =========================================================================
    
    def isolate_network(self, adapter_name: str = "Ethernet") -> ActionResult:
        """
        Isolate the network by disabling the network adapter.
        """
        command = f'netsh interface set interface "{adapter_name}" disable'
        description = f"Disable network adapter '{adapter_name}'"
        
        return self._execute_or_simulate(
            action_name="isolate_network",
            target=adapter_name,
            command=command,
            description=description,
            requires_admin=True
        )
    
    # =========================================================================
    # ACTION: QUARANTINE FILE
    # =========================================================================
    
    def quarantine_file(self, file_path: str) -> ActionResult:
        """
        Move suspicious file to quarantine folder.
        """
        quarantine_dir = Path("C:/CyberShell/Quarantine")
        quarantine_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(file_path).name}"
        
        command = (f'mkdir "{quarantine_dir}" 2>nul & '
                  f'move "{file_path}" "{quarantine_dir / quarantine_name}"')
        
        description = f"Quarantine file: {file_path}"
        
        return self._execute_or_simulate(
            action_name="quarantine_file",
            target=file_path,
            command=command,
            description=description,
            requires_admin=True
        )
    
    # =========================================================================
    # ACTION: BLOCK IP
    # =========================================================================
    
    def block_ip(self, ip_address: str, direction: str = "outbound") -> ActionResult:
        """
        Block network connection to/from specific IP.
        """
        if direction == "outbound":
            command = (f'netsh advfirewall firewall add rule '
                      f'name="CyberShell Block {ip_address}" '
                      f'dir=out action=block remoteip={ip_address}')
        else:
            command = (f'netsh advfirewall firewall add rule '
                      f'name="CyberShell Block {ip_address}" '
                      f'dir=in action=block remoteip={ip_address}')
        
        description = f"Block {direction} traffic to/from {ip_address}"
        
        return self._execute_or_simulate(
            action_name="block_ip",
            target=ip_address,
            command=command,
            description=description,
            requires_admin=True
        )
    
    # =========================================================================
    # ACTION: COLLECT LOGS
    # =========================================================================
    
    def collect_logs(self, host_hash: str,
                    log_types: List[str] = None) -> ActionResult:
        """
        Collect Windows event logs for investigation.
        
        Default logs: Security, System, Application
        """
        log_types = log_types or ["Security", "System", "Application"]
        output_dir = f"collected_logs_{host_hash}_{datetime.now().strftime('%Y%m%d')}"
        
        commands = []
        for log_type in log_types:
            commands.append(
                f'wevtutil epl {log_type} "{output_dir}\\{log_type}.evtx"'
            )
        
        command = f'mkdir "{output_dir}" & ' + ' & '.join(commands)
        description = f"Collect event logs from host {host_hash}"
        
        return self._execute_or_simulate(
            action_name="collect_logs",
            target=host_hash,
            command=command,
            description=description,
            requires_admin=True
        )
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_action_log(self) -> List[Dict]:
        """Get log of all actions taken in this session"""
        return [action.to_dict() for action in self.action_log]
    
    def save_action_log(self, path: str = "action_log.json"):
        """Save action log to file"""
        with open(path, 'w') as f:
            json.dump(self.get_action_log(), f, indent=2)
        print(f"[INFO] Action log saved to {path}")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CyberShell Playbook Actions",
        epilog="⚠️  Default mode is --simulate. Use --execute --vm for real actions."
    )
    
    # Mode flags
    parser.add_argument("--simulate", action="store_true", default=True,
                        help="Simulate mode - print commands only (DEFAULT)")
    parser.add_argument("--execute", action="store_true",
                        help="Execute mode - run real commands")
    parser.add_argument("--vm", action="store_true",
                        help="Confirm running in VM environment")
    
    # Actions
    parser.add_argument("--action", choices=[
        'isolate', 'unisolate', 'block-process', 'forensic', 
        'block-network', 'quarantine', 'collect-logs'
    ], help="Action to perform")
    
    parser.add_argument("--target", help="Target for action (host, process, IP, file)")
    parser.add_argument("--pid", type=int, help="Process ID (for block-process)")
    
    args = parser.parse_args()
    
    # Determine mode
    if args.execute and args.vm:
        mode = ExecutionMode.EXECUTE_VM
        print("\n⚠️  EXECUTE MODE ENABLED - Real commands will be run!\n")
    else:
        mode = ExecutionMode.SIMULATE
        print("\n🔸 SIMULATE MODE - Commands will be printed only\n")
    
    playbook = PlaybookActions(mode=mode, vm_mode=args.vm)
    
    # Execute requested action
    if args.action == 'isolate':
        playbook.isolate_host(args.target or "demo_host")
    elif args.action == 'unisolate':
        playbook.unisolate_host(args.target or "demo_host")
    elif args.action == 'block-process':
        playbook.block_process(args.target or "malware.exe", args.pid)
    elif args.action == 'forensic':
        playbook.forensic_capture(args.target or "demo_host")
    elif args.action == 'block-network':
        playbook.block_network(args.target or "192.168.1.100")
    elif args.action == 'quarantine':
        playbook.quarantine_file(args.target or "C:\\suspicious\\file.exe")
    elif args.action == 'collect-logs':
        playbook.collect_logs(args.target or "demo_host")
    else:
        # Demo all actions
        print("[DEMO] Running all actions in simulate mode...\n")
        playbook.isolate_host("host_abc123")
        playbook.block_process("ransomware.exe")
        playbook.forensic_capture("host_abc123", "memory")
        playbook.block_network("10.0.0.100")
        playbook.quarantine_file("C:\\Users\\victim\\malware.exe")
        playbook.collect_logs("host_abc123")
    
    # Save action log
    playbook.save_action_log()


if __name__ == "__main__":
    main()
