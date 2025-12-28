import svgwrite
from svgwrite import cm, mm

def create_cyberpunk_diagram():
    # Canvas setup - WIDENED for better fit
    width = 1100
    height = 650
    dwg = svgwrite.Drawing('images/system_architecture.svg', size=(width, height), profile='full')
    
    # Definitions for gradients and filters
    defs = dwg.defs
    
    # Dark Background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0E1117'))
    
    # Neon Gradients
    # Green (Safe/Userland)
    grad_green = defs.add(dwg.linearGradient(id="grad_green", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_green.add_stop_color(0, "#00b894", opacity=0.8)
    grad_green.add_stop_color(1, "#00ff41", opacity=0.8)
    
    # Red (Kernel/Action)
    grad_red = defs.add(dwg.linearGradient(id="grad_red", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_red.add_stop_color(0, "#d63031", opacity=0.8)
    grad_red.add_stop_color(1, "#ff003c", opacity=0.8)
    
    # Blue (Logic)
    grad_blue = defs.add(dwg.linearGradient(id="grad_blue", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_blue.add_stop_color(0, "#0984e3", opacity=0.8)
    grad_blue.add_stop_color(1, "#00f3ff", opacity=0.8)
    
    # Purple (AI)
    grad_purple = defs.add(dwg.linearGradient(id="grad_purple", x1="0%", y1="0%", x2="100%", y2="0%"))
    grad_purple.add_stop_color(0, "#6c5ce7", opacity=0.8)
    grad_purple.add_stop_color(1, "#a29bfe", opacity=0.8)

    # Styles
    style_text = "font-family: 'Segoe UI', sans-serif; font-weight: bold; fill: white;"
    style_subtext = "font-family: 'Segoe UI', sans-serif; font-size: 12px; fill: #b2bec3;"
    style_title = "font-family: 'Segoe UI', sans-serif; font-weight: bold; font-size: 24px; fill: white;"
    
    # Title
    dwg.add(dwg.text("CyberShell: Autonomous Edge-Native Defense Architecture", insert=(50, 30), style=style_title))

    # Helper to draw box
    def draw_box(x, y, w, h, text, subtext, gradient_id, icon=""):
        # Glow effect (simple stroke)
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=10, ry=10, 
                         fill=f"url(#{gradient_id})", stroke="white", stroke_width=1))
        
        # Text
        dwg.add(dwg.text(f"{icon} {text}", insert=(x + 15, y + 30), style=style_text, font_size="16px"))
        dwg.add(dwg.text(subtext, insert=(x + 15, y + 50), style=style_subtext))
        
        return (x + w, y + h/2) # Return connection point (right side)

    # Helper to draw arrow
    def draw_arrow(start, end, label=""):
        path = dwg.path(d=f"M {start[0]} {start[1]} L {end[0]} {end[1]}", 
                        stroke="#00f3ff", stroke_width=2, fill="none", marker_end="url(#arrow)")
        dwg.add(path)
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            dwg.add(dwg.text(label, insert=(mid_x - 20, mid_y - 10), style="font-family: sans-serif; font-size: 10px; fill: #00f3ff;"))

    # Marker for arrow
    marker = defs.add(dwg.marker(id="arrow", insert=(10, 5), size=(10, 10), orient="auto"))
    marker.add(dwg.path(d="M 0 0 L 10 5 L 0 10 z", fill="#00f3ff"))

    # --- DRAWING THE FLOW ---
    
    # 1. Kernel Space
    dwg.add(dwg.rect(insert=(50, 80), size=(200, 100), rx=5, ry=5, fill="none", stroke="#ff003c", stroke_dasharray="5,5"))
    dwg.add(dwg.text("KERNEL SPACE (Ring 0)", insert=(60, 70), style="fill: #ff003c; font-family: sans-serif; font-size: 12px;"))
    
    wmi_pos = draw_box(70, 100, 160, 60, "Windows WMI", "Async Event Source", "grad_red", "📡")
    
    # 2. User Space Container - WIDENED
    # Starts at 300, needs to cover up to ~1000. Width = 750.
    dwg.add(dwg.rect(insert=(300, 80), size=(750, 500), rx=5, ry=5, fill="none", stroke="#00ff41", stroke_width=2))
    dwg.add(dwg.text("USERLAND (Ring 3) - Safe Execution Zone", insert=(320, 70), style="fill: #00ff41; font-family: sans-serif; font-weight: bold; font-size: 14px;"))

    # Pipeline
    # Collector
    coll_pos = draw_box(350, 150, 180, 60, "Collector Agent", "Event Subscription", "grad_green", "🕵️")
    
    # Hasher
    hash_pos = draw_box(350, 250, 180, 60, "Privacy Vault", "SHA-256 Hashing", "grad_green", "🔒")
    
    # Extractor
    ext_pos = draw_box(350, 350, 180, 60, "Feature Extractor", "Entropy & Vectors", "grad_blue", "⚙️")
    
    # AI Core
    ml_pos = draw_box(600, 300, 180, 60, "IsolationForest", "Stochastic ML", "grad_purple", "🧠")
    rule_pos = draw_box(600, 400, 180, 60, "Rule Engine", "Deterministic Logic", "grad_blue", "📜")
    
    # Scorer
    score_pos = draw_box(850, 350, 160, 60, "Hybrid Scorer", "Weighted Aggregation", "grad_red", "⚖️")
    
    # Outputs - RENAMED
    ui_pos = draw_box(850, 150, 160, 60, "Streamlit/Web UI", "Command Center", "grad_green", "🖥️")
    
    # --- CONNECTIONS ---
    
    # WMI -> Collector (Cross Boundary)
    # Visual tweak: Draw line from WMI out, down, then into Collector
    dwg.add(dwg.path(d=f"M {wmi_pos[0]} {wmi_pos[1]} L 320 {wmi_pos[1]} L 320 180 L 350 180", 
                     stroke="#00f3ff", stroke_width=2, fill="none", marker_end="url(#arrow)"))
    
    # Collector -> Hasher
    draw_arrow((440, 210), (440, 250), "Raw Data")
    
    # Hasher -> Extractor
    draw_arrow((440, 310), (440, 350), "Anonymized")
    
    # Extractor -> ML & Rules
    draw_arrow((530, 380), (600, 330), "Vectors")
    draw_arrow((530, 380), (600, 430), "Metadata")
    
    # ML/Rules -> Scorer
    draw_arrow((780, 330), (850, 380), "Score")
    draw_arrow((780, 430), (850, 380), "Flag")
    
    # Scorer -> UI
    draw_arrow((930, 350), (930, 210), "Alerts")

    dwg.save()
    print("SVG Generated at images/system_architecture.svg")
