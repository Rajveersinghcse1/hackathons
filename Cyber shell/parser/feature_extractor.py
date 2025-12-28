"""
CyberShell Parser - Feature Extractor Module
=============================================

Purpose: Convert raw telemetry events into ML-ready feature rows
Input: RawEvent objects from collector
Output: FeatureRow dataclass with detection-relevant features

Feature Categories:
1. Process features: entropy, unusual paths, LOLBins indicators
2. Network features: bytes/5m, unique destinations, rare ports
3. File features: write rate, rename patterns, encryption indicators  
4. Auth features: failed logons, new accounts, lateral movement

All features are numeric for ML model compatibility.
Privacy: All identifiers remain hashed from collector stage.
"""

import math
import hashlib
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import json

# Import event types from collector
import sys
sys.path.append(str(Path(__file__).parent.parent))
from agent.collector import (
    RawEvent, ProcessEvent, NetworkEvent, FileEvent, LogonEvent
)


# =============================================================================
# FEATURE ROW DATA STRUCTURE
# =============================================================================

@dataclass
class FeatureRow:
    """
    Single row of features for ML model input.
    All fields are numeric except identifiers (hashed strings).
    """
    # Identifiers (hashed for privacy)
    timestamp: str                    # ISO format timestamp
    host_hash: str                    # Hashed hostname
    
    # Process features
    process_name: str                 # Process name (not hashed - needed for rules)
    parent_process: str               # Parent process name
    cmdline_entropy: float            # Shannon entropy of command line (0-8)
    cmdline_length: int               # Length of command line
    cmdline_has_base64: int           # 1 if Base64 pattern detected
    cmdline_has_url: int              # 1 if URL pattern detected
    is_unusual_path: int              # 1 if process from unusual location
    is_lolbin: int                    # 1 if Living-off-the-Land binary
    
    # Network features (aggregated over time windows)
    outbound_bytes_5m: int            # Bytes sent in last 5 minutes
    outbound_bytes_1hr: int           # Bytes sent in last hour
    unique_dst_ips_5m: int            # Unique destination IPs (5 min)
    unique_dst_ips_1hr: int           # Unique destination IPs (1 hour)
    unique_dst_ports_1hr: int         # Unique destination ports (1 hour)
    dns_query_count_5m: int           # DNS queries in 5 minutes
    dns_txt_query_count: int          # TXT/unusual DNS query types
    rare_port_connections: int        # Connections to non-standard ports
    periodic_connection_score: float  # Beaconing indicator (0-1)
    
    # File features (aggregated over time windows)
    file_write_rate_1m: float         # File writes per minute
    file_write_rate_5m: float         # File writes per 5 minutes
    file_rename_count_5m: int         # File renames in 5 minutes
    unique_extensions_written: int    # Unique file extensions written
    encryption_indicator: float       # Entropy of file operations (0-1)
    
    # Authentication features
    failed_logons_10m: int            # Failed logon attempts (10 min)
    failed_logons_1hr: int            # Failed logon attempts (1 hour)
    unique_failed_users_1hr: int      # Unique users with failed logons
    remote_logon_count: int           # Type 10 (RDP) logons
    new_admin_indicator: int          # New admin account created
    
    # Aggregated risk indicators (pre-computed for rules)
    ransomware_score: float           # Combined ransomware indicators (0-1)
    exfil_score: float                # Combined exfiltration indicators (0-1)
    c2_beacon_score: float            # Combined C2/beaconing indicators (0-1)
    lateral_movement_score: float     # Combined lateral movement indicators (0-1)
    
    # Metadata
    event_count: int                  # Number of raw events aggregated
    primary_event_type: str           # Most common event type in window
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_ml_features(self) -> List[float]:
        """Extract numeric features for ML model input"""
        return [
            self.cmdline_entropy,
            self.cmdline_length,
            self.cmdline_has_base64,
            self.cmdline_has_url,
            self.is_unusual_path,
            self.is_lolbin,
            self.outbound_bytes_5m,
            self.outbound_bytes_1hr,
            self.unique_dst_ips_5m,
            self.unique_dst_ips_1hr,
            self.unique_dst_ports_1hr,
            self.dns_query_count_5m,
            self.dns_txt_query_count,
            self.rare_port_connections,
            self.periodic_connection_score,
            self.file_write_rate_1m,
            self.file_write_rate_5m,
            self.file_rename_count_5m,
            self.unique_extensions_written,
            self.encryption_indicator,
            self.failed_logons_10m,
            self.failed_logons_1hr,
            self.unique_failed_users_1hr,
            self.remote_logon_count,
            self.new_admin_indicator,
        ]
    
    @staticmethod
    def feature_names() -> List[str]:
        """Names of ML features in order"""
        return [
            'cmdline_entropy', 'cmdline_length', 'cmdline_has_base64',
            'cmdline_has_url', 'is_unusual_path', 'is_lolbin',
            'outbound_bytes_5m', 'outbound_bytes_1hr', 'unique_dst_ips_5m',
            'unique_dst_ips_1hr', 'unique_dst_ports_1hr', 'dns_query_count_5m',
            'dns_txt_query_count', 'rare_port_connections', 'periodic_connection_score',
            'file_write_rate_1m', 'file_write_rate_5m', 'file_rename_count_5m',
            'unique_extensions_written', 'encryption_indicator', 'failed_logons_10m',
            'failed_logons_1hr', 'unique_failed_users_1hr', 'remote_logon_count',
            'new_admin_indicator'
        ]


