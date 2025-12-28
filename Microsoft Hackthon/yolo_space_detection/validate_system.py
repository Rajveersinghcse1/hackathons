#!/usr/bin/env python3
"""
YOLOv8 Space Detection - System Validation Script
Checks if everything is properly installed and configured
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemValidator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.all_checks_passed = True
        self.required_packages = [
            'ultralytics', 'torch', 'torchvision', 'cv2', 'PIL', 
            'numpy', 'matplotlib', 'pandas', 'albumentations', 
            'wandb', 'tqdm', 'sklearn', 'yaml'
        ]
        
    def check_python_version(self):
        """Check Python version compatibility"""
        logger.info("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            logger.error(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            self.all_checks_passed = False
            return False
    
    def check_required_packages(self):
        """Check if all required packages are installed"""
        logger.info("📦 Checking required packages...")
        
        missing_packages = []
        
        for package in self.required_packages:
            try:
                if package == 'cv2':
                    importlib.import_module('cv2')
                elif package == 'PIL':
                    importlib.import_module('PIL')
                elif package == 'sklearn':
                    importlib.import_module('sklearn')
                elif package == 'yaml':
                    importlib.import_module('yaml')
                else:
                    importlib.import_module(package)
                
                logger.info(f"✅ {package} - Installed")
            except ImportError:
                logger.error(f"❌ {package} - Missing")
                missing_packages.append(package)
                self.all_checks_passed = False
        
        if missing_packages:
            logger.info(f"💡 To install missing packages: pip install {' '.join(missing_packages)}")
        
        return len(missing_packages) == 0
    
    def check_gpu_setup(self):
        """Check GPU availability and configuration"""
        logger.info("🎮 Checking GPU setup...")
        
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                current_device = torch.cuda.current_device()
                gpu_name = torch.cuda.get_device_name(current_device)
                gpu_memory = torch.cuda.get_device_properties(current_device).total_memory / 1e9
                
                logger.info(f"✅ GPU Available: {gpu_name}")
                logger.info(f"   GPU Memory: {gpu_memory:.1f} GB")
                logger.info(f"   GPU Count: {gpu_count}")
                
                # Test GPU computation
                try:
                    test_tensor = torch.randn(100, 100).cuda()
                    _ = torch.matmul(test_tensor, test_tensor)
                    torch.cuda.synchronize()
                    logger.info("✅ GPU computation test passed")
                    return True
                except Exception as e:
                    logger.error(f"❌ GPU computation test failed: {e}")
                    return False
            else:
                logger.warning("⚠️ No GPU detected - training will be slower on CPU")
                logger.info("💡 For GPU support, install: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
                return False
                
        except ImportError:
            logger.error("❌ PyTorch not installed")
            self.all_checks_passed = False
            return False
    
    def check_project_structure(self):
        """Check if project structure is correct"""
        logger.info("📁 Checking project structure...")
        
        required_files = [
            'train_max_accuracy.py',
            'detection_app.py',
            'monitor_training.py',
            'augment_data.py',
            'optimize_hyperparameters.py',
            'setup.py',
            'generate_sample_data.py',
            'requirements.txt',
            'README.md'
        ]
        
        required_dirs = [
            'data',
            'data/train',
            'data/train/images',
            'data/train/labels',
            'data/val',
            'data/val/images',
            'data/val/labels',
            'runs'
        ]
        
        # Check files
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                logger.error(f"❌ Missing file: {file_path}")
                self.all_checks_passed = False
            else:
                logger.info(f"✅ Found: {file_path}")
        
        # Check directories
        missing_dirs = []
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)
                logger.error(f"❌ Missing directory: {dir_path}")
                self.all_checks_passed = False
            else:
                logger.info(f"✅ Found: {dir_path}/")
        
        return len(missing_files) == 0 and len(missing_dirs) == 0
    
    def check_dataset_configuration(self):
        """Check dataset configuration file"""
        logger.info("⚙️ Checking dataset configuration...")
        
        dataset_yaml = self.project_root / 'data' / 'dataset.yaml'
        
        if not dataset_yaml.exists():
            logger.error("❌ dataset.yaml not found")
            self.all_checks_passed = False
            return False
        
        try:
            import yaml
            with open(dataset_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            required_keys = ['path', 'train', 'val', 'nc', 'names']
            for key in required_keys:
                if key not in config:
                    logger.error(f"❌ Missing key in dataset.yaml: {key}")
                    self.all_checks_passed = False
                    return False
            
            # Check class configuration
            if config['nc'] != len(config['names']):
                logger.error(f"❌ Class count mismatch: nc={config['nc']}, names={len(config['names'])}")
                self.all_checks_passed = False
                return False
            
            logger.info(f"✅ Dataset config valid:")
            logger.info(f"   Classes: {config['nc']} ({', '.join(config['names'])})")
            logger.info(f"   Train path: {config['train']}")
            logger.info(f"   Val path: {config['val']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reading dataset.yaml: {e}")
            self.all_checks_passed = False
            return False
    
    def check_sample_data(self):
        """Check if sample data exists"""
        logger.info("🖼️ Checking sample data...")
        
        train_images = list((self.project_root / 'data' / 'train' / 'images').glob('*.jpg'))
        train_labels = list((self.project_root / 'data' / 'train' / 'labels').glob('*.txt'))
        val_images = list((self.project_root / 'data' / 'val' / 'images').glob('*.jpg'))
        val_labels = list((self.project_root / 'data' / 'val' / 'labels').glob('*.txt'))
        
        logger.info(f"📊 Data Summary:")
        logger.info(f"   Training images: {len(train_images)}")
        logger.info(f"   Training labels: {len(train_labels)}")
        logger.info(f"   Validation images: {len(val_images)}")
        logger.info(f"   Validation labels: {len(val_labels)}")
        
        if len(train_images) == 0:
            logger.warning("⚠️ No training data found")
            logger.info("💡 Run: python generate_sample_data.py")
            return False
        
        if len(train_images) != len(train_labels):
            logger.warning(f"⚠️ Image-label count mismatch in training set")
            return False
        
        if len(val_images) != len(val_labels):
            logger.warning(f"⚠️ Image-label count mismatch in validation set")
            return False
        
        logger.info("✅ Sample data looks good")
        return True
    
    def check_ultralytics_functionality(self):
        """Test basic YOLO functionality"""
        logger.info("🎯 Testing YOLOv8 functionality...")
        
        try:
            from ultralytics import YOLO
            
            # Try to load a pre-trained model
            model = YOLO('yolov8n.pt')  # Download smallest model for testing
            logger.info("✅ YOLO model loading successful")
            
            # Test inference on dummy data
            import numpy as np
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            results = model(dummy_image, verbose=False)
            logger.info("✅ YOLO inference test successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ YOLO functionality test failed: {e}")
            self.all_checks_passed = False
            return False
    
    def run_all_checks(self):
        """Run all validation checks"""
        logger.info("🔍 YOLOv8 Space Detection - System Validation")
        logger.info("=" * 60)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Required Packages", self.check_required_packages),
            ("GPU Setup", self.check_gpu_setup),
            ("Project Structure", self.check_project_structure),
            ("Dataset Configuration", self.check_dataset_configuration),
            ("Sample Data", self.check_sample_data),
            ("YOLOv8 Functionality", self.check_ultralytics_functionality)
        ]
        
        results = {}
        
        for check_name, check_function in checks:
            logger.info(f"\n--- {check_name} ---")
            try:
                results[check_name] = check_function()
            except Exception as e:
                logger.error(f"❌ {check_name} check failed with error: {e}")
                results[check_name] = False
                self.all_checks_passed = False
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("📋 VALIDATION SUMMARY")
        logger.info("=" * 60)
        
        for check_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{status} - {check_name}")
        
        if self.all_checks_passed:
            logger.info("\n🎉 ALL CHECKS PASSED!")
            logger.info("🚀 System is ready for maximum accuracy training!")
            logger.info("\n📝 Next steps:")
            logger.info("1. Generate sample data: python generate_sample_data.py")
            logger.info("2. Start training: python train_max_accuracy.py")
            logger.info("3. Monitor progress: python monitor_training.py")
            logger.info("4. Run detection: python detection_app.py --mode gui")
        else:
            logger.error("\n❌ SOME CHECKS FAILED!")
            logger.info("🔧 Please fix the issues above before proceeding.")
            logger.info("💡 Run: python setup.py for automated setup")
        
        return self.all_checks_passed
    
    def fix_common_issues(self):
        """Attempt to fix common issues automatically"""
        logger.info("🔧 Attempting to fix common issues...")
        
        # Create missing directories
        required_dirs = [
            'data/train/images', 'data/train/labels',
            'data/val/images', 'data/val/labels', 'runs'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created directory: {dir_path}")
        
        # Install missing packages
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True)
            logger.info("✅ Attempted to install missing packages")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Could not install packages automatically: {e}")
        
        logger.info("🔧 Common fixes attempted. Re-run validation to check.")

def main():
    """Main validation function"""
    validator = SystemValidator()
    
    print("🔍 YOLOv8 Space Detection - System Validation")
    print("=" * 50)
    print("This script will check if your system is ready for training.")
    print()
    
    # Check if user wants to fix issues automatically
    try:
        choice = input("Do you want to attempt automatic fixes? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            validator.fix_common_issues()
            print()
    except KeyboardInterrupt:
        print("\nValidation cancelled.")
        return
    
    # Run all validation checks
    success = validator.run_all_checks()
    
    if success:
        print("\n🎉 System validation successful!")
        print("Ready to start training for maximum accuracy!")
    else:
        print("\n❌ System validation failed.")
        print("Please address the issues above.")
    
    return success

if __name__ == "__main__":
    main()
