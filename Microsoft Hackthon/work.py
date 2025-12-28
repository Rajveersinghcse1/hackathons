#!/usr/bin/env python3
"""
YOLOv8 Space Station Object Detection - Quick Launcher
🚀 Maximum Accuracy Detection for Toolbox, Oxygen Tank, Fire Extinguisher
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 YOLOv8 Space Station Object Detection")
    print("🎯 Maximum Accuracy for Space Equipment Detection")
    print("=" * 60)
    
    # Check if yolo_space_detection directory exists
    project_dir = Path("yolo_space_detection")
    
    if not project_dir.exists():
        print("❌ Project directory not found!")
        print("Please run this script from the Microsoft Hackthon folder.")
        return
    
    # Change to project directory
    os.chdir(project_dir)
    
    print("\n🎛️ Choose an option:")
    print("1. 📦 Setup Project (First time)")
    print("2. 🎯 Start Training (Maximum Accuracy)")
    print("3. 📊 Monitor Training Progress")
    print("4. 🔍 Run Detection App (GUI)")
    print("5. 🔄 Data Augmentation")
    print("6. 🧪 Hyperparameter Optimization")
    print("7. 📈 View Results")
    print("8. ℹ️  Help & Documentation")
    
    try:
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting project setup...")
            subprocess.run([sys.executable, "setup.py"], check=True)
        
        elif choice == "2":
            print("\n🎯 Starting maximum accuracy training...")
            subprocess.run([sys.executable, "train_max_accuracy.py"], check=True)
        
        elif choice == "3":
            print("\n📊 Opening training monitor...")
            subprocess.run([sys.executable, "monitor_training.py"], check=True)
        
        elif choice == "4":
            print("\n🔍 Launching detection application...")
            subprocess.run([sys.executable, "detection_app.py", "--mode", "gui"], check=True)
        
        elif choice == "5":
            print("\n🔄 Running data augmentation...")
            subprocess.run([sys.executable, "augment_data.py"], check=True)
        
        elif choice == "6":
            print("\n🧪 Starting hyperparameter optimization...")
            subprocess.run([sys.executable, "optimize_hyperparameters.py"], check=True)
        
        elif choice == "7":
            print("\n📈 Opening results directory...")
            results_dir = Path("runs")
            if results_dir.exists():
                if sys.platform.startswith('win'):
                    os.startfile(str(results_dir))
                elif sys.platform.startswith('darwin'):
                    subprocess.run(["open", str(results_dir)])
                else:
                    subprocess.run(["xdg-open", str(results_dir)])
            else:
                print("❌ No results found. Please run training first.")
        
        elif choice == "8":
            print("\n📚 Opening documentation...")
            readme_path = Path("README.md")
            if readme_path.exists():
                if sys.platform.startswith('win'):
                    os.startfile(str(readme_path))
                else:
                    subprocess.run(["less", str(readme_path)])
            else:
                print("README.md not found")
        
        else:
            print("❌ Invalid choice. Please select 1-8.")
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
