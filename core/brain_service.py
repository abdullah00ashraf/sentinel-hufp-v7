import os
from .predictor import SentinelPredictor

class SentinelBrain:
    def __init__(self):
        self.predictor = SentinelPredictor()

    def run_inference(self, feature_dict: dict) -> float:
        """Runs calibrated inference on live features using SentinelPredictor."""
        try:
            risk_pct = self.predictor.predict_risk(feature_dict)
            return float(risk_pct[0])
        except Exception as e:
            print(f"⚠️ Brain Service Error: {e}")
            return 0.15  # Fallback safety risk ratio