#!/usr/bin/env python3
"""
Hyperparameter Optimization for YOLOv8 Space Detection
Automatically finds the best parameters for maximum accuracy
"""

import itertools
import json
import time
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ultralytics import YOLO
import torch
import logging
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLOHyperparameterOptimizer:
    def __init__(self, data_path='data/dataset.yaml', base_model='yolov8x.pt'):
        self.data_path = data_path
        self.base_model = base_model
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.results = []
        
        # Create results directory
        self.results_dir = Path('runs/hyperparameter_tuning')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔬 Initializing Hyperparameter Optimizer")
        logger.info(f"Device: {self.device}")
        logger.info(f"Base model: {self.base_model}")

    def define_parameter_grid(self):
        """Define comprehensive parameter grid for optimization"""
        
        # Core parameters that significantly impact accuracy
        self.param_grid = {
            'learning_rates': [0.0005, 0.001, 0.002, 0.005],
            'batch_sizes': [4, 8, 16, 32],
            'image_sizes': [640, 800, 1024, 1280],
            'optimizers': ['SGD', 'Adam', 'AdamW'],
            'weight_decays': [0.0001, 0.0005, 0.001, 0.005],
            'momentum': [0.9, 0.937, 0.95],
            'box_loss_weights': [7.5, 10.0, 15.0],
            'cls_loss_weights': [0.5, 1.0, 2.0],
            'warmup_epochs': [3, 5, 10],
            'label_smoothing': [0.0, 0.05, 0.1, 0.15]
        }
        
        logger.info(f"📊 Parameter grid defined:")
        for param, values in self.param_grid.items():
            logger.info(f"  {param}: {values}")
        
        # Calculate total combinations
        total_combinations = 1
        for values in self.param_grid.values():
            total_combinations *= len(values)
        
        logger.info(f"🔢 Total possible combinations: {total_combinations}")
        
        return self.param_grid

    def generate_smart_combinations(self, max_trials=50):
        """Generate smart parameter combinations using strategies"""
        
        combinations = []
        
        # Strategy 1: High accuracy focused combinations
        high_accuracy_combos = [
            {
                'lr0': 0.001, 'batch': 8, 'imgsz': 1280, 'optimizer': 'AdamW',
                'weight_decay': 0.0005, 'momentum': 0.937, 'box': 7.5,
                'cls': 0.5, 'warmup_epochs': 5, 'label_smoothing': 0.1
            },
            {
                'lr0': 0.0005, 'batch': 4, 'imgsz': 1024, 'optimizer': 'AdamW',
                'weight_decay': 0.001, 'momentum': 0.9, 'box': 10.0,
                'cls': 1.0, 'warmup_epochs': 10, 'label_smoothing': 0.05
            },
            {
                'lr0': 0.002, 'batch': 16, 'imgsz': 800, 'optimizer': 'Adam',
                'weight_decay': 0.0001, 'momentum': 0.95, 'box': 15.0,
                'cls': 2.0, 'warmup_epochs': 3, 'label_smoothing': 0.15
            }
        ]
        
        # Strategy 2: Speed vs accuracy balance
        balanced_combos = [
            {
                'lr0': 0.001, 'batch': 16, 'imgsz': 640, 'optimizer': 'SGD',
                'weight_decay': 0.0005, 'momentum': 0.937, 'box': 7.5,
                'cls': 1.0, 'warmup_epochs': 5, 'label_smoothing': 0.1
            },
            {
                'lr0': 0.005, 'batch': 32, 'imgsz': 640, 'optimizer': 'Adam',
                'weight_decay': 0.0001, 'momentum': 0.9, 'box': 10.0,
                'cls': 0.5, 'warmup_epochs': 3, 'label_smoothing': 0.0
            }
        ]
        
        # Strategy 3: Random combinations for exploration
        random_combos = []
        import random
        random.seed(42)
        
        for _ in range(max_trials - len(high_accuracy_combos) - len(balanced_combos)):
            combo = {
                'lr0': random.choice(self.param_grid['learning_rates']),
                'batch': random.choice(self.param_grid['batch_sizes']),
                'imgsz': random.choice(self.param_grid['image_sizes']),
                'optimizer': random.choice(self.param_grid['optimizers']),
                'weight_decay': random.choice(self.param_grid['weight_decays']),
                'momentum': random.choice(self.param_grid['momentum']),
                'box': random.choice(self.param_grid['box_loss_weights']),
                'cls': random.choice(self.param_grid['cls_loss_weights']),
                'warmup_epochs': random.choice(self.param_grid['warmup_epochs']),
                'label_smoothing': random.choice(self.param_grid['label_smoothing'])
            }
            random_combos.append(combo)
        
        # Combine all strategies
        combinations = high_accuracy_combos + balanced_combos + random_combos
        
        logger.info(f"🎯 Generated {len(combinations)} smart parameter combinations")
        logger.info(f"  High accuracy focused: {len(high_accuracy_combos)}")
        logger.info(f"  Balanced: {len(balanced_combos)}")
        logger.info(f"  Random exploration: {len(random_combos)}")
        
        return combinations

    def quick_train_and_evaluate(self, params, trial_num, max_epochs=30):
        """Quick training and evaluation for hyperparameter testing"""
        
        logger.info(f"🧪 Trial {trial_num}: Testing parameters...")
        for key, value in params.items():
            logger.info(f"  {key}: {value}")
        
        try:
            # Initialize model
            model = YOLO(self.base_model)
            
            # Training arguments
            train_args = {
                'data': self.data_path,
                'epochs': max_epochs,
                'patience': 10,  # Early stopping
                'device': self.device,
                'verbose': False,
                'plots': False,
                'save': False,
                'project': str(self.results_dir),
                'name': f'trial_{trial_num:03d}',
                'exist_ok': True,
                **params  # Unpack the parameters
            }
            
            # Start training
            start_time = time.time()
            results = model.train(**train_args)
            training_time = time.time() - start_time
            
            # Extract metrics
            if hasattr(results, 'results_dict'):
                metrics = results.results_dict
                map50 = metrics.get('metrics/mAP50(B)', 0)
                map50_95 = metrics.get('metrics/mAP50-95(B)', 0)
                train_loss = metrics.get('train/box_loss', float('inf'))
                val_loss = metrics.get('val/box_loss', float('inf'))
            else:
                map50 = 0
                map50_95 = 0
                train_loss = float('inf')
                val_loss = float('inf')
            
            # Calculate speed (approximate)
            speed_score = max_epochs / training_time  # epochs per second
            
            # Composite score (weighted combination)
            composite_score = (map50 * 0.7) + (map50_95 * 0.2) + (speed_score * 0.1)
            
            result = {
                'trial': trial_num,
                'map50': map50,
                'map50_95': map50_95,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'training_time': training_time,
                'speed_score': speed_score,
                'composite_score': composite_score,
                **params
            }
            
            logger.info(f"✅ Trial {trial_num} completed:")
            logger.info(f"  mAP@0.5: {map50:.4f}")
            logger.info(f"  mAP@0.5:0.95: {map50_95:.4f}")
            logger.info(f"  Training time: {training_time:.1f}s")
            logger.info(f"  Composite score: {composite_score:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Trial {trial_num} failed: {e}")
            
            # Return failed result
            result = {
                'trial': trial_num,
                'map50': 0,
                'map50_95': 0,
                'train_loss': float('inf'),
                'val_loss': float('inf'),
                'training_time': 0,
                'speed_score': 0,
                'composite_score': 0,
                'error': str(e),
                **params
            }
            
            return result

    def optimize_hyperparameters(self, max_trials=20, quick_epochs=30):
        """Run hyperparameter optimization"""
        
        logger.info(f"🚀 Starting hyperparameter optimization")
        logger.info(f"Max trials: {max_trials}")
        logger.info(f"Quick training epochs: {quick_epochs}")
        
        # Generate parameter combinations
        self.define_parameter_grid()
        combinations = self.generate_smart_combinations(max_trials)
        
        # Run optimization trials
        for i, params in enumerate(combinations[:max_trials], 1):
            logger.info(f"🔄 Starting trial {i}/{max_trials}")
            
            result = self.quick_train_and_evaluate(params, i, quick_epochs)
            self.results.append(result)
            
            # Save intermediate results
            self.save_results()
            
            # Print current best
            best_result = max(self.results, key=lambda x: x['composite_score'])
            logger.info(f"🏆 Current best (Trial {best_result['trial']}): "
                       f"mAP@0.5={best_result['map50']:.4f}, "
                       f"Score={best_result['composite_score']:.4f}")
        
        # Analyze and report final results
        self.analyze_results()
        
        return self.get_best_parameters()

    def save_results(self):
        """Save optimization results"""
        
        # Save as CSV
        df = pd.DataFrame(self.results)
        csv_path = self.results_dir / 'optimization_results.csv'
        df.to_csv(csv_path, index=False)
        
        # Save as JSON
        json_path = self.results_dir / 'optimization_results.json'
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"💾 Results saved to {csv_path} and {json_path}")

    def analyze_results(self):
        """Analyze optimization results and create visualizations"""
        
        if not self.results:
            logger.error("❌ No results to analyze")
            return
        
        df = pd.DataFrame(self.results)
        
        logger.info(f"📊 Optimization Analysis:")
        logger.info(f"  Total trials: {len(df)}")
        logger.info(f"  Successful trials: {len(df[df['map50'] > 0])}")
        
        # Best results
        best_map50 = df.loc[df['map50'].idxmax()]
        best_composite = df.loc[df['composite_score'].idxmax()]
        
        logger.info(f"🏆 Best mAP@0.5: {best_map50['map50']:.4f} (Trial {best_map50['trial']})")
        logger.info(f"🏆 Best composite score: {best_composite['composite_score']:.4f} (Trial {best_composite['trial']})")
        
        # Create visualizations
        self.create_optimization_plots(df)
        
        # Parameter correlation analysis
        self.analyze_parameter_correlations(df)

    def create_optimization_plots(self, df):
        """Create optimization visualization plots"""
        
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('YOLOv8 Hyperparameter Optimization Results', fontsize=16, fontweight='bold')
        
        # 1. mAP@0.5 vs Trial
        axes[0, 0].plot(df['trial'], df['map50'], 'bo-', alpha=0.7)
        axes[0, 0].set_title('mAP@0.5 vs Trial')
        axes[0, 0].set_xlabel('Trial')
        axes[0, 0].set_ylabel('mAP@0.5')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Learning Rate vs mAP@0.5
        sns.boxplot(data=df, x='lr0', y='map50', ax=axes[0, 1])
        axes[0, 1].set_title('Learning Rate vs mAP@0.5')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Batch Size vs mAP@0.5
        sns.boxplot(data=df, x='batch', y='map50', ax=axes[0, 2])
        axes[0, 2].set_title('Batch Size vs mAP@0.5')
        
        # 4. Image Size vs mAP@0.5
        sns.boxplot(data=df, x='imgsz', y='map50', ax=axes[1, 0])
        axes[1, 0].set_title('Image Size vs mAP@0.5')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Optimizer vs mAP@0.5
        sns.boxplot(data=df, x='optimizer', y='map50', ax=axes[1, 1])
        axes[1, 1].set_title('Optimizer vs mAP@0.5')
        
        # 6. Composite Score Distribution
        axes[1, 2].hist(df['composite_score'], bins=15, alpha=0.7, color='green')
        axes[1, 2].set_title('Composite Score Distribution')
        axes[1, 2].set_xlabel('Composite Score')
        axes[1, 2].set_ylabel('Frequency')
        
        plt.tight_layout()
        plot_path = self.results_dir / 'optimization_plots.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Optimization plots saved to {plot_path}")

    def analyze_parameter_correlations(self, df):
        """Analyze correlations between parameters and performance"""
        
        # Select numeric columns for correlation
        numeric_cols = ['lr0', 'batch', 'imgsz', 'weight_decay', 'momentum', 
                       'box', 'cls', 'warmup_epochs', 'label_smoothing',
                       'map50', 'map50_95', 'composite_score']
        
        corr_df = df[numeric_cols].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f')
        plt.title('Parameter Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        corr_path = self.results_dir / 'parameter_correlations.png'
        plt.savefig(corr_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Correlation analysis saved to {corr_path}")
        
        # Print top correlations with mAP@0.5
        map50_corrs = corr_df['map50'].abs().sort_values(ascending=False)
        logger.info(f"🔗 Top parameter correlations with mAP@0.5:")
        for param, corr in map50_corrs.items():
            if param != 'map50':
                logger.info(f"  {param}: {corr:.3f}")

    def get_best_parameters(self):
        """Get the best parameters from optimization"""
        
        if not self.results:
            logger.error("❌ No results available")
            return None
        
        # Find best result based on composite score
        best_result = max(self.results, key=lambda x: x['composite_score'])
        
        # Extract parameter names (exclude metrics)
        param_keys = ['lr0', 'batch', 'imgsz', 'optimizer', 'weight_decay', 
                     'momentum', 'box', 'cls', 'warmup_epochs', 'label_smoothing']
        
        best_params = {key: best_result[key] for key in param_keys if key in best_result}
        
        logger.info(f"🏆 Best Parameters (Composite Score: {best_result['composite_score']:.4f}):")
        for key, value in best_params.items():
            logger.info(f"  {key}: {value}")
        
        logger.info(f"📊 Best Performance:")
        logger.info(f"  mAP@0.5: {best_result['map50']:.4f}")
        logger.info(f"  mAP@0.5:0.95: {best_result['map50_95']:.4f}")
        
        return best_params

    def create_optimized_training_config(self, best_params):
        """Create optimized training configuration file"""
        
        config = {
            "model": "yolov8x.pt",
            "data": self.data_path,
            "epochs": 500,  # Full training epochs
            "patience": 100,
            "device": self.device,
            "project": "runs/optimized",
            "name": "best_params_training",
            **best_params
        }
        
        config_path = self.results_dir / 'optimized_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"⚙️ Optimized training config saved to {config_path}")
        
        return config

def main():
    """Main optimization function"""
    print("🔬 YOLOv8 Space Detection - Hyperparameter Optimization")
    print("=" * 70)
    
    # Initialize optimizer
    optimizer = YOLOHyperparameterOptimizer()
    
    # Check if data exists
    if not Path('data/dataset.yaml').exists():
        logger.error("❌ Dataset configuration not found!")
        logger.info("Please run the data preparation script first.")
        return
    
    # Run optimization
    try:
        logger.info("🚀 Starting hyperparameter optimization...")
        
        # Run with 30 trials for comprehensive search
        best_params = optimizer.optimize_hyperparameters(max_trials=30, quick_epochs=25)
        
        if best_params:
            # Create optimized training configuration
            config = optimizer.create_optimized_training_config(best_params)
            
            logger.info("🎉 Hyperparameter optimization completed!")
            logger.info("📋 Next steps:")
            logger.info("  1. Review results in runs/hyperparameter_tuning/")
            logger.info("  2. Use optimized_config.json for final training")
            logger.info("  3. Run final training with best parameters")
            
            # Generate training command
            print("\n" + "="*70)
            print("🚀 RECOMMENDED TRAINING COMMAND:")
            print("="*70)
            print("python train_max_accuracy.py --config runs/hyperparameter_tuning/optimized_config.json")
            print("="*70)
        
    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}")
        raise

if __name__ == "__main__":
    main()
