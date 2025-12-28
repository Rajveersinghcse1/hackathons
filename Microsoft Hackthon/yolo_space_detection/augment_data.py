#!/usr/bin/env python3
"""
Advanced Data Augmentation Pipeline for YOLOv8 Space Detection
Creates 10x more training data with intelligent augmentations
"""

import cv2
import numpy as np
import os
import random
from pathlib import Path
import albumentations as A
from albumentations.core.bbox_utils import convert_bbox_to_albumentations, convert_bbox_from_albumentations
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpaceDetectionAugmenter:
    def __init__(self, train_images_dir='data/train/images', train_labels_dir='data/train/labels'):
        self.train_images_dir = Path(train_images_dir)
        self.train_labels_dir = Path(train_labels_dir)
        
        # Create augmented directories
        self.aug_images_dir = self.train_images_dir.parent / 'images_augmented'
        self.aug_labels_dir = self.train_labels_dir.parent / 'labels_augmented'
        
        self.aug_images_dir.mkdir(exist_ok=True)
        self.aug_labels_dir.mkdir(exist_ok=True)
        
        logger.info(f"🔄 Augmentation setup complete")
        logger.info(f"Original images: {self.train_images_dir}")
        logger.info(f"Augmented images: {self.aug_images_dir}")

    def setup_augmentation_pipeline(self):
        """Setup advanced augmentation pipeline optimized for space station objects"""
        
        # Define multiple augmentation pipelines for variety
        self.augmentation_pipelines = {
            'brightness_contrast': A.Compose([
                A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=1.0),
                A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.5),
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])),
            
            'lighting_effects': A.Compose([
                A.RandomShadow(shadow_roi=(0, 0.5, 1, 1), num_shadows_lower=1, num_shadows_upper=2, p=0.7),
                A.RandomSunFlare(flare_roi=(0, 0, 1, 0.5), angle_lower=0, angle_upper=1, p=0.3),
                A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, alpha_coef=0.1, p=0.3),
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])),
            
            'geometric_transforms': A.Compose([
                A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=15, p=0.8),
                A.Perspective(scale=(0.05, 0.1), p=0.3),
                A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])),
            
            'noise_blur': A.Compose([
                A.OneOf([
                    A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
                    A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.5),
                    A.MultiplicativeNoise(multiplier=[0.9, 1.1], p=0.5),
                ], p=0.6),
                A.OneOf([
                    A.Blur(blur_limit=(3, 7), p=0.4),
                    A.MotionBlur(blur_limit=(3, 7), p=0.4),
                    A.GaussianBlur(blur_limit=(3, 7), p=0.4),
                ], p=0.5),
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])),
            
            'color_space': A.Compose([
                A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.8),
                A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=0.5),
                A.ChannelShuffle(p=0.3),
                A.ToGray(p=0.1),
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])),
            
            'space_specific': A.Compose([
                # Space-specific augmentations
                A.RandomBrightness(limit=0.4, p=0.7),  # Varying lighting conditions
                A.Emboss(alpha=(0.2, 0.5), strength=(0.2, 0.7), p=0.3),  # Metallic surfaces
                A.Sharpen(alpha=(0.2, 0.5), lightness=(0.5, 1.0), p=0.4),  # Sharp edges
                A.CoarseDropout(max_holes=8, max_height=32, max_width=32, p=0.3),  # Occlusions
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels'])),
        }
        
        logger.info(f"✅ {len(self.augmentation_pipelines)} augmentation pipelines configured")

    def read_yolo_annotation(self, label_file):
        """Read YOLO format annotation file"""
        bboxes = []
        class_labels = []
        
        if not label_file.exists():
            return bboxes, class_labels
        
        with open(label_file, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:])
                    
                    # YOLO format: x_center, y_center, width, height (normalized)
                    bboxes.append([x_center, y_center, width, height])
                    class_labels.append(class_id)
        
        return bboxes, class_labels

    def write_yolo_annotation(self, label_file, bboxes, class_labels):
        """Write YOLO format annotation file"""
        with open(label_file, 'w') as f:
            for bbox, class_id in zip(bboxes, class_labels):
                x_center, y_center, width, height = bbox
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def augment_single_image(self, image_path, augmentation_name, pipeline):
        """Augment a single image with its annotations"""
        
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            logger.warning(f"⚠️ Could not read image: {image_path}")
            return False
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Read corresponding label file
        label_file = self.train_labels_dir / f"{image_path.stem}.txt"
        bboxes, class_labels = self.read_yolo_annotation(label_file)
        
        try:
            # Apply augmentation
            augmented = pipeline(image=image, bboxes=bboxes, class_labels=class_labels)
            
            aug_image = augmented['image']
            aug_bboxes = augmented['bboxes']
            aug_class_labels = augmented['class_labels']
            
            # Generate output filenames
            aug_image_name = f"{image_path.stem}_{augmentation_name}.jpg"
            aug_label_name = f"{image_path.stem}_{augmentation_name}.txt"
            
            # Save augmented image
            aug_image_bgr = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(self.aug_images_dir / aug_image_name), aug_image_bgr)
            
            # Save augmented labels
            if aug_bboxes:
                self.write_yolo_annotation(
                    self.aug_labels_dir / aug_label_name,
                    aug_bboxes,
                    aug_class_labels
                )
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Augmentation failed for {image_path}: {e}")
            return False

    def create_super_augmented_dataset(self, augmentations_per_image=10):
        """Create extensively augmented dataset"""
        
        logger.info(f"🚀 Starting super augmentation with {augmentations_per_image}x multiplier")
        
        # Setup augmentation pipelines
        self.setup_augmentation_pipeline()
        
        # Get all training images
        image_files = list(self.train_images_dir.glob('*.jpg')) + list(self.train_images_dir.glob('*.png'))
        
        if not image_files:
            logger.error("❌ No training images found!")
            return
        
        logger.info(f"📁 Found {len(image_files)} original images")
        
        total_augmentations = 0
        successful_augmentations = 0
        
        # Process each image
        for img_file in image_files:
            logger.info(f"🔄 Processing: {img_file.name}")
            
            # Create multiple augmented versions
            for i in range(augmentations_per_image):
                # Randomly select an augmentation pipeline
                aug_name = random.choice(list(self.augmentation_pipelines.keys()))
                pipeline = self.augmentation_pipelines[aug_name]
                
                # Add version number to make unique
                unique_aug_name = f"{aug_name}_v{i+1}"
                
                success = self.augment_single_image(img_file, unique_aug_name, pipeline)
                
                total_augmentations += 1
                if success:
                    successful_augmentations += 1
        
        # Update dataset.yaml to include augmented data
        self.update_dataset_config()
        
        # Report results
        success_rate = (successful_augmentations / total_augmentations) * 100
        
        logger.info(f"✅ Augmentation Complete!")
        logger.info(f"📊 Results:")
        logger.info(f"  Original images: {len(image_files)}")
        logger.info(f"  Augmented images: {successful_augmentations}")
        logger.info(f"  Total dataset size: {len(image_files) + successful_augmentations}")
        logger.info(f"  Success rate: {success_rate:.1f}%")
        logger.info(f"  Augmentation factor: {successful_augmentations/len(image_files):.1f}x")

    def update_dataset_config(self):
        """Update dataset.yaml to include augmented data"""
        
        # Copy original images to augmented directory for unified training
        logger.info("🔄 Merging original and augmented datasets...")
        
        # Copy original images
        for img_file in self.train_images_dir.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                import shutil
                shutil.copy2(img_file, self.aug_images_dir / img_file.name)
        
        # Copy original labels
        for label_file in self.train_labels_dir.glob('*.txt'):
            import shutil
            shutil.copy2(label_file, self.aug_labels_dir / label_file.name)
        
        # Update dataset.yaml
        dataset_config = f"""# YOLOv8 Space Station Object Detection Dataset Configuration (Augmented)
path: ./data
train: train/images_augmented
val: val/images

# Number of classes
nc: 3

# Class names
names: ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher']

# Dataset info
augmented: true
augmentation_factor: 10x
original_images: {len(list(self.train_images_dir.glob('*.jpg')))}
total_images: {len(list(self.aug_images_dir.glob('*.jpg')))}
"""
        
        with open('data/dataset_augmented.yaml', 'w') as f:
            f.write(dataset_config)
        
        logger.info("✅ Updated dataset configuration: data/dataset_augmented.yaml")

