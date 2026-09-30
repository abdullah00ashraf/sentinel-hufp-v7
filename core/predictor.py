import os
import sys
import joblib
import numpy as np
import pandas as pd

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

class SentinelPredictor:
    """
    Unified Production Predictor for Sentinel V7.0.
    Handles scaling, tensor dynamic reshaping, model inference, and physics nudge.
    """
    FEATURE_NAMES = [
        'elevation', 'river_dist', 'rainfall_mm', 'runoff_mm',
        'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh'
    ]

    def __init__(self, model_path=None, scaler_path=None):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if scaler_path is None:
            scaler_path = os.path.join(self.BASE_DIR, "brain", "scaler.joblib")
        
        if model_path is None:
            # Phase 1 Benchmark Model
            primary = os.path.join(self.BASE_DIR, "brain", "crash_recovery_final.keras")
            fallback = os.path.join(self.BASE_DIR, "brain", "bi_lstm_flood_model.keras")
            model_path = primary if os.path.exists(primary) else fallback

        self.model_path = model_path
        self.scaler_path = scaler_path
        
        # Load scaler
        if os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)
        else:
            self.scaler = None
            print(f"⚠️ Warning: Scaler not found at {self.scaler_path}")

        # Load model
        if os.path.exists(self.model_path):
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            self.in_shape = self.model.input_shape
        else:
            self.model = None
            self.in_shape = None
            print(f"⚠️ Warning: Model not found at {self.model_path}")

    def predict_risk(self, feature_data) -> np.ndarray:
        """
        Calculates calibrated flood risk percentage [0.0%, 100.0%].
        Accepts dict, list of dicts, or pandas DataFrame.
        """
        if self.model is None or self.scaler is None:
            return np.array([0.0])

        # Convert input to DataFrame if dict or list of dicts
        if isinstance(feature_data, dict):
            df = pd.DataFrame([feature_data])
        elif isinstance(feature_data, list):
            df = pd.DataFrame(feature_data)
        elif isinstance(feature_data, pd.DataFrame):
            df = feature_data.copy()
        else:
            df = pd.DataFrame(feature_data, columns=self.FEATURE_NAMES)

        # Fill missing default feature values if needed
        defaults = {
            'elevation': 70.0, 'river_dist': 2.5, 'rainfall_mm': 0.0,
            'runoff_mm': df.get('rainfall_mm', 0.0) * 0.3 if 'rainfall_mm' in df else 0.0,
            'soil_moisture': 0.45, 'river_discharge': 300.0,
            'pop_density': 1500.0, 'sar_vh': 49.0
        }
        for col, def_val in defaults.items():
            if col not in df.columns:
                df[col] = def_val

        # Ensure correct column ordering
        df_ordered = df[self.FEATURE_NAMES].astype(float)
        
        # Scale features
        scaled_features = self.scaler.transform(df_ordered.values)

        # Dynamic tensor reshaping based on model input shape
        if len(self.in_shape) == 3: # 3D tensor: (batch, timesteps, features)
            timesteps = self.in_shape[1] if self.in_shape[1] is not None else 1
            input_tensor = scaled_features.reshape((-1, timesteps, len(self.FEATURE_NAMES)))
        else: # 2D tensor: (batch, features)
            input_tensor = scaled_features

        # Neural Inference
        raw_pred = self.model.predict(input_tensor, verbose=0).flatten()

        # Physics-Informed Calibration & Post-Processing
        elevation = df_ordered['elevation'].values
        river_discharge = df_ordered['river_discharge'].values
        rainfall = df_ordered['rainfall_mm'].values

        # If model is linear-output benchmark (e.g. crash_recovery_final ~ 0.05 max), apply linear probability mapping
        if "crash_recovery_final" in self.model_path:
            # Map raw output (0.0 to 0.05) to (0.0 to 0.70) base risk
            base_ai = np.clip(raw_pred * 14.0, 0.0, 0.75)
        elif getattr(self.model.layers[-1], 'activation', None).__name__ == 'sigmoid':
            base_ai = np.clip(raw_pred, 0.0, 1.0)
        else:
            base_ai = np.clip(raw_pred / 3.0, 0.0, 1.0)

        # Domain Physics Nudge
        topo_penalty = np.maximum(0.0, (71.77 - elevation) * 0.005)
        discharge_ratio = np.clip(river_discharge / 1311.20, 0.0, 1.0) * 0.20
        rain_ratio = np.clip(rainfall / 250.0, 0.0, 1.0) * 0.15

        # Final Sigmoid Synthesis into percentage [0.0 - 100.0]
        combined_score = base_ai + topo_penalty + discharge_ratio + rain_ratio
        final_risk_pct = np.clip(combined_score * 100.0, 0.0, 100.0)
        
        return np.round(final_risk_pct, 2)
