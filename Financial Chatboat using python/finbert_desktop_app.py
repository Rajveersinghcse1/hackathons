import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import json
import threading
import subprocess
import sys
import os
from datetime import datetime
import csv
import pandas as pd

class FinBERTDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinBERT Financial Sentiment Analysis")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Backend URL
        self.backend_url = "http://localhost:8001"
        self.backend_process = None
        
        # Create main interface
        self.create_widgets()
        
        # Check backend status
        self.check_backend_status()
        
    def create_widgets(self):
        """Create the main UI components"""
        
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="FinBERT Financial Sentiment Analysis", 
            font=("Arial", 18, "bold"),
            bg='#2c3e50', 
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg='#f0f0f0')
        status_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame, 
            text="Backend Status: Checking...", 
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#e74c3c'
        )
        self.status_label.pack(side='left')
        
        self.start_backend_btn = tk.Button(
            status_frame,
            text="Start Backend",
            command=self.start_backend,
            bg='#27ae60',
            fg='white',
            font=("Arial", 10),
            relief='flat'
        )
        self.start_backend_btn.pack(side='right', padx=(0, 10))
        
        self.refresh_btn = tk.Button(
            status_frame,
            text="Refresh",
            command=self.check_backend_status,
            bg='#3498db',
            fg='white',
            font=("Arial", 10),
            relief='flat'
        )
        self.refresh_btn.pack(side='right', padx=(0, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Single Analysis Tab
        self.create_single_analysis_tab()
        
        # Batch Analysis Tab
        self.create_batch_analysis_tab()
        
        # Demo Tab
        self.create_demo_tab()
        
        # Model Info Tab
        self.create_model_info_tab()
        
    def create_single_analysis_tab(self):
        """Create single text analysis tab"""
        single_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(single_frame, text="Single Analysis")
        
        # Input section
        input_label = tk.Label(
            single_frame, 
            text="Enter Financial Text:", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        input_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.text_input = scrolledtext.ScrolledText(
            single_frame, 
            height=8, 
            width=100,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.text_input.pack(padx=10, pady=(0, 10), fill='x')
        
        # Analyze button
        analyze_btn = tk.Button(
            single_frame,
            text="Analyze Sentiment",
            command=self.analyze_single_text,
            bg='#3498db',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            height=2
        )
        analyze_btn.pack(pady=10)
        
        # Results section
        results_label = tk.Label(
            single_frame, 
            text="Analysis Results:", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        results_label.pack(anchor='w', padx=10, pady=(20, 5))
        
        # Results frame with styling
        results_frame = tk.Frame(single_frame, bg='white', relief='ridge', bd=2)
        results_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=10,
            font=("Courier", 10),
            bg='white',
            state='disabled'
        )
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def create_batch_analysis_tab(self):
        """Create batch analysis tab"""
        batch_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(batch_frame, text="Batch Analysis")
        
        # Input section
        input_label = tk.Label(
            batch_frame, 
            text="Enter Multiple Financial Texts (one per line):", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        input_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.batch_input = scrolledtext.ScrolledText(
            batch_frame, 
            height=10, 
            width=100,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.batch_input.pack(padx=10, pady=(0, 10), fill='x')
        
        # Buttons frame
        buttons_frame = tk.Frame(batch_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=10)
        
        analyze_batch_btn = tk.Button(
            buttons_frame,
            text="Analyze Batch",
            command=self.analyze_batch_text,
            bg='#3498db',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat'
        )
        analyze_batch_btn.pack(side='left', padx=(0, 10))
        
        load_file_btn = tk.Button(
            buttons_frame,
            text="Load from File",
            command=self.load_from_file,
            bg='#9b59b6',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat'
        )
        load_file_btn.pack(side='left', padx=(0, 10))
        
        export_btn = tk.Button(
            buttons_frame,
            text="Export Results",
            command=self.export_results,
            bg='#e67e22',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat'
        )
        export_btn.pack(side='left')
        
        # Results section
        results_label = tk.Label(
            batch_frame, 
            text="Batch Analysis Results:", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        results_label.pack(anchor='w', padx=10, pady=(20, 5))
        
        # Results with treeview for better display
        tree_frame = tk.Frame(batch_frame, bg='white', relief='ridge', bd=2)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=('Text', 'Positive', 'Negative', 'Neutral', 'Sentiment', 'Confidence'), show='headings', height=8)
        
        # Define headings
        self.tree.heading('Text', text='Text')
        self.tree.heading('Positive', text='Positive')
        self.tree.heading('Negative', text='Negative')
        self.tree.heading('Neutral', text='Neutral')
        self.tree.heading('Sentiment', text='Predicted')
        self.tree.heading('Confidence', text='Confidence')
        
        # Configure column widths
        self.tree.column('Text', width=200)
        self.tree.column('Positive', width=80)
        self.tree.column('Negative', width=80)
        self.tree.column('Neutral', width=80)
        self.tree.column('Sentiment', width=100)
        self.tree.column('Confidence', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Store batch results for export
        self.batch_results = []
        
    def create_demo_tab(self):
        """Create demo tab with sample financial texts"""
        demo_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(demo_frame, text="Demo")
        
        demo_label = tk.Label(
            demo_frame, 
            text="Demo: Financial Sentiment Analysis", 
            font=("Arial", 14, "bold"),
            bg='#f0f0f0'
        )
        demo_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        demo_desc = tk.Label(
            demo_frame, 
            text="Click the button below to analyze sample financial texts with FinBERT:", 
            font=("Arial", 10),
            bg='#f0f0f0',
            justify='left'
        )
        demo_desc.pack(anchor='w', padx=10, pady=(0, 10))
        
        demo_btn = tk.Button(
            demo_frame,
            text="Run Demo Analysis",
            command=self.run_demo,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            height=2
        )
        demo_btn.pack(pady=20)
        
        # Demo results
        self.demo_results = scrolledtext.ScrolledText(
            demo_frame,
            height=20,
            font=("Courier", 9),
            bg='white',
            state='disabled'
        )
        self.demo_results.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
    def create_model_info_tab(self):
        """Create model information tab"""
        info_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(info_frame, text="Model Info")
        
        info_label = tk.Label(
            info_frame, 
            text="FinBERT Model Information", 
            font=("Arial", 14, "bold"),
            bg='#f0f0f0'
        )
        info_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        refresh_info_btn = tk.Button(
            info_frame,
            text="Refresh Model Info",
            command=self.get_model_info,
            bg='#2ecc71',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat'
        )
        refresh_info_btn.pack(pady=10)
        
        self.model_info_text = scrolledtext.ScrolledText(
            info_frame,
            height=25,
            font=("Courier", 10),
            bg='white',
            state='disabled'
        )
        self.model_info_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
    def check_backend_status(self):
        """Check if backend is running"""
        def check():
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    model_status = data.get('finbert_model_status', 'unknown')
                    self.status_label.config(
                        text=f"Backend Status: Connected ({model_status})", 
                        fg='#27ae60'
                    )
                    self.start_backend_btn.config(text="Backend Running", state='disabled')
                else:
                    self.status_label.config(
                        text="Backend Status: Error", 
                        fg='#e74c3c'
                    )
                    self.start_backend_btn.config(text="Start Backend", state='normal')
            except:
                self.status_label.config(
                    text="Backend Status: Disconnected", 
                    fg='#e74c3c'
                )
                self.start_backend_btn.config(text="Start Backend", state='normal')
        
        threading.Thread(target=check, daemon=True).start()
        
    def start_backend(self):
        """Start the FinBERT backend"""
        def start():
            try:
                backend_path = os.path.join(os.path.dirname(__file__), "backend", "finbert_main.py")
                if os.path.exists(backend_path):
                    self.backend_process = subprocess.Popen([
                        sys.executable, backend_path
                    ], cwd=os.path.join(os.path.dirname(__file__), "backend"))
                    
                    self.status_label.config(text="Backend Status: Starting...", fg='#f39c12')
                    
                    # Wait a bit and check status
                    self.root.after(3000, self.check_backend_status)
                else:
                    messagebox.showerror("Error", "Backend file not found!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start backend: {str(e)}")
        
        threading.Thread(target=start, daemon=True).start()
        
    def analyze_single_text(self):
        """Analyze single text input"""
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to analyze")
            return
            
        def analyze():
            try:
                response = requests.post(
                    f"{self.backend_url}/api/v1/analyze",
                    json={"text": text},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.display_single_result(result)
                else:
                    messagebox.showerror("Error", f"Analysis failed: {response.text}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Connection failed: {str(e)}")
        
        threading.Thread(target=analyze, daemon=True).start()
        
    def display_single_result(self, result):
        """Display single analysis result"""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        # Format the results nicely
        display_text = f"""
═══════════════════════════════════════════════════════════════════
                        FINBERT SENTIMENT ANALYSIS
═══════════════════════════════════════════════════════════════════

📝 TEXT ANALYZED:
{result.get('Text', 'N/A')}

📊 SENTIMENT PROBABILITIES:
   • Positive: {result.get('Positive', 0):.4f} ({result.get('Positive', 0)*100:.2f}%)
   • Negative: {result.get('Negative', 0):.4f} ({result.get('Negative', 0)*100:.2f}%)
   • Neutral:  {result.get('Neutral', 0):.4f} ({result.get('Neutral', 0)*100:.2f}%)

🎯 PREDICTION:
   Sentiment: {result.get('Predicted Sentiment', 'N/A').upper()}
   Confidence: {result.get('confidence', 0):.4f} ({result.get('confidence', 0)*100:.2f}%)

🤖 MODEL USED:
   {result.get('model_used', 'N/A')}

⏰ ANALYSIS TIME:
   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════════════════════════════════
"""
        
        self.results_text.insert(tk.END, display_text)
        self.results_text.config(state='disabled')
        
    def analyze_batch_text(self):
        """Analyze batch text input"""
        text = self.batch_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some texts to analyze")
            return
            
        texts = [line.strip() for line in text.split('\n') if line.strip()]
        
        def analyze():
            try:
                response = requests.post(
                    f"{self.backend_url}/api/v1/analyze_batch",
                    json={"texts": texts},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.batch_results = data.get('results', [])
                    self.display_batch_results(self.batch_results)
                else:
                    messagebox.showerror("Error", f"Batch analysis failed: {response.text}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Connection failed: {str(e)}")
        
        threading.Thread(target=analyze, daemon=True).start()
        
    def display_batch_results(self, results):
        """Display batch analysis results in treeview"""
        # Clear existing results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new results
        for i, result in enumerate(results):
            text = result.get('Text', '')
            # Truncate text for display
            display_text = text[:50] + "..." if len(text) > 50 else text
            
            self.tree.insert('', 'end', values=(
                display_text,
                f"{result.get('Positive', 0):.3f}",
                f"{result.get('Negative', 0):.3f}",
                f"{result.get('Neutral', 0):.3f}",
                result.get('Predicted Sentiment', 'N/A'),
                f"{result.get('confidence', 0):.3f}"
            ))
            
    def load_from_file(self):
        """Load texts from file"""
        file_path = filedialog.askopenfilename(
            title="Select text file",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    # Try to read CSV and get text column
                    df = pd.read_csv(file_path)
                    if 'text' in df.columns:
                        texts = df['text'].tolist()
                    else:
                        # Use first column
                        texts = df.iloc[:, 0].tolist()
                    text_content = '\n'.join([str(text) for text in texts])
                else:
                    # Read as text file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text_content = file.read()
                
                self.batch_input.delete(1.0, tk.END)
                self.batch_input.insert(1.0, text_content)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def export_results(self):
        """Export batch results to file"""
        if not self.batch_results:
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save results",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("Text files", "*.txt")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.DataFrame(self.batch_results)
                    df.to_csv(file_path, index=False)
                elif file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(self.batch_results, file, indent=2)
                else:
                    # Export as formatted text
                    with open(file_path, 'w', encoding='utf-8') as file:
                        for i, result in enumerate(self.batch_results, 1):
                            file.write(f"Result {i}:\n")
                            file.write(f"Text: {result.get('Text', '')}\n")
                            file.write(f"Positive: {result.get('Positive', 0):.4f}\n")
                            file.write(f"Negative: {result.get('Negative', 0):.4f}\n")
                            file.write(f"Neutral: {result.get('Neutral', 0):.4f}\n")
                            file.write(f"Predicted: {result.get('Predicted Sentiment', '')}\n")
                            file.write(f"Confidence: {result.get('confidence', 0):.4f}\n")
                            file.write("-" * 50 + "\n")
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
                
    def run_demo(self):
        """Run demo analysis"""
        def demo():
            try:
                response = requests.post(f"{self.backend_url}/api/v1/demo", timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    self.display_demo_results(data)
                else:
                    messagebox.showerror("Error", f"Demo failed: {response.text}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Connection failed: {str(e)}")
        
        threading.Thread(target=demo, daemon=True).start()
        
    def display_demo_results(self, data):
        """Display demo results"""
        self.demo_results.config(state='normal')
        self.demo_results.delete(1.0, tk.END)
        
        demo_text = f"""
═══════════════════════════════════════════════════════════════════
                        FINBERT DEMO ANALYSIS
═══════════════════════════════════════════════════════════════════

🤖 MODEL INFORMATION:
{json.dumps(data.get('model_info', {}), indent=2)}

📊 DEMO ANALYSIS RESULTS:
"""
        
        for i, result in enumerate(data.get('demo_results', []), 1):
            demo_text += f"""
--- Sample {i} ---
📝 Text: {result.get('Text', '')}
📊 Positive: {result.get('Positive', 0):.4f} ({result.get('Positive', 0)*100:.2f}%)
📊 Negative: {result.get('Negative', 0):.4f} ({result.get('Negative', 0)*100:.2f}%)
📊 Neutral:  {result.get('Neutral', 0):.4f} ({result.get('Neutral', 0)*100:.2f}%)
🎯 Predicted: {result.get('Predicted Sentiment', '').upper()}
🔍 Confidence: {result.get('confidence', 0):.4f} ({result.get('confidence', 0)*100:.2f}%)
🤖 Model: {result.get('model_used', '')}
"""
        
        demo_text += f"""
⏰ Analysis completed at: {data.get('timestamp', '')}
═══════════════════════════════════════════════════════════════════
"""
        
        self.demo_results.insert(tk.END, demo_text)
        self.demo_results.config(state='disabled')
        
    def get_model_info(self):
        """Get and display model information"""
        def get_info():
            try:
                response = requests.get(f"{self.backend_url}/api/v1/model/info", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.display_model_info(data)
                else:
                    messagebox.showerror("Error", f"Failed to get model info: {response.text}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Connection failed: {str(e)}")
        
        threading.Thread(target=get_info, daemon=True).start()
        
    def display_model_info(self, data):
        """Display model information"""
        self.model_info_text.config(state='normal')
        self.model_info_text.delete(1.0, tk.END)
        
        info_text = f"""
═══════════════════════════════════════════════════════════════════
                        FINBERT MODEL INFORMATION
═══════════════════════════════════════════════════════════════════

📋 MODEL DETAILS:
{json.dumps(data, indent=2)}

📝 ABOUT FINBERT:
FinBERT is a specialized BERT model for financial sentiment analysis.
It was trained on financial texts and can classify sentiment into:
- Positive: Bullish, optimistic financial sentiment
- Negative: Bearish, pessimistic financial sentiment  
- Neutral: Balanced or informational financial sentiment

🎯 USE CASES:
- Financial news analysis
- Earnings call sentiment
- Social media financial sentiment
- Investment research
- Risk assessment

⚡ FEATURES:
- Real-time analysis
- Batch processing
- High accuracy on financial texts
- Confidence scoring
- Fallback keyword analysis

⏰ Information retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════════
"""
        
        self.model_info_text.insert(tk.END, info_text)
        self.model_info_text.config(state='disabled')

def main():
    root = tk.Tk()
    app = FinBERTDesktopApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
