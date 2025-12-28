#!/usr/bin/env python3
"""
YOLOv8 Space Detection - Model Evaluation Script
Comprehensive evaluation of trained models with detailed metrics
"""

import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import time
import cv2
from ultralytics import YOLO
import logging
from sklearn.metrics import confusion_matrix, classification_report
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, model_path, data_yaml='data/dataset.yaml'):
        self.model_path = Path(model_path)
        self.data_yaml = data_yaml
        self.model = None
        self.class_names = ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher']
        self.results_dir = Path('results/evaluation')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔍 Model Evaluator initialized")
        logger.info(f"Model: {self.model_path}")
        logger.info(f"Data: {self.data_yaml}")

    def load_model(self):
        """Load the trained model"""
        try:
            if not self.model_path.exists():
                logger.error(f"❌ Model file not found: {self.model_path}")
                return False
            
            self.model = YOLO(str(self.model_path))
            logger.info(f"✅ Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False

    def run_validation(self):
        """Run validation on the test set"""
        logger.info("📊 Running model validation...")
        
        if not self.model:
            logger.error("❌ Model not loaded")
            return None
        
        try:
            # Run validation
            results = self.model.val(
                data=self.data_yaml,
                imgsz=1280,
                conf=0.001,  # Low confidence for comprehensive evaluation
                iou=0.6,
                save_json=True,
                save_hybrid=True,
                plots=True,
                verbose=True
            )
            
            # Extract key metrics
            metrics = {
                'map50': float(results.box.map50),
                'map50_95': float(results.box.map),
                'precision': float(results.box.mp),
                'recall': float(results.box.mr),
                'fitness': float(results.fitness)
            }
            
            # Per-class metrics
            if hasattr(results.box, 'maps'):
                for i, class_name in enumerate(self.class_names):
                    if i < len(results.box.maps):
                        metrics[f'{class_name.lower()}_map50'] = float(results.box.maps[i])
            
            logger.info(f"📈 Validation Results:")
            logger.info(f"  mAP@0.5: {metrics['map50']:.4f} ({metrics['map50']*100:.1f}%)")
            logger.info(f"  mAP@0.5:0.95: {metrics['map50_95']:.4f} ({metrics['map50_95']*100:.1f}%)")
            logger.info(f"  Precision: {metrics['precision']:.4f}")
            logger.info(f"  Recall: {metrics['recall']:.4f}")
            
            return metrics, results
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return None, None

    def speed_benchmark(self, num_runs=100):
        """Benchmark inference speed"""
        logger.info(f"⚡ Running speed benchmark ({num_runs} runs)...")
        
        if not self.model:
            logger.error("❌ Model not loaded")
            return None
        
        # Create test images of different sizes
        test_sizes = [640, 800, 1024, 1280]
        speed_results = {}
        
        for size in test_sizes:
            logger.info(f"  Testing {size}x{size} images...")
            
            # Create dummy image
            test_image = np.random.randint(0, 255, (size, size, 3), dtype=np.uint8)
            
            # Warmup runs
            for _ in range(10):
                _ = self.model(test_image, verbose=False)
            
            # Timed runs
            times = []
            for _ in range(num_runs):
                start_time = time.time()
                _ = self.model(test_image, verbose=False)
                times.append(time.time() - start_time)
            
            # Calculate statistics
            times = np.array(times) * 1000  # Convert to milliseconds
            speed_results[f'{size}x{size}'] = {
                'mean_ms': float(np.mean(times)),
                'std_ms': float(np.std(times)),
                'min_ms': float(np.min(times)),
                'max_ms': float(np.max(times)),
                'fps': float(1000 / np.mean(times))
            }
            
            logger.info(f"    Mean: {np.mean(times):.1f}ms ± {np.std(times):.1f}ms")
            logger.info(f"    FPS: {1000/np.mean(times):.1f}")
        
        return speed_results

    def analyze_predictions(self, test_dir=None):
        """Analyze model predictions in detail"""
        logger.info("🔬 Analyzing model predictions...")
        
        if test_dir is None:
            test_dir = Path('data/val/images')
        else:
            test_dir = Path(test_dir)
        
        if not test_dir.exists():
            logger.error(f"❌ Test directory not found: {test_dir}")
            return None
        
        # Get test images
        test_images = list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.png'))
        
        if not test_images:
            logger.error(f"❌ No test images found in {test_dir}")
            return None
        
        logger.info(f"📸 Found {len(test_images)} test images")
        
        predictions_analysis = {
            'total_images': len(test_images),
            'images_with_detections': 0,
            'total_detections': 0,
            'class_detections': {name: 0 for name in self.class_names},
            'confidence_distribution': [],
            'detection_sizes': [],
            'failed_images': []
        }
        
        # Process each image
        for i, img_path in enumerate(test_images):
            try:
                # Run prediction
                results = self.model(str(img_path), verbose=False)
                
                if results and len(results) > 0:
                    result = results[0]
                    
                    if result.boxes is not None and len(result.boxes) > 0:
                        predictions_analysis['images_with_detections'] += 1
                        
                        for box in result.boxes:
                            # Extract detection info
                            conf = float(box.conf[0])
                            cls = int(box.cls[0])
                            
                            if cls < len(self.class_names):
                                class_name = self.class_names[cls]
                                predictions_analysis['class_detections'][class_name] += 1
                                predictions_analysis['total_detections'] += 1
                                predictions_analysis['confidence_distribution'].append(conf)
                                
                                # Calculate detection size
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                width = x2 - x1
                                height = y2 - y1
                                area = width * height
                                predictions_analysis['detection_sizes'].append(area)
                
                # Progress update
                if (i + 1) % 20 == 0:
                    logger.info(f"  Processed {i + 1}/{len(test_images)} images")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to process {img_path}: {e}")
                predictions_analysis['failed_images'].append(str(img_path))
        
        # Calculate final statistics
        detection_rate = predictions_analysis['images_with_detections'] / predictions_analysis['total_images']
        avg_detections_per_image = predictions_analysis['total_detections'] / predictions_analysis['total_images']
        
        logger.info(f"📊 Prediction Analysis Results:")
        logger.info(f"  Detection rate: {detection_rate:.1%}")
        logger.info(f"  Avg detections per image: {avg_detections_per_image:.2f}")
        logger.info(f"  Total detections: {predictions_analysis['total_detections']}")
        
        for class_name, count in predictions_analysis['class_detections'].items():
            percentage = (count / predictions_analysis['total_detections'] * 100) if predictions_analysis['total_detections'] > 0 else 0
            logger.info(f"  {class_name}: {count} ({percentage:.1f}%)")
        
        return predictions_analysis

    def create_evaluation_plots(self, metrics, speed_results, predictions_analysis):
        """Create comprehensive evaluation plots"""
        logger.info("📊 Creating evaluation plots...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Model Performance Overview
        ax1 = plt.subplot(3, 4, 1)
        performance_metrics = ['mAP@0.5', 'mAP@0.5:0.95', 'Precision', 'Recall']
        performance_values = [metrics['map50'], metrics['map50_95'], 
                            metrics['precision'], metrics['recall']]
        
        bars = ax1.bar(performance_metrics, performance_values, 
                      color=['#2E8B57', '#4169E1', '#FF6347', '#FFD700'])
        ax1.set_title('Model Performance Metrics', fontweight='bold')
        ax1.set_ylabel('Score')
        ax1.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, performance_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Per-Class Performance
        ax2 = plt.subplot(3, 4, 2)
        class_scores = []
        for class_name in self.class_names:
            key = f'{class_name.lower()}_map50'
            if key in metrics:
                class_scores.append(metrics[key])
            else:
                class_scores.append(0)
        
        bars = ax2.bar(self.class_names, class_scores, 
                      color=['#FF4500', '#32CD32', '#1E90FF'])
        ax2.set_title('Per-Class mAP@0.5', fontweight='bold')
        ax2.set_ylabel('mAP@0.5')
        ax2.set_ylim(0, 1)
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        for bar, value in zip(bars, class_scores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Speed Benchmark
        ax3 = plt.subplot(3, 4, 3)
        if speed_results:
            sizes = list(speed_results.keys())
            mean_times = [speed_results[size]['mean_ms'] for size in sizes]
            std_times = [speed_results[size]['std_ms'] for size in sizes]
            
            bars = ax3.bar(sizes, mean_times, yerr=std_times, capsize=5,
                          color='#9370DB', alpha=0.7)
            ax3.set_title('Inference Speed by Image Size', fontweight='bold')
            ax3.set_ylabel('Time (ms)')
            plt.setp(ax3.get_xticklabels(), rotation=45)
            
            for bar, time_val in zip(bars, mean_times):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                        f'{time_val:.1f}ms', ha='center', va='bottom')
        
        # 4. FPS Performance
        ax4 = plt.subplot(3, 4, 4)
        if speed_results:
            fps_values = [speed_results[size]['fps'] for size in sizes]
            bars = ax4.bar(sizes, fps_values, color='#20B2AA', alpha=0.7)
            ax4.set_title('FPS by Image Size', fontweight='bold')
            ax4.set_ylabel('FPS')
            plt.setp(ax4.get_xticklabels(), rotation=45)
            
            for bar, fps in zip(bars, fps_values):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{fps:.1f}', ha='center', va='bottom')
        
        # 5. Detection Distribution
        ax5 = plt.subplot(3, 4, 5)
        if predictions_analysis:
            class_counts = list(predictions_analysis['class_detections'].values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            wedges, texts, autotexts = ax5.pie(class_counts, labels=self.class_names, 
                                              autopct='%1.1f%%', colors=colors)
            ax5.set_title('Detection Distribution', fontweight='bold')
        
        # 6. Confidence Distribution
        ax6 = plt.subplot(3, 4, 6)
        if predictions_analysis and predictions_analysis['confidence_distribution']:
            confidences = predictions_analysis['confidence_distribution']
            ax6.hist(confidences, bins=20, alpha=0.7, color='#FF7F50', edgecolor='black')
            ax6.set_title('Confidence Score Distribution', fontweight='bold')
            ax6.set_xlabel('Confidence')
            ax6.set_ylabel('Frequency')
            ax6.axvline(np.mean(confidences), color='red', linestyle='--', 
                       label=f'Mean: {np.mean(confidences):.3f}')
            ax6.legend()
        
        # 7. Detection Size Distribution
        ax7 = plt.subplot(3, 4, 7)
        if predictions_analysis and predictions_analysis['detection_sizes']:
            sizes = predictions_analysis['detection_sizes']
            ax7.hist(sizes, bins=20, alpha=0.7, color='#98D8C8', edgecolor='black')
            ax7.set_title('Detection Size Distribution', fontweight='bold')
            ax7.set_xlabel('Bounding Box Area (pixels²)')
            ax7.set_ylabel('Frequency')
        
        # 8. Model Summary Stats
        ax8 = plt.subplot(3, 4, 8)
        ax8.axis('off')
        
        summary_text = f"""
Model Evaluation Summary
{'='*25}

Overall Performance:
• mAP@0.5: {metrics['map50']:.1%}
• mAP@0.5:0.95: {metrics['map50_95']:.1%}
• Precision: {metrics['precision']:.1%}
• Recall: {metrics['recall']:.1%}

Speed Performance:
"""
        
        if speed_results and '640x640' in speed_results:
            summary_text += f"• 640x640: {speed_results['640x640']['fps']:.1f} FPS\n"
        if speed_results and '1280x1280' in speed_results:
            summary_text += f"• 1280x1280: {speed_results['1280x1280']['fps']:.1f} FPS\n"
        
        if predictions_analysis:
            summary_text += f"""
Detection Analysis:
• Total detections: {predictions_analysis['total_detections']}
• Detection rate: {predictions_analysis['images_with_detections']/predictions_analysis['total_images']:.1%}
• Avg per image: {predictions_analysis['total_detections']/predictions_analysis['total_images']:.1f}
"""
        
        ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        # 9-12: Individual class performance bars
        for i, class_name in enumerate(self.class_names):
            ax = plt.subplot(3, 4, 9 + i)
            
            if predictions_analysis:
                class_count = predictions_analysis['class_detections'][class_name]
                class_map = class_scores[i] if i < len(class_scores) else 0
                
                metrics_names = ['Detections', 'mAP@0.5']
                metrics_values = [class_count / 10, class_map]  # Normalize detections for display
                
                bars = ax.bar(metrics_names, metrics_values, 
                             color=['#FF6B6B', '#4ECDC4'])
                ax.set_title(f'{class_name} Performance', fontweight='bold')
                ax.set_ylabel('Normalized Score')
                
                for bar, value in zip(bars, [class_count, class_map]):
                    label = str(value) if bar.get_x() < 0.5 else f'{value:.3f}'
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           label, ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        # Save the plot
        plot_path = self.results_dir / 'comprehensive_evaluation.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Evaluation plots saved to: {plot_path}")
        return plot_path

    def save_evaluation_report(self, metrics, speed_results, predictions_analysis):
        """Save comprehensive evaluation report"""
        logger.info("💾 Saving evaluation report...")
        
        # Create comprehensive report
        report = {
            'model_info': {
                'model_path': str(self.model_path),
                'evaluation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'classes': self.class_names
            },
            'performance_metrics': metrics,
            'speed_benchmark': speed_results,
            'prediction_analysis': predictions_analysis,
            'summary': {
                'accuracy_grade': self.get_accuracy_grade(metrics['map50']),
                'speed_grade': self.get_speed_grade(speed_results),
                'overall_grade': self.get_overall_grade(metrics, speed_results)
            }
        }
        
        # Save as JSON
        json_path = self.results_dir / 'evaluation_report.json'
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save as readable text report
        txt_path = self.results_dir / 'evaluation_report.txt'
        with open(txt_path, 'w') as f:
            f.write(self.generate_text_report(report))
        
        logger.info(f"📄 Evaluation report saved:")
        logger.info(f"  JSON: {json_path}")
        logger.info(f"  Text: {txt_path}")
        
        return json_path, txt_path

    def get_accuracy_grade(self, map50):
        """Get accuracy grade based on mAP@0.5"""
        if map50 >= 0.95:
            return 'A+ (Excellent)'
        elif map50 >= 0.90:
            return 'A (Very Good)'
        elif map50 >= 0.85:
            return 'B+ (Good)'
        elif map50 >= 0.80:
            return 'B (Above Average)'
        elif map50 >= 0.70:
            return 'C (Average)'
        else:
            return 'D (Needs Improvement)'

    def get_speed_grade(self, speed_results):
        """Get speed grade based on FPS"""
        if not speed_results or '640x640' not in speed_results:
            return 'Unknown'
        
        fps = speed_results['640x640']['fps']
        if fps >= 60:
            return 'A+ (Real-time+)'
        elif fps >= 30:
            return 'A (Real-time)'
        elif fps >= 20:
            return 'B+ (Good)'
        elif fps >= 10:
            return 'B (Acceptable)'
        elif fps >= 5:
            return 'C (Slow)'
        else:
            return 'D (Very Slow)'

    def get_overall_grade(self, metrics, speed_results):
        """Get overall system grade"""
        accuracy_score = metrics['map50']
        speed_score = speed_results['640x640']['fps'] / 60 if speed_results and '640x640' in speed_results else 0.1
        
        # Weighted score (accuracy 70%, speed 30%)
        overall_score = (accuracy_score * 0.7) + (min(speed_score, 1.0) * 0.3)
        
        if overall_score >= 0.9:
            return 'A+ (Production Ready)'
        elif overall_score >= 0.8:
            return 'A (Excellent)'
        elif overall_score >= 0.7:
            return 'B+ (Good)'
        elif overall_score >= 0.6:
            return 'B (Above Average)'
        elif overall_score >= 0.5:
            return 'C (Average)'
        else:
            return 'D (Needs Work)'

    def generate_text_report(self, report):
        """Generate human-readable text report"""
        text = f"""
YOLOv8 Space Detection - Model Evaluation Report
{'='*55}

Model Information:
  Path: {report['model_info']['model_path']}
  Date: {report['model_info']['evaluation_date']}
  Classes: {', '.join(report['model_info']['classes'])}

Performance Metrics:
  mAP@0.5:     {report['performance_metrics']['map50']:.4f} ({report['performance_metrics']['map50']*100:.1f}%)
  mAP@0.5:0.95: {report['performance_metrics']['map50_95']:.4f} ({report['performance_metrics']['map50_95']*100:.1f}%)
  Precision:   {report['performance_metrics']['precision']:.4f} ({report['performance_metrics']['precision']*100:.1f}%)
  Recall:      {report['performance_metrics']['recall']:.4f} ({report['performance_metrics']['recall']*100:.1f}%)

Per-Class Performance:
"""
        
        for class_name in report['model_info']['classes']:
            key = f'{class_name.lower()}_map50'
            if key in report['performance_metrics']:
                score = report['performance_metrics'][key]
                text += f"  {class_name:15}: {score:.4f} ({score*100:.1f}%)\n"
        
        if report['speed_benchmark']:
            text += f"\nSpeed Benchmark:\n"
            for size, metrics in report['speed_benchmark'].items():
                text += f"  {size:8}: {metrics['mean_ms']:6.1f}ms ± {metrics['std_ms']:4.1f}ms ({metrics['fps']:5.1f} FPS)\n"
        
        if report['prediction_analysis']:
            pa = report['prediction_analysis']
            text += f"""
Prediction Analysis:
  Total images:     {pa['total_images']}
  Images with detections: {pa['images_with_detections']} ({pa['images_with_detections']/pa['total_images']*100:.1f}%)
  Total detections: {pa['total_detections']}
  Avg per image:    {pa['total_detections']/pa['total_images']:.2f}
  
  Class Distribution:
"""
            for class_name, count in pa['class_detections'].items():
                percentage = (count / pa['total_detections'] * 100) if pa['total_detections'] > 0 else 0
                text += f"    {class_name:15}: {count:4d} ({percentage:5.1f}%)\n"
            
            if pa['confidence_distribution']:
                avg_conf = np.mean(pa['confidence_distribution'])
                min_conf = np.min(pa['confidence_distribution'])
                max_conf = np.max(pa['confidence_distribution'])
                text += f"\n  Confidence Statistics:\n"
                text += f"    Average: {avg_conf:.3f}\n"
                text += f"    Range:   {min_conf:.3f} - {max_conf:.3f}\n"
        
        text += f"""
Summary Grades:
  Accuracy:  {report['summary']['accuracy_grade']}
  Speed:     {report['summary']['speed_grade']}
  Overall:   {report['summary']['overall_grade']}

Recommendations:
"""
        
        # Add recommendations based on performance
        map50 = report['performance_metrics']['map50']
        if map50 < 0.8:
            text += "  • Consider training for more epochs or improving data quality\n"
        if map50 < 0.9:
            text += "  • Try different augmentation strategies or hyperparameters\n"
        
        if report['speed_benchmark'] and '640x640' in report['speed_benchmark']:
            fps = report['speed_benchmark']['640x640']['fps']
            if fps < 20:
                text += "  • Consider model optimization or smaller input size for better speed\n"
        
        if report['prediction_analysis']:
            detection_rate = report['prediction_analysis']['images_with_detections'] / report['prediction_analysis']['total_images']
            if detection_rate < 0.5:
                text += "  • Low detection rate - check confidence thresholds or model training\n"
        
        text += f"\nEvaluation completed successfully!\n"
        
        return text

    def run_complete_evaluation(self):
        """Run complete model evaluation pipeline"""
        logger.info("🚀 Starting complete model evaluation...")
        
        # Load model
        if not self.load_model():
            return False
        
        # Run validation
        metrics, val_results = self.run_validation()
        if not metrics:
            logger.error("❌ Validation failed")
            return False
        
        # Run speed benchmark
        speed_results = self.speed_benchmark(num_runs=50)
        
        # Analyze predictions
        predictions_analysis = self.analyze_predictions()
        
        # Create plots
        plot_path = self.create_evaluation_plots(metrics, speed_results, predictions_analysis)
        
        # Save report
        json_path, txt_path = self.save_evaluation_report(metrics, speed_results, predictions_analysis)
        
        # Print final summary
        logger.info("\n" + "="*50)
        logger.info("🎉 EVALUATION COMPLETE!")
        logger.info("="*50)
        logger.info(f"📊 Results saved to: {self.results_dir}")
        logger.info(f"📈 Performance: mAP@0.5 = {metrics['map50']:.1%}")
        
        if speed_results and '640x640' in speed_results:
            logger.info(f"⚡ Speed: {speed_results['640x640']['fps']:.1f} FPS")
        
        logger.info(f"📄 Full report: {txt_path}")
        logger.info(f"📊 Plots: {plot_path}")
        
        return True

def main():
    """Main evaluation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLOv8 Space Detection Model Evaluation')
    parser.add_argument('--model', type=str, default='runs/detect/max_accuracy_v1/weights/best.pt',
                       help='Path to trained model')
    parser.add_argument('--data', type=str, default='data/dataset.yaml',
                       help='Path to dataset configuration')
    parser.add_argument('--speed-runs', type=int, default=100,
                       help='Number of runs for speed benchmark')
    
    args = parser.parse_args()
    
    print("🔍 YOLOv8 Space Detection - Model Evaluation")
    print("=" * 50)
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"❌ Model not found: {args.model}")
        print("Please train a model first or specify correct path.")
        return
    
    # Initialize evaluator
    evaluator = ModelEvaluator(args.model, args.data)
    
    # Run complete evaluation
    success = evaluator.run_complete_evaluation()
    
    if success:
        print("\n✅ Model evaluation completed successfully!")
        print(f"📂 Results available in: {evaluator.results_dir}")
    else:
        print("\n❌ Model evaluation failed!")

if __name__ == "__main__":
    main()
