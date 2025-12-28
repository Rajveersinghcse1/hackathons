import svgwrite
import os

def ensure_dir():
    if not os.path.exists('images'):
        os.makedirs('images')

# --- DESIGN 1: CYBERPUNK (The Complex One) ---
def create_cyberpunk_diagram():
    width = 1100
    height = 650
    dwg = svgwrite.Drawing('images/arch_1_cyberpunk.svg', size=(width, height), profile='full')
    defs = dwg.defs
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0E1117'))
    
    grad_green = defs.add(dwg.linearGradient(id="grad_green", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_green.add_stop_color(0, "#00b894", opacity=0.8); grad_green.add_stop_color(1, "#00ff41", opacity=0.8)
    grad_red = defs.add(dwg.linearGradient(id="grad_red", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_red.add_stop_color(0, "#d63031", opacity=0.8); grad_red.add_stop_color(1, "#ff003c", opacity=0.8)
    grad_blue = defs.add(dwg.linearGradient(id="grad_blue", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_blue.add_stop_color(0, "#0984e3", opacity=0.8); grad_blue.add_stop_color(1, "#00f3ff", opacity=0.8)
    grad_purple = defs.add(dwg.linearGradient(id="grad_purple", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_purple.add_stop_color(0, "#6c5ce7", opacity=0.8); grad_purple.add_stop_color(1, "#a29bfe", opacity=0.8)

    style_text = "font-family: 'Segoe UI', sans-serif; font-weight: bold; fill: white;"
    style_subtext = "font-family: 'Segoe UI', sans-serif; font-size: 12px; fill: #b2bec3;"
    style_title = "font-family: 'Segoe UI', sans-serif; font-weight: bold; font-size: 24px; fill: white;"
    
    dwg.add(dwg.text("CyberShell: Cyberpunk Architecture", insert=(50, 30), style=style_title))

    def draw_box(x, y, w, h, text, subtext, gradient_id, icon=""):
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=10, ry=10, fill=f"url(#{gradient_id})", stroke="white", stroke_width=1))
        dwg.add(dwg.text(f"{icon} {text}", insert=(x + 15, y + 30), style=style_text, font_size="16px"))
        dwg.add(dwg.text(subtext, insert=(x + 15, y + 50), style=style_subtext))
        return (x + w, y + h/2)

    marker = defs.add(dwg.marker(id="arrow", insert=(10, 5), size=(10, 10), orient="auto"))
    marker.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill="#00f3ff"))

    dwg.add(dwg.rect(insert=(50, 80), size=(200, 100), rx=5, ry=5, fill="none", stroke="#ff003c", stroke_dasharray="5,5"))
    dwg.add(dwg.text("KERNEL SPACE (Ring 0)", insert=(60, 70), style="fill: #ff003c; font-family: sans-serif; font-size: 12px;"))
    wmi_pos = draw_box(70, 100, 160, 60, "Windows WMI", "Async Event Source", "grad_red", "📡")
    
    dwg.add(dwg.rect(insert=(300, 80), size=(750, 500), rx=5, ry=5, fill="none", stroke="#00ff41", stroke_width=2))
    dwg.add(dwg.text("USERLAND (Ring 3) - Safe Execution Zone", insert=(320, 70), style="fill: #00ff41; font-family: sans-serif; font-weight: bold; font-size: 14px;"))

    coll_pos = draw_box(350, 150, 180, 60, "Collector Agent", "Event Subscription", "grad_green", "🕵️")
    hash_pos = draw_box(350, 250, 180, 60, "Privacy Vault", "SHA-256 Hashing", "grad_green", "🔒")
    ext_pos = draw_box(350, 350, 180, 60, "Feature Extractor", "Entropy & Vectors", "grad_blue", "⚙️")
    ml_pos = draw_box(600, 300, 180, 60, "IsolationForest", "Stochastic ML", "grad_purple", "🧠")
    rule_pos = draw_box(600, 400, 180, 60, "Rule Engine", "Deterministic Logic", "grad_blue", "📜")
    score_pos = draw_box(850, 350, 160, 60, "Hybrid Scorer", "Weighted Aggregation", "grad_red", "⚖️")
    ui_pos = draw_box(850, 150, 160, 60, "Streamlit/Web UI", "Command Center", "grad_green", "🖥️")

    def draw_arrow(start, end):
        dwg.add(dwg.path(d=f"M {start[0]} {start[1]} L {end[0]} {end[1]}", stroke="#00f3ff", stroke_width=2, fill="none", marker_end="url(#arrow)"))

    dwg.add(dwg.path(d=f"M {wmi_pos[0]} {wmi_pos[1]} L 320 {wmi_pos[1]} L 320 180 L 350 180", stroke="#00f3ff", stroke_width=2, fill="none", marker_end="url(#arrow)"))
    draw_arrow((440, 210), (440, 250))
    draw_arrow((440, 310), (440, 350))
    draw_arrow((530, 380), (600, 330))
    draw_arrow((530, 380), (600, 430))
    draw_arrow((780, 330), (850, 380))
    draw_arrow((780, 430), (850, 380))
    draw_arrow((930, 350), (930, 210))
    dwg.save()

# --- GENERIC GENERATOR FOR OTHER STYLES ---
def draw_common_layout(filename, title, style_config):
    width = 1100
    height = 650
    dwg = svgwrite.Drawing(filename, size=(width, height), profile='full')
    
    bg_color = style_config.get('bg', 'white')
    stroke_color = style_config.get('stroke', 'black')
    text_color = style_config.get('text', 'black')
    box_fill = style_config.get('box_fill', 'none')
    font = style_config.get('font', 'Arial')
    
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=bg_color))
    dwg.add(dwg.text(title, insert=(50, 40), fill=text_color, font_family=font, font_size="24px", font_weight="bold"))

    defs = dwg.defs
    marker = defs.add(dwg.marker(id="arrow", insert=(10, 5), size=(10, 10), orient="auto"))
    marker.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill=stroke_color))

    def draw_node(x, y, w, h, label, sublabel, icon):
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=8, ry=8, fill=box_fill, stroke=stroke_color, stroke_width=2))
        dwg.add(dwg.text(f"{icon} {label}", insert=(x+10, y+25), fill=text_color, font_family=font, font_size="14px", font_weight="bold"))
        dwg.add(dwg.text(sublabel, insert=(x+10, y+45), fill=text_color, font_family=font, font_size="10px"))
        return (x+w, y+h/2)

    def draw_edge(p1, p2):
        dwg.add(dwg.path(d=f"M {p1[0]} {p1[1]} L {p2[0]} {p2[1]}", stroke=stroke_color, stroke_width=2, fill="none", marker_end="url(#arrow)"))

    dwg.add(dwg.text("KERNEL (Ring 0)", insert=(50, 80), fill=text_color, font_family=font, font_size="12px"))
    wmi = draw_node(50, 100, 180, 60, "Windows WMI", "Async Events", "📡")

    dwg.add(dwg.rect(insert=(280, 80), size=(750, 500), rx=10, ry=10, fill="none", stroke=stroke_color, stroke_dasharray="5,5"))
    dwg.add(dwg.text("USERLAND (Ring 3)", insert=(300, 70), fill=text_color, font_family=font, font_size="12px"))

    coll = draw_node(320, 120, 160, 50, "Collector", "Event Sub", "🕵️")
    hash_node = draw_node(320, 200, 160, 50, "Privacy Vault", "SHA-256", "🔒")
    ext = draw_node(320, 280, 160, 50, "Extractor", "Features", "⚙️")
    ml = draw_node(550, 240, 160, 50, "IsolationForest", "Stochastic ML", "🧠")
    rules = draw_node(550, 320, 160, 50, "Rule Engine", "Deterministic", "📜")
    scorer = draw_node(780, 280, 160, 50, "Hybrid Scorer", "Aggregation", "⚖️")
    ui = draw_node(780, 120, 160, 50, "Streamlit/Web UI", "Dashboard", "🖥️")

    dwg.add(dwg.path(d=f"M {wmi[0]} {wmi[1]} L 260 {wmi[1]} L 260 145 L 320 145", stroke=stroke_color, stroke_width=2, fill="none", marker_end="url(#arrow)"))
    draw_edge((400, 170), (400, 200))
    draw_edge((400, 250), (400, 280))
    draw_edge((480, 305), (550, 265))
    draw_edge((480, 305), (550, 345))
    draw_edge((710, 265), (780, 305))
    draw_edge((710, 345), (780, 305))
    draw_edge((860, 280), (860, 170))
    dwg.save()

