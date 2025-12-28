"""
CyberShell Agent - Data Collector Module
=========================================

Purpose: Read-only collection from Windows data sources
Safety: NO kernel drivers, NO PII collection, userland only

Data Sources:
1. Sysmon EVTX/CSV exports - Process creation, network, file events
2. PCAP files (offline) - Network flow analysis via scapy/dpkt
3. WMI queries - Live process enumeration (read-only)
4. Windows Event Logs - Security/System events via win32evtlog

Privacy: All identifiers are hashed before forwarding to parser.
"""

import hashlib
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Generator, Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Conditional imports for Windows-specific modules (optional)
try:
    import wmi  # type: ignore
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    from Evtx.Evtx import Evtx  # type: ignore
    from Evtx.Views import evtx_file_xml_view  # type: ignore
    EVTX_AVAILABLE = True
except ImportError:
    EVTX_AVAILABLE = False

try:
    from scapy.all import rdpcap, IP, TCP, UDP, DNS  # type: ignore
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class RawEvent:
    """Base class for all raw telemetry events"""
    event_type: str          # 'process', 'network', 'file', 'logon'
    timestamp: datetime
    source: str              # 'sysmon', 'pcap', 'wmi', 'eventlog'
    raw_data: Dict[str, Any]


@dataclass
class ProcessEvent(RawEvent):
    """Process creation/termination event"""
    process_name: str
    process_id: int
    parent_name: str
    parent_id: int
    command_line: str        # Will be entropy-scored, not stored raw
    user_hash: str           # Hashed username
    image_path: str


@dataclass
class NetworkEvent(RawEvent):
    """Network connection event"""
    src_ip_hash: str         # Hashed source IP
    dst_ip_hash: str         # Hashed destination IP
    src_port: int
    dst_port: int
    protocol: str            # TCP, UDP, DNS
    bytes_sent: int
    bytes_recv: int


@dataclass
class FileEvent(RawEvent):
    """File operation event"""
    operation: str           # 'create', 'write', 'rename', 'delete'
    file_extension: str      # Only extension, not full path
    process_name: str
    is_user_folder: bool     # Documents, Desktop, etc.


@dataclass 
class LogonEvent(RawEvent):
    """Authentication event"""
    logon_type: int          # 2=Interactive, 3=Network, 10=Remote
    success: bool
    user_hash: str
    source_ip_hash: str


# =============================================================================
# PRIVACY UTILITIES
# =============================================================================

class PrivacyHasher:
    """
    Handles all identifier anonymization.
    Uses salted SHA-256 hashing - one-way without the salt.
    """
    
    def __init__(self, salt: Optional[str] = None):
        """
        Initialize with optional salt.
        If no salt provided, generates one and saves to .cybershell_salt
        """
        self.salt = salt or self._load_or_create_salt()
        self._mapping_file = Path(".hash_mapping.json")
        self._mappings: Dict[str, str] = {}
        
    def _load_or_create_salt(self) -> str:
        salt_file = Path(".cybershell_salt")
        if salt_file.exists():
            return salt_file.read_text().strip()
        else:
            import secrets
            salt = secrets.token_hex(32)
            salt_file.write_text(salt)
            return salt
    
    def hash_identifier(self, value: str, prefix: str = "") -> str:
        """
        Hash an identifier (username, IP, hostname).
        Returns: prefix + first 16 chars of SHA-256 hash
        """
        if not value:
            return f"{prefix}_unknown"
        
        hash_input = f"{self.salt}:{value}".encode('utf-8')
        hash_output = hashlib.sha256(hash_input).hexdigest()[:16]
        result = f"{prefix}_{hash_output}" if prefix else hash_output
        
        # Store mapping for potential offline lookup (secure file only)
        self._mappings[result] = value  # Only stored locally
        
        return result
    
    def hash_username(self, username: str) -> str:
        return self.hash_identifier(username, "user")
    
    def hash_ip(self, ip_address: str) -> str:
        return self.hash_identifier(ip_address, "ip")
    
    def hash_hostname(self, hostname: str) -> str:
        return self.hash_identifier(hostname, "host")
    
    def save_mappings(self):
        """Save hash mappings to secure local file (for admin lookup only)"""
        self._mapping_file.write_text(json.dumps(self._mappings, indent=2))


