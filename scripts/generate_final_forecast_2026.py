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

class SentinelForecaster2026:
    def __init__(self):
        print("🛡️  Sentinel V7.0: Initializing 2026 Master Forecast...")
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        with open(MESH_PATH, 'r') as f: self.mesh = json.load(f)
        self.feature_cols = ['elevation', 'river_dist', 'rainfall_mm', 'runoff_mm', 
                            'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh']

    def apply_physical_filter(self, df):
        """Applies the 'Sanity Filter' derived from Monte Carlo stress logs."""
        # 1. SAR Clipping: Ensure radar values stay within physical dB limits
        df['sar_vh'] = df['sar_vh'].clip(lower=-35.0, upper=-5.0)
        
        # 2. Rainfall Correlation: No rain = No runoff logic
        df.loc[df['rainfall_mm'] < 1.0, 'runoff_mm'] = 0.0
        
        # 3. Saturation Logic: High Soil Moisture if heavy rain persists
        df.loc[df['rainfall_mm'] > 100, 'soil_moisture'] = 0.95
        return df

    def generate_2026_prediction(self):
        print("🔮 Simulating 2026 Monsoon Peak (1,250 m³/s Discharge)...")
        
        # Scenario Parameters (Simulating a severe but realistic 2026 peak)
        SIM_PARAMS = {
            'rainfall_mm': 180.0,
            'river_discharge': 1250.0,
            'soil_moisture': 0.85,
            'sar_vh': -26.5 # Simulated radar water detection
        }

        node_data = []
        for node in self.mesh:
            # Constructing the 'Intelligence Octet' for each node
            row = {
                'elevation': node['elevation'],
                'river_dist': node['river_dist'],
                'rainfall_mm': SIM_PARAMS['rainfall_mm'],
                'runoff_mm': SIM_PARAMS['rainfall_mm'] * 0.25, # Est. urban runoff
                'soil_moisture': SIM_PARAMS['soil_moisture'],
                'river_discharge': SIM_PARAMS['river_discharge'],
                'pop_density': node.get('pop_density', 1500), # Fallback if missing
                'sar_vh': SIM_PARAMS['sar_vh']
            }
            node_data.append(row)

        df = pd.DataFrame(node_data)
        
        # Apply the V7.0 Strategic Guardrails
        df = self.apply_physical_filter(df)
        
        # Inference
        X_scaled = self.scaler.transform(df[self.feature_cols])
        risk_predictions = self.model.predict(X_scaled, batch_size=2048, verbose=0).flatten()
        
        # Fuse predictions back into the JSON mesh structure
        final_mesh = []
        for i, node in enumerate(self.mesh):
            risk_val = float(risk_predictions[i])
            
            # Humanitarian Impact Calculation (ED: Estimated Displacement)
            pop = node.get('pop_density', 1500)
            ed = int(pop * risk_val * 0.45) # 45% displacement factor for high-risk zones

            final_mesh.append({
                "name": node['name'],
                "lat": node['lat'],
                "lon": node['lon'],
                "risk_score": risk_val,
                "risk_level": "EXTREME" if risk_val > 0.8 else "HIGH" if risk_val > 0.5 else "MODERATE",
                "estimated_displacement": ed,
                "elevation": node['elevation']
            })

        with open(OUTPUT_PATH, 'w') as f:
            json.dump(final_mesh, f, indent=4)
        
        print(f"✅ FINAL 2026 FORECAST LOCKED: {OUTPUT_PATH}")

if __name__ == "__main__":
    SentinelForecaster2026().generate_2026_prediction()