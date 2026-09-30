import os
import sys
import time
import psutil
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.predictor import SentinelPredictor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "audits", "monte_carlo_stress_log.csv")

class SentinelStressTester:
    def __init__(self, total_sims=100000):
        print("\n" + "!"*60)
        print("🛡️  SENTINEL V7.0: MONTE CARLO TACTICAL STRESS TEST ACTIVE")
        print("!"*60)
        
        self.total_sims = total_sims
        self.batch_size = 10000
        self.predictor = SentinelPredictor()
        self.feature_cols = ['elevation', 'river_dist', 'rainfall_mm', 'runoff_mm', 
                            'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh']

    def log_resources(self, current_sim):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        progress = (current_sim / self.total_sims) * 100
        print(f"   [PROGRESS: {progress:.1f}%] CPU: {cpu}% | RAM: {ram}% | Sims: {current_sim:,}")

    def generate_chaos_batch(self):
        data = {
            'elevation': np.random.uniform(60, 160, self.batch_size),
            'river_dist': np.random.uniform(0, 10000, self.batch_size),
            'rainfall_mm': np.random.uniform(0, 800, self.batch_size),
            'runoff_mm': np.random.uniform(0, 300, self.batch_size),
            'soil_moisture': np.random.uniform(0.1, 1.0, self.batch_size),
            'river_discharge': np.random.uniform(0, 3000, self.batch_size),
            'pop_density': np.random.uniform(0, 50000, self.batch_size),
            'sar_vh': np.random.uniform(-35, -5, self.batch_size)
        }
        return pd.DataFrame(data)

    def run_test(self):
        start_time = time.time()
        processed_sims = 0
        
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        pd.DataFrame(columns=self.feature_cols + ['predicted_risk', 'category']).to_csv(LOG_PATH, index=False)

        print(f"\n🚀 Launching {self.total_sims:,} Simulations. Logging to {LOG_PATH}...")

        while processed_sims < self.total_sims:
            df_batch = self.generate_chaos_batch()
            predictions = self.predictor.predict_risk(df_batch)
            df_batch['predicted_risk'] = predictions
            
            df_batch['category'] = 'Standard'
            df_batch.loc[(df_batch['predicted_risk'] > 80.0) & (df_batch['river_discharge'] < 400), 'category'] = 'High_Risk_Low_Q'
            df_batch.loc[(df_batch['predicted_risk'] < 20.0) & (df_batch['river_discharge'] > 1300), 'category'] = 'False_Negative_Risk'

            df_batch.to_csv(LOG_PATH, mode='a', header=False, index=False)
            processed_sims += self.batch_size
            self.log_resources(processed_sims)

        total_time = (time.time() - start_time) / 60
        print("\n" + "="*60)
        print(f"✅ STRESS TEST COMPLETE. Duration: {total_time:.2f} minutes.")
        print(f"📁 Full Tactical Log saved at: {LOG_PATH}")
        print("="*60)

if __name__ == "__main__":
    tester = SentinelStressTester(total_sims=50000)
    tester.run_test()