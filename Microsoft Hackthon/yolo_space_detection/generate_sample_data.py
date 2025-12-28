#!/usr/bin/env python3
"""
Sample Data Generator for YOLOv8 Space Detection
Creates realistic synthetic training data for immediate testing
"""

import cv2
import numpy as np
import random
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpaceSampleDataGenerator:
    def __init__(self):
        self.train_dir = Path('data/train')
        self.val_dir = Path('data/val')
        self.class_names = ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher']
        
        # Ensure directories exist
        for split in ['train', 'val']:
            (Path('data') / split / 'images').mkdir(parents=True, exist_ok=True)
            (Path('data') / split / 'labels').mkdir(parents=True, exist_ok=True)

    def create_space_background(self, size=(640, 640)):
        """Create realistic space station background"""
        img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        
        # Dark space background with blue tint
        img[:] = [15, 20, 35]
        
        # Add stars
        for _ in range(random.randint(30, 80)):
            x = random.randint(0, size[0]-1)
            y = random.randint(0, size[1]-1)
            brightness = random.randint(180, 255)
            cv2.circle(img, (x, y), random.randint(1, 2), (brightness, brightness, brightness), -1)
        
        # Add space station structure
        self.add_station_structure(img, size)
        
        # Add lighting effects
        self.add_lighting_effects(img, size)
        
        return img

    def add_station_structure(self, img, size):
        """Add space station structural elements"""
        h, w = size[1], size[0]
        
        # Main hull (horizontal structure)
        hull_color = (80, 90, 110)
        cv2.rectangle(img, (50, h//3), (w-50, 2*h//3), hull_color, -1)
        
        # Solar panels
        panel_color = (40, 60, 120)
        cv2.rectangle(img, (20, h//2-30), (80, h//2+30), panel_color, -1)
        cv2.rectangle(img, (w-80, h//2-30), (w-20, h//2+30), panel_color, -1)
        
        # Add panel grid lines
        for i in range(3):
            y = h//2-20 + i*13
            cv2.line(img, (20, y), (80, y), (60, 80, 140), 1)
            cv2.line(img, (w-80, y), (w-20, y), (60, 80, 140), 1)
        
        # Docking ports
        cv2.circle(img, (w//4, h//2), 25, (100, 120, 140), -1)
        cv2.circle(img, (3*w//4, h//2), 25, (100, 120, 140), -1)
        
        # Windows/viewports
        for i in range(3):
            x = w//3 + i * 80
            cv2.rectangle(img, (x, h//2-10), (x+15, h//2+10), (200, 220, 255), -1)

    def add_lighting_effects(self, img, size):
        """Add realistic space lighting"""
        h, w = size[1], size[0]
        
        # Create lighting gradient (simulating sun direction)
        overlay = np.zeros_like(img)
        
        # Bright side (left)
        for x in range(w//3):
            intensity = int(30 * (1 - x/(w//3)))
            overlay[:, x] = [intensity, intensity, intensity//2]
        
        # Shadow side (right)
        for x in range(2*w//3, w):
            intensity = int(-20 * (x - 2*w//3)/(w//3))
            overlay[:, x] = [intensity, intensity, intensity]
        
        # Blend lighting
        img = cv2.addWeighted(img, 1.0, overlay, 0.3, 0)
        
        return img

    def create_object(self, obj_type, size_range=(40, 120)):
        """Create a specific object type"""
        width = random.randint(*size_range)
        height = random.randint(int(width*0.8), int(width*1.5))
        
        # Object colors based on type
        colors = {
            0: [(180, 100, 50), (220, 140, 80)],    # Toolbox - metallic blue/gray
            1: [(50, 180, 50), (80, 220, 80)],      # Oxygen Tank - green
            2: [(50, 50, 200), (80, 80, 255)]       # Fire Extinguisher - red
        }
        
        base_color, highlight_color = colors[obj_type]
        
        # Create object image
        obj_img = np.zeros((height, width, 3), dtype=np.uint8)
        obj_img[:] = base_color
        
        # Add highlights and shadows for 3D effect
        # Highlight (top-left)
        cv2.rectangle(obj_img, (0, 0), (width//3, height//3), highlight_color, -1)
        
        # Shadow (bottom-right)
        shadow_color = tuple(int(c * 0.6) for c in base_color)
        cv2.rectangle(obj_img, (2*width//3, 2*height//3), (width, height), shadow_color, -1)
        
        # Add object-specific details
        if obj_type == 0:  # Toolbox
            # Handle
            cv2.rectangle(obj_img, (width//4, height//8), (3*width//4, height//4), (200, 200, 200), 2)
            # Latch
            cv2.rectangle(obj_img, (width//2-5, height//2), (width//2+5, height//2+10), (150, 150, 150), -1)
        
        elif obj_type == 1:  # Oxygen Tank
            # Valve on top
            cv2.rectangle(obj_img, (width//2-8, 0), (width//2+8, height//6), (120, 120, 120), -1)
            # Pressure gauge
            cv2.circle(obj_img, (width//2, height//3), width//8, (200, 200, 200), 2)
        
        elif obj_type == 2:  # Fire Extinguisher
            # Nozzle
            cv2.rectangle(obj_img, (width//4, 0), (width//4+10, height//4), (100, 100, 100), -1)
            # Label area
            cv2.rectangle(obj_img, (width//6, height//3), (5*width//6, 2*height//3), (255, 255, 255), -1)
            cv2.putText(obj_img, 'FIRE', (width//4, height//2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
        
        return obj_img

    def place_objects_in_scene(self, background, num_objects=None):
        """Place random objects in the scene"""
        if num_objects is None:
            num_objects = random.randint(1, 4)
        
        h, w = background.shape[:2]
        objects_info = []
        
        # Available placement areas (avoid edges and existing structures)
        safe_zones = [
            (100, 150, w-200, h//3-50),     # Upper area
            (150, 2*h//3+50, w-300, h-100), # Lower area
            (w//2-100, h//3+50, w//2+100, 2*h//3-50), # Center area
        ]
        
        for _ in range(num_objects):
            # Random object type
            obj_type = random.randint(0, 2)
            
            # Create object
            obj_size = random.randint(60, 150)
            obj_img = self.create_object(obj_type, (obj_size, obj_size))
            obj_h, obj_w = obj_img.shape[:2]
            
            # Find placement position
            attempts = 0
            placed = False
            
            while attempts < 20 and not placed:
                # Choose random safe zone
                zone = random.choice(safe_zones)
                x1, y1, x2, y2 = zone
                
                if x2 - x1 > obj_w and y2 - y1 > obj_h:
                    x = random.randint(x1, x2 - obj_w)
                    y = random.randint(y1, y2 - obj_h)
                    
                    # Check for overlap with existing objects
                    overlap = False
                    for existing in objects_info:
                        ex_x, ex_y, ex_w, ex_h = existing['bbox_pixel']
                        if not (x + obj_w < ex_x or x > ex_x + ex_w or 
                               y + obj_h < ex_y or y > ex_y + ex_h):
                            overlap = True
                            break
                    
                    if not overlap:
                        # Place object
                        background[y:y+obj_h, x:x+obj_w] = obj_img
                        
                        # Calculate YOLO format bbox (normalized)
                        x_center = (x + obj_w/2) / w
                        y_center = (y + obj_h/2) / h
                        bbox_w = obj_w / w
                        bbox_h = obj_h / h
                        
                        objects_info.append({
                            'class': obj_type,
                            'bbox_yolo': (x_center, y_center, bbox_w, bbox_h),
                            'bbox_pixel': (x, y, obj_w, obj_h)
                        })
                        
                        placed = True
                
                attempts += 1
        
        return background, objects_info

    def add_realistic_effects(self, img):
        """Add realistic space environment effects"""
        # Add slight noise
        noise = np.random.normal(0, 8, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Add slight blur to simulate camera focus
        if random.random() < 0.3:
            img = cv2.GaussianBlur(img, (3, 3), 0.5)
        
        # Adjust contrast randomly
        alpha = random.uniform(0.8, 1.2)
        beta = random.randint(-10, 10)
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        
        return img

    def generate_sample_dataset(self, num_train=100, num_val=30):
        """Generate complete sample dataset"""
        logger.info(f"🎨 Generating sample dataset: {num_train} train, {num_val} val images")
        
        # Generate training data
        logger.info("📸 Creating training samples...")
        for i in range(num_train):
            # Create background
            background = self.create_space_background((640, 640))
            
            # Add objects
            img, objects = self.place_objects_in_scene(background)
            
            # Add realistic effects
            img = self.add_realistic_effects(img)
            
            # Save image
            img_path = self.train_dir / 'images' / f'train_{i:04d}.jpg'
            cv2.imwrite(str(img_path), img)
            
            # Save labels
            label_path = self.train_dir / 'labels' / f'train_{i:04d}.txt'
            with open(label_path, 'w') as f:
                for obj in objects:
                    class_id = obj['class']
                    x_center, y_center, width, height = obj['bbox_yolo']
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            
            if (i + 1) % 20 == 0:
                logger.info(f"  Created {i + 1}/{num_train} training samples")
        
        # Generate validation data
        logger.info("📸 Creating validation samples...")
        for i in range(num_val):
            background = self.create_space_background((640, 640))
            img, objects = self.place_objects_in_scene(background)
            img = self.add_realistic_effects(img)
            
            img_path = self.val_dir / 'images' / f'val_{i:04d}.jpg'
            cv2.imwrite(str(img_path), img)
            
            label_path = self.val_dir / 'labels' / f'val_{i:04d}.txt'
            with open(label_path, 'w') as f:
                for obj in objects:
                    class_id = obj['class']
                    x_center, y_center, width, height = obj['bbox_yolo']
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        # Generate statistics
        train_images = len(list((self.train_dir / 'images').glob('*.jpg')))
        val_images = len(list((self.val_dir / 'images').glob('*.jpg')))
        
        logger.info("✅ Sample dataset generation complete!")
        logger.info(f"📊 Dataset Statistics:")
        logger.info(f"  Training images: {train_images}")
        logger.info(f"  Validation images: {val_images}")
        logger.info(f"  Total images: {train_images + val_images}")
        logger.info(f"  Classes: {len(self.class_names)} ({', '.join(self.class_names)})")
        
        return train_images, val_images

def main():
    """Generate sample dataset"""
    print("🎨 YOLOv8 Space Detection - Sample Data Generator")
    print("=" * 55)
    
    generator = SpaceSampleDataGenerator()
    
    # Ask user for dataset size
    try:
        print("\nDataset size options:")
        print("1. Small (50 train, 15 val) - Quick testing")
        print("2. Medium (100 train, 30 val) - Good for development")
        print("3. Large (200 train, 60 val) - Better training")
        print("4. Custom - Specify your own numbers")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            num_train, num_val = 50, 15
        elif choice == "2":
            num_train, num_val = 100, 30
        elif choice == "3":
            num_train, num_val = 200, 60
        elif choice == "4":
            num_train = int(input("Number of training images: "))
            num_val = int(input("Number of validation images: "))
        else:
            print("Invalid choice, using medium dataset...")
            num_train, num_val = 100, 30
        
        # Generate dataset
        train_count, val_count = generator.generate_sample_dataset(num_train, num_val)
        
        print(f"\n🎉 Dataset generation successful!")
        print(f"📂 Files created in:")
        print(f"  data/train/images/ - {train_count} training images")
        print(f"  data/train/labels/ - {train_count} training labels") 
        print(f"  data/val/images/ - {val_count} validation images")
        print(f"  data/val/labels/ - {val_count} validation labels")
        print(f"\n🚀 Ready for training! Run: python train_max_accuracy.py")
        
    except KeyboardInterrupt:
        print("\n⏹️ Generation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