# =============================================================================
# FEATURE COMPUTATION UTILITIES
# =============================================================================

class FeatureUtils:
    """Static utility functions for feature computation"""
    
    # Living-off-the-Land Binaries (LOLBins) list
    LOLBINS = {
        'powershell.exe', 'pwsh.exe', 'cmd.exe', 'wscript.exe', 
        'cscript.exe', 'mshta.exe', 'certutil.exe', 'bitsadmin.exe',
        'regsvr32.exe', 'rundll32.exe', 'msiexec.exe', 'installutil.exe',
        'regasm.exe', 'regsvcs.exe', 'msconfig.exe', 'wmic.exe',
        'cmstp.exe', 'msbuild.exe', 'dnscmd.exe', 'ftp.exe'
    }
    
    # Unusual process paths (indicators of malware)
    UNUSUAL_PATHS = [
        r'\\temp\\', r'\\tmp\\', r'\\appdata\\local\\temp',
        r'\\downloads\\', r'\\public\\', r'\\programdata\\',
        r'\\users\\[^\\]+\\desktop\\', r'\\recycler\\',
    ]
    
    # Standard ports (connections to other ports are "rare")
    STANDARD_PORTS = {80, 443, 53, 22, 21, 25, 110, 143, 993, 995, 3389}
    
    @staticmethod
    def calculate_entropy(text: str) -> float:
        """
        Calculate Shannon entropy of a string.
        High entropy may indicate: Base64, encryption, obfuscation
        Returns: 0.0 to ~8.0 (8 = maximum randomness for ASCII)
        """
        if not text:
            return 0.0
        
        # Count character frequencies
        freq = defaultdict(int)
        for char in text:
            freq[char] += 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return round(entropy, 4)
    
    @staticmethod
    def detect_base64(text: str) -> bool:
        """
        Detect Base64 encoded content in command line.
        Common in PowerShell attacks: -EncodedCommand, -e, -enc
        """
        if not text:
            return False
        
        # PowerShell encoded command patterns
        patterns = [
            r'-[eE](?:nc(?:odedcommand)?)?[\s]+[A-Za-z0-9+/=]{20,}',
            r'[A-Za-z0-9+/=]{50,}',  # Long Base64 string
            r'FromBase64String',
            r'\[Convert\]::FromBase64',
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)
    
    @staticmethod
    def detect_url(text: str) -> bool:
        """Detect URL patterns in command line"""
        if not text:
            return False
        
        patterns = [
            r'https?://[^\s]+',
            r'\\\\[^\s]+\\',  # UNC path
            r'ftp://[^\s]+',
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)
    
    @staticmethod
    def is_unusual_path(path: str) -> bool:
        """Check if executable path is suspicious"""
        if not path:
            return False
        
        path_lower = path.lower()
        return any(re.search(p, path_lower) for p in FeatureUtils.UNUSUAL_PATHS)
    
    @staticmethod
    def is_lolbin(process_name: str) -> bool:
        """Check if process is a Living-off-the-Land binary"""
        if not process_name:
            return False
        return process_name.lower() in FeatureUtils.LOLBINS
    
    @staticmethod
    def is_rare_port(port: int) -> bool:
        """Check if port is non-standard"""
        return port not in FeatureUtils.STANDARD_PORTS and port > 0
    
    @staticmethod
    def calculate_beacon_score(timestamps: List[datetime]) -> float:
        """
        Calculate beaconing score based on connection timing.
        Regular intervals suggest C2 beaconing.
        Returns: 0.0 to 1.0 (1.0 = perfect periodic behavior)
        """
        if len(timestamps) < 3:
            return 0.0
        
        # Calculate intervals between connections
        sorted_ts = sorted(timestamps)
        intervals = [
            (sorted_ts[i+1] - sorted_ts[i]).total_seconds()
            for i in range(len(sorted_ts) - 1)
        ]
        
        if not intervals:
            return 0.0
        
        # Calculate coefficient of variation (CV)
        # Low CV = regular intervals = potential beaconing
        mean_interval = sum(intervals) / len(intervals)
        if mean_interval == 0:
            return 0.0
        
        variance = sum((i - mean_interval) ** 2 for i in intervals) / len(intervals)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_interval
        
        # Convert CV to score (lower CV = higher score)
        # CV < 0.1 is highly regular, CV > 1.0 is random
        beacon_score = max(0.0, 1.0 - cv)
        
        return round(beacon_score, 4)