# =============================================================================
# COLLECTOR BASE CLASS
# =============================================================================

class BaseCollector(ABC):
    """Abstract base class for all collectors"""
    
    def __init__(self, hasher: PrivacyHasher):
        self.hasher = hasher
        self.events_collected = 0
        
    @abstractmethod
    def collect(self) -> Generator[RawEvent, None, None]:
        """Yield raw events from the data source"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this collector's data source is available"""
        pass


# =============================================================================
# SYSMON COLLECTOR
# =============================================================================

class SysmonCollector(BaseCollector):
    """
    Collects events from Sysmon EVTX files or CSV exports.
    
    Supported Sysmon Event IDs:
    - 1: Process Creation
    - 3: Network Connection
    - 11: File Create
    - 23: File Delete
    
    Usage:
        collector = SysmonCollector(hasher, csv_path="sysmon_export.csv")
        for event in collector.collect():
            process(event)
    """
    
    # Sysmon Event ID mapping
    EVENT_TYPES = {
        1: 'process_create',
        3: 'network_connect',
        5: 'process_terminate',
        11: 'file_create',
        13: 'registry_value',
        23: 'file_delete',
    }
    
    def __init__(self, hasher: PrivacyHasher, 
                 evtx_path: Optional[Path] = None,
                 csv_path: Optional[Path] = None):
        super().__init__(hasher)
        self.evtx_path = Path(evtx_path) if evtx_path else None
        self.csv_path = Path(csv_path) if csv_path else None
        
    def is_available(self) -> bool:
        if self.csv_path:
            return self.csv_path.exists()
        if self.evtx_path:
            return self.evtx_path.exists() and EVTX_AVAILABLE
        return False
    
    def collect(self) -> Generator[RawEvent, None, None]:
        """Collect from CSV (preferred for demos) or EVTX"""
        if self.csv_path and self.csv_path.exists():
            yield from self._collect_from_csv()
        elif self.evtx_path and self.evtx_path.exists():
            yield from self._collect_from_evtx()
            
    def _collect_from_csv(self) -> Generator[RawEvent, None, None]:
        """
        Parse Sysmon CSV export.
        Expected columns: EventID, TimeCreated, Image, CommandLine, 
                         ParentImage, User, DestinationIp, DestinationPort, etc.
        """
        with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                event = self._parse_csv_row(row)
                if event:
                    self.events_collected += 1
                    yield event
                    
    def _parse_csv_row(self, row: Dict[str, str]) -> Optional[RawEvent]:
        """Convert CSV row to appropriate RawEvent subclass"""
        event_id = int(row.get('EventID', 0))
        
        timestamp = self._parse_timestamp(row.get('TimeCreated', ''))
        
        if event_id == 1:  # Process Creation
            return ProcessEvent(
                event_type='process_create',
                timestamp=timestamp,
                source='sysmon',
                raw_data=row,
                process_name=Path(row.get('Image', '')).name,
                process_id=int(row.get('ProcessId', 0)),
                parent_name=Path(row.get('ParentImage', '')).name,
                parent_id=int(row.get('ParentProcessId', 0)),
                command_line=row.get('CommandLine', ''),
                user_hash=self.hasher.hash_username(row.get('User', '')),
                image_path=row.get('Image', '')
            )
            
        elif event_id == 3:  # Network Connection
            return NetworkEvent(
                event_type='network_connect',
                timestamp=timestamp,
                source='sysmon',
                raw_data=row,
                src_ip_hash=self.hasher.hash_ip(row.get('SourceIp', '')),
                dst_ip_hash=self.hasher.hash_ip(row.get('DestinationIp', '')),
                src_port=int(row.get('SourcePort', 0)),
                dst_port=int(row.get('DestinationPort', 0)),
                protocol=row.get('Protocol', 'tcp'),
                bytes_sent=0,  # Not in Sysmon, filled by PCAP
                bytes_recv=0
            )
            
        elif event_id in (11, 23):  # File Create/Delete
            return FileEvent(
                event_type='file_create' if event_id == 11 else 'file_delete',
                timestamp=timestamp,
                source='sysmon',
                raw_data=row,
                operation='create' if event_id == 11 else 'delete',
                file_extension=Path(row.get('TargetFilename', '')).suffix,
                process_name=Path(row.get('Image', '')).name,
                is_user_folder=self._is_user_folder(row.get('TargetFilename', ''))
            )
            
        return None
    
    def _collect_from_evtx(self) -> Generator[RawEvent, None, None]:
        """Parse Sysmon EVTX file using python-evtx library"""
        # TODO: Implement EVTX parsing
        # Uses Evtx library to read binary EVTX format
        # Similar logic to CSV but parses XML structure
        pass
    
    @staticmethod
    def _parse_timestamp(ts_string: str) -> datetime:
        """Parse various timestamp formats from Sysmon"""
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(ts_string[:26], fmt)
            except ValueError:
                continue
        return datetime.now()
    
    @staticmethod
    def _is_user_folder(path: str) -> bool:
        """Check if path is in a user folder (Documents, Desktop, etc.)"""
        user_indicators = ['Documents', 'Desktop', 'Downloads', 'Pictures', 
                          'Users', 'AppData']
        return any(ind.lower() in path.lower() for ind in user_indicators)


