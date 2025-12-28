"""
Generate Enhanced Architecture Diagram
Shows world-class additions: SHAP Explainability, MITRE ATT&CK, Performance Monitoring
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects

# Ultra Style
plt.style.use('dark_background')

COLORS = {
    'bg': '#0b0f19',
    'card': '#151b2b',
    'cyan': '#00f2ea',
    'pink': '#ff0055',
    'orange': '#ff9f1c',
    'purple': '#b026ff',
    'green': '#00ff88',
    'gold': '#ffd700',
    'text': '#e2e8f0',
    'subtext': '#94a3b8',
}

def add_glow(artist, color, alpha=0.3, linewidth=5):
    artist.set_path_effects([
        path_effects.Stroke(linewidth=linewidth, foreground=color, alpha=alpha),
        path_effects.Normal()
    ])

def draw_component(ax, x, y, w, h, title, subtitle, color, badge=None):
    """Draw a component box with glow effect"""
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                  fc=COLORS['card'], ec=color, lw=2.5)
    ax.add_patch(rect)
    add_glow(rect, color, alpha=0.3, linewidth=8)
    
    # Title
    ax.text(x + w/2, y + h*0.65, title, ha='center', va='center',
            color=color, fontsize=11, fontweight='bold')
    
    # Subtitle
    ax.text(x + w/2, y + h*0.35, subtitle, ha='center', va='center',
            color=COLORS['subtext'], fontsize=8)
    
    # Badge (e.g., "NEW")
    if badge:
        badge_rect = patches.FancyBboxPatch((x + w - 0.6, y + h - 0.35), 0.5, 0.25,
                                            boxstyle="round,pad=0.02", fc=COLORS['pink'], ec='white', lw=1)
        ax.add_patch(badge_rect)
        ax.text(x + w - 0.35, y + h - 0.225, badge, ha='center', va='center',
                color='white', fontsize=7, fontweight='bold')
    
    return (x + w/2, y + h), (x + w/2, y)  # top, bottom connection points

def draw_arrow(ax, start, end, color, style='-', label=None):
    """Draw connection arrow"""
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->, head_width=0.3, head_length=0.3",
                               color=color, lw=2, linestyle=style))
    if label:
        mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2
        ax.text(mid_x + 0.2, mid_y, label, color=color, fontsize=7,
                bbox=dict(boxstyle='round,pad=0.3', fc=COLORS['bg'], ec=color, lw=1))

# Create figure
fig, ax = plt.subplots(figsize=(16, 12), facecolor=COLORS['bg'])
ax.set_facecolor(COLORS['bg'])
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# Title
ax.text(8, 11.3, "CYBERSHELL WORLD-CLASS ARCHITECTURE", ha='center',
        color='white', fontsize=22, fontweight='bold')
ax.text(8, 10.8, "Explainable AI + Threat Intelligence + Elite Performance Monitoring",
        ha='center', color=COLORS['subtext'], fontsize=11)

# === LAYER 1: DATA SOURCES ===
ax.text(8, 9.8, "DATA SOURCES", ha='center', color=COLORS['cyan'],
        fontsize=10, fontweight='bold')

wmi_top, wmi_bot = draw_component(ax, 1, 8.5, 2.2, 1, "WMI Events", "Windows Kernel", COLORS['cyan'])
sysmon_top, sysmon_bot = draw_component(ax, 3.8, 8.5, 2.2, 1, "Sysmon", "Process Logs", COLORS['cyan'])
pcap_top, pcap_bot = draw_component(ax, 6.6, 8.5, 2.2, 1, "PCAP", "Network Traffic", COLORS['cyan'])
evtx_top, evtx_bot = draw_component(ax, 9.4, 8.5, 2.2, 1, "Event Logs", "Auth Events", COLORS['cyan'])

# === LAYER 2: COLLECTION ===
ax.text(8, 7.3, "COLLECTION LAYER", ha='center', color=COLORS['orange'],
        fontsize=10, fontweight='bold')

collector_top, collector_bot = draw_component(ax, 4, 6, 4, 1.2, "Async Collector Agent",
                                               "Privacy Hashing (SHA-256)", COLORS['orange'])

# Connect sources to collector
for bot in [wmi_bot, sysmon_bot, pcap_bot, evtx_bot]:
    draw_arrow(ax, bot, collector_top, COLORS['cyan'], style='--')

# === LAYER 3: FEATURE EXTRACTION ===
ax.text(8, 5, "FEATURE ENGINEERING", ha='center', color=COLORS['purple'],
        fontsize=10, fontweight='bold')

features_top, features_bot = draw_component(ax, 3.5, 3.5, 5, 1.4, "Feature Extractor",
                                             "30+ Features: Entropy, Beaconing, Lateral Movement",
                                             COLORS['purple'])

draw_arrow(ax, collector_bot, features_top, COLORS['orange'])

# === LAYER 4: DETECTION ENGINE (Enhanced) ===
ax.text(8, 2.8, "HYBRID DETECTION ENGINE (ENHANCED)", ha='center', color=COLORS['pink'],
        fontsize=10, fontweight='bold')

# Main detector
detector_top, detector_bot = draw_component(ax, 5, 1.2, 3, 1.5, "Neuro-Symbolic Detector",
                                             "Rules + IsolationForest ML", COLORS['pink'])

draw_arrow(ax, features_bot, detector_top, COLORS['purple'])

# === NEW: EXPLAINABILITY MODULE ===
shap_top, shap_bot = draw_component(ax, 0.5, 1.2, 2.8, 1.5, "SHAP Explainer",
                                     "Feature Importance + NL", COLORS['green'], badge="NEW")

draw_arrow(ax, detector_bot, (shap_top[0], shap_top[1] - 0.3), COLORS['pink'], label="ML Output")
draw_arrow(ax, (shap_top[0], shap_bot[1] + 0.3), detector_top, COLORS['green'], style='--', label="Explanation")

# === NEW: MITRE ATT&CK MAPPING ===
mitre_top, mitre_bot = draw_component(ax, 8.7, 1.2, 2.8, 1.5, "MITRE ATT&CK",
                                       "Threat Intelligence", COLORS['orange'], badge="NEW")

draw_arrow(ax, detector_bot, (mitre_top[0], mitre_top[1] - 0.3), COLORS['pink'], label="Detection")
draw_arrow(ax, (mitre_top[0], mitre_bot[1] + 0.3), detector_top, COLORS['orange'], style='--', label="TTPs")

# === NEW: PERFORMANCE MONITORING ===
perf_top, perf_bot = draw_component(ax, 12.2, 1.2, 2.8, 1.5, "Performance Monitor",
                                     "Latency & Throughput", COLORS['gold'], badge="NEW")

draw_arrow(ax, detector_bot, (perf_top[0], perf_top[1] - 0.3), COLORS['pink'], label="Metrics")

# === LAYER 5: OUTPUT & UI ===
ax.text(8, -0.3, "OUTPUT LAYER", ha='center', color=COLORS['cyan'],
        fontsize=10, fontweight='bold')

# Dashboard
dashboard_top, dashboard_bot = draw_component(ax, 2, -1.8, 4, 1.3, "Elite Dashboard",
                                               "Plotly Timeline + MITRE Heatmap", COLORS['purple'], badge="NEW")

# Alerts
alerts_top, alerts_bot = draw_component(ax, 7, -1.8, 4, 1.3, "Alert System",
                                         "JSONL + Real-time Feed", COLORS['cyan'])

# Response
response_top, response_bot = draw_component(ax, 12, -1.8, 3, 1.3, "Response",
                                             "Playbooks", COLORS['orange'])

# Connect outputs
draw_arrow(ax, shap_bot, dashboard_top, COLORS['green'])
draw_arrow(ax, detector_bot, alerts_top, COLORS['pink'])
draw_arrow(ax, mitre_bot, response_top, COLORS['orange'])

# === LEGEND ===
legend_x, legend_y = 0.5, -3
ax.text(legend_x, legend_y, "LEGEND:", color='white', fontsize=9, fontweight='bold')
ax.text(legend_x, legend_y - 0.3, "● Cyan: Data Flow", color=COLORS['cyan'], fontsize=8)
ax.text(legend_x, legend_y - 0.6, "● Pink: AI Detection", color=COLORS['pink'], fontsize=8)
ax.text(legend_x + 3, legend_y - 0.3, "● Green: Explainability (NEW)", color=COLORS['green'], fontsize=8)
ax.text(legend_x + 3, legend_y - 0.6, "● Orange: Threat Intel (NEW)", color=COLORS['orange'], fontsize=8)
ax.text(legend_x + 7, legend_y - 0.3, "● Gold: Performance (NEW)", color=COLORS['gold'], fontsize=8)

# Save
plt.savefig('images/architecture_enhanced.png', dpi=300, bbox_inches='tight', facecolor=COLORS['bg'])
print("✅ Generated architecture_enhanced.png")
plt.close()
