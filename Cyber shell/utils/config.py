"""
CyberShell Configuration Management
====================================

Centralized configuration for all modules.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class CollectionConfig:
    """Data collection settings"""
    sysmon: bool = True
    pcap: bool = True
    wmi: bool = False          # Disabled by default (live)
    eventlog: bool = True
    live_mode: bool = False    # Safe default


@dataclass
class PrivacyConfig:
    """Privacy settings"""
    hash_all_identifiers: bool = True
    strip_command_args: bool = False
    aggregate_only: bool = False


@dataclass
class DetectionConfig:
    """Detection engine settings"""
    threshold: int = 50
    rule_weight: float = 0.6
    ml_weight: float = 0.4
    model_path: str = "model/model.pkl"


@dataclass
class UIConfig:
    """UI settings"""
    simulate_mode: bool = True
    replay_sandbox: bool = True
    auto_refresh_seconds: int = 30


@dataclass
class Config:
    """Main configuration class"""
    collection: CollectionConfig = field(default_factory=CollectionConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary"""
        return cls(
            collection=CollectionConfig(**data.get('collection', {})),
            privacy=PrivacyConfig(**data.get('privacy', {})),
            detection=DetectionConfig(**data.get('detection', {})),
            ui=UIConfig(**data.get('ui', {}))
        )
    
    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        """Load config from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data or {})
    
    def to_yaml(self, path: str):
        """Save config to YAML file"""
        data = {
            'collection': self.collection.__dict__,
            'privacy': self.privacy.__dict__,
            'detection': self.detection.__dict__,
            'ui': self.ui.__dict__,
        }
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from file or return defaults"""
    if path and Path(path).exists():
        return Config.from_yaml(path)
    
    # Try default locations
    for default_path in ['config/settings.yaml', 'settings.yaml', '.cybershell.yaml']:
        if Path(default_path).exists():
            return Config.from_yaml(default_path)
    
    # Return defaults
    return Config()


# Create default config file if it doesn't exist
DEFAULT_CONFIG_CONTENT = """
# CyberShell Configuration
# ========================

collection:
  sysmon: true
  pcap: true
  wmi: false
  eventlog: true
  live_mode: false

privacy:
  hash_all_identifiers: true
  strip_command_args: false
  aggregate_only: false

detection:
  threshold: 50
  rule_weight: 0.6
  ml_weight: 0.4
  model_path: model/model.pkl

ui:
  simulate_mode: true
  replay_sandbox: true
  auto_refresh_seconds: 30
"""


def create_default_config(path: str = "config/settings.yaml"):
    """Create default configuration file"""
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(DEFAULT_CONFIG_CONTENT.strip())
    print(f"[INFO] Created default config at {path}")
