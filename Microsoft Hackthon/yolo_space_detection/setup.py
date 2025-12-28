#!/usr/bin/env python3
"""
YOLOv8 Space Detection - Setup and Execution Script
Complete automated setup for maximum accuracy space station object detection
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YOLOSpaceDetectionSetup:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.requirements_installed = False
        self.data_prepared = False
        self.model_trained = False
        
        logger.info("🚀 YOLOv8 Space Detection Setup Initialized")
        logger.info(f"Project directory: {self.project_dir}")

    def install_requirements(self):
        """Install all required packages"""
        
        logger.info("📦 Installing required packages...")
        
        packages = [
            "ultralytics>=8.0.0",
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "opencv-python>=4.5.0",
            "pillow>=9.0.0",
            "numpy>=1.21.0",
            "matplotlib>=3.5.0",
            "pandas>=1.5.0",
            "seaborn>=0.11.0",
            "scikit-learn>=1.0.0",
            "albumentations>=1.3.0",
            "wandb>=0.15.0",
            "tqdm>=4.64.0"
        ]
        
        try:
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True, check=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ {package} installed successfully")
                else:
                    logger.error(f"❌ Failed to install {package}: {result.stderr}")
                    return False
            
            self.requirements_installed = True
            logger.info("✅ All requirements installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            return False

    def verify_gpu_setup(self):
        """Verify GPU setup for optimal performance"""
        
        logger.info("🔍 Verifying GPU setup...")
        
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                current_device = torch.cuda.current_device()
                gpu_name = torch.cuda.get_device_name(current_device)
                gpu_memory = torch.cuda.get_device_properties(current_device).total_memory / 1e9
                
                logger.info(f"✅ GPU Setup Verified:")
                logger.info(f"  Available GPUs: {gpu_count}")
                logger.info(f"  Current GPU: {gpu_name}")
                logger.info(f"  GPU Memory: {gpu_memory:.1f} GB")
                
                # Test GPU performance
                logger.info("🧪 Testing GPU performance...")
                test_tensor = torch.randn(1000, 1000).cuda()
                start_time = time.time()
                _ = torch.matmul(test_tensor, test_tensor)
                torch.cuda.synchronize()
                gpu_test_time = time.time() - start_time
                
                logger.info(f"  GPU Performance Test: {gpu_test_time*1000:.1f}ms")
                
                if gpu_memory < 4.0:
                    logger.warning("⚠️ GPU memory < 4GB. Consider reducing batch size.")
                
                return True
            else:
                logger.warning("⚠️ No GPU detected. Training will use CPU (much slower).")
                logger.info("💡 For best performance, install CUDA-enabled PyTorch:")
                logger.info("   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
                return False
                
        except ImportError:
            logger.error("❌ Could not import PyTorch. Installation may have failed.")
            return False

    def setup_data_structure(self):
        """Setup the complete data structure"""
        
        logger.info("📁 Setting up data structure...")
        
        directories = [
            "data/train/images",
            "data/train/labels",
            "data/val/images", 
            "data/val/labels",
            "data/test/images",
            "data/test/labels",
            "runs/detect",
            "runs/hyperparameter_tuning",
            "runs/final",
            "sample_data",
            "models",
            "results"
        ]
        
        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created: {directory}")
        
        # Create sample training data for demonstration
        self.create_sample_data()
        
        self.data_prepared = True
        logger.info("✅ Data structure setup complete")

    def create_sample_data(self):
        """Create sample data for immediate testing"""
        
        logger.info("📝 Creating sample training data...")
        
        try:
            import cv2
            import numpy as np
            import random
            
            # Sample data parameters
            num_train_samples = 50
            num_val_samples = 15
            image_size = (640, 640)
            
            # Create training samples
            for i in range(num_train_samples):
                # Create synthetic space station image
                img = self.create_synthetic_space_image(image_size)
                
                # Save image
                img_path = self.project_dir / f"data/train/images/sample_{i:03d}.jpg"
                cv2.imwrite(str(img_path), img)
                
                # Create corresponding label
                label_path = self.project_dir / f"data/train/labels/sample_{i:03d}.txt"
                self.create_synthetic_labels(label_path)
            
            # Create validation samples
            for i in range(num_val_samples):
                img = self.create_synthetic_space_image(image_size)
                
                img_path = self.project_dir / f"data/val/images/val_{i:03d}.jpg"
                cv2.imwrite(str(img_path), img)
                
                label_path = self.project_dir / f"data/val/labels/val_{i:03d}.txt"
                self.create_synthetic_labels(label_path)
            
            logger.info(f"✅ Created {num_train_samples} training and {num_val_samples} validation samples")
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample data: {e}")

    def create_synthetic_space_image(self, size=(640, 640)):
        """Create a synthetic space station-like image"""
        
        import cv2
        import numpy as np
        import random
        
        # Create dark space background
        img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        img[:] = [10, 15, 25]  # Dark blue space background
        
        # Add some stars
        for _ in range(random.randint(20, 50)):
            x = random.randint(0, size[0]-1)
            y = random.randint(0, size[1]-1)
            cv2.circle(img, (x, y), 1, (255, 255, 255), -1)
        
        # Add space station structure (rectangular panels)
        structure_color = (100, 120, 140)
        cv2.rectangle(img, (50, 200), (590, 440), structure_color, -1)
        cv2.rectangle(img, (100, 100), (540, 180), structure_color, -1)
        cv2.rectangle(img, (100, 460), (540, 540), structure_color, -1)
        
        # Add some random objects (simulating our target objects)
        self.add_synthetic_objects(img)
        
        # Add some noise and lighting effects
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)
        
        return img

    def add_synthetic_objects(self, img):
        """Add synthetic objects to the image"""
        
        import cv2
        import random
        
        # Object colors (roughly representing our target objects)
        colors = [
            (50, 100, 200),   # Toolbox - reddish
            (200, 200, 50),   # Oxygen Tank - yellowish
            (50, 200, 50)     # Fire Extinguisher - greenish
        ]
        
        # Add 1-4 objects per image
        num_objects = random.randint(1, 4)
        
        for _ in range(num_objects):
            # Random position and size
            x = random.randint(100, 500)
            y = random.randint(150, 450)
            w = random.randint(40, 120)
            h = random.randint(60, 140)
            
            # Random color
            color = random.choice(colors)
            
            # Draw rectangular object
            cv2.rectangle(img, (x, y), (x + w, y + h), color, -1)
            
            # Add some highlights/shadows for realism
            cv2.rectangle(img, (x, y), (x + w//4, y + h), 
                         tuple(int(c * 1.3) for c in color), -1)
            cv2.rectangle(img, (x + 3*w//4, y), (x + w, y + h), 
                         tuple(int(c * 0.7) for c in color), -1)

    def create_synthetic_labels(self, label_path):
        """Create synthetic YOLO format labels"""
        
        import random
        
        with open(label_path, 'w') as f:
            # Add 1-3 random objects
            num_objects = random.randint(1, 3)
            
            for _ in range(num_objects):
                class_id = random.randint(0, 2)  # 0: Toolbox, 1: Oxygen Tank, 2: Fire Extinguisher
                
                # Random but reasonable bounding box
                x_center = random.uniform(0.2, 0.8)
                y_center = random.uniform(0.3, 0.7)
                width = random.uniform(0.1, 0.25)
                height = random.uniform(0.15, 0.3)
                
                # Ensure box stays within image bounds
                x_center = max(width/2, min(1-width/2, x_center))
                y_center = max(height/2, min(1-height/2, y_center))
                
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def run_full_pipeline(self):
        """Run the complete training pipeline"""
        
        logger.info("🚀 Starting Full Maximum Accuracy Pipeline")
        logger.info("=" * 70)
        
        pipeline_steps = [
            ("📦 Installing Requirements", self.install_requirements),
            ("🔧 Verifying GPU Setup", self.verify_gpu_setup),
            ("📁 Setting up Data Structure", self.setup_data_structure),
            ("🔄 Running Data Augmentation", self.run_data_augmentation),
            ("🧪 Optimizing Hyperparameters", self.run_hyperparameter_optimization),
            ("🎯 Training Maximum Accuracy Model", self.run_maximum_accuracy_training),
            ("📊 Evaluating Final Model", self.evaluate_final_model),
            ("🚀 Setting up Inference App", self.setup_inference_app)
        ]
        
        for step_name, step_function in pipeline_steps:
            logger.info(f"\n{step_name}")
            logger.info("-" * 50)
            
            try:
                start_time = time.time()
                success = step_function()
                elapsed_time = time.time() - start_time
                
                if success:
                    logger.info(f"✅ {step_name} completed in {elapsed_time:.1f}s")
                else:
                    logger.error(f"❌ {step_name} failed")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ {step_name} failed with error: {e}")
                return False
        
        logger.info("\n🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        self.print_final_summary()
        
        return True

    def run_data_augmentation(self):
        """Run data augmentation script"""
        
        logger.info("🔄 Running advanced data augmentation...")
        
        try:
            # Install albumentations if not already installed
            subprocess.run([sys.executable, "-m", "pip", "install", "albumentations"], 
                          capture_output=True, check=True)
            
            # Run augmentation script
            result = subprocess.run([
                sys.executable, "augment_data.py"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Data augmentation completed successfully")
                return True
            else:
                logger.error(f"❌ Data augmentation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Data augmentation timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Data augmentation error: {e}")
            return False

    def run_hyperparameter_optimization(self):
        """Run hyperparameter optimization"""
        
        logger.info("🧪 Running hyperparameter optimization...")
        
        try:
            # Run optimization with limited trials for setup
            result = subprocess.run([
                sys.executable, "optimize_hyperparameters.py"
            ], capture_output=True, text=True, timeout=1800)  # 30 minutes timeout
            
            if result.returncode == 0:
                logger.info("✅ Hyperparameter optimization completed")
                return True
            else:
                logger.warning(f"⚠️ Hyperparameter optimization had issues: {result.stderr}")
                logger.info("Continuing with default parameters...")
                return True  # Continue even if optimization fails
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Hyperparameter optimization timed out, using default parameters")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Hyperparameter optimization error: {e}")
            logger.info("Continuing with default parameters...")
            return True

    def run_maximum_accuracy_training(self):
        """Run the maximum accuracy training"""
        
        logger.info("🎯 Starting maximum accuracy training...")
        
        try:
            # Start training with a reasonable number of epochs for setup
            import subprocess
            import sys
            
            # Create a quick training script for setup
            quick_train_script = f'''
import sys
sys.path.append(".")
from train_max_accuracy import MaxAccuracyYOLOTrainer

# Initialize and run quick training
trainer = MaxAccuracyYOLOTrainer()
model, results = trainer.train_maximum_accuracy()
print("Training completed successfully!")
'''
            
            # Write quick training script
            with open("quick_train.py", "w") as f:
                f.write(quick_train_script)
            
            # Run training
            result = subprocess.run([
                sys.executable, "quick_train.py"
            ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
            
            if result.returncode == 0:
                logger.info("✅ Maximum accuracy training completed")
                self.model_trained = True
                return True
            else:
                logger.error(f"❌ Training failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Training timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Training error: {e}")
            return False

    def evaluate_final_model(self):
        """Evaluate the final trained model"""
        
        logger.info("📊 Evaluating final model...")
        
        try:
            # Check if model file exists
            model_path = Path("runs/detect/max_accuracy_v1/weights/best.pt")
            
            if not model_path.exists():
                logger.error(f"❌ Model file not found: {model_path}")
                return False
            
            # Simple evaluation
            from ultralytics import YOLO
            
            model = YOLO(str(model_path))
            results = model.val(data='data/dataset.yaml')
            
            map50 = results.box.map50
            map50_95 = results.box.map
            
            logger.info(f"📈 Final Model Performance:")
            logger.info(f"  mAP@0.5: {map50:.4f} ({map50*100:.1f}%)")
            logger.info(f"  mAP@0.5:0.95: {map50_95:.4f} ({map50_95*100:.1f}%)")
            
            # Save evaluation results
            eval_results = {
                "model_path": str(model_path),
                "map50": float(map50),
                "map50_95": float(map50_95),
                "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open("results/final_evaluation.json", "w") as f:
                json.dump(eval_results, f, indent=2)
            
            logger.info("✅ Model evaluation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return False

    def setup_inference_app(self):
        """Setup the inference application"""
        
        logger.info("🚀 Setting up inference application...")
        
        try:
            # Test if the inference app can be imported and initialized
            exec_script = '''
import sys
sys.path.append(".")
from detection_app import SpaceDetectionApp

app = SpaceDetectionApp()
if app.load_model():
    print("Inference app setup successful!")
else:
    print("Model loading failed")
'''
            
            with open("test_inference.py", "w") as f:
                f.write(exec_script)
            
            result = subprocess.run([
                sys.executable, "test_inference.py"
            ], capture_output=True, text=True, timeout=60)
            
            if "successful" in result.stdout:
                logger.info("✅ Inference application ready")
                return True
            else:
                logger.error(f"❌ Inference app setup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Inference app setup error: {e}")
            return False

    def print_final_summary(self):
        """Print final setup summary"""
        
        summary = f"""