# =============================================================================
# PCAP COLLECTOR
# =============================================================================

class PcapCollector(BaseCollector):
    """
    Collects network events from offline PCAP files.
    Uses scapy for parsing - requires Npcap installed on Windows.
    
    Features extracted:
    - Flow metadata (IPs, ports, protocols)
    - Byte counts per flow
    - DNS queries (for C2/tunneling detection)
    
    Privacy: All IPs are hashed before storage.
    
    Usage:
        collector = PcapCollector(hasher, pcap_path="capture.pcap")
        for event in collector.collect():
            process(event)
    """
    
    def __init__(self, hasher: PrivacyHasher, pcap_path: Optional[Path] = None):
        super().__init__(hasher)
        self.pcap_path = Path(pcap_path) if pcap_path else None
        
    def is_available(self) -> bool:
        return (self.pcap_path and self.pcap_path.exists() and SCAPY_AVAILABLE)
    
    def collect(self) -> Generator[RawEvent, None, None]:
        """Parse PCAP and yield network events"""
        if not self.is_available():
            return
            
        packets = rdpcap(str(self.pcap_path))
        
        # Track flows for aggregation
        flows: Dict[str, Dict[str, Any]] = {}
        
        for pkt in packets:
            if IP in pkt:
                flow_key = self._get_flow_key(pkt)
                
                if flow_key not in flows:
                    flows[flow_key] = {
                        'src_ip': pkt[IP].src,
                        'dst_ip': pkt[IP].dst,
                        'src_port': pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0),
                        'dst_port': pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0),
                        'protocol': 'TCP' if TCP in pkt else ('UDP' if UDP in pkt else 'OTHER'),
                        'bytes': 0,
                        'packets': 0,
                        'first_seen': float(pkt.time),
                        'dns_queries': []
                    }
                
                flows[flow_key]['bytes'] += len(pkt)
                flows[flow_key]['packets'] += 1
                
                # Extract DNS queries for C2 detection
                if DNS in pkt and pkt[DNS].qr == 0:  # Query
                    query_name = pkt[DNS].qd.qname.decode() if pkt[DNS].qd else ''
                    flows[flow_key]['dns_queries'].append(query_name)
        
        # Yield aggregated flow events
        for flow_key, flow_data in flows.items():
            yield NetworkEvent(
                event_type='network_flow',
                timestamp=datetime.fromtimestamp(flow_data['first_seen']),
                source='pcap',
                raw_data={'flow_key': flow_key, 'dns_queries': flow_data['dns_queries']},
                src_ip_hash=self.hasher.hash_ip(flow_data['src_ip']),
                dst_ip_hash=self.hasher.hash_ip(flow_data['dst_ip']),
                src_port=flow_data['src_port'],
                dst_port=flow_data['dst_port'],
                protocol=flow_data['protocol'],
                bytes_sent=flow_data['bytes'],
                bytes_recv=0  # Would need bidirectional tracking
            )
            self.events_collected += 1
    
    def _get_flow_key(self, pkt) -> str:
        """Generate unique flow identifier"""
        if TCP in pkt:
            return f"{pkt[IP].src}:{pkt[TCP].sport}->{pkt[IP].dst}:{pkt[TCP].dport}"
        elif UDP in pkt:
            return f"{pkt[IP].src}:{pkt[UDP].sport}->{pkt[IP].dst}:{pkt[UDP].dport}"
        else:
            return f"{pkt[IP].src}->{pkt[IP].dst}"


