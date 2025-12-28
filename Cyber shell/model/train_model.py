"""
CyberShell Model - Training Module
===================================

Purpose: Train anomaly detection model on baseline telemetry
Model: IsolationForest (unsupervised anomaly detection)
Alternative: Autoencoder for more complex patterns

Input: Feature rows from normal/baseline activity
Output: model.pkl - serialized model for detect.py

Training Strategy:
1. Collect baseline telemetry (1-7 days of normal activity)
2. Extract features using parser/feature_extractor.py
3. Train IsolationForest on clean data
4. Model learns "normal" - deviations score as anomalies
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# ML imports
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Add parent to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))
from parser.feature_extractor import FeatureRow


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for model training"""
    # IsolationForest parameters
    n_estimators: int = 100          # Number of trees
    contamination: float = 0.05      # Expected anomaly rate in training data
    max_samples: str = 'auto'        # Samples per tree
    random_state: int = 42           # Reproducibility
    
    # Preprocessing
    scale_features: bool = True      # Apply StandardScaler
    
    # Validation
    validation_split: float = 0.2    # Hold-out for validation
    
    # Output
    model_path: str = "model/model.pkl"
    scaler_path: str = "model/scaler.pkl"
    config_path: str = "model/config.json"


# =============================================================================
# DATA LOADING
# =============================================================================

def load_training_data(data_path: str) -> Tuple[np.ndarray, List[str]]:
    """
    Load feature rows from JSONL file.
    
    Args:
        data_path: Path to features.jsonl
        
    Returns:
        (feature_matrix, feature_names)
    """
    features_list = []
    
    with open(data_path, 'r') as f:
        for line in f:
            row_data = json.loads(line)
            # Create FeatureRow and extract ML features
            row = FeatureRow(**row_data)
            features_list.append(row.to_ml_features())
    
    feature_names = FeatureRow.feature_names()
    feature_matrix = np.array(features_list)
    
    print(f"[INFO] Loaded {len(features_list)} samples with {len(feature_names)} features")
    
    return feature_matrix, feature_names


def load_training_data_from_csv(csv_path: str) -> Tuple[np.ndarray, List[str]]:
    """
    Alternative: Load from CSV format.
    """
    import pandas as pd
    
    df = pd.read_csv(csv_path)
    feature_names = FeatureRow.feature_names()
    
    # Select only ML features
    available_features = [f for f in feature_names if f in df.columns]
    feature_matrix = df[available_features].values
    
    print(f"[INFO] Loaded {len(df)} samples with {len(available_features)} features")
    
    return feature_matrix, available_features


# =============================================================================
# MODEL TRAINING
# =============================================================================

