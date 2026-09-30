import os
import time
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_A_PATH = os.path.join(BASE_DIR, "brain", "bi_lstm_flood_model.keras")           # Old Model
MODEL_B_PATH = os.path.join(BASE_DIR, "brain", "bi_lstm_flood_model_v7_optimized.keras") # New Model
SCALER_PATH = os.path.join(BASE_DIR, "brain", "scaler.joblib")

def run_ab_test():
    print("="*70)
    print("🛡️ SENTINEL V7.0 | A/B NEURAL BENCHMARK")
    print("="*70)

    # 1. Load Assets
    print("Loading Scaler...")
    scaler = joblib.load(SCALER_PATH)

    print("Loading Model A (Legacy)...")
    model_a = tf.keras.models.load_model(MODEL_A_PATH) if os.path.exists(MODEL_A_PATH) else None
    
    print("Loading Model B (Optimized)...")
    model_b = tf.keras.models.load_model(MODEL_B_PATH)

    if not model_a:
        print("⚠️ Model A not found. Running standalone diagnostic on Model B.")

    # 2. Define Stress Scenarios
    # Order: ['elevation', 'river_dist', 'rainfall_mm', 'runoff_mm', 'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh']
    scenarios = {
        "1. DRY DAY (Baseline)":      [70.0, 5.0, 0.0,   0.0,  0.30,  300.0, 1500, -20.0],
        "2. MODERATE MONSOON":        [65.0, 2.0, 45.0,  15.0, 0.65,  600.0, 2000, -15.0],
        "3. SEVERE FLASH FLOOD":      [60.0, 0.5, 180.0, 60.0, 0.95, 1250.0, 4500, -8.0],
        "4. EXTREME RIVER SURGE":     [58.0, 0.1, 20.0,  5.0,  0.80, 2800.0, 3000, -5.0],
        "5. HIGH ELEVATION STORM":    [110.0, 8.0, 200.0, 70.0, 0.90,  500.0, 500,  -12.0]
    }

    print("\n📊 INFERENCE LOGIC COMPARISON (Risk %):")
    print(f"{'SCENARIO':<25} | {'MODEL A (Legacy)':<18} | {'MODEL B (Optimized)':<18} | {'DELTA'}")
    print("-" * 70)

    latency_a, latency_b = 0, 0

    for name, vector in scenarios.items():
        # Prepare Tensor
        x_raw = pd.DataFrame([vector], columns=['elevation', 'river_dist', 'rainfall_mm', 'runoff_mm', 'soil_moisture', 'river_discharge', 'pop_density', 'sar_vh'])
        x_scaled = scaler.transform(x_raw)
        
        # Inference B (Optimized)
        start_b = time.perf_counter()
        pred_b = float(model_b.predict(x_scaled, verbose=0)[0][0]) * 100
        latency_b += (time.perf_counter() - start_b)

        # Inference A (Legacy)
        pred_a = 0.0
        if model_a:
            start_a = time.perf_counter()
            pred_a = float(model_a.predict(x_scaled, verbose=0)[0][0]) * 100
            latency_a += (time.perf_counter() - start_a)
            
        delta = pred_b - pred_a

        # Format output
        val_a = f"{pred_a:>6.2f}%" if model_a else "N/A"
        val_b = f"{pred_b:>6.2f}%"
        val_d = f"{delta:>+6.2f}%" if model_a else "N/A"
        
        print(f"{name:<25} | {val_a:<18} | {val_b:<18} | {val_d}")

    # 3. Latency & Size Comparison
    print("\n⚡ HARDWARE & LATENCY METRICS:")
    if model_a:
        print(f"Model A Inference Time (5 passes): {latency_a*1000:.2f} ms")
    print(f"Model B Inference Time (5 passes): {latency_b*1000:.2f} ms")
    
    size_b = os.path.getsize(MODEL_B_PATH) / (1024*1024)
    print(f"Model B File Size: {size_b:.2f} MB")

    print("\n✅ A/B TESTING COMPLETE.")

if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    run_ab_test()