# --- DESIGN 6: ULTRA (Advanced Shapes & Flow) ---
def create_ultra_diagram():
    width = 1600  # Increased from 1400 for better spacing
    height = 900  # Increased from 800 for better spacing
    dwg = svgwrite.Drawing('images/arch_6_ultra.svg', size=(width, height), profile='full')
    defs = dwg.defs
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0f172a')) # Slate-900
    
    # Grid Pattern (smaller grid for professional look)
    pattern = defs.add(dwg.pattern(id="grid", size=(40, 40), patternUnits="userSpaceOnUse"))
    pattern.add(dwg.path(d="M 40 0 L 0 0 0 40", fill="none", stroke="#1e293b", stroke_width=1))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill="url(#grid)"))

    # Gradients
    grad_cyan = defs.add(dwg.linearGradient(id="grad_cyan", x1="0%", y1="0%", x2="100%", y2="100%"))
    grad_cyan.add_stop_color(0, "#22d3ee"); grad_cyan.add_stop_color(1, "#0ea5e9")
    
    grad_pink = defs.add(dwg.linearGradient(id="grad_pink", x1="0%", y1="0%", x2="100%", y2="100%"))
    grad_pink.add_stop_color(0, "#f472b6"); grad_pink.add_stop_color(1, "#db2777")
    
    grad_violet = defs.add(dwg.linearGradient(id="grad_violet", x1="0%", y1="0%", x2="100%", y2="100%"))
    grad_violet.add_stop_color(0, "#a78bfa"); grad_violet.add_stop_color(1, "#7c3aed")

    grad_red = defs.add(dwg.linearGradient(id="grad_red", x1="0%", y1="0%", x2="100%", y2="100%"))
    grad_red.add_stop_color(0, "#ef4444"); grad_red.add_stop_color(1, "#b91c1c")

    grad_glass = defs.add(dwg.linearGradient(id="grad_glass", x1="0%", y1="0%", x2="0%", y2="100%"))
    grad_glass.add_stop_color(0, "#ffffff", opacity=0.1); grad_glass.add_stop_color(1, "#ffffff", opacity=0.05)
    
    grad_dark_glass = defs.add(dwg.linearGradient(id="grad_dark_glass", x1="0%", y1="0%", x2="0%", y2="100%"))
    grad_dark_glass.add_stop_color(0, "#000000", opacity=0.3); grad_dark_glass.add_stop_color(1, "#000000", opacity=0.5)

    # Filters (Glow effect) - simplified
    filter_glow = defs.add(dwg.filter(id="glow"))
    filter_glow.feGaussianBlur(in_="SourceGraphic", stdDeviation=3)

    # Styles
    style_title = "font-family: 'Segoe UI', sans-serif; font-weight: 800; font-size: 42px; fill: white;"
    style_label = "font-family: 'Segoe UI', sans-serif; font-weight: 600; font-size: 16px; fill: white;"
    style_sub = "font-family: 'Segoe UI', sans-serif; font-size: 12px; fill: #94a3b8;"
    style_code = "font-family: 'Consolas', monospace; font-size: 11px; fill: #22d3ee;"

    # Title with better spacing
    dwg.add(dwg.text("CyberShell: Autonomous Edge-Native Defense", insert=(70, 70), style=style_title))
    dwg.add(dwg.text("Architecture v3.0 | World-Class Competition Edition", insert=(70, 105), style="font-family: 'Segoe UI'; font-size: 18px; fill: #64748b;"))

    # --- Helper Shapes with Enhanced Spacing ---
    def draw_cylinder(x, y, w, h, fill_id, label, sublabel):
        # Top ellipse with shadow
        dwg.add(dwg.ellipse(center=(x + w/2, y + 12), r=(w/2, 12), fill=f"url(#{fill_id})", opacity=0.8, filter="url(#glow)"))
        # Body
        dwg.add(dwg.rect(insert=(x, y + 12), size=(w, h - 24), fill=f"url(#{fill_id})"))
        # Bottom ellipse
        dwg.add(dwg.ellipse(center=(x + w/2, y + h - 12), r=(w/2, 12), fill=f"url(#{fill_id})"))
        # Outline with better visibility
        path = dwg.path(d=f"M {x} {y+12} L {x} {y+h-12} A {w/2} 12 0 0 0 {x+w} {y+h-12} L {x+w} {y+12}", 
                        stroke="white", stroke_width=2, fill="none", opacity=0.6)
        dwg.add(path)
        dwg.add(dwg.ellipse(center=(x + w/2, y + 12), r=(w/2, 12), stroke="white", stroke_width=2, fill="none", opacity=0.6))
        
        # Labels with better positioning
        dwg.add(dwg.text(label, insert=(x + w/2, y + h + 25), style=style_label, text_anchor="middle"))
        dwg.add(dwg.text(sublabel, insert=(x + w/2, y + h + 45), style=style_sub, text_anchor="middle"))

    def draw_card(x, y, w, h, title, icon, color_id, details=[], badge=None):
        # Glass background with glow
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=15, ry=15, fill="url(#grad_glass)", 
                        stroke=f"url(#{color_id})", stroke_width=3, filter="url(#glow)"))
        # Icon circle with better sizing
        dwg.add(dwg.circle(center=(x + 35, y + 35), r=22, fill=f"url(#{color_id})", opacity=0.25))
        dwg.add(dwg.text(icon, insert=(x + 20, y + 42), font_size="24px"))
        # Title with better spacing
        dwg.add(dwg.text(title, insert=(x + 70, y + 30), style=style_label))
        # Status dot
        dwg.add(dwg.circle(center=(x + w - 20, y + 20), r=5, fill="#4ade80"))
        
        # Badge for new features
        if badge:
            dwg.add(dwg.rect(insert=(x + w - 80, y - 10), size=(70, 22), rx=11, ry=11, 
                           fill="#ff0055", stroke="white", stroke_width=1.5))
            dwg.add(dwg.text(badge, insert=(x + w - 45, y + 5), 
                           style="font-family: 'Segoe UI'; font-weight: bold; font-size: 11px; fill: white;", 
                           text_anchor="middle"))
        
        # Details with better spacing
        dy = 70
        for detail in details:
            dwg.add(dwg.rect(insert=(x+18, y+dy), size=(w-36, 28), rx=5, ry=5, fill="url(#grad_dark_glass)"))
            dwg.add(dwg.text(detail, insert=(x+30, y+dy+18), style=style_code))
            dy += 35

    def draw_cloud(x, y, w, h, color_id):
        # Enhanced cloud shape with better circles
        dwg.add(dwg.circle(center=(x+35, y+35), r=30, fill=f"url(#{color_id})", opacity=0.35, filter="url(#glow)"))
        dwg.add(dwg.circle(center=(x+70, y+22), r=38, fill=f"url(#{color_id})", opacity=0.35, filter="url(#glow)"))
        dwg.add(dwg.circle(center=(x+105, y+35), r=30, fill=f"url(#{color_id})", opacity=0.35, filter="url(#glow)"))
        dwg.add(dwg.text("Windows Kernel", insert=(x+20, y+80), 
                        style="font-family: 'Segoe UI'; font-weight: bold; font-size: 16px; fill: #ef4444;"))
        dwg.add(dwg.text("(Ring 0 - Event Source)", insert=(x+15, y+100), style=style_sub))

    # --- Enhanced Layout with Professional Spacing ---
    
    # 1. Kernel Cloud (Left) - Better positioning
    draw_cloud(50, 350, 200, 140, "grad_red")
    
    # 2. Userland Container (Main Area) - Expanded with better margins
    dwg.add(dwg.rect(insert=(330, 170), size=(1200, 650), rx=25, ry=25, fill="#1e293b", 
                    stroke="#334155", stroke_width=3, stroke_dasharray="8,8"))
    dwg.add(dwg.text("USERLAND (Ring 3) - Secure Processing Enclave", insert=(370, 220), 
                    style="font-family: 'Segoe UI'; font-weight: bold; fill: #64748b; font-size: 20px;"))

    # Components with Professional Spacing
    # WMI (Cylinder) - Better aligned with cloud
    draw_cylinder(100, 440, 100, 120, "grad_red", "WMI Events", "Win32_Process")

    # Collector (Card) - Better spacing from left edge
    draw_card(380, 470, 260, 160, "Async Collector", "⚡", "grad_cyan", 
             ["Event Subscription", "Raw Data Parsing", "Queue Management"])
    
    # Privacy (Cylinder) - Better vertical positioning to avoid line crossing
    draw_cylinder(710, 250, 110, 130, "grad_violet", "Privacy Vault", "SHA-256 + Salt")

    # ML Engine (Card) - Aligned with new features badge
    draw_card(880, 460, 300, 180, "Neuro-Symbolic AI", "🧠", "grad_pink", 
             ["IsolationForest (ML)", "SHAP Explainability", "MITRE ATT&CK Mapping"], badge="NEW")

    # UI (Browser Window) - Better positioning
    ui_x, ui_y = 1280, 460
    dwg.add(dwg.rect(insert=(ui_x, ui_y), size=(220, 260), rx=8, ry=8, fill="#0f172a", 
                    stroke="#94a3b8", stroke_width=2))
    dwg.add(dwg.rect(insert=(ui_x, ui_y), size=(220, 30), rx=8, ry=8, fill="#334155")) # Title bar
    dwg.add(dwg.circle(center=(ui_x+15, ui_y+15), r=4, fill="#ef4444"))
    dwg.add(dwg.circle(center=(ui_x+28, ui_y+15), r=4, fill="#eab308"))
    dwg.add(dwg.circle(center=(ui_x+41, ui_y+15), r=4, fill="#22c55e"))
    dwg.add(dwg.text("Streamlit/Web UI", insert=(ui_x+60, ui_y+20), 
                    style="font-family: 'Segoe UI'; font-size: 12px; fill: white;"))
    
    # UI Content Mockup with better spacing
    dwg.add(dwg.rect(insert=(ui_x+15, ui_y+50), size=(190, 75), rx=4, ry=4, fill="#1e293b")) # Graph
    dwg.add(dwg.path(d=f"M {ui_x+15} {ui_y+115} L {ui_x+60} {ui_y+70} L {ui_x+110} {ui_y+95} L {ui_x+160} {ui_y+60}", 
                    stroke="#22d3ee", stroke_width=2, fill="none"))
    dwg.add(dwg.rect(insert=(ui_x+15, ui_y+140), size=(190, 25), rx=4, ry=4, fill="#334155")) # Alert
    dwg.add(dwg.rect(insert=(ui_x+15, ui_y+175), size=(190, 25), rx=4, ry=4, fill="#334155")) # Alert
    dwg.add(dwg.rect(insert=(ui_x+15, ui_y+210), size=(190, 25), rx=4, ry=4, fill="#334155")) # Alert

    # Connectors with Enhanced Bezier Curves and Better Spacing
    path_style = "stroke: #94a3b8; stroke-width: 2.5; fill: none; stroke-dasharray: 6,6;"
    path_active = "stroke: #f472b6; stroke-width: 3; fill: none;"
    
    # WMI -> Collector (improved curve)
    dwg.add(dwg.path(d="M 200 540 C 290 540, 320 540, 380 540", style=path_style))
    
    # Collector -> Privacy (smoother upward curve)
    dwg.add(dwg.path(d="M 640 540 C 670 540, 680 315, 710 315", style=path_style))
    
    # Privacy -> ML (elegant downward curve)
    dwg.add(dwg.path(d="M 820 315 C 850 315, 860 540, 880 540", style=path_style))
    
    # ML -> UI (horizontal with slight curve)
    dwg.add(dwg.path(d="M 1180 550 C 1230 550, 1230 570, 1280 570", style=path_style))
    
    # Active Defense (Loopback) - Better routing
    dwg.add(dwg.path(d="M 1030 640 C 1030 750, 510 750, 510 630", style=path_active))
    dwg.add(dwg.text("Active Defense (Kill Signal)", insert=(700, 735), 
                    style="font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; fill: #f472b6;"))

    # Competition Badge
    badge_x, badge_y = 800, 50
    dwg.add(dwg.rect(insert=(badge_x - 160, badge_y - 20), size=(320, 50), rx=25, ry=25,
                    fill="#b026ff", stroke="white", stroke_width=3, filter="url(#glow)"))
    dwg.add(dwg.text("⭐ INTERNATIONAL COMPETITION READY ⭐", insert=(badge_x, badge_y + 10),
                    style="font-family: 'Segoe UI'; font-weight: 900; font-size: 18px; fill: white;",
                    text_anchor="middle"))

    dwg.save()