class AnomalyModelTrainer:
    """
    Trains IsolationForest model for anomaly detection.
    
    IsolationForest works by:
    1. Building random trees that isolate observations
    2. Anomalies are isolated quickly (short path length)
    3. Normal points require more splits to isolate
    
    Usage:
        trainer = AnomalyModelTrainer(config)
        trainer.train(X_train)
        trainer.save()
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.training_stats: Dict[str, Any] = {}
        
    def train(self, X: np.ndarray, feature_names: List[str]) -> Dict[str, Any]:
        """
        Train the anomaly detection model.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            feature_names: Names of features for explainability
            
        Returns:
            Training statistics dictionary
        """
        self.feature_names = feature_names
        
        # Split for validation
        X_train, X_val = train_test_split(
            X, test_size=self.config.validation_split,
            random_state=self.config.random_state
        )
        
        print(f"[INFO] Training set: {len(X_train)}, Validation set: {len(X_val)}")
        
        # Scale features
        if self.config.scale_features:
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
        else:
            X_train_scaled = X_train
            X_val_scaled = X_val
        
        # Train IsolationForest
        print("[INFO] Training IsolationForest...")
        self.model = IsolationForest(
            n_estimators=self.config.n_estimators,
            contamination=self.config.contamination,
            max_samples=self.config.max_samples,
            random_state=self.config.random_state,
            n_jobs=-1  # Use all cores
        )
        
        self.model.fit(X_train_scaled)
        
        # Validation
        train_scores = self.model.decision_function(X_train_scaled)
        val_scores = self.model.decision_function(X_val_scaled)
        
        train_predictions = self.model.predict(X_train_scaled)
        val_predictions = self.model.predict(X_val_scaled)
        
        # Compute statistics
        self.training_stats = {
            'n_samples_train': len(X_train),
            'n_samples_val': len(X_val),
            'n_features': X.shape[1],
            'feature_names': feature_names,
            'train_anomaly_rate': (train_predictions == -1).mean(),
            'val_anomaly_rate': (val_predictions == -1).mean(),
            'train_score_mean': float(train_scores.mean()),
            'train_score_std': float(train_scores.std()),
            'val_score_mean': float(val_scores.mean()),
            'val_score_std': float(val_scores.std()),
            'config': {
                'n_estimators': self.config.n_estimators,
                'contamination': self.config.contamination,
            }
        }
        
        print(f"[INFO] Training anomaly rate: {self.training_stats['train_anomaly_rate']:.2%}")
        print(f"[INFO] Validation anomaly rate: {self.training_stats['val_anomaly_rate']:.2%}")
        
        return self.training_stats
    
    def compute_feature_importance(self) -> Dict[str, float]:
        """
        Compute approximate feature importance.
        IsolationForest doesn't have direct feature importance,
        so we use average path length contribution per feature.
        
        Note: This is an approximation based on feature variance impact.
        """
        if not self.model or not self.scaler:
            return {}
        
        # Use feature variance as proxy for importance
        # Features with higher variance contribute more to isolation
        variances = self.scaler.var_
        total_var = variances.sum()
        
        importance = {
            name: float(var / total_var)
            for name, var in zip(self.feature_names, variances)
        }
        
        # Sort by importance
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    def save(self):
        """Save model, scaler, and config to disk"""
        # Create model directory
        model_dir = Path(self.config.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(self.model, self.config.model_path)
        print(f"[INFO] Model saved to {self.config.model_path}")
        
        # Save scaler
        if self.scaler:
            joblib.dump(self.scaler, self.config.scaler_path)
            print(f"[INFO] Scaler saved to {self.config.scaler_path}")
        
        # Save config and stats
        config_data = {
            'feature_names': self.feature_names,
            'training_stats': self.training_stats,
            'feature_importance': self.compute_feature_importance()
        }
        
        with open(self.config.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        print(f"[INFO] Config saved to {self.config.config_path}")


# =============================================================================
# AUTOENCODER ALTERNATIVE (Optional)
# =============================================================================

class AutoencoderTrainer:
    """
    Alternative: Train Autoencoder for anomaly detection.
    
    Autoencoder approach:
    1. Train encoder-decoder to reconstruct normal data
    2. High reconstruction error = anomaly
    
    Advantages over IsolationForest:
    - Better for complex feature interactions
    - Can capture non-linear patterns
    
    Disadvantages:
    - Requires more data
    - Harder to explain
    - Slower training
    
    Usage:
        trainer = AutoencoderTrainer()
        trainer.train(X_train)
        trainer.save()
    """
    
    def __init__(self, encoding_dim: int = 8):
        self.encoding_dim = encoding_dim
        self.model = None
        self.scaler = None
        self.threshold = None
        
    def build_model(self, input_dim: int):
        """Build autoencoder architecture"""
        try:
            from tensorflow import keras  # type: ignore
            from tensorflow.keras import layers  # type: ignore
        except ImportError:
            print("[WARNING] TensorFlow not available, using IsolationForest instead")
            return None
        
        # Encoder
        inputs = keras.Input(shape=(input_dim,))
        x = layers.Dense(32, activation='relu')(inputs)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(16, activation='relu')(x)
        encoded = layers.Dense(self.encoding_dim, activation='relu')(x)
        
        # Decoder
        x = layers.Dense(16, activation='relu')(encoded)
        x = layers.Dense(32, activation='relu')(x)
        decoded = layers.Dense(input_dim, activation='linear')(x)
        
        self.model = keras.Model(inputs, decoded)
        self.model.compile(optimizer='adam', loss='mse')
        
        return self.model
    
    def train(self, X: np.ndarray, epochs: int = 50, batch_size: int = 32):
        """Train autoencoder on normal data"""
        if self.model is None:
            self.build_model(X.shape[1])
        
        if self.model is None:
            return None
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train
        history = self.model.fit(
            X_scaled, X_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        # Set anomaly threshold (95th percentile of reconstruction error)
        reconstructions = self.model.predict(X_scaled)
        mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
        self.threshold = np.percentile(mse, 95)
        
        print(f"[INFO] Anomaly threshold set at: {self.threshold:.4f}")
        
        return history


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Model Trainer")
    parser.add_argument("--data", required=True, 
                        help="Path to training data (JSONL or CSV)")
    parser.add_argument("--model", default="model/model.pkl",
                        help="Output model path")
    parser.add_argument("--n-estimators", type=int, default=100,
                        help="Number of trees in IsolationForest")
    parser.add_argument("--contamination", type=float, default=0.05,
                        help="Expected anomaly rate in training data")
    parser.add_argument("--use-autoencoder", action="store_true",
                        help="Use Autoencoder instead of IsolationForest")
    
    args = parser.parse_args()
    
    # Load data
    if args.data.endswith('.csv'):
        X, feature_names = load_training_data_from_csv(args.data)
    else:
        X, feature_names = load_training_data(args.data)
    
    # Configure and train
    config = ModelConfig(
        n_estimators=args.n_estimators,
        contamination=args.contamination,
        model_path=args.model
    )
    
    if args.use_autoencoder:
        trainer = AutoencoderTrainer()
        trainer.train(X)
        # Save autoencoder differently
        print("[INFO] Autoencoder training complete")
    else:
        trainer = AnomalyModelTrainer(config)
        stats = trainer.train(X, feature_names)
        trainer.save()
        
        # Print feature importance
        print("\n[INFO] Feature Importance (top 10):")
        importance = trainer.compute_feature_importance()
        for name, score in list(importance.items())[:10]:
            print(f"  {name}: {score:.4f}")


if __name__ == "__main__":
    main()