def main():
    """Main augmentation function"""
    print("🚀 YOLOv8 Space Detection - Advanced Data Augmentation")
    print("=" * 60)
    
    # Initialize augmenter
    augmenter = SpaceDetectionAugmenter()
    
    # Check if original data exists
    if not augmenter.train_images_dir.exists():
        logger.error(f"❌ Training images directory not found: {augmenter.train_images_dir}")
        return
    
    if not augmenter.train_labels_dir.exists():
        logger.error(f"❌ Training labels directory not found: {augmenter.train_labels_dir}")
        return
    
    # Count original images
    original_images = len(list(augmenter.train_images_dir.glob('*.jpg')))
    if original_images == 0:
        logger.warning("⚠️ No training images found. Creating sample data for demonstration...")
        create_sample_training_data()
        original_images = len(list(augmenter.train_images_dir.glob('*.jpg')))
    
    logger.info(f"📁 Found {original_images} original training images")
    
    # Create super augmented dataset
    augmenter.create_super_augmented_dataset(augmentations_per_image=10)
    
    logger.info("🎉 Data augmentation pipeline completed!")
    logger.info("📝 Next steps:")
    logger.info("  1. Review augmented images in data/train/images_augmented/")
    logger.info("  2. Use data/dataset_augmented.yaml for training")
    logger.info("  3. Run: python train_max_accuracy.py")

