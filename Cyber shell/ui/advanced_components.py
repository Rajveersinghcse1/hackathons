"""
CyberShell Advanced UI Components
==================================

Purpose: Elite-tier visualizations for SOC operations
Features:
- Interactive timeline with Plotly
- MITRE ATT&CK heatmap showing technique coverage
- Real-time threat graph with filtering
- Performance metrics dashboard
- Threat intelligence integration panel
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import streamlit as st
import numpy as np


# =============================================================================
# INTERACTIVE TIMELINE VISUALIZATION
# =============================================================================

def render_interactive_timeline(detections: List[Dict[str, Any]]):
    """
    Render interactive Plotly timeline showing detections over time.
    Allows zooming, panning, and hovering for details.
    
    Args:
        detections: List of detection results (each a dict)
    """
    if not detections:
        st.info("No detections to display in timeline")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(detections)
    
    # Parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Color mapping for severity
    severity_colors = {
        'critical': '#FF0055',  # Neon red
        'high': '#FF6B35',      # Orange
        'medium': '#FFD23F',    # Yellow
        'low': '#06FFA5',       # Cyan
        'info': '#4D4D4D'       # Gray
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter plot for detections
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        severity_df = df[df['severity'] == severity]
        if not severity_df.empty:
            fig.add_trace(go.Scatter(
                x=severity_df['timestamp'],
                y=severity_df['risk_score'],
                mode='markers',
                name=severity.upper(),
                marker=dict(
                    size=12,
                    color=severity_colors[severity],
                    line=dict(width=1, color='#FFFFFF'),
                    opacity=0.8
                ),
                text=severity_df['alert_type'],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Time: %{x}<br>"
                    "Risk Score: %{y}<br>"
                    "Severity: " + severity.upper() + "<br>"
                    "<extra></extra>"
                ),
                customdata=severity_df[['host_hash', 'category']].values
            ))
    
    # Update layout with cyber aesthetic
    fig.update_layout(
        title={
            'text': "🔍 Detection Timeline - Interactive View",
            'font': {'size': 24, 'color': '#00D9FF', 'family': 'Courier New'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Timestamp",
        yaxis_title="Risk Score (0-100)",
        plot_bgcolor='#0A0E27',
        paper_bgcolor='#0A0E27',
        font=dict(color='#FFFFFF', family='Courier New'),
        xaxis=dict(
            showgrid=True,
            gridcolor='#1E2749',
            zeroline=False
        ),
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor='#1E2749',
            zeroline=False
        ),
        hovermode='closest',
        height=500,
        legend=dict(
            bgcolor='#1E2749',
            bordercolor='#00D9FF',
            borderwidth=1
        )
    )
    
    # Add threshold lines
    fig.add_hline(y=80, line_dash="dash", line_color="#FF0055", 
                  annotation_text="Critical Threshold", annotation_position="right")
    fig.add_hline(y=60, line_dash="dash", line_color="#FFD23F", 
                  annotation_text="High Threshold", annotation_position="right")
    
    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# MITRE ATT&CK HEATMAP
# =============================================================================

def render_mitre_heatmap(detections: List[Dict[str, Any]]):
    """
    Render MITRE ATT&CK technique coverage heatmap.
    Shows which techniques have been detected and their frequency.
    """
    st.markdown("### 🎯 MITRE ATT&CK Technique Coverage")
    
    if not detections:
        st.info("No detections with MITRE mapping yet")
        return
    
    # Extract MITRE techniques from detections
    technique_counts = {}
    for det in detections:
        if 'evidence' in det and 'mitre_attack' in det['evidence']:
            mitre = det['evidence']['mitre_attack']
            primary = mitre.get('primary_technique', {})
            technique_id = primary.get('id', 'Unknown')
            technique_name = primary.get('name', 'Unknown')
            tactic = primary.get('tactic', 'Unknown')
            
            key = f"{technique_id}: {technique_name}"
            if key not in technique_counts:
                technique_counts[key] = {'count': 0, 'tactic': tactic, 'id': technique_id}
            technique_counts[key]['count'] += 1
    
    if not technique_counts:
        st.info("No MITRE ATT&CK mappings found in detections")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {'technique': k, 'count': v['count'], 'tactic': v['tactic'], 'id': v['id']}
        for k, v in technique_counts.items()
    ])
    
    # Sort by count
    df = df.sort_values('count', ascending=False)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Color by tactic
    tactic_colors = {
        'INITIAL_ACCESS': '#FF0055',
        'EXECUTION': '#FF6B35',
        'PERSISTENCE': '#FFD23F',
        'PRIVILEGE_ESCALATION': '#06FFA5',
        'DEFENSE_EVASION': '#00D9FF',
        'CREDENTIAL_ACCESS': '#BF40BF',
        'DISCOVERY': '#7FFF00',
        'LATERAL_MOVEMENT': '#FF1493',
        'COLLECTION': '#FFA500',
        'COMMAND_AND_CONTROL': '#00CED1',
        'EXFILTRATION': '#DC143C',
        'IMPACT': '#8B0000'
    }
    
    colors = [tactic_colors.get(tactic, '#FFFFFF') for tactic in df['tactic']]
    
    fig.add_trace(go.Bar(
        y=df['technique'],
        x=df['count'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='#FFFFFF', width=1)
        ),
        text=df['count'],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Detections: %{x}<br>"
            "Tactic: %{customdata}<br>"
            "<extra></extra>"
        ),
        customdata=df['tactic']
    ))
    
    fig.update_layout(
        title={
            'text': "MITRE ATT&CK Technique Frequency",
            'font': {'size': 18, 'color': '#00D9FF', 'family': 'Courier New'}
        },
        xaxis_title="Number of Detections",
        yaxis_title="",
        plot_bgcolor='#0A0E27',
        paper_bgcolor='#0A0E27',
        font=dict(color='#FFFFFF', family='Courier New', size=10),
        height=400,
        margin=dict(l=300)
    )
    
    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PERFORMANCE METRICS DASHBOARD
# =============================================================================

def render_performance_dashboard(detections: List[Dict[str, Any]]):
    """
    Render performance metrics showing detection latency and throughput.
    """
    st.markdown("### ⚡ Performance Metrics")
    
    if not detections:
        st.info("No performance data available")
        return
    
    # Extract detection times
    detection_times = [
        d.get('detection_time_ms', 0) 
        for d in detections 
        if 'detection_time_ms' in d
    ]
    
    if not detection_times:
        st.warning("No detection time data available")
        return
    
    # Calculate statistics
    avg_time = np.mean(detection_times)
    median_time = np.median(detection_times)
    p95_time = np.percentile(detection_times, 95)
    p99_time = np.percentile(detection_times, 99)
    max_time = np.max(detection_times)
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Avg Latency",
            value=f"{avg_time:.2f}ms",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Median",
            value=f"{median_time:.2f}ms"
        )
    
    with col3:
        st.metric(
            label="P95",
            value=f"{p95_time:.2f}ms"
        )
    
    with col4:
        st.metric(
            label="P99",
            value=f"{p99_time:.2f}ms"
        )
    
    with col5:
        st.metric(
            label="Max",
            value=f"{max_time:.2f}ms"
        )
    
    # Latency distribution histogram
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=detection_times,
        nbinsx=30,
        marker=dict(
            color='#00D9FF',
            line=dict(color='#FFFFFF', width=1)
        ),
        hovertemplate=(
            "Latency: %{x:.2f}ms<br>"
            "Count: %{y}<br>"
            "<extra></extra>"
        )
    ))
    
    fig.update_layout(
        title={
            'text': "Detection Latency Distribution",
            'font': {'size': 18, 'color': '#00D9FF', 'family': 'Courier New'}
        },
        xaxis_title="Latency (ms)",
        yaxis_title="Frequency",
        plot_bgcolor='#0A0E27',
        paper_bgcolor='#0A0E27',
        font=dict(color='#FFFFFF', family='Courier New'),
        height=300
    )
    
    # Add target SLA line (15ms)
    fig.add_vline(x=15, line_dash="dash", line_color="#06FFA5", 
                  annotation_text="Target SLA (15ms)", annotation_position="top")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Throughput calculation
    if len(detections) > 1:
        df = pd.DataFrame(detections)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        time_range = (df['timestamp'].max() - df['timestamp'].min()).total_seconds()
        if time_range > 0:
            throughput = len(detections) / time_range
            st.metric(
                label="📊 Throughput",
                value=f"{throughput:.2f} events/sec",
                help="Number of events processed per second"
            )


# =============================================================================
# THREAT INTELLIGENCE PANEL
# =============================================================================

def render_threat_intelligence_panel(detection: Dict[str, Any]):
    """
    Render detailed threat intelligence panel for a selected detection.
    Shows MITRE ATT&CK details, recommended actions, and attribution.
    """
    st.markdown("### 🛡️ Threat Intelligence")
    
    if 'evidence' not in detection or 'mitre_attack' not in detection['evidence']:
        st.info("No threat intelligence available for this detection")
        return
    
    mitre = detection['evidence']['mitre_attack']
    primary = mitre.get('primary_technique', {})
    
    # Primary technique card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E2749 0%, #2D3561 100%); 
                padding: 20px; 
                border-radius: 10px; 
                border-left: 4px solid #FF0055;
                margin-bottom: 15px;">
        <h4 style="color: #00D9FF; margin: 0;">{primary.get('id', 'Unknown')}: {primary.get('name', 'Unknown')}</h4>
        <p style="color: #FFFFFF; margin-top: 10px;">{primary.get('description', 'No description available')}</p>
        <p style="color: #06FFA5; margin-top: 10px;">
            <b>Tactic:</b> {primary.get('tactic', 'Unknown')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Kill chain phase
    kill_chain = mitre.get('kill_chain_phase', 'Unknown')
    st.markdown(f"**Kill Chain Phase:** `{kill_chain}`")
    
    # Severity justification
    severity_just = mitre.get('severity_justification', 'No justification available')
    st.markdown(f"**Severity Justification:** {severity_just}")
    
    # Recommended actions
    st.markdown("#### 🚨 Recommended Actions")
    actions = mitre.get('recommended_actions', [])
    if actions:
        for i, action in enumerate(actions[:5], 1):
            st.markdown(f"{i}. {action}")
    else:
        st.info("No specific actions recommended")
    
    # Related techniques
    related = mitre.get('related_techniques', [])
    if related:
        st.markdown("#### 🔗 Related Techniques")
        for tech in related:
            st.markdown(f"- **{tech.get('id')}**: {tech.get('name')}")
    
    # Threat actor profile
    if 'threat_actor_profile' in mitre and mitre['threat_actor_profile']:
        st.markdown("#### 🎭 Threat Actor Profile")
        st.warning(mitre['threat_actor_profile'])


# =============================================================================
# SHAP EXPLAINABILITY VISUALIZATION
# =============================================================================

def render_shap_explanation(detection: Dict[str, Any]):
    """
    Render SHAP force plot showing feature contributions to detection.
    """
    st.markdown("### 🧠 ML Explainability (SHAP)")
    
    if 'evidence' not in detection or 'shap_values' not in detection['evidence']:
        st.info("No SHAP explanation available for this detection")
        return
    
    shap_data = detection['evidence']['shap_values']
    
    # Display prediction vs baseline
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Base Value", f"{shap_data.get('base_value', 0):.3f}")
    with col2:
        st.metric("Prediction", f"{shap_data.get('prediction', 0):.3f}")
    with col3:
        delta = shap_data.get('prediction', 0) - shap_data.get('base_value', 0)
        st.metric("Shift", f"{delta:.3f}")
    
    # Top positive features (push toward detection)
    st.markdown("#### ⬆️ Top Features Increasing Threat Score")
    positive_features = shap_data.get('top_positive_features', [])
    if positive_features:
        for feat in positive_features[:5]:
            st.markdown(
                f"- **{feat['feature']}**: +{feat['contribution']:.4f}"
            )
    
    # Top negative features (push toward benign)
    st.markdown("#### ⬇️ Top Features Decreasing Threat Score")
    negative_features = shap_data.get('top_negative_features', [])
    if negative_features:
        for feat in negative_features[:3]:
            st.markdown(
                f"- **{feat['feature']}**: {feat['contribution']:.4f}"
            )
    
    # Natural language explanation
    if 'explanation' in detection and detection['explanation']:
        st.markdown("#### 💬 Explanation")
        st.info(detection['explanation'])


if __name__ == "__main__":
    print("Advanced UI Components Module")
    print("Import these functions into streamlit_app.py")
