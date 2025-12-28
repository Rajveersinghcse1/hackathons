"""
CyberShell Privacy Utilities
=============================

Centralized privacy functions for consistent anonymization.
All PII (usernames, IPs, hostnames) are SHA-256 hashed before storage/transmission.
"""

import hashlib
import re
import json
from pathlib import Path
from typing import Dict, Optional, Any


class PrivacyHasher:
    """
    Handles all identifier anonymization.
    Uses salted SHA-256 hashing - one-way without the salt.
    
    This is the primary class for privacy operations.
    Aliased as PrivacyManager for backward compatibility.
    """
    
    def __init__(self, salt: Optional[str] = None, salt_file: str = ".cybershell_salt"):
        """
        Initialize with optional salt.
        If no salt provided, loads from file or creates new one.
        
        Args:
            salt: Optional explicit salt value
            salt_file: Path to salt file (used if salt not provided)
        """
        self.salt_file = Path(salt_file)
        self.salt = salt or self._load_or_create_salt()
        self._mappings: Dict[str, str] = {}
    
    def _load_or_create_salt(self) -> str:
        """Load existing salt or create new one"""
        if self.salt_file.exists():
            return self.salt_file.read_text().strip()
        
        import secrets
        salt = secrets.token_hex(32)
        # Only write if parent directory exists
        try:
            self.salt_file.write_text(salt)
        except:
            pass  # Skip file creation in test environments
        return salt
    
    def hash(self, value: str, prefix: str = "") -> str:
        """Hash an identifier with optional prefix"""
        if value is None:
            return f"{prefix}_NONE" if prefix else "NONE"
        if value == "":
            return f"{prefix}_EMPTY" if prefix else "EMPTY"
        
        hash_input = f"{self.salt}:{value}".encode('utf-8')
        hash_output = hashlib.sha256(hash_input).hexdigest()[:16]
        
        result = f"{prefix}_{hash_output}" if prefix else hash_output
        self._mappings[result] = value
        
        return result
    
    def hash_username(self, username: str) -> str:
        """Hash a username. Returns USR_<hash>"""
        return self.hash(username, "USR")
    
    def hash_ip(self, ip: str) -> str:
        """Hash an IP address. Returns IP_<hash>"""
        return self.hash(ip, "IP")
    
    def hash_hostname(self, hostname: str) -> str:
        """Hash a hostname. Returns HOST_<hash>"""
        return self.hash(hostname, "HOST")
    
    def sanitize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize an entire event dictionary.
        Hashes known PII fields while preserving other data.
        
        Args:
            event: Dictionary containing event data
            
        Returns:
            New dictionary with PII fields hashed
        """
        result = event.copy()
        
        # Hash known PII fields
        pii_mappings = {
            'username': self.hash_username,
            'user': self.hash_username,
            'user_hash': lambda x: x,  # Already hashed
            'src_ip': self.hash_ip,
            'dst_ip': self.hash_ip,
            'source_ip': self.hash_ip,
            'dest_ip': self.hash_ip,
            'ip_address': self.hash_ip,
            'hostname': self.hash_hostname,
            'computer_name': self.hash_hostname,
        }
        
        for field, hash_func in pii_mappings.items():
            if field in result and result[field]:
                result[field] = hash_func(result[field])
        
        return result
    
    def save_mappings(self, path: str = ".hash_mapping.json"):
        """Save hash mappings for authorized lookup"""
        Path(path).write_text(json.dumps(self._mappings, indent=2))
    
    def lookup(self, hashed_value: str) -> Optional[str]:
        """
        Look up original value from hash (if in local mappings).
        This only works for values hashed in this session.
        """
        return self._mappings.get(hashed_value)


# Backward compatibility alias
PrivacyManager = PrivacyHasher


def hash_identifier(value: str, salt: str = "default_salt") -> str:
    """Standalone hash function"""
    if not value:
        return "unknown"
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:16]


def anonymize_log_line(line: str, privacy_manager: Optional[PrivacyManager] = None) -> str:
    """
    Anonymize a log line by replacing IPs and usernames.
    
    Patterns replaced:
    - IP addresses: 192.168.1.1 -> ip_abc123
    - Usernames: DOMAIN\\user -> user_def456
    - Email patterns: user@domain.com -> email_ghi789
    """
    pm = privacy_manager or PrivacyManager()
    
    # Replace IP addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    for match in re.finditer(ip_pattern, line):
        ip = match.group()
        line = line.replace(ip, pm.hash_ip(ip))
    
    # Replace DOMAIN\user patterns
    user_pattern = r'\b[A-Za-z0-9]+\\[A-Za-z0-9._-]+\b'
    for match in re.finditer(user_pattern, line):
        user = match.group()
        line = line.replace(user, pm.hash_username(user))
    
    # Replace email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for match in re.finditer(email_pattern, line):
        email = match.group()
        line = line.replace(email, pm.hash(email, "email"))
    
    return line