# =============================================================================
# TIME WINDOW AGGREGATOR
# =============================================================================

class TimeWindowAggregator:
    """
    Aggregates events over sliding time windows.
    Maintains state for computing time-based features.
    """
    
    def __init__(self):
        # Event buffers keyed by host_hash
        self.process_events: Dict[str, List[ProcessEvent]] = defaultdict(list)
        self.network_events: Dict[str, List[NetworkEvent]] = defaultdict(list)
        self.file_events: Dict[str, List[FileEvent]] = defaultdict(list)
        self.logon_events: Dict[str, List[LogonEvent]] = defaultdict(list)
        
        # Connection timestamps for beaconing detection
        self.connection_times: Dict[str, List[datetime]] = defaultdict(list)
        
    def add_event(self, event: RawEvent, host_hash: str):
        """Add event to appropriate buffer"""
        if isinstance(event, ProcessEvent):
            self.process_events[host_hash].append(event)
        elif isinstance(event, NetworkEvent):
            self.network_events[host_hash].append(event)
            self.connection_times[host_hash].append(event.timestamp)
        elif isinstance(event, FileEvent):
            self.file_events[host_hash].append(event)
        elif isinstance(event, LogonEvent):
            self.logon_events[host_hash].append(event)
    
    def prune_old_events(self, host_hash: str, current_time: datetime, 
                         max_age: timedelta = timedelta(hours=2)):
        """Remove events older than max_age"""
        cutoff = current_time - max_age
        
        self.process_events[host_hash] = [
            e for e in self.process_events[host_hash] if e.timestamp > cutoff
        ]
        self.network_events[host_hash] = [
            e for e in self.network_events[host_hash] if e.timestamp > cutoff
        ]
        self.file_events[host_hash] = [
            e for e in self.file_events[host_hash] if e.timestamp > cutoff
        ]
        self.logon_events[host_hash] = [
            e for e in self.logon_events[host_hash] if e.timestamp > cutoff
        ]
        self.connection_times[host_hash] = [
            t for t in self.connection_times[host_hash] if t > cutoff
        ]
    
    def get_network_features(self, host_hash: str, 
                            current_time: datetime) -> Dict[str, Any]:
        """Compute network-related features from buffered events"""
        events = self.network_events[host_hash]
        
        # Time windows
        t_5m = current_time - timedelta(minutes=5)
        t_1hr = current_time - timedelta(hours=1)
        
        events_5m = [e for e in events if e.timestamp > t_5m]
        events_1hr = [e for e in events if e.timestamp > t_1hr]
        
        return {
            'outbound_bytes_5m': sum(e.bytes_sent for e in events_5m),
            'outbound_bytes_1hr': sum(e.bytes_sent for e in events_1hr),
            'unique_dst_ips_5m': len(set(e.dst_ip_hash for e in events_5m)),
            'unique_dst_ips_1hr': len(set(e.dst_ip_hash for e in events_1hr)),
            'unique_dst_ports_1hr': len(set(e.dst_port for e in events_1hr)),
            'dns_query_count_5m': len([e for e in events_5m if e.dst_port == 53]),
            'rare_port_connections': len([
                e for e in events_1hr if FeatureUtils.is_rare_port(e.dst_port)
            ]),
            'periodic_connection_score': FeatureUtils.calculate_beacon_score(
                self.connection_times[host_hash]
            )
        }
    
    def get_file_features(self, host_hash: str,
                         current_time: datetime) -> Dict[str, Any]:
        """Compute file-related features from buffered events"""
        events = self.file_events[host_hash]
        
        t_1m = current_time - timedelta(minutes=1)
        t_5m = current_time - timedelta(minutes=5)
        
        events_1m = [e for e in events if e.timestamp > t_1m]
        events_5m = [e for e in events if e.timestamp > t_5m]
        
        writes_1m = [e for e in events_1m if e.operation in ('write', 'create')]
        writes_5m = [e for e in events_5m if e.operation in ('write', 'create')]
        renames_5m = [e for e in events_5m if e.operation == 'rename']
        
        extensions = set(e.file_extension for e in events_5m if e.file_extension)
        
        return {
            'file_write_rate_1m': len(writes_1m),
            'file_write_rate_5m': len(writes_5m) / 5.0,  # Per minute average
            'file_rename_count_5m': len(renames_5m),
            'unique_extensions_written': len(extensions),
            'encryption_indicator': self._calc_encryption_indicator(events_5m)
        }
    
    def get_auth_features(self, host_hash: str,
                         current_time: datetime) -> Dict[str, Any]:
        """Compute authentication-related features"""
        events = self.logon_events[host_hash]
        
        t_10m = current_time - timedelta(minutes=10)
        t_1hr = current_time - timedelta(hours=1)
        
        events_10m = [e for e in events if e.timestamp > t_10m]
        events_1hr = [e for e in events if e.timestamp > t_1hr]
        
        failed_10m = [e for e in events_10m if not e.success]
        failed_1hr = [e for e in events_1hr if not e.success]
        remote_logons = [e for e in events_1hr if e.logon_type == 10 and e.success]
        
        return {
            'failed_logons_10m': len(failed_10m),
            'failed_logons_1hr': len(failed_1hr),
            'unique_failed_users_1hr': len(set(e.user_hash for e in failed_1hr)),
            'remote_logon_count': len(remote_logons),
        }
    
    def _calc_encryption_indicator(self, file_events: List[FileEvent]) -> float:
        """
        Calculate encryption indicator based on file patterns.
        High values indicate: many files, many extensions, rapid writes
        """
        if not file_events:
            return 0.0
        
        extensions = set(e.file_extension for e in file_events)
        
        # Indicators of ransomware:
        # - Many different extensions being written
        # - Unusual extensions (.encrypted, .locked, .cry, etc.)
        
        suspicious_exts = {'.encrypted', '.locked', '.crypto', '.cry', '.enc'}
        has_suspicious = any(ext in suspicious_exts for ext in extensions)
        
        # Score based on number of unique extensions and suspicious patterns
        ext_score = min(len(extensions) / 20.0, 1.0)  # Normalize to 0-1
        suspicious_score = 0.5 if has_suspicious else 0.0
        
        return round(min(ext_score + suspicious_score, 1.0), 4)