def generate_all():
    ensure_dir()
    dwg.add(dwg.circle(center=(ui_x+30, ui_y+12), r=3, fill="#22c55e"))
    dwg.add(dwg.text("Streamlit/Web UI", insert=(ui_x+45, ui_y+17), style="font-family: 'Segoe UI'; font-size: 10px; fill: white;"))
    
    # UI Content Mockup
    dwg.add(dwg.rect(insert=(ui_x+10, ui_y+40), size=(160, 60), rx=2, ry=2, fill="#1e293b")) # Graph
    dwg.add(dwg.path(d=f"M {ui_x+10} {ui_y+90} L {ui_x+50} {ui_y+60} L {ui_x+90} {ui_y+80} L {ui_x+130} {ui_y+50}", stroke="#22d3ee", stroke_width=1, fill="none"))
    dwg.add(dwg.rect(insert=(ui_x+10, ui_y+110), size=(160, 20), rx=2, ry=2, fill="#334155")) # Alert
    dwg.add(dwg.rect(insert=(ui_x+10, ui_y+140), size=(160, 20), rx=2, ry=2, fill="#334155")) # Alert

    # Connectors (Curved Bezier)
    path_style = "stroke: #94a3b8; stroke-width: 2; fill: none; stroke-dasharray: 5,5;"
    path_active = "stroke: #f472b6; stroke-width: 2; fill: none;"
    
    # WMI -> Collector
    # WMI Center: x=130, y=500. Collector Left: x=330, y=450 (center).
    dwg.add(dwg.path(d="M 170 500 C 250 500, 250 450, 330 450", style=path_style))
    
    # Collector -> Privacy
    # Collector Right: x=570, y=450. Privacy Left/Bottom: x=620, y=255 (mid).
    # Curve up sharply but avoid crossing text.
    dwg.add(dwg.path(d="M 570 450 C 600 450, 580 255, 620 255", style=path_style))
    
    # Privacy -> ML
    # Privacy Right: x=710, y=255. ML Left: x=780, y=450.
    dwg.add(dwg.path(d="M 710 255 C 750 255, 740 450, 780 450", style=path_style))
    
    # ML -> UI
    # ML Right: x=1040, y=450. UI Left: x=1120, y=480 (mid).
    dwg.add(dwg.path(d="M 1040 450 C 1080 450, 1080 480, 1120 480", style=path_style))
    
    # Active Defense (Loopback)
    # From ML Bottom (x=910, y=530) to Collector Bottom (x=450, y=520)
    # Route it low to avoid crossing.
    dwg.add(dwg.path(d="M 910 530 C 910 650, 450 650, 450 520", style=path_active))
    dwg.add(dwg.text("Active Defense (Kill Signal)", insert=(600, 640), style="font-family: 'Segoe UI'; font-size: 12px; fill: #f472b6;"))

    dwg.save()