🎉 YOLOv8 Space Detection - Setup Complete!
{'='*60}

✅ Requirements installed: {self.requirements_installed}
✅ Data structure created: {self.data_prepared}  
✅ Model trained: {self.model_trained}

📂 Project Structure:
  data/                  - Training and validation data
  runs/                  - Training results and models
  models/                - Saved models
  results/               - Evaluation results

🚀 Quick Start Commands:
  
  1. Data Augmentation:
     python augment_data.py
     
  2. Hyperparameter Optimization:
     python optimize_hyperparameters.py
     
  3. Maximum Accuracy Training:
     python train_max_accuracy.py
     
  4. Real-time Monitoring:
     python monitor_training.py
     
  5. Inference Application:
     python detection_app.py --mode gui
     
  6. Command Line Detection:
     python detection_app.py --mode image --input path/to/image.jpg

🎯 Expected Performance:
  - Target Accuracy: >95% mAP@0.5
  - Inference Speed: <50ms per image
  - Real-time FPS: >20 FPS

📚 Next Steps:
  1. Replace sample data with your real space station images
  2. Run full training pipeline with your data
  3. Fine-tune hyperparameters for your specific use case
  4. Deploy the inference app for real-time detection

💡 Tips for Maximum Accuracy:
  - Use high-quality, well-annotated training data
  - Ensure balanced representation of all three classes
  - Consider transfer learning from space-domain datasets
  - Monitor training carefully and adjust parameters as needed

