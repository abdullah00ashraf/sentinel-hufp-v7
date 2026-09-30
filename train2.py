import os
import json
import glob
import time
import psutil
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib
import rasterio
from pyproj import Transformer

# --- TACTICAL PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_CSV = os.path.join(BASE_DIR, "data", "master_flood_intelligence_80m.csv")
TRAINING_LOG = os.path.join(BASE_DIR, "data", "training_step_log.csv")
BRAIN_DIR = os.path.join(BASE_DIR, "brain")

DATA_PATHS = {
    "mesh": os.path.join(BASE_DIR, "data", "geospatial", "localities.json"),
    "hydro": os.path.join(BASE_DIR, "data", "hydrology", "lucknow_flood_hist_19_21.csv"),
    "pop": os.path.join(BASE_DIR, "data", "geospatial", "GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R6_C26.tif"),
    "sar_dir": os.path.join(BASE_DIR, "data", "satellite", "sar")
}

class SentinelProfessionalTrainerV7:
    def __init__(self):
        print("\n" + "="*80)
        print("🛡️  SENTINEL V7.0: PROFESSIONAL TACTICAL TRAINER ACTIVE")
        print("="*80)
        self.scaler = MinMaxScaler()
        self.feature_cols = ['elevation', 'river_dist', 'rainfall_mm', 'runoff_mm', 
                            'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh']
        if not os.path.exists(BRAIN_DIR): os.makedirs(BRAIN_DIR)

    def log_hardware(self):
        """Displays current Microprocess details in terminal."""
        cpu_p = psutil.cpu_percent()
        ram_p = psutil.virtual_memory().percent
        disk_io = psutil.disk_io_counters()
        print(f"   [MICROPROCESS] CPU: {cpu_p}% | RAM: {ram_p}% | DISK-READ: {disk_io.read_bytes//1024**2}MB")

    def pre_cache_spatial_data(self):
        print(f"\n🌍 [STEP 1] Pre-Caching Spatial Intelligence...")
        self.log_hardware()
        
        with open(DATA_PATHS["mesh"], 'r') as f: mesh = json.load(f)
        sar_files = glob.glob(os.path.join(DATA_PATHS["sar_dir"], "**", "*vh*.tiff"), recursive=True)
        
        mollweide = "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
        wgs84 = "EPSG:4326"
        
        cached_nodes = []
        sar_file = sar_files[0] if sar_files else None
        
        with rasterio.open(DATA_PATHS["pop"]) as pop_src:
            pop_trans = Transformer.from_crs(wgs84, mollweide, always_xy=True)
            
            for i, node in enumerate(mesh):
                px, py = pop_trans.transform(node['lon'], node['lat'])
                r, c = pop_src.index(px, py)
                pop = pop_src.read(1)[r, c] if (0<=r<pop_src.height and 0<=c<pop_src.width) else 450
                
                cached_nodes.append({
                    'elevation': node['elevation'], 'river_dist': node['river_dist'],
                    'pop_density': max(0, float(pop)), 'sar_vh': -21.0
                })
                if i % 500 == 0: print(f"      -> Cached {i}/{len(mesh)} Nodes...")
        return cached_nodes

    def train_with_logging(self, num_epochs=10):
        print(f"\n🧠 [STEP 2] Initializing Neural Engine Training (Class-Weighted Sigmoid Pass)...")
        # Sample 1M rows for high-velocity calibrated training
        csv_file = MASTER_CSV if os.path.exists(MASTER_CSV) else os.path.join(BASE_DIR, "master_flood_intelligence_80m.csv")
        data = pd.read_csv(csv_file, nrows=1000000)
        
        X = self.scaler.fit_transform(data[self.feature_cols])
        y = data['target'].values
        
        # Calculate Class Weights to fix 99.8% / 0.2% class imbalance
        neg_count = np.sum(y == 0)
        pos_count = np.sum(y == 1)
        class_weight = {0: 1.0, 1: float(neg_count / max(1, pos_count))}
        print(f"📊 Dataset Balance: Negatives = {neg_count:,}, Positives = {pos_count:,}")
        print(f"⚖️ Applied Class Weighting: {class_weight}")

        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(len(self.feature_cols),)),
            tf.keras.layers.Reshape((1, len(self.feature_cols))),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True, activation='tanh')),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, activation='tanh')),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid') # Calibrated Probability Output
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', 'AUC'])

        csv_logger = tf.keras.callbacks.CSVLogger(TRAINING_LOG, separator=",", append=False)
        
        print(f"🚀 Training for {num_epochs} Epochs. Logging matrices to {TRAINING_LOG}")
        model.fit(X, y, epochs=num_epochs, batch_size=2048, validation_split=0.1, class_weight=class_weight, callbacks=[csv_logger], verbose=1)
        
        model.save(f"{BRAIN_DIR}/bi_lstm_flood_model.keras")
        joblib.dump(self.scaler, f"{BRAIN_DIR}/scaler.joblib")
        print("\n✅ V7.0 TACTICAL MISSION SUCCESS: RE-CALIBRATED MASTER MODEL DEPLOYED.")

if __name__ == "__main__":
    trainer = SentinelProfessionalTrainerV7()
    trainer.train_with_logging(num_epochs=5)