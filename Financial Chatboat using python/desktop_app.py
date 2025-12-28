import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
from datetime import datetime
import webbrowser

class FinBERTChatbotDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("FinBERT AGI Chatbot - Desktop")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1f3a")
        
        # Backend URL
        self.backend_url = "http://localhost:8001"
        self.session_id = "desktop_session"
        
        # Create main style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure("Title.TLabel", 
                           foreground="#2196f3", 
                           background="#1a1f3a", 
                           font=("Arial", 16, "bold"))
        
        self.style.configure("Custom.TFrame", 
                           background="#1a1f3a")
        
        self.style.configure("Chat.TFrame", 
                           background="#0a0e27",
                           relief="solid",
                           borderwidth=1)
        
        self.setup_ui()
        self.check_backend_connection()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, style="Custom.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🤖 FinBERT AGI Chatbot Desktop", 
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, 
                                   text="🔴 Checking backend connection...", 
                                   bg="#1a1f3a", 
                                   fg="#ff9800",
                                   font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Memory toggle
        self.use_memory_var = tk.BooleanVar(value=True)
        memory_check = tk.Checkbutton(control_frame, 
                                    text="Use Memory", 
                                    variable=self.use_memory_var,
                                    bg="#1a1f3a", 
                                    fg="#ffffff",
                                    selectcolor="#2196f3",
                                    font=("Arial", 10))
        memory_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # Clear chat button
        clear_btn = tk.Button(control_frame, 
                            text="Clear Chat", 
                            command=self.clear_chat,
                            bg="#ff5722", 
                            fg="white",
                            font=("Arial", 10),
                            relief=tk.FLAT,
                            padx=15)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Web interface button
        web_btn = tk.Button(control_frame, 
                          text="Open Web Interface", 
                          command=self.open_web_interface,
                          bg="#4caf50", 
                          fg="white",
                          font=("Arial", 10),
                          relief=tk.FLAT,
                          padx=15)
        web_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Chat display area
        chat_frame = ttk.Frame(main_frame, style="Chat.TFrame")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                     wrap=tk.WORD,
                                                     width=80,
                                                     height=25,
                                                     bg="#0a0e27",
                                                     fg="#ffffff",
                                                     font=("Consolas", 11),
                                                     insertbackground="#2196f3",
                                                     selectbackground="#2196f3",
                                                     selectforeground="#ffffff")
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#2196f3", font=("Consolas", 11, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#4caf50", font=("Consolas", 11, "bold"))
        self.chat_display.tag_configure("system", foreground="#ff9800", font=("Consolas", 10, "italic"))
        self.chat_display.tag_configure("metadata", foreground="#9e9e9e", font=("Consolas", 9))
        
        # Input area
        input_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        input_frame.pack(fill=tk.X)
        
        # Message input
        input_label = tk.Label(input_frame, 
                             text="Your Message:", 
                             bg="#1a1f3a", 
                             fg="#ffffff",
                             font=("Arial", 11, "bold"))
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.message_input = tk.Text(input_frame,
                                   height=3,
                                   wrap=tk.WORD,
                                   bg="#2c3e50",
                                   fg="#ffffff",
                                   font=("Arial", 11),
                                   insertbackground="#2196f3",
                                   selectbackground="#2196f3",
                                   selectforeground="#ffffff")
        self.message_input.pack(fill=tk.X, pady=(0, 10))
        
        # Bind Enter key to send message
        self.message_input.bind("<Control-Return>", self.send_message_event)
        
        # Send button
        button_frame = ttk.Frame(input_frame, style="Custom.TFrame")
        button_frame.pack(fill=tk.X)
        
        self.send_button = tk.Button(button_frame,
                                   text="Send Message (Ctrl+Enter)",
                                   command=self.send_message,
                                   bg="#2196f3",
                                   fg="white",
                                   font=("Arial", 12, "bold"),
                                   relief=tk.FLAT,
                                   padx=20,
                                   pady=8)
        self.send_button.pack(side=tk.RIGHT)
        
        # Add welcome message
        self.add_system_message("Welcome to FinBERT Financial Chatbot Desktop Application!")
        self.add_system_message("This desktop app uses FinBERT for advanced financial sentiment analysis.")
        self.add_system_message("Ask me about financial markets, sentiment analysis, or investment guidance!")
        self.add_system_message("Type your message below and press Ctrl+Enter or click Send.")
        
    def check_backend_connection(self):
        """Check if backend is running"""
        def check():
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    self.root.after(0, self.update_status, "🟢 FinBERT Connected", "#4caf50")
                    self.root.after(0, self.add_system_message, "✅ Successfully connected to FinBERT backend!")
                else:
                    self.root.after(0, self.update_status, "🔴 Backend Error", "#ff5722")
                    self.root.after(0, self.add_system_message, "❌ Backend returned error status")
            except requests.exceptions.RequestException as e:
                self.root.after(0, self.update_status, "🔴 Backend Offline", "#ff5722")
                self.root.after(0, self.add_system_message, f"❌ Cannot connect to backend: {str(e)}")
                self.root.after(0, self.add_system_message, "💡 Make sure to start the FinBERT backend: python finbert_desktop_main.py")
        
        # Run check in separate thread
        threading.Thread(target=check, daemon=True).start()
    
    def update_status(self, message, color):
        """Update status label"""
        self.status_label.config(text=message, fg=color)
    
    def add_message(self, role, content, metadata=None):
        """Add a message to the chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add timestamp and role
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "metadata")
        
        if role == "user":
            self.chat_display.insert(tk.END, "You: ", "user")
        elif role == "assistant":
            self.chat_display.insert(tk.END, "FinBERT: ", "assistant")
        
        # Add message content
        self.chat_display.insert(tk.END, f"{content}\n")
        
        # Add metadata if available
        if metadata:
            meta_text = f"   📊 Type: {metadata.get('response_type', 'N/A')} | "
            meta_text += f"💭 Sentiment: {metadata.get('sentiment', {}).get('label', 'N/A')} | "
            meta_text += f"🎯 Confidence: {metadata.get('confidence', 0):.2f} | "
            meta_text += f"⚡ Time: {metadata.get('processing_time', 0):.2f}s\n"
            
            self.chat_display.insert(tk.END, meta_text, "metadata")
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.see(tk.END)
    
    def add_system_message(self, message):
        """Add a system message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "metadata")
        self.chat_display.insert(tk.END, "System: ", "system")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
    
    def send_message_event(self, event):
        """Handle Enter key press"""
        self.send_message()
        return "break"  # Prevent default behavior
    
    def send_message(self):
        """Send message to the backend"""
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.message_input.delete("1.0", tk.END)
        
        # Add user message to display
        self.add_message("user", message)
        
        # Disable send button
        self.send_button.config(state=tk.DISABLED, text="Sending...")
        
        # Send to backend in separate thread
        def send_to_backend():
            try:
                payload = {
                    "message": message,
                    "session_id": self.session_id
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/v1/chat",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Add AI response to display
                    self.root.after(0, self.add_message, "assistant", data["response"], {
                        "response_type": data.get("response_type"),
                        "sentiment": data.get("sentiment"),
                        "processing_time": data.get("processing_time"),
                        "confidence": data.get("confidence")
                    })
                else:
                    error_msg = f"Backend error: {response.status_code}"
                    self.root.after(0, self.add_system_message, f"❌ {error_msg}")
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Connection error: {str(e)}"
                self.root.after(0, self.add_system_message, f"❌ {error_msg}")
            
            finally:
                # Re-enable send button
                self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL, text="Send Message (Ctrl+Enter)"))
        
        # Run in separate thread
        threading.Thread(target=send_to_backend, daemon=True).start()
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.delete("1.0", tk.END)
        self.add_system_message("Chat cleared. Ready for new conversation!")
    
    def open_web_interface(self):
        """Open web interface in browser"""
        try:
            webbrowser.open("http://localhost:3000")
            self.add_system_message("🌐 Opening web interface in your default browser...")
        except Exception as e:
            self.add_system_message(f"❌ Could not open web interface: {str(e)}")

