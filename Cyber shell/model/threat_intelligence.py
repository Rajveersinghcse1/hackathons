"""
CyberShell Threat Intelligence - MITRE ATT&CK Mapping Module
============================================================

Purpose: Map detected threats to MITRE ATT&CK framework tactics and techniques.
This provides standardized threat classification and helps SOC teams
understand the attack kill chain and appropriate countermeasures.

Features:
- Automatic mapping of detection categories to ATT&CK TTPs
- Kill chain phase identification
- Recommended mitigations from MITRE
- Threat actor profiling (APT group linkage)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class AttackTactic(Enum):
    """MITRE ATT&CK Tactics (high-level goals)"""
    INITIAL_ACCESS = "TA0001"
    EXECUTION = "TA0002"
    PERSISTENCE = "TA0003"
    PRIVILEGE_ESCALATION = "TA0004"
    DEFENSE_EVASION = "TA0005"
    CREDENTIAL_ACCESS = "TA0006"
    DISCOVERY = "TA0007"
    LATERAL_MOVEMENT = "TA0008"
    COLLECTION = "TA0009"
    COMMAND_AND_CONTROL = "TA0011"
    EXFILTRATION = "TA0010"
    IMPACT = "TA0040"


@dataclass
class AttackTechnique:
    """MITRE ATT&CK Technique details"""
    technique_id: str          # e.g., "T1486"
    technique_name: str        # e.g., "Data Encrypted for Impact"
    tactic: AttackTactic       # Parent tactic
    description: str           # Brief description
    detection_methods: List[str]  # How to detect
    mitigations: List[str]     # How to prevent/mitigate
    example_groups: List[str]  # APT groups known to use this


@dataclass
class ThreatIntelligence:
    """Enriched threat intelligence for a detection"""
    primary_technique: AttackTechnique
    related_techniques: List[AttackTechnique]
    kill_chain_phase: str      # e.g., "Actions on Objectives"
    severity_justification: str  # Why this severity level
    recommended_actions: List[str]  # Immediate response steps
    threat_actor_profile: Optional[str]  # Possible attribution
    
    def to_dict(self) -> Dict:
        return {
            'primary_technique': {
                'id': self.primary_technique.technique_id,
                'name': self.primary_technique.technique_name,
                'tactic': self.primary_technique.tactic.name,
                'description': self.primary_technique.description
            },
            'related_techniques': [
                {'id': t.technique_id, 'name': t.technique_name} 
                for t in self.related_techniques
            ],
            'kill_chain_phase': self.kill_chain_phase,
            'severity_justification': self.severity_justification,
            'recommended_actions': self.recommended_actions,
            'threat_actor_profile': self.threat_actor_profile
        }


# =============================================================================
# TECHNIQUE DATABASE (Subset of MITRE ATT&CK)
# =============================================================================

TECHNIQUE_DATABASE = {
    # Ransomware / Impact
    'T1486': AttackTechnique(
        technique_id='T1486',
        technique_name='Data Encrypted for Impact',
        tactic=AttackTactic.IMPACT,
        description='Adversaries may encrypt data on target systems to interrupt availability and demand ransom.',
        detection_methods=[
            'Monitor for rapid file modifications/renames',
            'Unusual processes accessing many files',
            'High entropy file content'
        ],
        mitigations=[
            'Maintain offline backups',
            'Implement application whitelisting',
            'Use Behavior Prevention on Endpoint Security'
        ],
        example_groups=['Conti', 'REvil', 'LockBit', 'BlackCat']
    ),
    
    # C2 Communication
    'T1071': AttackTechnique(
        technique_id='T1071',
        technique_name='Application Layer Protocol',
        tactic=AttackTactic.COMMAND_AND_CONTROL,
        description='Adversaries may communicate using application layer protocols to avoid detection.',
        detection_methods=[
            'Monitor for beaconing patterns',
            'Analyze traffic to unusual destinations',
            'Detect protocol anomalies'
        ],
        mitigations=[
            'Network Intrusion Prevention',
            'Filter Network Traffic',
            'SSL/TLS Inspection'
        ],
        example_groups=['APT29', 'FIN7', 'Lazarus Group']
    ),
    
    # Data Exfiltration
    'T1041': AttackTechnique(
        technique_id='T1041',
        technique_name='Exfiltration Over C2 Channel',
        tactic=AttackTactic.EXFILTRATION,
        description='Adversaries may steal data by exfiltrating it over an existing C2 channel.',
        detection_methods=[
            'Monitor for large outbound transfers',
            'Detect data leaving through unusual ports',
            'Baseline normal data flow volumes'
        ],
        mitigations=[
            'Data Loss Prevention',
            'Network Segmentation',
            'Monitor Outbound Traffic'
        ],
        example_groups=['APT28', 'APT33', 'Carbanak']
    ),
    
    # LOLBins / Defense Evasion
    'T1218': AttackTechnique(
        technique_id='T1218',
        technique_name='System Binary Proxy Execution',
        tactic=AttackTactic.DEFENSE_EVASION,
        description='Adversaries may bypass process and signature-based defenses by proxying execution via trusted system binaries.',
        detection_methods=[
            'Monitor command-line parameters of system utilities',
            'Detect unusual parent-child process relationships',
            'Alert on rare arguments to common tools'
        ],
        mitigations=[
            'Execution Prevention',
            'Privileged Account Management',
            'Restrict PowerShell/WMI Usage'
        ],
        example_groups=['APT32', 'FIN6', 'Turla']
    ),
    
    # Lateral Movement
    'T1021': AttackTechnique(
        technique_id='T1021',
        technique_name='Remote Services',
        tactic=AttackTactic.LATERAL_MOVEMENT,
        description='Adversaries may use valid accounts to log into services like RDP, SMB, or WinRM.',
        detection_methods=[
            'Monitor logon events (Type 3, 10)',
            'Detect authentication from unusual sources',
            'Alert on off-hours access'
        ],
        mitigations=[
            'Multi-Factor Authentication',
            'Limit Remote Access',
            'Network Segmentation'
        ],
        example_groups=['APT1', 'APT3', 'Dragonfly']
    ),
    
    # PowerShell / Execution
    'T1059.001': AttackTechnique(
        technique_id='T1059.001',
        technique_name='PowerShell',
        tactic=AttackTactic.EXECUTION,
        description='Adversaries may abuse PowerShell commands and scripts for execution.',
        detection_methods=[
            'Monitor PowerShell execution logs (Event ID 4104)',
            'Detect obfuscated/encoded commands',
            'Alert on suspicious cmdlets'
        ],
        mitigations=[
            'Disable PowerShell if not needed',
            'Enable PowerShell logging',
            'Use Constrained Language Mode'
        ],
        example_groups=['APT29', 'APT33', 'FIN8']
    ),
}


# =============================================================================
# MAPPING LOGIC
# =============================================================================

class MITREMapper:
    """Maps CyberShell detection categories to MITRE ATT&CK techniques"""
    
    CATEGORY_TO_TECHNIQUE = {
        'ransomware': ['T1486'],  # Data Encrypted for Impact
        'exfil': ['T1041'],       # Exfiltration Over C2
        'c2': ['T1071'],          # Application Layer Protocol
        'lolbin': ['T1218', 'T1059.001'],  # System Binary Proxy, PowerShell
        'lateral': ['T1021'],     # Remote Services
        'credential_access': ['T1003'],  # OS Credential Dumping (would add to DB)
    }
    
    KILL_CHAIN_MAPPING = {
        'ransomware': 'Actions on Objectives',
        'exfil': 'Exfiltration',
        'c2': 'Command and Control',
        'lolbin': 'Execution / Defense Evasion',
        'lateral': 'Lateral Movement',
        'credential_access': 'Credential Access'
    }
    
    @classmethod
    def enrich_detection(cls, detection_result) -> ThreatIntelligence:
        """
        Enrich a detection with MITRE ATT&CK context.
        
        Args:
            detection_result: DetectionResult from HybridDetector
            
        Returns:
            ThreatIntelligence with ATT&CK mapping
        """
        category = detection_result.category
        
        # Get primary technique
        technique_ids = cls.CATEGORY_TO_TECHNIQUE.get(category, [])
        if not technique_ids:
            return cls._unknown_threat(category)
        
        primary_id = technique_ids[0]
        primary_tech = TECHNIQUE_DATABASE.get(primary_id)
        
        if not primary_tech:
            return cls._unknown_threat(category)
        
        # Get related techniques
        related = [
            TECHNIQUE_DATABASE[tid] 
            for tid in technique_ids[1:] 
            if tid in TECHNIQUE_DATABASE
        ]
        
        # Determine kill chain phase
        kill_chain = cls.KILL_CHAIN_MAPPING.get(category, 'Unknown Phase')
        
        # Generate severity justification
        severity_just = cls._generate_severity_justification(
            detection_result, primary_tech
        )
        
        # Recommended immediate actions
        actions = cls._generate_recommended_actions(category, detection_result)
        
        # Threat actor profiling (basic)
        actor_profile = cls._infer_threat_actor(detection_result, primary_tech)
        
        return ThreatIntelligence(
            primary_technique=primary_tech,
            related_techniques=related,
            kill_chain_phase=kill_chain,
            severity_justification=severity_just,
            recommended_actions=actions,
            threat_actor_profile=actor_profile
        )
    
    @classmethod
    def _generate_severity_justification(cls, detection, technique) -> str:
        """Generate explanation for severity rating"""
        if detection.risk_score >= 80:
            return f"Critical severity due to {technique.technique_name} detection with score {detection.risk_score}/100. This indicates active {technique.tactic.name.lower()} in progress."
        elif detection.risk_score >= 60:
            return f"High severity - {technique.technique_name} indicators observed with moderate confidence."
        elif detection.risk_score >= 40:
            return f"Medium severity - possible {technique.technique_name} activity detected."
        else:
            return f"Low severity - weak indicators of {technique.technique_name}."
    
    @classmethod
    def _generate_recommended_actions(cls, category: str, detection) -> List[str]:
        """Generate context-aware response recommendations"""
        base_actions = [
            "1. Isolate affected host from network",
            "2. Capture memory dump for forensic analysis",
            "3. Review security event logs for related activity",
            "4. Check for persistence mechanisms",
            "5. Escalate to Incident Response team"
        ]
        
        category_specific = {
            'ransomware': [
                "IMMEDIATE: Disconnect from network to prevent spread",
                "DO NOT pay ransom - contact law enforcement",
                "Restore from offline backups if available",
                "Preserve evidence for law enforcement"
            ],
            'exfil': [
                "Block outbound connection to C2 IP immediately",
                "Identify what data was accessed/exfiltrated",
                "Reset credentials for affected accounts",
                "Review DLP logs for data classification"
            ],
            'c2': [
                "Terminate suspicious process immediately",
                "Block C2 IP/domain at firewall",
                "Check for additional compromised hosts",
                "Hunt for beaconing patterns across network"
            ],
            'lolbin': [
                "Analyze PowerShell/WMI command history",
                "Check for scheduled tasks or WMI persistence",
                "Review recent script executions",
                "Enable enhanced PowerShell logging"
            ],
            'lateral': [
                "Disable compromised account immediately",
                "Review authentication logs for source IP",
                "Check for privilege escalation",
                "Audit group membership changes"
            ]
        }
        
        specific = category_specific.get(category, [])
        return specific + base_actions[:3]
    
    @classmethod
    def _infer_threat_actor(cls, detection, technique) -> Optional[str]:
        """Basic threat actor profiling based on TTPs"""
        # In production, this would use a threat intelligence feed
        # For now, provide generic profiling based on technique
        
        if detection.category == 'ransomware' and detection.risk_score >= 80:
            return f"Possible ransomware group: {', '.join(technique.example_groups[:2])}. TTPs align with known ransomware operators."
        elif detection.category == 'c2':
            return f"C2 behavior consistent with APT groups: {', '.join(technique.example_groups[:2])}."
        else:
            return None
    
    @classmethod
    def _unknown_threat(cls, category: str) -> ThreatIntelligence:
        """Fallback for unknown categories"""
        return ThreatIntelligence(
            primary_technique=AttackTechnique(
                technique_id='T0000',
                technique_name='Unknown Technique',
                tactic=AttackTactic.DISCOVERY,
                description=f'Unknown threat category: {category}',
                detection_methods=[],
                mitigations=[],
                example_groups=[]
            ),
            related_techniques=[],
            kill_chain_phase='Unknown',
            severity_justification='Insufficient data for severity assessment',
            recommended_actions=['Investigate manually', 'Gather more context'],
            threat_actor_profile=None
        )


# =============================================================================
# INTEGRATION WITH DETECTOR
# =============================================================================

def add_mitre_context_to_detection(detection_result):
    """
    Enrich detection with MITRE ATT&CK context.
    
    Usage:
        result = detector.detect(features)
        enriched = add_mitre_context_to_detection(result)
        print(enriched.mitre_attack)
    """
    mitre_intel = MITREMapper.enrich_detection(detection_result)
    detection_result.mitre_attack = mitre_intel.to_dict()
    detection_result.kill_chain_phase = mitre_intel.kill_chain_phase
    detection_result.recommended_actions = mitre_intel.recommended_actions
    return detection_result


if __name__ == "__main__":
    print("CyberShell MITRE ATT&CK Mapping Module")
    print("=" * 50)
    print(f"Loaded {len(TECHNIQUE_DATABASE)} ATT&CK techniques")
    print("\nSupported categories:")
    for cat, techniques in MITREMapper.CATEGORY_TO_TECHNIQUE.items():
        print(f"  - {cat}: {techniques}")
