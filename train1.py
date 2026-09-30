import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger, ReduceLROnPlateau
import logging

# --- 1. GLOBAL PATH CONFIGURATION ---
# This defines the "Root" of your HUFP_SENTINEL_V6 folder dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "master_flood_intelligence_80m.csv")
BRAIN_DIR = os.path.join(BASE_DIR, "brain")
MODEL_SAVE_PATH = os.path.join(BRAIN_DIR, "bi_lstm_flood_model_v7_deep.keras")
LOG_FILE = os.path.join(BASE_DIR, "sentinel_training_overnight.log")
METRICS_LOG = os.path.join(BASE_DIR, "training_metrics_v7.log")

# --- 2. FOLDER GUARD ---
# Ensure the brain folder exists so the model can be saved locally
if not os.path.exists(BRAIN_DIR):
    os.makedirs(BRAIN_DIR)
    print(f"📁 Created directory: {BRAIN_DIR}")

# --- 3. SYSTEM LOGGING SETUP ---
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

print("🚀 Sentinel V7.0 Deep Training Initialized.")
print(f"📍 Data Source: {DATA_PATH}")
print("🧠 Architecture: Deep Bi-LSTM (999 Epochs Target)")
print("🛡️ RAM Protection: Stream-Engine Active")

# --- 4. THE RAM PROTECTOR (Generator) ---
def data_generator(file_path, chunk_size=50000):
    """Streams data from 8.69GB CSV in chunks to protect system RAM."""
    while True:
        try:
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # Features: Rainfall, River Level, Soil Moisture, Humidity
                X = chunk[['rainfall', 'river_level', 'soil_moisture', 'humidity']].values
                y = chunk['flood_risk_score'].values
                
                # Reshape for LSTM: [samples, time_steps, features]
                X = X.reshape((X.shape[0], 1, X.shape[1]))
                yield X, y
        except Exception as e:
            logging.error(f"Stream Error: {str(e)}")
            break

# --- 5. THE NEURAL ARCHITECTURE ---
def build_deep_brain():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(1, 4)),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

# --- 6. OVERNIGHT EXECUTION ENGINE ---
def run_overnight_session():
    model = build_deep_brain()
    
    # Callbacks: The "Auto-Pilot" Safety Gear
    callbacks = [
        # Checkpoint: Saves best local model after every epoch
        ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='loss', verbose=1),
        
        # Early Stopping: Prevents CPU waste if model stops improving
        EarlyStopping(monitor='loss', patience=20, restore_best_weights=True),
        
        # Metrics Log: For your morning review
        CSVLogger(METRICS_LOG, append=True),
        
        # Performance: Drops learning rate if progress slows down
        ReduceLROnPlateau(monitor='loss', factor=0.5, patience=7, min_lr=1e-7, verbose=1)
    ]

    # Calculate steps per epoch (83.9M rows / 50k chunk size)
    total_rows = 83900000 
    chunk_size = 50000
    steps_per_epoch = total_rows // chunk_size 

    try:
        model.fit(
            data_generator(DATA_PATH, chunk_size=chunk_size),
            steps_per_epoch=steps_per_epoch,
            epochs=999,
            callbacks=callbacks,
            verbose=1 # Keeps the terminal status active
        )
        print(f"✅ Training Complete. Model saved to: {MODEL_SAVE_PATH}")
    except Exception as e:
        logging.error(f"CRITICAL OVERNIGHT CRASH: {str(e)}")
        print(f"❌ System halted. Check '{LOG_FILE}' for crash details.")

if __name__ == "__main__":
    run_overnight_session()