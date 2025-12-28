#!/usr/bin/env python3
"""
Real-time Training Monitor for YOLOv8 Space Detection
Monitors training progress and provides live updates
"""

import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import numpy as np
from datetime import datetime
import json
import logging
import threading
import queue
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLOTrainingMonitor:
    def __init__(self, results_dir='runs/detect/max_accuracy_v1'):
        self.results_dir = Path(results_dir)
        self.results_file = self.results_dir / 'results.csv'
        self.is_monitoring = False
        self.data_queue = queue.Queue()
        
        # Training metrics
        self.epochs = []
        self.map50_values = []
        self.map50_95_values = []
        self.train_losses = []
        self.val_losses = []
        self.timestamps = []
        
        # Best metrics tracking
        self.best_map50 = 0
        self.best_epoch = 0
        self.target_accuracy = 0.99  # 99% target
        
        logger.info(f"📊 Training Monitor initialized")
        logger.info(f"Results directory: {self.results_dir}")

    def check_training_progress(self):
        """Check and parse training progress from results file"""
        
        if not self.results_file.exists():
            return None
        
        try:
            # Read the results CSV
            df = pd.read_csv(self.results_file)
            
            if df.empty:
                return None
            
            # Get the latest row
            latest = df.iloc[-1]
            
            # Extract metrics (handle different column name formats)
            epoch = latest.get('epoch', latest.get('Epoch', 0))
            
            # Try different possible column names for mAP
            map50_cols = ['metrics/mAP50(B)', 'mAP50', 'val/mAP50', 'metrics/mAP50']
            map50_95_cols = ['metrics/mAP50-95(B)', 'mAP50-95', 'val/mAP50-95', 'metrics/mAP50-95']
            train_loss_cols = ['train/box_loss', 'train_loss', 'box_loss']
            val_loss_cols = ['val/box_loss', 'val_loss', 'val/box_loss']
            
            map50 = 0
            for col in map50_cols:
                if col in latest.index:
                    map50 = latest[col]
                    break
            
            map50_95 = 0
            for col in map50_95_cols:
                if col in latest.index:
                    map50_95 = latest[col]
                    break
            
            train_loss = 0
            for col in train_loss_cols:
                if col in latest.index:
                    train_loss = latest[col]
                    break
            
            val_loss = 0
            for col in val_loss_cols:
                if col in latest.index:
                    val_loss = latest[col]
                    break
            
            progress_data = {
                'epoch': int(epoch),
                'map50': float(map50),
                'map50_95': float(map50_95),
                'train_loss': float(train_loss),
                'val_loss': float(val_loss),
                'timestamp': datetime.now()
            }
            
            return progress_data
            
        except Exception as e:
            logger.warning(f"⚠️ Error reading results file: {e}")
            return None

    def update_metrics(self, data):
        """Update internal metrics tracking"""
        
        if data is None:
            return
        
        # Add to tracking lists
        self.epochs.append(data['epoch'])
        self.map50_values.append(data['map50'])
        self.map50_95_values.append(data['map50_95'])
        self.train_losses.append(data['train_loss'])
        self.val_losses.append(data['val_loss'])
        self.timestamps.append(data['timestamp'])
        
        # Update best metrics
        if data['map50'] > self.best_map50:
            self.best_map50 = data['map50']
            self.best_epoch = data['epoch']
        
        # Keep only last 100 points for performance
        if len(self.epochs) > 100:
            self.epochs = self.epochs[-100:]
            self.map50_values = self.map50_values[-100:]
            self.map50_95_values = self.map50_95_values[-100:]
            self.train_losses = self.train_losses[-100:]
            self.val_losses = self.val_losses[-100:]
            self.timestamps = self.timestamps[-100:]

    def print_progress_summary(self, data):
        """Print formatted progress summary"""
        
        if data is None:
            return
        
        # Calculate training speed
        if len(self.timestamps) > 1:
            time_diff = (self.timestamps[-1] - self.timestamps[-2]).total_seconds()
            if time_diff > 0:
                epochs_per_hour = 3600 / time_diff
            else:
                epochs_per_hour = 0
        else:
            epochs_per_hour = 0
        
        # Progress indicators
        accuracy_progress = (data['map50'] / self.target_accuracy) * 100
        accuracy_bar = self.create_progress_bar(accuracy_progress, 50)
        
        # Print formatted summary
        print("\n" + "="*80)
        print(f"🚀 YOLOv8 Space Detection Training - Live Monitor")
        print("="*80)
        print(f"📊 Current Progress:")
        print(f"   Epoch: {data['epoch']:4d} | Time: {data['timestamp'].strftime('%H:%M:%S')}")
        print(f"   Speed: {epochs_per_hour:.1f} epochs/hour")
        print()
        print(f"🎯 Accuracy Metrics:")
        print(f"   mAP@0.5:     {data['map50']:.4f} ({data['map50']*100:.1f}%)")
        print(f"   mAP@0.5:0.95: {data['map50_95']:.4f} ({data['map50_95']*100:.1f}%)")
        print(f"   Progress to 99%: {accuracy_bar} {accuracy_progress:.1f}%")
        print()
        print(f"📉 Loss Values:")
        print(f"   Train Loss: {data['train_loss']:.4f}")
        print(f"   Val Loss:   {data['val_loss']:.4f}")
        print()
        print(f"🏆 Best Results So Far:")
        print(f"   Best mAP@0.5: {self.best_map50:.4f} ({self.best_map50*100:.1f}%) at epoch {self.best_epoch}")
        
        # Achievement notifications
        if data['map50'] > 0.95:
            print(f"🎉 EXCELLENT: >95% accuracy achieved!")
        if data['map50'] > 0.99:
            print(f"🏆 SUCCESS: Target 99% accuracy achieved!")
        
        # ETA calculation
        if data['map50'] < self.target_accuracy and len(self.map50_values) > 5:
            recent_improvement = np.mean(np.diff(self.map50_values[-5:]))
            if recent_improvement > 0:
                epochs_to_target = (self.target_accuracy - data['map50']) / recent_improvement
                eta_hours = epochs_to_target / max(epochs_per_hour, 1)
                print(f"⏰ ETA to 99%: ~{eta_hours:.1f} hours ({epochs_to_target:.0f} epochs)")
        
        print("="*80)

    def create_progress_bar(self, percentage, width=50):
        """Create a text-based progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"

    def create_live_plots(self):
        """Create live matplotlib plots"""
        
        if len(self.epochs) < 2:
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('YOLOv8 Space Detection - Live Training Monitor', fontsize=16, fontweight='bold')
        
        # 1. mAP Progress
        ax1.plot(self.epochs, self.map50_values, 'b-', label='mAP@0.5', linewidth=2)
        ax1.plot(self.epochs, self.map50_95_values, 'r-', label='mAP@0.5:0.95', linewidth=2)
        ax1.axhline(y=0.99, color='g', linestyle='--', alpha=0.7, label='Target (99%)')
        ax1.set_title('Accuracy Progress')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('mAP')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Loss Progress
        ax2.plot(self.epochs, self.train_losses, 'orange', label='Train Loss', linewidth=2)
        ax2.plot(self.epochs, self.val_losses, 'purple', label='Val Loss', linewidth=2)
        ax2.set_title('Loss Progress')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Accuracy Distribution
        if len(self.map50_values) > 10:
            ax3.hist(self.map50_values, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
            ax3.axvline(x=np.mean(self.map50_values), color='red', linestyle='--', 
                       label=f'Mean: {np.mean(self.map50_values):.3f}')
            ax3.set_title('mAP@0.5 Distribution')
            ax3.set_xlabel('mAP@0.5')
            ax3.set_ylabel('Frequency')
            ax3.legend()
        
        # 4. Training Speed
        if len(self.timestamps) > 1:
            time_diffs = [(self.timestamps[i] - self.timestamps[i-1]).total_seconds() 
                         for i in range(1, len(self.timestamps))]
            epochs_per_hour = [3600 / max(td, 1) for td in time_diffs]
            
            ax4.plot(self.epochs[1:], epochs_per_hour, 'green', linewidth=2)
            ax4.set_title('Training Speed')
            ax4.set_xlabel('Epoch')
            ax4.set_ylabel('Epochs per Hour')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = self.results_dir / 'live_monitor.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return plot_path

    def monitor_training_loop(self, update_interval=30):
        """Main monitoring loop"""
        
        logger.info(f"🔄 Starting training monitor loop (update every {update_interval}s)")
        self.is_monitoring = True
        
        last_epoch = -1
        
        while self.is_monitoring:
            try:
                # Check for new progress
                data = self.check_training_progress()
                
                if data and data['epoch'] > last_epoch:
                    # New progress detected
                    self.update_metrics(data)
                    self.print_progress_summary(data)
                    
                    # Create live plots
                    plot_path = self.create_live_plots()
                    if plot_path:
                        logger.info(f"📊 Live plots saved to: {plot_path}")
                    
                    last_epoch = data['epoch']
                    
                    # Check if target achieved
                    if data['map50'] >= self.target_accuracy:
                        logger.info(f"🎯 TARGET ACHIEVED: {data['map50']:.4f} >= {self.target_accuracy}")
                        self.save_achievement_report(data)
                        break
                
                # Wait before next check
                time.sleep(update_interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(5)  # Wait before retrying
        
        self.is_monitoring = False
        logger.info("📊 Training monitoring completed")

    def save_achievement_report(self, final_data):
        """Save achievement report when target is reached"""
        
        report = {
            "achievement": "Target Accuracy Reached",
            "target_accuracy": self.target_accuracy,
            "achieved_accuracy": final_data['map50'],
            "achieved_at_epoch": final_data['epoch'],
            "timestamp": final_data['timestamp'].isoformat(),
            "best_map50": self.best_map50,
            "best_epoch": self.best_epoch,
            "training_summary": {
                "total_epochs_monitored": len(self.epochs),
                "average_map50": np.mean(self.map50_values),
                "final_train_loss": final_data['train_loss'],
                "final_val_loss": final_data['val_loss']
            }
        }
        
        report_path = self.results_dir / 'achievement_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"🏆 Achievement report saved to: {report_path}")

    def create_gui_monitor(self):
        """Create GUI-based real-time monitor"""
        
        root = tk.Tk()
        root.title("YOLOv8 Space Detection - Training Monitor")
        root.geometry("1200x800")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Metrics tab
        metrics_frame = ttk.Frame(notebook)
        notebook.add(metrics_frame, text="Metrics")
        
        # Create matplotlib figure for GUI
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        canvas = FigureCanvasTkAgg(fig, metrics_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status tab
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="Status")
        
        # Status text widget
        status_text = tk.Text(status_frame, wrap=tk.WORD, font=('Consolas', 10))
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=status_text.yview)
        status_text.configure(yscrollcommand=status_scrollbar.set)
        
        status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def update_gui():
            """Update GUI with latest data"""
            data = self.check_training_progress()
            
            if data:
                self.update_metrics(data)
                
                if len(self.epochs) > 1:
                    # Clear previous plots
                    for ax in [ax1, ax2, ax3, ax4]:
                        ax.clear()
                    
                    # Update plots
                    ax1.plot(self.epochs, self.map50_values, 'b-', label='mAP@0.5', linewidth=2)
                    ax1.plot(self.epochs, self.map50_95_values, 'r-', label='mAP@0.5:0.95', linewidth=2)
                    ax1.axhline(y=0.99, color='g', linestyle='--', alpha=0.7, label='Target (99%)')
                    ax1.set_title('Accuracy Progress')
                    ax1.set_xlabel('Epoch')
                    ax1.set_ylabel('mAP')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    ax2.plot(self.epochs, self.train_losses, 'orange', label='Train Loss', linewidth=2)
                    ax2.plot(self.epochs, self.val_losses, 'purple', label='Val Loss', linewidth=2)
                    ax2.set_title('Loss Progress')
                    ax2.set_xlabel('Epoch')
                    ax2.set_ylabel('Loss')
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    
                    # Refresh canvas
                    canvas.draw()
                    
                    # Update status text
                    status_text.delete(1.0, tk.END)
                    status_text.insert(tk.END, f"""YOLOv8 Space Detection Training Status

