import os
import json
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

# --- TACTICAL PATHS ---
BASE_DIR = "C:/HUFP_SENTINEL_V6"
MODEL_PATH = f"{BASE_DIR}/brain/bi_lstm_flood_model.keras"
SCALER_PATH = f"{BASE_DIR}/brain/scaler.joblib"
MESH_PATH = f"{BASE_DIR}/data/geospatial/localities.json"
OUTPUT_PATH = f"{BASE_DIR}/web/lucknow_2026_forecast.json"

class SentinelMasterForecaster:
    def __init__(self):
        print("🛡️ Sentinel V7.0: Initializing Tactical Mitigation...")
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        with open(MESH_PATH, 'r') as f: self.mesh = json.load(f)
        self.feature_cols = ['elevation', 'river_dist', 'rainfall_mm', 'runoff_mm', 
                            'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh']

    def apply_phase_1_guardrails(self, df):
        """Implements the Physical Reality Filter to solve the paradoxes."""
        print("🧪 Applying Phase 1: Tactical Guardrails...")
        
        # Constraint 1: Rainfall/Runoff correlation
        df.loc[df['rainfall_mm'] == 0, 'runoff_mm'] = 0
        
        # Constraint 2: SAR Clipping to physical dB range
        df['sar_vh'] = df['sar_vh'].clip(lower=-35, upper=-5)
        
        return df

    def generate_phase_2_forecast(self):
        """Generates the Master 2026 Prediction JSON."""
        print("🔮 Phase 2: Generating 2026 Intelligence...")
        
        # Scenario: High-Intensity Monsoon Peak for 2026
        # Audited Discharge: 1250 m3/s (Near 2021 Peak)
        LUCKNOW_2026_SCENARIO = {
            'rainfall': 145.0, 
            'q_discharge': 1250.0,
            'soil_sat': 0.88,
            'sar_verify': -28.5 # Simulated radar water detection
        }

        forecast_rows = []
        for node in self.mesh:
            forecast_rows.append({
                'elevation': node['elevation'],
                'river_dist': node['river_dist'],
                'rainfall_mm': LUCKNOW_2026_SCENARIO['rainfall'],
                'runoff_mm': LUCKNOW_2026_SCENARIO['rainfall'] * 0.3, # Urban coefficient
                'soil_moisture': LUCKNOW_2026_SCENARIO['soil_sat'],
                'river_discharge': LUCKNOW_2026_SCENARIO['q_discharge'],
                'pop_density': node.get('pop_density', 1500),
                'sar_vh': LUCKNOW_2026_SCENARIO['sar_verify']
            })

        df = pd.DataFrame(forecast_rows)
        
        # EXECUTE GUARDRAILS
        df = self.apply_phase_1_guardrails(df)
        
        # SCALE & PREDICT
        X_scaled = self.scaler.transform(df[self.feature_cols])
        raw_risks = self.model.predict(X_scaled, batch_size=2048, verbose=0).flatten()

        # APPLY CONSTRAINT 3: Risk Dampening (Post-Prediction logic)
        # If the environment is physically 'safe', dampen the neural noise.
        for i in range(len(raw_risks)):
            if LUCKNOW_2026_SCENARIO['q_discharge'] < 300 and LUCKNOW_2026_SCENARIO['rainfall'] < 15:
                raw_risks[i] *= 0.1 # 90% dampening for safety
        
        # BUILD FINAL JSON
        final_forecast = []
        for i, node in enumerate(self.mesh):
            risk = float(raw_risks[i])
            # Estimated Displacement (ED) based on Risk * Population
            ed = int(node.get('pop_density', 1500) * risk * 0.4) 

            final_forecast.append({
                "name": node['name'],
                "lat": node['lat'],
                "lon": node['lon'],
                "risk_score": risk,
                "risk_level": "EXTREME" if risk > 0.85 else "HIGH" if risk > 0.6 else "MODERATE",
                "estimated_displacement": ed,
                "elevation": node['elevation']
            })

        with open(OUTPUT_PATH, 'w') as f:
            json.dump(final_forecast, f, indent=4)
        
        print(f"✅ SUCCESS: Master Forecast Generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    SentinelMasterForecaster().generate_phase_2_forecast()