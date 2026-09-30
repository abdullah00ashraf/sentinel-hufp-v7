import os
import sys

# Ensure root modules are visible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.predictor import SentinelPredictor

class BrainProxy:
    """Managed interface for Bi-LSTM Model V7.0 via SentinelPredictor."""
    
    def __init__(self):
        self.predictor = SentinelPredictor()

    def compute_risk(self, weather_data: dict, node_data: dict) -> float:
        """Processes 8-factor vector through SentinelPredictor and returns normalized probability [0.0, 1.0]."""
        feature_dict = {
            'elevation': node_data.get('elevation', 70.0),
            'river_dist': node_data.get('river_dist', 2.5),
            'rainfall_mm': weather_data.get('rainfall_mm', 0.0),
            'runoff_mm': weather_data.get('rainfall_mm', 0.0) * 0.42,
            'soil_moisture': weather_data.get('soil_moisture', 0.45),
            'river_discharge': weather_data.get('river_discharge', 300.0),
            'pop_density': float(node_data.get('pop_density', 1500.0)),
            'sar_vh': 49.0
        }
        
        try:
            risk_pct = self.predictor.predict_risk(feature_dict)
            return float(risk_pct[0] / 100.0)
        except Exception as e:
            print(f"⚠️ BrainProxy Error: {e}")
            return 0.15