🆘 Support:
  - Check logs in each script for detailed information
  - Adjust batch sizes if running out of GPU memory
  - Use CPU training if no GPU is available (slower)

Happy detecting! 🚀
"""
        
        print(summary)
        
        # Save summary to file
        with open("SETUP_SUMMARY.txt", "w") as f:
            f.write(summary)

def main():
    """Main setup function"""
    
    print("🚀 YOLOv8 Space Station Object Detection - Complete Setup")
    print("🎯 Target: >99% Accuracy for Toolbox, Oxygen Tank, Fire Extinguisher Detection")
    print("=" * 80)
    
    setup = YOLOSpaceDetectionSetup()
    
    # Ask user for setup mode
    print("\nSetup Options:")
    print("1. Quick Setup (basic requirements + sample data)")
    print("2. Full Pipeline (complete training pipeline)")
    print("3. Custom Setup (step-by-step)")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            logger.info("🚀 Running Quick Setup...")
            success = (setup.install_requirements() and
                      setup.verify_gpu_setup() and
                      setup.setup_data_structure())
            
            if success:
                logger.info("✅ Quick setup completed!")
                setup.print_final_summary()
            else:
                logger.error("❌ Quick setup failed")
        
        elif choice == "2":
            logger.info("🚀 Running Full Pipeline...")
            success = setup.run_full_pipeline()
            
            if not success:
                logger.error("❌ Full pipeline failed")
        
        elif choice == "3":
            logger.info("🚀 Starting Custom Setup...")
            # Interactive step-by-step setup
            steps = [
                ("Install Requirements", setup.install_requirements),
                ("Verify GPU Setup", setup.verify_gpu_setup),
                ("Setup Data Structure", setup.setup_data_structure),
                ("Run Data Augmentation", setup.run_data_augmentation),
                ("Optimize Hyperparameters", setup.run_hyperparameter_optimization),
                ("Train Maximum Accuracy Model", setup.run_maximum_accuracy_training),
                ("Evaluate Final Model", setup.evaluate_final_model),
                ("Setup Inference App", setup.setup_inference_app)
            ]
            
            for step_name, step_function in steps:
                run_step = input(f"\nRun '{step_name}'? (y/n): ").strip().lower()
                if run_step in ['y', 'yes']:
                    logger.info(f"🔄 Running {step_name}...")
                    success = step_function()
                    if success:
                        logger.info(f"✅ {step_name} completed")
                    else:
                        logger.error(f"❌ {step_name} failed")
                        continue_anyway = input("Continue anyway? (y/n): ").strip().lower()
                        if continue_anyway not in ['y', 'yes']:
                            break
            
            setup.print_final_summary()
        
        else:
            logger.info("Invalid choice. Running quick setup...")
            setup.install_requirements()
            setup.verify_gpu_setup()
            setup.setup_data_structure()
            setup.print_final_summary()
    
    except KeyboardInterrupt:
        logger.info("\n⏹️ Setup interrupted by user")
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    main()