# =============================================================================
# MAIN FEATURE EXTRACTOR
# =============================================================================

class FeatureExtractor:
    """
    Main feature extraction class.
    Converts raw events into ML-ready feature rows.
    
    Usage:
        extractor = FeatureExtractor()
        for event in collector.collect_all():
            feature_row = extractor.process(event, host_hash)
            if feature_row:
                detector.score(feature_row)
    """
    
    def __init__(self, aggregation_window: int = 60):
        """
        Args:
            aggregation_window: Seconds between feature row emissions
        """
        self.aggregator = TimeWindowAggregator()
        self.aggregation_window = aggregation_window
        self.last_emission: Dict[str, datetime] = {}
        
    def process(self, event: RawEvent, host_hash: str) -> Optional[FeatureRow]:
        """
        Process a single event, potentially returning a feature row.
        Returns FeatureRow if aggregation window elapsed, else None.
        """
        current_time = event.timestamp
        
        # Add to aggregator
        self.aggregator.add_event(event, host_hash)
        
        # Check if we should emit a feature row
        last_emit = self.last_emission.get(host_hash)
        if last_emit and (current_time - last_emit).total_seconds() < self.aggregation_window:
            return None
        
        # Emit feature row
        self.last_emission[host_hash] = current_time
        return self._create_feature_row(event, host_hash, current_time)
    
    def _create_feature_row(self, event: RawEvent, host_hash: str,
                           current_time: datetime) -> FeatureRow:
        """Create a complete feature row from aggregated events"""
        
        # Get aggregated features
        network_features = self.aggregator.get_network_features(host_hash, current_time)
        file_features = self.aggregator.get_file_features(host_hash, current_time)
        auth_features = self.aggregator.get_auth_features(host_hash, current_time)
        
        # Process features (from most recent process event or current event)
        process_name = ""
        parent_process = ""
        cmdline = ""
        image_path = ""
        
        if isinstance(event, ProcessEvent):
            process_name = event.process_name
            parent_process = event.parent_name
            cmdline = event.command_line
            image_path = event.image_path
        
        # Compute risk scores
        ransomware_score = self._calc_ransomware_score(file_features, cmdline)
        exfil_score = self._calc_exfil_score(network_features)
        c2_beacon_score = network_features['periodic_connection_score']
        lateral_score = self._calc_lateral_movement_score(auth_features)
        
        # Prune old events
        self.aggregator.prune_old_events(host_hash, current_time)
        
        return FeatureRow(
            timestamp=current_time.isoformat(),
            host_hash=host_hash,
            process_name=process_name,
            parent_process=parent_process,
            cmdline_entropy=FeatureUtils.calculate_entropy(cmdline),
            cmdline_length=len(cmdline),
            cmdline_has_base64=1 if FeatureUtils.detect_base64(cmdline) else 0,
            cmdline_has_url=1 if FeatureUtils.detect_url(cmdline) else 0,
            is_unusual_path=1 if FeatureUtils.is_unusual_path(image_path) else 0,
            is_lolbin=1 if FeatureUtils.is_lolbin(process_name) else 0,
            **network_features,
            dns_txt_query_count=0,  # TODO: Implement TXT query detection
            **file_features,
            **auth_features,
            new_admin_indicator=0,  # TODO: Implement admin creation detection
            ransomware_score=ransomware_score,
            exfil_score=exfil_score,
            c2_beacon_score=c2_beacon_score,
            lateral_movement_score=lateral_score,
            event_count=self._count_events(host_hash),
            primary_event_type=event.event_type
        )
    
    def _calc_ransomware_score(self, file_features: Dict, cmdline: str) -> float:
        """Combined ransomware indicator score"""
        score = 0.0
        
        # High file write rate
        if file_features['file_write_rate_1m'] > 50:
            score += 0.3
        elif file_features['file_write_rate_1m'] > 20:
            score += 0.15
        
        # Many file renames
        if file_features['file_rename_count_5m'] > 100:
            score += 0.3
        elif file_features['file_rename_count_5m'] > 30:
            score += 0.15
        
        # Encryption indicator
        score += file_features['encryption_indicator'] * 0.4
        
        return round(min(score, 1.0), 4)
    
    def _calc_exfil_score(self, network_features: Dict) -> float:
        """Combined exfiltration indicator score"""
        score = 0.0
        
        # High outbound bytes
        if network_features['outbound_bytes_5m'] > 100_000_000:  # 100MB
            score += 0.4
        elif network_features['outbound_bytes_5m'] > 10_000_000:  # 10MB
            score += 0.2
        
        # Many unique destinations
        if network_features['unique_dst_ips_1hr'] > 50:
            score += 0.3
        elif network_features['unique_dst_ips_1hr'] > 20:
            score += 0.15
        
        # Rare ports
        if network_features['rare_port_connections'] > 10:
            score += 0.3
        
        return round(min(score, 1.0), 4)
    
    def _calc_lateral_movement_score(self, auth_features: Dict) -> float:
        """Combined lateral movement indicator score"""
        score = 0.0
        
        # Many failed logons
        if auth_features['failed_logons_10m'] > 10:
            score += 0.4
        elif auth_features['failed_logons_10m'] > 5:
            score += 0.2
        
        # Multiple failed users (password spraying)
        if auth_features['unique_failed_users_1hr'] > 5:
            score += 0.3
        
        # Remote logons
        if auth_features['remote_logon_count'] > 5:
            score += 0.3
        
        return round(min(score, 1.0), 4)
    
    def _count_events(self, host_hash: str) -> int:
        """Count total events in aggregator for this host"""
        return (
            len(self.aggregator.process_events[host_hash]) +
            len(self.aggregator.network_events[host_hash]) +
            len(self.aggregator.file_events[host_hash]) +
            len(self.aggregator.logon_events[host_hash])
        )
    
    def flush(self, host_hash: str) -> Optional[FeatureRow]:
        """Force emission of current aggregated features"""
        if not any([
            self.aggregator.process_events[host_hash],
            self.aggregator.network_events[host_hash],
            self.aggregator.file_events[host_hash],
            self.aggregator.logon_events[host_hash]
        ]):
            return None
        
        # Create a dummy event for timestamp
        from datetime import datetime
        current_time = datetime.now()
        
        dummy_event = RawEvent(
            event_type='flush',
            timestamp=current_time,
            source='internal',
            raw_data={}
        )
        
        return self._create_feature_row(dummy_event, host_hash, current_time)


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Feature Extractor")
    parser.add_argument("--input", required=True, help="Input events JSONL file")
    parser.add_argument("--output", default="features.jsonl",
                        help="Output features JSONL file")
    parser.add_argument("--window", type=int, default=60,
                        help="Aggregation window in seconds")
    
    args = parser.parse_args()
    
    extractor = FeatureExtractor(aggregation_window=args.window)
    
    count = 0
    with open(args.input, 'r') as f_in, open(args.output, 'w') as f_out:
        for line in f_in:
            event_data = json.loads(line)
            
            # Deserialize based on event type
            event_type = event_data.get('event_type')
            if event_type in ('process_create', 'process_terminate', 'process_snapshot'):
                event = ProcessEvent(**event_data)
            elif event_type in ('network_connect', 'network_flow'):
                event = NetworkEvent(**event_data)
            elif event_type in ('file_create', 'file_delete', 'file_rename'):
                event = FileEvent(**event_data)
            elif event_type in ('logon_success', 'logon_failure', 'user_created'):
                event = LogonEvent(**event_data)
            else:
                # Fallback for unknown events - filter out extra fields for RawEvent
                base_fields = {'event_type', 'timestamp', 'source', 'raw_data'}
                filtered_data = {k: v for k, v in event_data.items() if k in base_fields}
                event = RawEvent(**filtered_data)
                
            # Fix timestamp string back to datetime
            if isinstance(event.timestamp, str):
                try:
                    event.timestamp = datetime.fromisoformat(event.timestamp)
                except ValueError:
                    pass

            host_hash = event_data.get('host_hash', 'unknown')
            
            feature_row = extractor.process(event, host_hash)
            if feature_row:
                f_out.write(json.dumps(feature_row.to_dict()) + '\n')
                count += 1
    
    print(f"[INFO] Extracted {count} feature rows")