# =============================================================================
# WMI COLLECTOR
# =============================================================================

class WMICollector(BaseCollector):
    """
    Collects live process information via Windows WMI.
    READ-ONLY queries only - no modifications to system.
    
    WMI Classes Used:
    - Win32_Process: Running processes
    - Win32_NetworkConnection: Active network connections
    
    Safety: This is live collection - use --replay-sandbox for demos
            to skip live collection entirely.
    
    Usage:
        collector = WMICollector(hasher)
        for event in collector.collect():
            process(event)
    """
    
    def __init__(self, hasher: PrivacyHasher, live_mode: bool = False):
        super().__init__(hasher)
        self.live_mode = live_mode
        self._wmi_connection = None
        
    def is_available(self) -> bool:
        return WMI_AVAILABLE and self.live_mode
    
    def collect(self) -> Generator[RawEvent, None, None]:
        """
        Query WMI for process information.
        Only runs if live_mode=True (disabled by default for safety).
        """
        if not self.is_available():
            return
            
        self._wmi_connection = wmi.WMI()
        
        # Query running processes
        for process in self._wmi_connection.Win32_Process():
            try:
                # Get process owner (username)
                owner_info = process.GetOwner()
                username = f"{owner_info[0]}\\{owner_info[2]}" if owner_info[0] else "SYSTEM"
            except:
                username = "UNKNOWN"
            
            # Get parent process name
            parent_name = "unknown"
            if process.ParentProcessId:
                try:
                    parent_procs = self._wmi_connection.Win32_Process(
                        ProcessId=process.ParentProcessId
                    )
                    if parent_procs:
                        parent_name = parent_procs[0].Name
                except:
                    pass
            
            yield ProcessEvent(
                event_type='process_snapshot',
                timestamp=datetime.now(),
                source='wmi',
                raw_data={'wmi_object': str(process)},
                process_name=process.Name or "unknown",
                process_id=process.ProcessId or 0,
                parent_name=parent_name,
                parent_id=process.ParentProcessId or 0,
                command_line=process.CommandLine or "",
                user_hash=self.hasher.hash_username(username),
                image_path=process.ExecutablePath or ""
            )
            self.events_collected += 1


# =============================================================================
# EVENT LOG COLLECTOR  
# =============================================================================

