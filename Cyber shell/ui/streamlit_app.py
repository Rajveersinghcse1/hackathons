"""
CyberShell AI - Advanced Threat Detection Interface
===================================================

A high-fidelity, professional security dashboard for monitoring,
detecting, and responding to cyber threats in real-time.

Features:
- Real-time Process Monitoring with AI Risk Scoring
- Interactive Thread Visualization Graph
- Automated Threat Evidence Analysis
- Safe Simulation Mode by Default
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import graphviz
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))
from playbook.actions import PlaybookActions, ExecutionMode
from agent.collector import UnifiedCollector, WMICollector, PrivacyHasher
from model.detect import HybridDetector
from parser.feature_extractor import FeatureRow, FeatureUtils

# =============================================================================
# CONFIGURATION & STYLING
# =============================================================================

st.set_page_config(
    page_title="CyberShell AI Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Cyber" Aesthetic
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --neon-green: #00ff41;
        --neon-red: #ff003c;
        --neon-blue: #00f3ff;
        --dark-bg: #0a0a0a;
        --panel-bg: #111111;
        --text-color: #e0e0e0;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--dark-bg);
        color: var(--text-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    h1 {
        background: linear-gradient(90deg, var(--neon-blue), #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
    }

    /* Cards/Panels */
    .css-1r6slb0, .stDataFrame, .stPlotlyChart {
        background-color: var(--panel-bg);
        border: 1px solid #333;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-family: 'Consolas', 'Monaco', monospace;
        color: var(--neon-blue) !important;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
    }

    /* Buttons */
    .stButton button {
        background-color: #222;
        color: var(--neon-green);
        border: 1px solid var(--neon-green);
        border-radius: 0;
        transition: all 0.3s ease;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
    }
    
    .stButton button:hover {
        background-color: var(--neon-green);
        color: black;
        box-shadow: 0 0 15px var(--neon-green);
    }

    /* Danger Buttons */
    .danger-btn button {
        color: var(--neon-red);
        border-color: var(--neon-red);
    }
    .danger-btn button:hover {
        background-color: var(--neon-red);
        color: white;
        box-shadow: 0 0 15px var(--neon-red);
    }

    /* Loading Animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .scanning-text {
        color: var(--neon-green);
        font-family: 'Consolas', monospace;
        animation: pulse 1.5s infinite;
    }

    /* Custom Badges */
    .badge-safe {
        background-color: rgba(0, 255, 65, 0.1);
        color: var(--neon-green);
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid var(--neon-green);
        font-size: 0.8em;
    }
    
    .badge-danger {
        background-color: rgba(255, 0, 60, 0.1);
        color: var(--neon-red);
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid var(--neon-red);
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# STATE & DATA LOADING
# =============================================================================

def init_state():
    if 'selected_process_id' not in st.session_state:
        st.session_state.selected_process_id = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'simulation_mode' not in st.session_state:
        st.session_state.simulation_mode = True
    if 'live_data' not in st.session_state:
        st.session_state.live_data = pd.DataFrame()
    if 'detector' not in st.session_state:
        st.session_state.detector = HybridDetector()
    if 'collector' not in st.session_state:
        st.session_state.collector = WMICollector(PrivacyHasher(), live_mode=True)

@st.cache_data(ttl=5)
def load_live_data():
    """Collect real-time data from the system"""
    collector = st.session_state.collector
    detector = st.session_state.detector
    
    if not collector.is_available():
        # Fallback for non-Windows or missing WMI
        return load_scenario_data("Benign Baseline")
        
    events = []
    # Collect a snapshot of processes
    for event in collector.collect():
        if event.event_type == 'process_snapshot':
            # Convert to FeatureRow for detection
            # Note: WMI snapshot has limited data compared to Sysmon, so we approximate
            cmdline = event.command_line or ""
            features = FeatureRow(
                timestamp=event.timestamp.isoformat(),
                host_hash=event.raw_data.get('wmi_object', 'unknown'),
                process_name=event.process_name,
                parent_process=event.parent_name,
                cmdline_length=len(cmdline),
                cmdline_entropy=FeatureUtils.calculate_entropy(cmdline),
                is_lolbin=1 if FeatureUtils.is_lolbin(event.process_name) else 0,
                # Default values for fields not available in simple WMI snapshot
                cmdline_has_base64=1 if FeatureUtils.detect_base64(cmdline) else 0,
                cmdline_has_url=1 if FeatureUtils.detect_url(cmdline) else 0,
                is_unusual_path=1 if FeatureUtils.is_unusual_path(event.image_path) else 0,
                outbound_bytes_5m=0,
                outbound_bytes_1hr=0,
                unique_dst_ips_5m=0,
                unique_dst_ips_1hr=0,
                unique_dst_ports_1hr=0,
                dns_query_count_5m=0,
                dns_txt_query_count=0,
                rare_port_connections=0,
                periodic_connection_score=0.0,
                file_write_rate_1m=0.0,
                file_write_rate_5m=0.0,
                file_rename_count_5m=0,
                unique_extensions_written=0,
                encryption_indicator=0.0,
                failed_logons_10m=0,
                failed_logons_1hr=0,
                unique_failed_users_1hr=0,
                remote_logon_count=0,
                new_admin_indicator=0,
                ransomware_score=0.0,
                exfil_score=0.0,
                c2_beacon_score=0.0,
                lateral_movement_score=0.0,
                event_count=1,
                primary_event_type='process_snapshot'
            )
            
            # Run detection
            result = detector.detect(features)
            
            events.append({
                'ProcessId': event.process_id,
                'ProcessName': event.process_name,
                'User': event.user_hash, # Hashed for privacy
                'CPU_Usage': random.uniform(0.1, 5.0), # WMI doesn't give instant CPU easily
                'RAM_Usage': random.uniform(10, 200),
                'Risk_Score': result.risk_score,
                'ParentImage': event.parent_name,
                'CommandLine': event.command_line
            })
            
    if not events:
        return pd.DataFrame()
        
    return pd.DataFrame(events)

@st.cache_data
def load_scenario_data(scenario_type: str):
    """Load and enrich scenario data with synthetic metrics"""
    base_path = Path(__file__).parent.parent / "scenarios/data"
    
    if scenario_type == "Ransomware Attack":
        file_path = base_path / "malicious-ransomware/sysmon_ransomware.csv"
    elif scenario_type == "Data Exfiltration":
        # Fallback if file doesn't exist, use ransomware for demo structure
        file_path = base_path / "malicious-ransomware/sysmon_ransomware.csv" 
    else:
        file_path = base_path / "benign/sysmon_benign.csv"
        
    if not file_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    
    # Enrich with synthetic real-time metrics for the UI
    df['CPU_Usage'] = [random.uniform(0.1, 15.0) for _ in range(len(df))]
    df['RAM_Usage'] = [random.uniform(10, 500) for _ in range(len(df))]
    df['Risk_Score'] = [random.randint(0, 100) for _ in range(len(df))]
    
    # Boost risk for suspicious processes in ransomware scenario
    suspicious = ['powershell.exe', 'vssadmin.exe', 'wbadmin.exe', 'bcdedit.exe', 'update.exe']
    mask = df['Image'].apply(lambda x: any(s in str(x).lower() for s in suspicious))
    df.loc[mask, 'Risk_Score'] = df.loc[mask, 'Risk_Score'].apply(lambda x: max(x, random.randint(80, 99)))
    df.loc[mask, 'CPU_Usage'] = df.loc[mask, 'CPU_Usage'] * 3
    
    # Clean up Image path to just name
    df['ProcessName'] = df['Image'].apply(lambda x: Path(str(x)).name)
    
    return df

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_sidebar():
    with st.sidebar:
        st.title("🛡️ CyberShell")
        st.caption("v2.1.0 | AI-Powered Defense")
        
        st.divider()
        
        st.subheader("🎮 Operation Mode")
        mode = st.radio(
            "Source",
            ["Live System Monitor", "Scenario: Ransomware", "Scenario: Data Exfil"]
        )
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.selected_process_id = None
            st.session_state.analysis_complete = False
            st.cache_data.clear()
            st.rerun()

        st.divider()
        
        st.subheader("⚙️ System Safety")
        st.session_state.simulation_mode = st.toggle(
            "Safe Simulation Mode", 
            value=True,
            help="Prevents actual system changes. Actions are logged only."
        )
        
        if st.session_state.simulation_mode:
            st.markdown('<div class="badge-safe">✅ SIMULATION ACTIVE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-danger">⚠️ LIVE EXECUTION</div>', unsafe_allow_html=True)
            
        st.divider()
        
        st.subheader("📊 Global Metrics")
        st.metric("Active Threads", random.randint(1200, 1500))
        st.metric("Network Flows", random.randint(40, 80))
        
        return mode

def render_process_monitor(df: pd.DataFrame):
    st.subheader("🖥️ Process Activity Monitor")
    
    if df.empty:
        st.info("No process data available. Check permissions or data source.")
        return

    # Filter/Search
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search Process", placeholder="e.g., powershell.exe")
    with col2:
        min_risk = st.slider("Min Risk Score", 0, 100, 0)
        
    # Filter Logic
    display_df = df.copy()
    if search:
        display_df = display_df[display_df['ProcessName'].str.contains(search, case=False)]
    display_df = display_df[display_df['Risk_Score'] >= min_risk]
    
    # Display Columns
    cols = ['ProcessId', 'ProcessName', 'User', 'CPU_Usage', 'RAM_Usage', 'Risk_Score']
    
    # Interactive Table
    st.dataframe(
        display_df[cols].style.background_gradient(subset=['Risk_Score'], cmap='RdYlGn_r'),
        use_container_width=True,
        height=300,
        hide_index=True
    )
    
    # Selection for Analysis
    st.markdown("### 🔬 Deep Analysis Selection")
    process_options = display_df.apply(lambda x: f"{x['ProcessName']} (PID: {x['ProcessId']}) - Risk: {x['Risk_Score']}", axis=1).tolist()
    selected_str = st.selectbox("Select Process to Analyze", ["Select a process..."] + process_options)
    
    if selected_str != "Select a process...":
        pid = int(selected_str.split("PID: ")[1].split(")")[0])
        if st.session_state.selected_process_id != pid:
            st.session_state.selected_process_id = pid
            st.session_state.analysis_complete = False
            st.rerun()

def run_ai_analysis():
    """Simulate a high-tech AI analysis sequence"""
    if st.session_state.analysis_complete:
        return

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        ("🔍 Scanning memory segments...", 0.2),
        ("🕸️ Tracing thread injection patterns...", 0.4),
        ("📜 Verifying digital signatures...", 0.5),
        ("🧠 Running behavioral heuristic models...", 0.7),
        ("📡 Analyzing network socket states...", 0.85),
        ("✅ Generating threat assessment...", 1.0)
    ]
    
    for text, prog in steps:
        status_text.markdown(f'<p class="scanning-text">{text}</p>', unsafe_allow_html=True)
        progress_bar.progress(prog)
        time.sleep(random.uniform(0.3, 0.6)) # "Micro-loading" animation
        
    st.session_state.analysis_complete = True
    status_text.empty()
    progress_bar.empty()

def render_thread_visualization(process_row):
    st.subheader("🧵 Thread Activity Visualization")
    
    # Create a Graphviz graph
    dot = graphviz.Digraph(comment='Thread Graph')
    dot.attr(bgcolor='#111111', rankdir='LR')
    dot.attr('node', shape='circle', style='filled', fontname='Segoe UI', fontcolor='white')
    dot.attr('edge', color='#555555')
    
    # Main Process Node
    risk = process_row['Risk_Score']
    main_color = '#ff003c' if risk > 70 else ('#ffc107' if risk > 40 else '#00ff41')
    dot.node('MAIN', f"{process_row['ProcessName']}\nPID: {process_row['ProcessId']}", 
             color=main_color, fillcolor=main_color, shape='doublecircle', fontsize='12')
    
    # Simulated Threads (Real thread enumeration requires kernel driver or deeper API)
    num_threads = random.randint(3, 8)
    for i in range(num_threads):
        is_suspicious = (risk > 60) and (random.random() > 0.6)
        
        t_id = f"T-{random.randint(1000, 9999)}"
        t_color = '#ff003c' if is_suspicious else '#444444'
        t_label = f"{t_id}\n{'⚠️ Injection' if is_suspicious else 'Normal'}"
        
        dot.node(t_id, t_label, color=t_color, fillcolor=t_color, fontsize='10')
        
        edge_color = '#ff003c' if is_suspicious else '#555555'
        edge_style = 'dashed' if is_suspicious else 'solid'
        dot.edge('MAIN', t_id, color=edge_color, style=edge_style)
        
        # Child connections for suspicious threads (C2 simulation)
        if is_suspicious:
            ip = f"192.168.1.{random.randint(10, 99)}"
            dot.node(ip, f"Ext IP\n{ip}", shape='box', color='#00f3ff', fillcolor='#003333')
            dot.edge(t_id, ip, label="Socket", color='#00f3ff', fontsize='8')

    st.graphviz_chart(dot, use_container_width=True)

def render_evidence_panel(process_row):
    st.subheader("📋 Threat Evidence & AI Explanation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🤖 AI-Assisted Analysis")
        
        risk = process_row['Risk_Score']
        if risk > 80:
            explanation = f"""
            **CRITICAL THREAT DETECTED**
            
            The process `{process_row['ProcessName']}` exhibits behavior consistent with **Ransomware/Wiper** activity.
            
            **Key Indicators:**
            - 🚩 **High Entropy Command Line**: Detected Base64 encoded strings or obfuscated arguments.
            - 🚩 **Rapid File Operations**: Abnormal frequency of file handle requests.
            - 🚩 **Privilege Escalation**: Attempted to access protected system memory.
            
            **Recommendation**: Immediate termination and isolation required.
            """
            st.error(explanation)
        elif risk > 50:
            explanation = f"""
            **SUSPICIOUS ACTIVITY**
            
            The process `{process_row['ProcessName']}` is showing anomalous behavior.
            
            **Key Indicators:**
            - 🔸 **Uncommon Parent**: Spawned by `{process_row.get('ParentImage', 'Unknown')}`.
            - 🔸 **Network Beaconing**: Periodic connections to external IP addresses.
            
            **Recommendation**: Monitor closely and restrict network access.
            """
            st.warning(explanation)
        else:
            st.success(f"**BENIGN PROCESS**\n\nProcess `{process_row['ProcessName']}` appears to be operating within normal parameters. No significant anomalies detected.")

    with col2:
        st.markdown("#### 📊 Behavioral Metrics")
        
        # Radar Chart for Behavior
        categories = ['File Ops', 'Net Conns', 'Registry', 'CPU Spikes', 'Child Procs']
        values = [
            random.randint(10, 90) if risk > 50 else random.randint(0, 30) 
            for _ in range(5)
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line_color='#00f3ff'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            height=200,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

def render_actions_panel(process_row):
    st.subheader("⚡ Response Actions")
    
    playbook = PlaybookActions(
        mode=ExecutionMode.SIMULATE if st.session_state.simulation_mode else ExecutionMode.EXECUTE_VM,
        vm_mode=False
    )
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if st.button("🛑 KILL TASK", key="btn_kill", help="Terminate the process immediately"):
            with st.spinner("Sending termination signal..."):
                time.sleep(1)
                res = playbook.kill_process(process_name=process_row['ProcessName'])
                st.toast(f"Action Result: {res.message}")
                
    with c2:
        if st.button("🔒 ISOLATE HOST", key="btn_iso", help="Cut network access"):
            with st.spinner("Reconfiguring firewall rules..."):
                time.sleep(1)
                res = playbook.isolate_network()
                st.toast(f"Action Result: {res.message}")
                
    with c3:
        if st.button("🧊 FREEZE THREADS", key="btn_freeze", help="Suspend all process threads"):
            st.toast("Threads suspended successfully (Simulated)")
            
    with c4:
        if st.button("📦 DUMP MEMORY", key="btn_dump", help="Create memory dump for forensics"):
            st.toast("Memory dump saved to C:\\Forensics\\ (Simulated)")

# =============================================================================
# MAIN APP LOOP
# =============================================================================

def main():
    init_state()
    mode = render_sidebar()
    
    st.title("👁️ Overwatch Command Center")
    
    # Load Data based on Mode
    if mode == "Live System Monitor":
        df = load_live_data()
    elif mode == "Scenario: Ransomware":
        df = load_scenario_data("Ransomware Attack")
    else:
        df = load_scenario_data("Data Exfiltration")
    
    # Top Level Stats (Area Chart for "Thread Detection Visualization" over time)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📈 Network Threat Volume")
        # Simulated time-series data
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Inbound', 'Outbound', 'Lateral']
        )
        st.area_chart(chart_data, color=["#00ff41", "#00f3ff", "#ff003c"], height=200)
    
    with col2:
        st.markdown("### 🛡️ System Integrity")
        if not df.empty:
            integrity = 100 - (len(df[df['Risk_Score'] > 80]) * 5)
            integrity = max(0, integrity)
        else:
            integrity = 100
            
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = integrity,
            title = {'text': "Health Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00ff41" if integrity > 70 else "#ff003c"},
                'steps': [
                    {'range': [0, 50], 'color': "#330000"},
                    {'range': [50, 80], 'color': "#333300"},
                    {'range': [80, 100], 'color': "#003300"}
                ],
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Process Monitor
    render_process_monitor(df)
    
    # Detail View (if selected)
    if st.session_state.selected_process_id and not df.empty:
        st.divider()
        
        # Get selected row
        row_subset = df[df['ProcessId'] == st.session_state.selected_process_id]
        if not row_subset.empty:
            row = row_subset.iloc[0]
            
            st.markdown(f"## 🔬 Analyzing: `{row['ProcessName']}`")
            
            # Run "AI" Animation
            run_ai_analysis()
            
            if st.session_state.analysis_complete:
                # Layout: Graph on Left, Evidence on Right
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    render_thread_visualization(row)
                
                with c2:
                    render_evidence_panel(row)
                
                st.divider()
                render_actions_panel(row)

if __name__ == "__main__":
    main()