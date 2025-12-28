from graphviz import Digraph
import os

def create_architecture_diagram():
    # Check if graphviz is likely installed/available
    # This script attempts to generate a high-quality PNG
    
    dot = Digraph('CyberShell_Architecture', comment='CyberShell System Design')
    
    # Global Graph Attributes (Cyberpunk/Dark Theme)
    dot.attr(bgcolor='#0E1117')  # Dark background matching Streamlit
    dot.attr(rankdir='LR')       # Left to Right flow
    dot.attr(splines='ortho')    # Orthogonal edges for circuit-board look
    dot.attr(pad='0.5')
    dot.attr(fontname='Segoe UI')
    dot.attr(fontsize='20')
    dot.attr(fontcolor='white')
    dot.attr(label='CyberShell: Autonomous Edge-Native Defense Architecture')
    
    # Node Attributes
    dot.attr('node', shape='box', style='filled,rounded', fontname='Segoe UI', fontsize='12', margin='0.2', penwidth='2')
    
    # Edge Attributes
    dot.attr('edge', color='#00f3ff', penwidth='2', arrowsize='1.0', fontname='Segoe UI', fontsize='10', fontcolor='#00f3ff')

    # --- Subgraph: Kernel Space (Ring 0) ---
    with dot.subgraph(name='cluster_kernel') as k:
        k.attr(label='Windows Kernel (Ring 0)', color='#ff003c', fontcolor='#ff003c', style='dashed')
        k.node('WMI', '📡 WMI Provider\n(Win32_Process)', shape='component', fillcolor='#2d3436', fontcolor='white', color='#ff003c')

    # --- Subgraph: User Space (Ring 3) ---
    with dot.subgraph(name='cluster_userland') as u:
        u.attr(label='CyberShell Userland (Ring 3) - Safe Execution', color='#00ff41', fontcolor='#00ff41')
        
        # Data Ingestion
        u.node('Collector', '🕵️ Async Collector\n(Event Subscription)', fillcolor='#2d3436', fontcolor='white', color='#00ff41')
        
        # Privacy
        u.node('Hasher', '🔒 Privacy Vault\n(SHA-256 Hashing)', shape='shield', fillcolor='#2d3436', fontcolor='white', color='#fab1a0')
        
        # Feature Extraction
        u.node('Extractor', '⚙️ Feature Extractor\n(Entropy, Vectors)', fillcolor='#2d3436', fontcolor='white', color='#74b9ff')
        
        # Intelligence Core
        with u.subgraph(name='cluster_brain') as b:
            b.attr(label='Neuro-Symbolic Core', color='#a29bfe', fontcolor='#a29bfe')
            b.node('ML', '🧠 IsolationForest\n(Anomaly Detection)', fillcolor='#6c5ce7', fontcolor='white', color='#a29bfe')
            b.node('Rules', '📜 Rule Engine\n(Deterministic)', fillcolor='#0984e3', fontcolor='white', color='#74b9ff')
            b.node('Scorer', '⚖️ Hybrid Scorer\n(Weighted Aggregation)', shape='diamond', fillcolor='#d63031', fontcolor='white', color='#ff7675')

        # UI & Action
        u.node('UI', '🖥️ Streamlit UI\n(Reactive Command Center)', shape='folder', fillcolor='#2d3436', fontcolor='white', color='#fdcb6e')
        u.node('Action', '⚡ Active Defense\n(Terminate Process)', shape='octagon', fillcolor='#d63031', fontcolor='white', color='#ff003c')

    # --- Edges ---
    dot.edge('WMI', 'Collector', label=' Async Event (Push)')
    dot.edge('Collector', 'Hasher', label=' Raw Data')
    dot.edge('Hasher', 'Extractor', label=' Anonymized Data')
    
    dot.edge('Extractor', 'ML', label=' Vectors')
    dot.edge('Extractor', 'Rules', label=' Metadata')
    
    dot.edge('ML', 'Scorer', label=' Score')
    dot.edge('Rules', 'Scorer', label=' Flag')
    
    dot.edge('Scorer', 'UI', label=' Alert')
    dot.edge('Scorer', 'Action', label=' High Conf.')

    # Render
    try:
        output_path = dot.render('system_architecture', format='png', cleanup=True)
        print(f"Successfully generated: {output_path}")
    except Exception as e:
        print(f"Error generating diagram: {e}")
        print("NOTE: You need to have Graphviz installed on your system (not just the python library).")
        print("Download from: https://graphviz.org/download/")

if __name__ == "__main__":
    create_architecture_diagram()