def create_sample_training_data():
    """Create sample training data for demonstration"""
    logger.info("📝 Creating sample training data...")
    
    import cv2
    import numpy as np
    
    # Create data directories
    Path('data/train/images').mkdir(parents=True, exist_ok=True)
    Path('data/train/labels').mkdir(parents=True, exist_ok=True)
    
    # Create sample images
    for i in range(10):
        # Create a sample space station-like image
        img = np.zeros((640, 640, 3), dtype=np.uint8)
        
        # Add some space-like background
        img[:] = [20, 20, 40]  # Dark space background
        
        # Add some random objects (simulated)
        for _ in range(random.randint(1, 3)):
            x = random.randint(50, 590)
            y = random.randint(50, 590)
            w = random.randint(40, 100)
            h = random.randint(40, 100)
            
            # Random color for object
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            cv2.rectangle(img, (x, y), (x+w, y+h), color, -1)
        
        # Save image
        cv2.imwrite(f'data/train/images/sample_{i:03d}.jpg', img)
        
        # Create corresponding label
        with open(f'data/train/labels/sample_{i:03d}.txt', 'w') as f:
            # Add 1-3 random objects
            for _ in range(random.randint(1, 3)):
                class_id = random.randint(0, 2)  # 0: Toolbox, 1: Oxygen Tank, 2: Fire Extinguisher
                x_center = random.uniform(0.2, 0.8)
                y_center = random.uniform(0.2, 0.8)
                width = random.uniform(0.1, 0.3)
                height = random.uniform(0.1, 0.3)
                
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
    
    logger.info("✅ Sample training data created")

if __name__ == "__main__":
    # Install albumentations if not already installed
    try:
        import albumentations as A
    except ImportError:
        logger.info("📦 Installing albumentations for advanced augmentation...")
        os.system("pip install albumentations")
        import albumentations as A
    
    main()