class SplashScreen:
    def __init__(self):
        self.splash = tk.Tk()
        self.splash.title("FinBERT AGI Chatbot")
        self.splash.geometry("500x300")
        self.splash.configure(bg="#0a0e27")
        self.splash.overrideredirect(True)  # Remove window decorations
        
        # Center the splash screen
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (300 // 2)
        self.splash.geometry(f"500x300+{x}+{y}")
        
        # Create splash content
        self.setup_splash()
        
        # Auto close after 3 seconds
        self.splash.after(3000, self.close_splash)
        
    def setup_splash(self):
        """Setup splash screen content"""
        # Title
        title = tk.Label(self.splash, 
                        text="💼 FinBERT Financial Chatbot", 
                        bg="#0a0e27", 
                        fg="#2196f3",
                        font=("Arial", 22, "bold"))
        title.pack(pady=(50, 20))
        
        # Subtitle
        subtitle = tk.Label(self.splash, 
                          text="Financial Sentiment Analysis Desktop App", 
                          bg="#0a0e27", 
                          fg="#ffffff",
                          font=("Arial", 14))
        subtitle.pack(pady=(0, 30))
        
        # Features
        features = [
            "📊 FinBERT Sentiment Analysis",
            "💬 Financial Market Insights", 
            "� Investment Guidance",
            "🎯 Real-time Analysis"
        ]
        
        for feature in features:
            feature_label = tk.Label(self.splash, 
                                   text=feature, 
                                   bg="#0a0e27", 
                                   fg="#4caf50",
                                   font=("Arial", 12))
            feature_label.pack(pady=5)
        
        # Loading message
        loading = tk.Label(self.splash, 
                         text="Loading application...", 
                         bg="#0a0e27", 
                         fg="#ff9800",
                         font=("Arial", 11, "italic"))
        loading.pack(pady=(30, 0))
    
    def close_splash(self):
        """Close splash screen and start main app"""
        self.splash.destroy()
        
        # Start main application
        root = tk.Tk()
        app = FinBERTChatbotDesktop(root)
        root.mainloop()

def main():
    """Main function to start the application"""
    try:
        # Show splash screen first
        splash = SplashScreen()
        splash.splash.mainloop()
        
    except Exception as e:
        # If splash fails, start main app directly
        print(f"Splash screen error: {e}")
        root = tk.Tk()
        app = FinBERTChatbotDesktop(root)
        root.mainloop()

if __name__ == "__main__":
    main()