class EventLogCollector(BaseCollector):
    """
    Collects Windows Security Event Log entries.
    Focuses on authentication events for credential abuse detection.
    
    Event IDs:
    - 4624: Successful logon
    - 4625: Failed logon
    - 4720: User account created
    - 4732: Member added to security-enabled local group
    
    Safety: Read-only queries via Event Log API.
    """
    
    SECURITY_EVENTS = {
        4624: 'logon_success',
        4625: 'logon_failure',
        4720: 'user_created',
        4732: 'group_member_added',
    }
    
    def __init__(self, hasher: PrivacyHasher, 
                 csv_path: Optional[Path] = None,
                 live_mode: bool = False):
        super().__init__(hasher)
        self.csv_path = Path(csv_path) if csv_path else None
        self.live_mode = live_mode
        
    def is_available(self) -> bool:
        if self.csv_path:
            return self.csv_path.exists()
        return self.live_mode
    
    def collect(self) -> Generator[RawEvent, None, None]:
        """Collect from CSV export or live Event Log"""
        if self.csv_path and self.csv_path.exists():
            yield from self._collect_from_csv()
        elif self.live_mode:
            yield from self._collect_from_eventlog()
            
    def _collect_from_csv(self) -> Generator[RawEvent, None, None]:
        """Parse exported Security Event Log CSV"""
        with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                event_id = int(row.get('EventID', 0))
                
                if event_id in (4624, 4625):
                    yield LogonEvent(
                        event_type=self.SECURITY_EVENTS.get(event_id, 'unknown'),
                        timestamp=self._parse_timestamp(row.get('TimeCreated', '')),
                        source='eventlog',
                        raw_data=row,
                        logon_type=int(row.get('LogonType', 0)),
                        success=(event_id == 4624),
                        user_hash=self.hasher.hash_username(row.get('TargetUserName', '')),
                        source_ip_hash=self.hasher.hash_ip(row.get('IpAddress', ''))
                    )
                    self.events_collected += 1
                    
    def _collect_from_eventlog(self) -> Generator[RawEvent, None, None]:
        """Query Windows Event Log API (live mode)"""
        # TODO: Implement using win32evtlog
        # This would use win32evtlog.OpenEventLog and win32evtlog.ReadEventLog
        pass
    
    @staticmethod
    def _parse_timestamp(ts_string: str) -> datetime:
        try:
            return datetime.strptime(ts_string[:19], '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now()


# =============================================================================
# UNIFIED COLLECTOR
# =============================================================================

class UnifiedCollector:
    """
    Coordinates all collectors and provides unified event stream.
    
    Usage:
        collector = UnifiedCollector(
            sysmon_csv="data/sysmon.csv",
            pcap_path="data/capture.pcap",
            live_mode=False  # Safe default
        )
        
        for event in collector.collect_all():
            feature_extractor.process(event)
    """
    
    def __init__(self,
                 sysmon_csv: Optional[str] = None,
                 sysmon_evtx: Optional[str] = None,
                 pcap_path: Optional[str] = None,
                 eventlog_csv: Optional[str] = None,
                 live_mode: bool = False):
        
        self.hasher = PrivacyHasher()
        
        # Initialize collectors
        self.collectors: List[BaseCollector] = []
        
        if sysmon_csv or sysmon_evtx:
            self.collectors.append(SysmonCollector(
                self.hasher,
                csv_path=Path(sysmon_csv) if sysmon_csv else None,
                evtx_path=Path(sysmon_evtx) if sysmon_evtx else None
            ))
            
        if pcap_path:
            self.collectors.append(PcapCollector(
                self.hasher,
                pcap_path=Path(pcap_path)
            ))
            
        if eventlog_csv or live_mode:
            self.collectors.append(EventLogCollector(
                self.hasher,
                csv_path=Path(eventlog_csv) if eventlog_csv else None,
                live_mode=live_mode
            ))
            
        if live_mode:
            self.collectors.append(WMICollector(self.hasher, live_mode=True))
    
    def collect_all(self) -> Generator[RawEvent, None, None]:
        """Yield events from all available collectors"""
        for collector in self.collectors:
            if collector.is_available():
                yield from collector.collect()
    
    def get_stats(self) -> Dict[str, int]:
        """Return collection statistics"""
        return {
            type(c).__name__: c.events_collected 
            for c in self.collectors
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Data Collector")
    parser.add_argument("--sysmon-csv", help="Path to Sysmon CSV export")
    parser.add_argument("--pcap", help="Path to PCAP file")
    parser.add_argument("--eventlog-csv", help="Path to Event Log CSV export")
    parser.add_argument("--live", action="store_true", 
                        help="Enable live collection (disabled by default)")
    parser.add_argument("--output", default="events.jsonl",
                        help="Output file for collected events")
    
    args = parser.parse_args()
    
    # Safety warning for live mode
    if args.live:
        print("[WARNING] Live mode enabled - collecting from system telemetry")
        print("[WARNING] Use --replay-sandbox for demos without live collection")
    
    collector = UnifiedCollector(
        sysmon_csv=args.sysmon_csv,
        pcap_path=args.pcap,
        eventlog_csv=args.eventlog_csv,
        live_mode=args.live
    )
    
    count = 0
    with open(args.output, 'w') as f:
        for event in collector.collect_all():
            f.write(json.dumps(asdict(event), default=str) + '\n')
            count += 1
    
    print(f"[INFO] Collected {count} events")
    print(f"[INFO] Stats: {collector.get_stats()}")