Current Epoch: {data['epoch']}
Timestamp: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

Accuracy Metrics:
  mAP@0.5: {data['map50']:.4f} ({data['map50']*100:.1f}%)
  mAP@0.5:0.95: {data['map50_95']:.4f} ({data['map50_95']*100:.1f}%)

Loss Values:
  Train Loss: {data['train_loss']:.4f}
  Validation Loss: {data['val_loss']:.4f}

Best Results:
  Best mAP@0.5: {self.best_map50:.4f} ({self.best_map50*100:.1f}%)
  Best Epoch: {self.best_epoch}

Target Progress: {(data['map50']/self.target_accuracy)*100:.1f}% to 99%
""")
            
            # Schedule next update
            root.after(5000, update_gui)  # Update every 5 seconds
        
        # Start GUI updates
        update_gui()
        
        # Start GUI
        root.mainloop()

def main():
    """Main monitoring function"""
    print("📊 YOLOv8 Space Detection - Real-time Training Monitor")
    print("=" * 60)
    
    # Initialize monitor
    monitor = YOLOTrainingMonitor()
    
    # Check if training results exist
    if not monitor.results_file.exists():
        logger.info("⚠️ No training results found yet.")
        logger.info("Starting monitoring mode - waiting for training to begin...")
    
    # Ask user for monitoring mode
    print("\nChoose monitoring mode:")
    print("1. Console Monitor (text-based, lightweight)")
    print("2. GUI Monitor (graphical interface)")
    print("3. Both")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            # Console monitoring
            monitor.monitor_training_loop(update_interval=30)
        elif choice == "2":
            # GUI monitoring
            monitor.create_gui_monitor()
        elif choice == "3":
            # Both - start console monitor in thread, GUI in main
            monitor_thread = threading.Thread(
                target=monitor.monitor_training_loop,
                args=(60,),  # Less frequent updates for background
                daemon=True
            )
            monitor_thread.start()
            monitor.create_gui_monitor()
        else:
            logger.info("Invalid choice, starting console monitor...")
            monitor.monitor_training_loop(update_interval=30)
    
    except KeyboardInterrupt:
        logger.info("⏹️  Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor failed: {e}")

if __name__ == "__main__":
    main()
