#!/usr/bin/env python3
"""
YOLOv8 Space Station Object Detection - Maximum Accuracy Training Script
Optimized for detecting Toolbox, Oxygen Tank, and Fire Extinguisher with near 100% accuracy
"""

import torch
import wandb
from ultralytics import YOLO
import os
import time
from pathlib import Path
import yaml
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaxAccuracyYOLOTrainer:
    def __init__(self, data_path='data/dataset.yaml', project_name='space_detection'):
        """Initialize the maximum accuracy YOLO trainer"""
        self.data_path = data_path
        self.project_name = project_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        logger.info(f"🚀 Initializing YOLOv8 Maximum Accuracy Trainer")
        logger.info(f"Device: {self.device}")
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    def setup_wandb(self, run_name="max_accuracy_training"):
        """Setup Weights & Biases for experiment tracking"""
        try:
            wandb.init(
                project=self.project_name,
                name=run_name,
                config={
                    "model": "YOLOv8x",
                    "dataset": "space_station_objects",
                    "classes": ["Toolbox", "Oxygen Tank", "Fire Extinguisher"],
                    "goal": "Maximum Accuracy (>99% mAP@0.5)"
                }
            )
            logger.info("✅ W&B initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ W&B initialization failed: {e}. Continuing without logging.")

    def train_maximum_accuracy(self):
        """Train YOLOv8 with optimized settings for maximum accuracy"""
        
        logger.info("🎯 Starting Maximum Accuracy Training...")
        
        # Initialize model with largest pre-trained weights for maximum accuracy
        model = YOLO('yolov8x.pt')  # Using YOLOv8x for maximum accuracy
        logger.info("✅ YOLOv8x model loaded with pre-trained weights")
        
        # Setup training parameters optimized for maximum accuracy
        train_args = {
            # Dataset configuration
            'data': self.data_path,
            
            # Core settings optimized for maximum accuracy
            'epochs': 300,              # More epochs for better convergence
            'imgsz': 1280,              # Higher resolution for better detail detection
            'batch': 8,                 # Smaller batch size for stability
            
            # Learning rate optimization
            'lr0': 0.001,               # Lower initial learning rate
            'lrf': 0.01,                # Final learning rate factor
            'momentum': 0.937,          # SGD momentum
            'weight_decay': 0.0005,     # L2 regularization
            
            # Advanced optimization
            'optimizer': 'AdamW',       # Better optimizer for fine-tuning
            'cos_lr': True,             # Cosine learning rate scheduler
            'warmup_epochs': 5,         # Warm-up period
            'warmup_momentum': 0.8,     # Warm-up momentum
            'warmup_bias_lr': 0.1,      # Warm-up bias learning rate
            
            # Loss function weights (optimized for accuracy)
            'box': 7.5,                 # Box regression loss weight
            'cls': 0.5,                 # Classification loss weight
            'dfl': 1.5,                 # Distribution focal loss weight
            
            # Data augmentation for robustness
            'hsv_h': 0.015,             # Hue augmentation
            'hsv_s': 0.7,               # Saturation augmentation
            'hsv_v': 0.4,               # Value augmentation
            'degrees': 10.0,            # Rotation degrees
            'translate': 0.1,           # Translation fraction
            'scale': 0.5,               # Scale factor
            'shear': 0.0,               # Shear degrees
            'perspective': 0.001,       # Perspective transformation
            'flipud': 0.0,              # Vertical flip probability
            'fliplr': 0.5,              # Horizontal flip probability
            'mosaic': 1.0,              # Mosaic augmentation probability
            'mixup': 0.15,              # Mixup augmentation probability
            'copy_paste': 0.3,          # Copy-paste augmentation probability
            
            # Training control
            'patience': 50,             # Early stopping patience
            'save_period': 25,          # Save checkpoint every N epochs
            'val': True,                # Validate during training
            
            # Quality assurance
            'plots': True,              # Generate training plots
            'save': True,               # Save training checkpoints
            'save_txt': True,           # Save results as txt
            'save_conf': True,          # Save confidence scores
            'save_crop': True,          # Save cropped predictions
            
            # Hardware optimization
            'device': self.device,
            'workers': 8,               # Number of dataloader workers
            'amp': True,                # Automatic mixed precision
            
            # Project organization
            'project': 'runs/detect',
            'name': 'max_accuracy_v1',
            'exist_ok': True,
            
            # Additional accuracy optimizations
            'label_smoothing': 0.1,     # Label smoothing for better generalization
            'nbs': 64,                  # Nominal batch size for batch norm
            'overlap_mask': True,       # Overlap mask for segmentation
            'mask_ratio': 4,            # Mask downsample ratio
            'dropout': 0.0,             # Dropout rate (0 for maximum accuracy)
            'verbose': True             # Verbose output
        }
        
        logger.info("🔧 Training configuration:")
        for key, value in train_args.items():
            logger.info(f"  {key}: {value}")
        
        # Start training
        start_time = time.time()
        
        try:
            results = model.train(**train_args)
            
            training_time = time.time() - start_time
            logger.info(f"✅ Training completed in {training_time/3600:.2f} hours")
            
            # Log final results
            if hasattr(results, 'results_dict'):
                final_map50 = results.results_dict.get('metrics/mAP50(B)', 0)
                final_map50_95 = results.results_dict.get('metrics/mAP50-95(B)', 0)
                
                logger.info(f"🎯 Final Results:")
                logger.info(f"  mAP@0.5: {final_map50:.4f} ({final_map50*100:.1f}%)")
                logger.info(f"  mAP@0.5:0.95: {final_map50_95:.4f} ({final_map50_95*100:.1f}%)")
                
                if final_map50 > 0.99:
                    logger.info("🏆 SUCCESS: Achieved >99% mAP@0.5!")
                elif final_map50 > 0.95:
                    logger.info("🎉 EXCELLENT: Achieved >95% mAP@0.5!")
                else:
                    logger.info("📈 Good progress. Consider more training or data augmentation.")
            
            return model, results
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise

    def validate_model(self, model_path):
        """Comprehensive model validation"""
        logger.info("📊 Starting comprehensive model validation...")
        
        model = YOLO(model_path)
        
        # Validate on test set
        results = model.val(data=self.data_path, imgsz=1280, conf=0.001, iou=0.6)
        
        # Extract metrics
        map50 = results.box.map50
        map50_95 = results.box.map
        
        logger.info(f"📈 Validation Results:")
        logger.info(f"  Overall mAP@0.5: {map50:.4f} ({map50*100:.1f}%)")
        logger.info(f"  Overall mAP@0.5:0.95: {map50_95:.4f} ({map50_95*100:.1f}%)")
        
        # Per-class results
        class_names = ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher']
        if hasattr(results.box, 'maps'):
            logger.info(f"📋 Per-Class Results:")
            for i, class_name in enumerate(class_names):
                if i < len(results.box.maps):
                    logger.info(f"  {class_name}: {results.box.maps[i]:.4f} ({results.box.maps[i]*100:.1f}%)")
        
        return results

    def speed_test(self, model_path, test_image=None):
        """Test inference speed"""
        logger.info("⚡ Testing inference speed...")
        
        model = YOLO(model_path)
        
        # Create dummy image if no test image provided
        if test_image is None:
            import numpy as np
            test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Warm-up runs
        for _ in range(10):
            _ = model(test_image, verbose=False)
        
        # Speed test
        times = []
        for _ in range(100):
            start = time.time()
            _ = model(test_image, verbose=False)
            times.append(time.time() - start)
        
        avg_time = np.mean(times) * 1000  # Convert to milliseconds
        std_time = np.std(times) * 1000
        
        logger.info(f"⚡ Inference Speed Results:")
        logger.info(f"  Average: {avg_time:.1f}ms ± {std_time:.1f}ms")
        logger.info(f"  FPS: {1000/avg_time:.1f}")
        
        return avg_time

