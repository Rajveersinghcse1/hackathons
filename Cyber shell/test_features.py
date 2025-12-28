"""Test feature extraction on ransomware scenario"""
from pathlib import Path
from agent.collector import SysmonCollector, PrivacyHasher
from parser.feature_extractor import FeatureExtractor, FeatureUtils
from model.detect import HybridDetector

# Load events
hasher = PrivacyHasher()
collector = SysmonCollector(hasher, csv_path=Path('scenarios/data/malicious-ransomware/sysmon_ransomware.csv'))
events = list(collector.collect())
print(f'Collected {len(events)} events')

# Check individual events for features
print('\n--- Per-Event Analysis ---')
for i, e in enumerate(events[:5]):
    pname = getattr(e, 'process_name', 'N/A')
    cmd = getattr(e, 'command_line', '')
    is_lolbin = FeatureUtils.is_lolbin(pname)
    has_base64 = FeatureUtils.detect_base64(cmd)
    entropy = FeatureUtils.calculate_entropy(cmd)
    print(f'Event {i}: {pname} - lolbin={is_lolbin}, base64={has_base64}, entropy={entropy:.2f}')

print('\n--- Feature Extraction (1s window) ---')
# Extract features with very small window
extractor = FeatureExtractor(aggregation_window=1)
rows = []
for i, event in enumerate(events):
    host_hash = getattr(event, 'user_hash', 'host_unknown')
    row = extractor.process(event, host_hash)
    if row:
        rows.append(row)
        pname = getattr(event, 'process_name', 'N/A')
        print(f'Row from event {i} ({pname}): is_lolbin={row.is_lolbin}, base64={row.cmdline_has_base64}, entropy={row.cmdline_entropy:.2f}')

# Flush remaining
final = extractor.flush('host_unknown')
if final:
    rows.append(final)
    print(f'Flushed Row: is_lolbin={final.is_lolbin}, base64={final.cmdline_has_base64}')

print(f'\nTotal feature rows: {len(rows)}')

# Run detection
print('\n--- Detection ---')
detector = HybridDetector()
for i, row in enumerate(rows):
    result = detector.detect(row)
    if result.risk_score >= 40:
        print(f'[ALERT] Row {i}: score={result.risk_score}, type={result.alert_type}, rules={result.rule_matches}')
