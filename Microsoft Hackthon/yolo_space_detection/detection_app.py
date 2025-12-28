#!/usr/bin/env python3
"""
YOLOv8 Space Station Object Detection - Inference Application
Real-time detection app for Toolbox, Oxygen Tank, and Fire Extinguisher
"""

import cv2
import numpy as np
import time
import argparse
from pathlib import Path
import json
from ultralytics import YOLO
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpaceDetectionApp:
    def __init__(self, model_path='runs/detect/max_accuracy_v1/weights/best.pt'):
        self.model_path = model_path
        self.model = None
        self.class_names = ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher']
        self.class_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # BGR colors
        
        # Performance tracking
        self.inference_times = []
        self.detection_stats = {name: 0 for name in self.class_names}
        
        logger.info(f"🚀 Space Detection App initialized")
        logger.info(f"Model path: {self.model_path}")

    def load_model(self):
        """Load the trained YOLOv8 model"""
        try:
            if not Path(self.model_path).exists():
                logger.error(f"❌ Model file not found: {self.model_path}")
                return False
            
            self.model = YOLO(self.model_path)
            logger.info(f"✅ Model loaded successfully")
            
            # Test inference speed
            dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            start_time = time.time()
            _ = self.model(dummy_img, verbose=False)
            warmup_time = (time.time() - start_time) * 1000
            
            logger.info(f"⚡ Model warmed up - inference time: {warmup_time:.1f}ms")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False

    def detect_objects(self, image, conf_threshold=0.5, iou_threshold=0.45):
        """Detect objects in an image"""
        
        if self.model is None:
            logger.error("❌ Model not loaded")
            return image, []
        
        start_time = time.time()
        
        # Run inference
        results = self.model(image, conf=conf_threshold, iou=iou_threshold, verbose=False)
        
        inference_time = (time.time() - start_time) * 1000
        self.inference_times.append(inference_time)
        
        # Keep only last 100 times for average calculation
        if len(self.inference_times) > 100:
            self.inference_times = self.inference_times[-100:]
        
        # Process results
        detections = []
        annotated_image = image.copy()
        
        if results and len(results) > 0:
            result = results[0]
            
            if result.boxes is not None:
                boxes = result.boxes.cpu().numpy()
                
                for box in boxes:
                    # Extract box information
                    x1, y1, x2, y2 = box.xyxy[0].astype(int)
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    if class_id < len(self.class_names):
                        class_name = self.class_names[class_id]
                        color = self.class_colors[class_id]
                        
                        # Update detection stats
                        self.detection_stats[class_name] += 1
                        
                        # Add to detections list
                        detections.append({
                            'class': class_name,
                            'confidence': confidence,
                            'bbox': (x1, y1, x2, y2)
                        })
                        
                        # Draw bounding box
                        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
                        
                        # Draw label
                        label = f"{class_name}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        
                        # Background rectangle for label
                        cv2.rectangle(annotated_image, 
                                    (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), 
                                    color, -1)
                        
                        # Label text
                        cv2.putText(annotated_image, label, 
                                  (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                                  (255, 255, 255), 2)
        
        # Add performance info
        avg_inference_time = np.mean(self.inference_times)
        fps = 1000 / avg_inference_time if avg_inference_time > 0 else 0
        
        info_text = f"Inference: {inference_time:.1f}ms | Avg: {avg_inference_time:.1f}ms | FPS: {fps:.1f}"
        cv2.putText(annotated_image, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Add detection count
        detection_text = f"Detections: {len(detections)}"
        cv2.putText(annotated_image, detection_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return annotated_image, detections

    def detect_image(self, image_path, output_path=None, conf_threshold=0.5):
        """Detect objects in a single image"""
        
        logger.info(f"🔍 Processing image: {image_path}")
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            logger.error(f"❌ Could not load image: {image_path}")
            return None
        
        # Run detection
        annotated_image, detections = self.detect_objects(image, conf_threshold)
        
        # Save result if output path provided
        if output_path:
            cv2.imwrite(str(output_path), annotated_image)
            logger.info(f"💾 Result saved to: {output_path}")
        
        # Print detection results
        logger.info(f"📊 Detection Results:")
        if detections:
            for detection in detections:
                logger.info(f"  {detection['class']}: {detection['confidence']:.3f}")
        else:
            logger.info("  No objects detected")
        
        return annotated_image, detections

    def detect_webcam(self, conf_threshold=0.5, camera_id=0):
        """Real-time detection from webcam"""
        
        logger.info(f"📹 Starting webcam detection (Camera {camera_id})")
        
        # Open webcam
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            logger.error(f"❌ Could not open camera {camera_id}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        logger.info("📹 Press 'q' to quit, 's' to save frame, 'r' to reset stats")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.error("❌ Failed to read frame")
                    break
                
                frame_count += 1
                
                # Run detection every frame
                annotated_frame, detections = self.detect_objects(frame, conf_threshold)
                
                # Add frame counter
                cv2.putText(annotated_frame, f"Frame: {frame_count}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Display frame
                cv2.imshow('YOLOv8 Space Detection - Real-time', annotated_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    timestamp = int(time.time())
                    save_path = f"detection_frame_{timestamp}.jpg"
                    cv2.imwrite(save_path, annotated_frame)
                    logger.info(f"💾 Frame saved: {save_path}")
                elif key == ord('r'):
                    # Reset stats
                    self.detection_stats = {name: 0 for name in self.class_names}
                    self.inference_times = []
                    logger.info("📊 Statistics reset")
        
        except KeyboardInterrupt:
            logger.info("⏹️ Webcam detection stopped by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            # Print final statistics
            self.print_session_stats()

    def detect_video(self, video_path, output_path=None, conf_threshold=0.5):
        """Detect objects in a video file"""
        
        logger.info(f"🎬 Processing video: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.error(f"❌ Could not open video: {video_path}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"📹 Video info: {width}x{height}, {fps} fps, {total_frames} frames")
        
        # Setup video writer if output path provided
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Run detection
                annotated_frame, detections = self.detect_objects(frame, conf_threshold)
                
                # Add progress info
                progress = (frame_count / total_frames) * 100
                progress_text = f"Progress: {progress:.1f}% ({frame_count}/{total_frames})"
                cv2.putText(annotated_frame, progress_text, (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Write frame if output video specified
                if out:
                    out.write(annotated_frame)
                
                # Display frame (optional, comment out for faster processing)
                cv2.imshow('Video Processing', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Print progress every 100 frames
                if frame_count % 100 == 0:
                    logger.info(f"📊 Processed {frame_count}/{total_frames} frames ({progress:.1f}%)")
        
        except KeyboardInterrupt:
            logger.info("⏹️ Video processing stopped by user")
        
        finally:
            cap.release()
            if out:
                out.release()
            cv2.destroyAllWindows()
            
            logger.info(f"✅ Video processing completed: {frame_count} frames processed")
            if output_path:
                logger.info(f"💾 Output saved to: {output_path}")

    def print_session_stats(self):
        """Print session statistics"""
        
        avg_inference_time = np.mean(self.inference_times) if self.inference_times else 0
        total_detections = sum(self.detection_stats.values())
        
        logger.info("📊 Session Statistics:")
        logger.info(f"  Total detections: {total_detections}")
        logger.info(f"  Average inference time: {avg_inference_time:.1f}ms")
        logger.info(f"  Average FPS: {1000/avg_inference_time:.1f}" if avg_inference_time > 0 else "  Average FPS: N/A")
        
        logger.info("📋 Detection breakdown:")
        for class_name, count in self.detection_stats.items():
            percentage = (count / total_detections * 100) if total_detections > 0 else 0
            logger.info(f"  {class_name}: {count} ({percentage:.1f}%)")

    def create_gui(self):
        """Create GUI application"""
        
        root = tk.Tk()
        root.title("YOLOv8 Space Station Object Detection")
        root.geometry("1000x700")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Detection Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Confidence threshold
        ttk.Label(control_frame, text="Confidence Threshold:").grid(row=0, column=0, sticky=tk.W)
        conf_var = tk.DoubleVar(value=0.5)
        conf_scale = ttk.Scale(control_frame, from_=0.1, to=0.9, variable=conf_var, orient=tk.HORIZONTAL)
        conf_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        conf_label = ttk.Label(control_frame, text="0.5")
        conf_label.grid(row=0, column=2, padx=(10, 0))
        
        def update_conf_label(value):
            conf_label.config(text=f"{float(value):.2f}")
        
        conf_scale.config(command=update_conf_label)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Select Image", 
                  command=lambda: self.gui_select_image(conf_var.get())).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Select Video", 
                  command=lambda: self.gui_select_video(conf_var.get())).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Start Webcam", 
                  command=lambda: self.gui_start_webcam(conf_var.get())).pack(side=tk.LEFT, padx=(0, 10))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Detection Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Image display
        self.image_label = ttk.Label(results_frame, text="No image loaded")
        self.image_label.pack(pady=10)
        
        # Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=20, width=40, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Initial stats update
        self.update_gui_stats()
        
        # Start GUI
        root.mainloop()

    def gui_select_image(self, conf_threshold):
        """GUI image selection and processing"""
        
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                annotated_image, detections = self.detect_image(file_path, conf_threshold=conf_threshold)
                
                if annotated_image is not None:
                    # Resize image for display
                    height, width = annotated_image.shape[:2]
                    max_size = 400
                    
                    if width > max_size or height > max_size:
                        scale = min(max_size / width, max_size / height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        annotated_image = cv2.resize(annotated_image, (new_width, new_height))
                    
                    # Convert BGR to RGB for Tkinter
                    image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
                    image_pil = Image.fromarray(image_rgb)
                    image_tk = ImageTk.PhotoImage(image_pil)
                    
                    # Update image display
                    self.image_label.configure(image=image_tk, text="")
                    self.image_label.image = image_tk  # Keep a reference
                    
                    # Update stats
                    self.update_gui_stats()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {e}")

    def gui_select_video(self, conf_threshold):
        """GUI video selection and processing"""
        
        file_path = filedialog.askopenfilename(
            title="Select Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        
        if file_path:
            output_path = filedialog.asksaveasfilename(
                title="Save Output Video",
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
            )
            
            if output_path:
                # Run video processing in separate thread
                thread = threading.Thread(
                    target=self.detect_video,
                    args=(file_path, output_path, conf_threshold),
                    daemon=True
                )
                thread.start()

    def gui_start_webcam(self, conf_threshold):
        """GUI webcam detection"""
        
        # Run webcam detection in separate thread
        thread = threading.Thread(
            target=self.detect_webcam,
            args=(conf_threshold,),
            daemon=True
        )
        thread.start()

    def update_gui_stats(self):
        """Update GUI statistics display"""
        
        avg_inference_time = np.mean(self.inference_times) if self.inference_times else 0
        total_detections = sum(self.detection_stats.values())
        
        stats_text = f"""Detection Statistics

Total Detections: {total_detections}
Average Inference Time: {avg_inference_time:.1f}ms
Average FPS: {1000/avg_inference_time:.1f if avg_inference_time > 0 else 'N/A'}

Class Breakdown:
"""
        
        for class_name, count in self.detection_stats.items():
            percentage = (count / total_detections * 100) if total_detections > 0 else 0
            stats_text += f"  {class_name}: {count} ({percentage:.1f}%)\n"
        
        stats_text += f"\nModel Information:
Model Path: {self.model_path}
Classes: {', '.join(self.class_names)}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)

def main():
    """Main application function"""
    parser = argparse.ArgumentParser(description='YOLOv8 Space Station Object Detection')
    parser.add_argument('--model', type=str, default='runs/detect/max_accuracy_v1/weights/best.pt',
                       help='Path to trained model')
    parser.add_argument('--mode', type=str, choices=['image', 'video', 'webcam', 'gui'], 
                       default='gui', help='Detection mode')
    parser.add_argument('--input', type=str, help='Input file path (for image/video mode)')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID for webcam mode')
    
    args = parser.parse_args()
    
    print("🚀 YOLOv8 Space Station Object Detection - Inference App")
    print("=" * 65)
    
    # Initialize app
    app = SpaceDetectionApp(args.model)
    
    # Load model
    if not app.load_model():
        logger.error("❌ Failed to load model. Please check the model path.")
        return
    
    # Run based on mode
    try:
        if args.mode == 'image':
            if not args.input:
                logger.error("❌ Input image path required for image mode")
                return
            app.detect_image(args.input, args.output, args.conf)
        
        elif args.mode == 'video':
            if not args.input:
                logger.error("❌ Input video path required for video mode")
                return
            app.detect_video(args.input, args.output, args.conf)
        
        elif args.mode == 'webcam':
            app.detect_webcam(args.conf, args.camera)
        
        elif args.mode == 'gui':
            app.create_gui()
        
        # Print final statistics
        app.print_session_stats()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")

if __name__ == "__main__":
    main()