def generate_all():
    ensure_dir()
    print("Generating 1: Cyberpunk...")
    create_cyberpunk_diagram()
    
    print("Generating 2: Enterprise...")
    draw_common_layout('images/arch_2_enterprise.svg', "CyberShell: Enterprise Architecture", {
        'bg': '#ffffff', 'stroke': '#2c3e50', 'text': '#2c3e50', 'box_fill': '#ecf0f1', 'font': 'Arial'
    })
    
    print("Generating 3: Blueprint...")
    draw_common_layout('images/arch_3_blueprint.svg', "CyberShell: Technical Blueprint", {
        'bg': '#2980b9', 'stroke': '#ffffff', 'text': '#ffffff', 'box_fill': 'none', 'font': 'Courier New'
    })
    
    print("Generating 4: Dark Minimal...")
    draw_common_layout('images/arch_4_minimal.svg', "CyberShell: Minimalist Dark", {
        'bg': '#2d3436', 'stroke': '#dfe6e9', 'text': '#dfe6e9', 'box_fill': '#636e72', 'font': 'Verdana'
    })
    
    print("Generating 5: Retro Terminal...")
    draw_common_layout('images/arch_5_retro.svg', "CyberShell: Terminal View", {
        'bg': '#000000', 'stroke': '#00ff00', 'text': '#00ff00', 'box_fill': '#000000', 'font': 'Consolas'
    })

    print("Generating 6: Ultra Modern...")
    create_ultra_diagram()

    print("Done!")

if __name__ == "__main__":
    generate_all()