def main():
    """Main training function"""
    print("🚀 YOLOv8 Space Station Object Detection - Maximum Accuracy Training")
    print("=" * 80)
    
    # Initialize trainer
    trainer = MaxAccuracyYOLOTrainer()
    
    # Setup experiment tracking
    trainer.setup_wandb()
    
    # Verify data structure
    data_path = Path('data')
    if not data_path.exists():
        logger.error("❌ Data directory not found! Please prepare your dataset.")
        return
    
    # Check if dataset.yaml exists
    if not (data_path / 'dataset.yaml').exists():
        logger.error("❌ dataset.yaml not found! Please create the configuration file.")
        return
    
    # Check for training images
    train_images = list((data_path / 'train' / 'images').glob('*'))
    val_images = list((data_path / 'val' / 'images').glob('*'))
    
    logger.info(f"📁 Dataset Overview:")
    logger.info(f"  Training images: {len(train_images)}")
    logger.info(f"  Validation images: {len(val_images)}")
    
    if len(train_images) == 0:
        logger.warning("⚠️ No training images found! Please add images to data/train/images/")
        logger.info("📝 For testing, I'll create a sample training setup...")
        
        # Create sample files for demonstration
        create_sample_data()
    
    # Start maximum accuracy training
    try:
        model, results = trainer.train_maximum_accuracy()
        
        # Validate the trained model
        best_model_path = 'runs/detect/max_accuracy_v1/weights/best.pt'
        if Path(best_model_path).exists():
            trainer.validate_model(best_model_path)
            trainer.speed_test(best_model_path)
        
        logger.info("🎉 Training pipeline completed successfully!")
        logger.info(f"📂 Results saved in: runs/detect/max_accuracy_v1/")
        logger.info(f"🏆 Best model: {best_model_path}")
        
    except Exception as e:
        logger.error(f"❌ Training pipeline failed: {e}")
        raise

def create_sample_data():
    """Create sample data structure for demonstration"""
    logger.info("📝 Creating sample data structure...")
    
    # Create sample images (colored rectangles as placeholders)
    import cv2
    import numpy as np
    
    # Sample training images
    for i in range(5):
        # Create colored image
        img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        cv2.imwrite(f'data/train/images/sample_{i}.jpg', img)
        
        # Create corresponding label file
        with open(f'data/train/labels/sample_{i}.txt', 'w') as f:
            # Sample annotations (class_id x_center y_center width height)
            f.write("0 0.5 0.5 0.3 0.4\n")  # Toolbox
            f.write("1 0.2 0.3 0.1 0.2\n")  # Oxygen Tank
    
    # Sample validation images
    for i in range(2):
        img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        cv2.imwrite(f'data/val/images/val_{i}.jpg', img)
        
        with open(f'data/val/labels/val_{i}.txt', 'w') as f:
            f.write("2 0.8 0.7 0.15 0.25\n")  # Fire Extinguisher
    
    logger.info("✅ Sample data created. Replace with your actual dataset for real training.")

if __name__ == "__main__":
    main()
