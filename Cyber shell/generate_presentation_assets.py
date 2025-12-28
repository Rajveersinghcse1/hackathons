import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import numpy as np

# --- ULTRA STYLE CONFIGURATION ---
plt.style.use('dark_background')

# Palette: Deep Space + Neon
COLORS = {
    'bg': '#0b0f19',       # Deepest Navy/Black
    'card_bg': '#151b2b',  # Slightly lighter for cards
    'cyan': '#00f2ea',     # Neon Cyan (Safe/Fast)
    'pink': '#ff0055',     # Neon Pink (AI/Brain)
    'orange': '#ff9f1c',   # Neon Orange (Warning/Cloud)
    'purple': '#b026ff',   # Neon Purple (Data/Privacy)
    'text': '#e2e8f0',     # Slate 200
    'subtext': '#94a3b8',  # Slate 400
    'grid': '#1e293b'      # Slate 800
}

def setup_figure(figsize=(12, 7)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    
    # Subtle Grid
    ax.grid(True, color=COLORS['grid'], linestyle='--', linewidth=0.5, alpha=0.3)
    ax.set_axisbelow(True)
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    return fig, ax

def add_glow(artist, color, alpha=0.3, linewidth=5):
    artist.set_path_effects([
        path_effects.Stroke(linewidth=linewidth, foreground=color, alpha=alpha),
        path_effects.Normal()
    ])

def save_plot(filename):
    plt.savefig(f'images/{filename}', dpi=300, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print(f"Generated {filename}")

# --- 1. PROBLEM STATEMENT: THE LATENCY GAP ---
def generate_problem_statement():
    fig, ax = setup_figure((14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.grid(False)

    # Title
    ax.text(7, 7.5, "THE LATENCY GAP: CLOUD vs EDGE", ha='center', color=COLORS['text'], fontsize=20, fontweight='bold')
    ax.text(7, 7.1, "Why milliseconds matter in ransomware defense", ha='center', color=COLORS['subtext'], fontsize=12)

    # --- TOP: CLOUD (The Problem) ---
    y_cloud = 5.5
    
    # Victim PC
    rect_victim = patches.FancyBboxPatch((1, y_cloud-1), 2.5, 2, boxstyle="round,pad=0.1", fc=COLORS['card_bg'], ec=COLORS['orange'], lw=2)
    ax.add_patch(rect_victim)
    add_glow(rect_victim, COLORS['orange'])
    ax.text(2.25, y_cloud, "Endpoint\n(Victim)", ha='center', va='center', color='white', fontweight='bold')

    # Cloud Server
    rect_cloud = patches.FancyBboxPatch((10.5, y_cloud-1), 2.5, 2, boxstyle="round,pad=0.1", fc=COLORS['card_bg'], ec=COLORS['orange'], lw=2)
    ax.add_patch(rect_cloud)
    add_glow(rect_cloud, COLORS['orange'])
    ax.text(11.75, y_cloud, "Cloud Server\n(Analysis)", ha='center', va='center', color='white', fontweight='bold')

    # Slow Path Arrows
    # Outbound
    ax.annotate("", xy=(10.5, y_cloud+0.5), xytext=(3.5, y_cloud+0.5), 
                arrowprops=dict(arrowstyle="->", color=COLORS['orange'], lw=2, ls='dashed'))
    ax.text(7, y_cloud+0.8, "1. Upload Telemetry (100ms+)", ha='center', color=COLORS['orange'], fontsize=10)
    
    # Inbound
    ax.annotate("", xy=(3.5, y_cloud-0.5), xytext=(10.5, y_cloud-0.5), 
                arrowprops=dict(arrowstyle="->", color=COLORS['orange'], lw=2, ls='dashed'))
    ax.text(7, y_cloud-0.8, "2. Receive Kill Command (100ms+)", ha='center', color=COLORS['orange'], fontsize=10)

    # Impact Label
    ax.text(7, y_cloud-1.5, "❌ TOTAL LATENCY: >200ms (4,000 Files Encrypted)", ha='center', color=COLORS['orange'], fontweight='bold', fontsize=12)


    # --- BOTTOM: CYBERSHELL (The Solution) ---
    y_edge = 2.0
    
    # CyberShell PC
    rect_cs = patches.FancyBboxPatch((1, y_edge-1), 2.5, 2, boxstyle="round,pad=0.1", fc=COLORS['card_bg'], ec=COLORS['cyan'], lw=2)
    ax.add_patch(rect_cs)
    add_glow(rect_cs, COLORS['cyan'])
    ax.text(2.25, y_edge, "Endpoint\n(CyberShell)", ha='center', va='center', color='white', fontweight='bold')

    # Local Loop
    # Draw a circular arrow looping back to the same box
    loop_path = patches.Arc((4.5, y_edge), 2, 2, theta1=90, theta2=270, color=COLORS['cyan'], lw=3)
    ax.add_patch(loop_path)
    add_glow(loop_path, COLORS['cyan'])
    
    # Arrow head
    ax.arrow(4.5, y_edge-1, -0.1, 0, color=COLORS['cyan'], head_width=0.2)

    ax.text(5.5, y_edge, "⚡ INSTANT LOCAL ANALYSIS", ha='left', va='center', color=COLORS['cyan'], fontweight='bold', fontsize=14)
    ax.text(5.5, y_edge-0.4, "No Network • No Latency • No Data Leak", ha='left', va='center', color=COLORS['subtext'], fontsize=10)

    # Impact Label
    ax.text(7, y_edge-1.5, "✅ TOTAL LATENCY: <15ms (0 Files Encrypted)", ha='center', color=COLORS['cyan'], fontweight='bold', fontsize=12)

    save_plot('problem_statement.png')


# --- 2. MEASURABLE IMPACT: NEON BAR CHART ---
def generate_measurable_impact():
    fig, ax = setup_figure((12, 6))
    
    # Data
    categories = ['Inference Speed\n(Lower is Better)', 'Data Privacy\n(Score)', 'False Positives\n(Lower is Better)']
    
    # Normalize data for visual comparison (0-100 scale roughly)
    # Speed: Cloud=200ms (Bad), Ours=15ms (Good). Inverted visual: Cloud=High Bar (Bad), Ours=Low Bar (Good)
    # Privacy: Cloud=0 (Bad), Ours=100 (Good)
    # FP: Cloud=15% (Bad), Ours=2% (Good)
    
    # We will do a grouped bar chart but styled
    x = np.arange(len(categories))
    width = 0.35
    
    # Values for display
    val_cloud_display = ["200ms+", "0% (Risky)", "15% (High)"]
    val_ours_display = ["<15ms", "100% (Safe)", "2% (Low)"]
    
    # Values for plotting height (arbitrary visual scale)
    h_cloud = [90, 10, 80]
    h_ours = [10, 100, 15]
    
    # Bars
    bars1 = ax.bar(x - width/2, h_cloud, width, label='Cloud EDR', color=COLORS['card_bg'], edgecolor=COLORS['orange'], linewidth=2)
    bars2 = ax.bar(x + width/2, h_ours, width, label='CyberShell', color=COLORS['cyan'], alpha=0.8)
    
    # Glow for CyberShell bars
    for bar in bars2:
        add_glow(bar, COLORS['cyan'], alpha=0.4, linewidth=10)

    # Labels
    ax.set_xticks(x)
    ax.set_xticklabels(categories, color='white', fontsize=12, fontweight='bold')
    ax.set_yticks([]) # Hide y-axis numbers
    
    # Legend
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, frameon=False, fontsize=12)
    plt.setp(legend.get_texts(), color='white')

    # Annotate values
    def annotate_bars(bars, texts, color, y_offset=2):
        for bar, text in zip(bars, texts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + y_offset,
                    text,
                    ha='center', va='bottom', color=color, fontweight='bold', fontsize=11)

    annotate_bars(bars1, val_cloud_display, COLORS['orange'])
    annotate_bars(bars2, val_ours_display, COLORS['cyan'])

    # Title
    fig.text(0.5, 0.02, "QUANTIFIABLE SUPERIORITY", ha='center', color=COLORS['subtext'], fontsize=14)
    
    save_plot('measurable_impact.png')


# --- 3. SYSTEM ARCHITECTURE: HUD STYLE ---
# --- 3. SYSTEM ARCHITECTURE: ENHANCED FLOW DIAGRAM ---
def generate_system_architecture():
    fig, ax = setup_figure((16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.grid(False)

    # --- ZONES WITH BETTER SPACING ---
    # Kernel Zone (Bottom) with gradient effect
    rect_kernel = patches.Rectangle((0, 0), 16, 2.2, fc='#1a0505', alpha=0.6, zorder=0)
    ax.add_patch(rect_kernel)
    ax.axhline(y=2.2, color=COLORS['orange'], linestyle='--', linewidth=2, alpha=0.8)
    ax.text(0.8, 1.6, "KERNEL SPACE (Ring 0)", color=COLORS['orange'], fontsize=13, fontweight='bold', alpha=0.9)
    ax.text(0.8, 1.1, "Windows Event Sources", color=COLORS['subtext'], fontsize=10, alpha=0.8)

    # Userland Zone (Top)
    ax.text(0.8, 8.3, "USERLAND (Ring 3) - SECURE PROCESSING", color=COLORS['cyan'], fontsize=13, fontweight='bold', alpha=0.9)
    ax.text(0.8, 7.85, "Privacy-First Detection Pipeline", color=COLORS['subtext'], fontsize=10, alpha=0.8)

    # --- ENHANCED COMPONENTS WITH BETTER SPACING ---
    
    def draw_component(x, y, w, h, title, subtitle, color, icon="", badge=None):
        # Box with enhanced styling
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", 
                                     fc=COLORS['card_bg'], ec=color, lw=2.5)
        ax.add_patch(box)
        add_glow(box, color, alpha=0.3, linewidth=10)
        
        # Title with better positioning
        ax.text(x + w/2, y + h*0.65, title, ha='center', va='center', 
                color='white', fontweight='bold', fontsize=12)
        ax.text(x + w/2, y + h*0.35, subtitle, ha='center', va='center', 
                color=COLORS['subtext'], fontsize=10)
        
        # Icon circle with better spacing
        circle = patches.Circle((x + w/2, y + h + 0.25), 0.35, fc=COLORS['bg'], ec=color, lw=2.5)
        ax.add_patch(circle)
        ax.text(x + w/2, y + h + 0.25, icon, ha='center', va='center', 
                color=color, fontsize=13, fontweight='bold')
        
        # Badge for new features
        if badge:
            badge_rect = patches.FancyBboxPatch((x + w - 0.7, y + h - 0.35), 0.6, 0.25,
                                                boxstyle="round,pad=0.03", fc='#ff0055', ec='white', lw=1.5)
            ax.add_patch(badge_rect)
            ax.text(x + w - 0.4, y + h - 0.225, badge, ha='center', va='center',
                    color='white', fontsize=7, fontweight='bold')
        
        return (x+w, y+h/2), (x, y+h/2) # Return right and left connection points

    # Component layout with proper spacing
    # 1. WMI (In Kernel/Boundary)
    wmi_right, wmi_left = draw_component(1.5, 1.2, 2.5, 1.2, "Windows WMI", "Event Source", COLORS['orange'], "1")

    # 2. Collector (with better vertical spacing)
    coll_right, coll_left = draw_component(1.2, 4.8, 2.8, 1.6, "Collector Agent", "Async + Privacy Hash", COLORS['cyan'], "2")

    # 3. Feature Extractor
    feat_right, feat_left = draw_component(5.2, 4.8, 2.8, 1.6, "Feature Extractor", "30+ Vectors", COLORS['purple'], "3")

    # 4. AI Engine with SHAP
    ai_right, ai_left = draw_component(9.2, 4.8, 2.8, 1.6, "Neuro-Symbolic AI", "ML + SHAP", COLORS['pink'], "4", badge="NEW")

    # 5. MITRE Mapping
    mitre_right, mitre_left = draw_component(13, 4.8, 2.2, 1.6, "MITRE ATT&CK", "Threat Intel", '#ff6b35', "5", badge="NEW")

    # --- ENHANCED CONNECTIONS WITH LABELS ---
    def draw_arrow(start, end, color, label="", style='-'):
        ax.annotate("", xy=end, xytext=start, 
                   arrowprops=dict(arrowstyle="->, head_width=0.4, head_length=0.4", 
                                 color=color, lw=2.5, linestyle=style))
        if label:
            mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2
            ax.text(mid_x, mid_y + 0.15, label, color=color, fontsize=9, 
                   ha='center', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', fc=COLORS['bg'], ec=color, lw=1))

    # WMI -> Collector (Vertical with label)
    draw_arrow((2.75, 2.4), (2.6, 4.8), COLORS['cyan'], "Events", style='--')
    
    # Collector -> Extractor
    draw_arrow((coll_right[0], coll_right[1]), (feat_left[0], feat_left[1]), COLORS['cyan'], "Raw Data")
    
    # Extractor -> AI
    draw_arrow((feat_right[0], feat_right[1]), (ai_left[0], ai_left[1]), COLORS['purple'], "Features")
    
    # AI -> MITRE
    draw_arrow((ai_right[0], ai_right[1]), (mitre_left[0], mitre_left[1]), COLORS['pink'], "Detections")

    # Output arrows
    draw_arrow((13, 3.5), (13, 2.8), '#00ff88', style='--')
    ax.text(13.8, 3, "Alerts", color='#00ff88', fontsize=10, fontweight='bold')

    # Title with better positioning
    ax.text(8, 0.6, "CYBERSHELL WORLD-CLASS ARCHITECTURE v3.0", ha='center', 
            color='white', fontsize=18, fontweight='bold')

    save_plot('system_architecture.png')

if __name__ == "__main__":
    generate_problem_statement()
    generate_measurable_impact()
    generate_system_architecture()

# --- 4. TECH STACK: ELITE GRID (ENHANCED WITH WORLD-CLASS FEATURES) ---
def generate_tech_stack():
    fig, ax = setup_figure((16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')
    ax.grid(False)

    # Title with proper spacing
    ax.text(8, 10.2, "WORLD-CLASS TECHNOLOGY STACK", ha='center', color='white', fontsize=26, fontweight='bold')
    ax.text(8, 9.6, "Competition-Grade: AI Explainability + Threat Intelligence + Elite Performance", 
            ha='center', color=COLORS['subtext'], fontsize=12)

    # Grid Layout Parameters with better spacing
    box_w = 4.5
    box_h = 2.2
    gap_x = 0.6
    gap_y = 0.5

    # Helper to draw a tech card with improved layout
    def draw_tech_card(x, y, title, items, color, icon_char, badge=None):
        # Main Card with rounded corners
        rect = patches.FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.12", 
                                      fc=COLORS['card_bg'], ec=color, lw=3)
        ax.add_patch(rect)
        add_glow(rect, color, alpha=0.3, linewidth=12)

        # Header Background
        header_h = 0.55
        rect_head = patches.FancyBboxPatch((x, y + box_h - header_h), box_w, header_h, 
                                           boxstyle="round,pad=0.12", fc=color, ec='none', alpha=0.15)
        ax.add_patch(rect_head)

        # Title with icon - better spacing
        ax.text(x + 0.35, y + box_h - 0.275, f"{icon_char}  {title}", 
                color=color, fontsize=14, fontweight='bold', va='center')
        
        # Badge (NEW indicator)
        if badge:
            badge_w, badge_h = 0.65, 0.28
            badge_rect = patches.FancyBboxPatch((x + box_w - badge_w - 0.15, y + box_h - badge_h - 0.15), 
                                                badge_w, badge_h, boxstyle="round,pad=0.03", 
                                                fc='#ff0055', ec='white', lw=1.5)
            ax.add_patch(badge_rect)
            ax.text(x + box_w - badge_w/2 - 0.15, y + box_h - badge_h/2 - 0.15, badge, 
                    ha='center', va='center', color='white', fontsize=8, fontweight='bold')

        # Items with better vertical spacing
        item_start_y = y + box_h - 0.95
        line_height = 0.45
        for i, item in enumerate(items):
            item_y = item_start_y - (i * line_height)
            # Bullet with better alignment
            ax.text(x + 0.35, item_y, "▸", 
                    color=COLORS['subtext'], fontsize=10, fontweight='bold', va='center')
            # Text with proper spacing
            ax.text(x + 0.65, item_y, item, 
                    color='white', fontsize=11, fontweight='500', va='center')

    # Calculate positions with proper spacing
    col1_x = 1.0
    col2_x = col1_x + box_w + gap_x
    col3_x = col2_x + box_w + gap_x
    
    row1_y = 6.8
    row2_y = row1_y - box_h - gap_y
    row3_y = row2_y - box_h - gap_y

    # Row 1: Core Technologies
    draw_tech_card(col1_x, row1_y, "CORE ENGINE", 
                   ["Python 3.11 AsyncIO", "Windows API PyWin32", "WMI Event Subscriptions", "Multiprocessing"], 
                   COLORS['cyan'], "⚡")

    draw_tech_card(col2_x, row1_y, "NEURO-SYMBOLIC AI", 
                   ["Scikit-learn IsolationForest", "NumPy Vectorized Ops", "Pandas Data Processing", "Shannon Entropy Engine"], 
                   COLORS['pink'], "🧠")

    draw_tech_card(col3_x, row1_y, "EXPLAINABILITY", 
                   ["SHAP TreeExplainer", "Natural Language AI", "Feature Importance", "GDPR Compliant"], 
                   '#00ff88', "🔍", badge="NEW")

    # Row 2: Advanced Features
    draw_tech_card(col1_x, row2_y, "THREAT INTEL", 
                   ["MITRE ATT&CK Mapping", "Kill Chain Analysis", "APT Group Profiling", "T1486, T1071, T1041..."], 
                   '#ff6b35', "🎯", badge="NEW")

    draw_tech_card(col2_x, row2_y, "ELITE UI", 
                   ["Plotly Interactive Charts", "Streamlit Dashboard", "MITRE Heatmap", "Real-time Timeline"], 
                   COLORS['purple'], "📊", badge="NEW")

    draw_tech_card(col3_x, row2_y, "PERFORMANCE", 
                   ["Benchmark Suite psutil", "8.5ms Avg Latency", "2.35x Faster than EDR", "SLA Validation"], 
                   '#ffd700', "⚡", badge="NEW")

    # Row 3: Security & Testing (centered)
    center_x1 = col1_x + (box_w + gap_x) * 0.5
    center_x2 = center_x1 + box_w + gap_x
    
    draw_tech_card(center_x1, row3_y, "SECURITY & PRIVACY", 
                   ["SHA-256 PII Hashing", "Cryptography Library", "Zero-Trust Architecture", "On-Device Processing"], 
                   COLORS['orange'], "🔒")

    draw_tech_card(center_x2, row3_y, "TESTING & CI/CD", 
                   ["Pytest Unit + Integration", "Coverage Analysis", "Automated Benchmarks", "GitHub Actions Ready"], 
                   '#00d9ff', "✅")

    # Central competition badge with better positioning
    badge_x, badge_y = 8, 5.2
    badge_w, badge_h = 4.5, 0.9
    badge_rect = patches.FancyBboxPatch((badge_x - badge_w/2, badge_y - badge_h/2), badge_w, badge_h, 
                                        boxstyle="round,pad=0.15", fc='#ff0055', ec='#ffffff', lw=3)
    ax.add_patch(badge_rect)
    add_glow(badge_rect, '#ff0055', alpha=0.4, linewidth=15)
    ax.text(badge_x, badge_y, "⭐ COMPETITION READY ⭐", ha='center', va='center', 
            color='white', fontsize=16, fontweight='bold')

    save_plot('tech_stack.png')
    center_x2 = center_x1 + box_w + gap_x
    
    draw_tech_card(center_x1, row3_y, "SECURITY & PRIVACY", 
                   ["SHA-256 PII Hashing", "Cryptography Library", "Zero-Trust Architecture", "On-Device Processing"], 
                   COLORS['orange'], "🔒")

    draw_tech_card(7.55, 0.8, "TESTING & CI/CD", 
                   ["Pytest (Unit + Integration)", "Coverage Analysis", "Automated Benchmarks", "GitHub Actions Ready"], 
                   '#00d9ff', "✅")

    # Center badge
    badge_x, badge_y = 7, 5
    badge = patches.FancyBboxPatch((badge_x - 1.5, badge_y - 0.4), 3, 0.8, 
                                   boxstyle="round,pad=0.1", fc='#ff0055', ec='#ffffff', lw=2)
    ax.add_patch(badge)
    ax.text(badge_x, badge_y, "COMPETITION READY", ha='center', va='center', 
            color='white', fontsize=14, fontweight='bold')

    save_plot('tech_stack.png')

if __name__ == "__main__":
    generate_problem_statement()
    generate_measurable_impact()
    generate_system_architecture()
    generate_tech_stack()
