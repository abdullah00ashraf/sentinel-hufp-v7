import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks, metrics
from tensorflow.keras import mixed_precision

# --- 1. SYSTEM OPTIMIZATION (i5-1235U Precision) ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'

# Enable Mixed Precision for high-speed gate calculations
try:
    policy = mixed_precision.Policy('mixed_float16')
    mixed_precision.set_global_policy(policy)
    print("⚡ Mixed Precision: ENABLED (Throughput Optimized)")
except:
    print("ℹ️ Mixed Precision: NOT SUPPORTED (Falling back to float32)")

# --- 2. CONFIG & BINARY PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
X_PATH = os.path.join(BASE_DIR, "brain", "features_80m.npy")
Y_PATH = os.path.join(BASE_DIR, "brain", "labels_80m.npy")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "brain", "bi_lstm_flood_model_v7_optimized.keras")
PREVIOUS_MODEL = os.path.join(BASE_DIR, "brain", "bi_lstm_flood_model.keras")

# Memory-Mapped Data Access: Prevents RAM crashes on 16GB systems
X_data = np.load(X_PATH, mmap_mode='r')
y_data = np.load(Y_PATH, mmap_mode='r')

# --- 3. ARCHITECTURE (Strict Mirror of Sentinel V7.0) ---
def build_mirrored_brain(input_dim=8):
    """
    Reconstructs the 9-layer architecture from the V7 audit report.
    Fixed metric identifiers for XLA compatibility.
    """
    model = models.Sequential([
        layers.Input(shape=(input_dim,), name="input_layer"),
        layers.Reshape((1, input_dim), name="reshape"),
        
        # Bi-LSTM Core
        layers.Bidirectional(layers.LSTM(128, return_sequences=True), name="bidirectional"),
        layers.BatchNormalization(name="batch_normalization"),
        layers.Bidirectional(layers.LSTM(64), name="bidirectional_1"),
        layers.Dropout(0.3, name="dropout"),
        
        # Decision Logic
        layers.Dense(128, activation='swish', name="dense"),
        layers.BatchNormalization(name="batch_normalization_1"),
        layers.Dense(64, activation='relu', name="dense_1"),
        
        # Output Layer (Dtype float32 is vital for mixed precision stability)
        layers.Dense(1, activation='linear', dtype='float32', name="dense_2")
    ])

    # Using explicit metric classes to avoid "Could not interpret metric" error
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0007),
        loss='mse',
        metrics=[
            metrics.MeanAbsoluteError(name='mae'),
            metrics.RootMeanSquaredError(name='rmse') 
        ],
        jit_compile=True 
    )
    return model

# --- 4. EXECUTION ENGINE ---
def run_burn():
    print(f"🛰️ SENTINEL V7 | Optimized Refinement Burn (60 Epochs)")
    print(f"📊 Dataset Scale: {X_data.shape[0]/1e6:.2f} Million Records")
    
    # Warm Start Logic
    if os.path.exists(PREVIOUS_MODEL):
        print("🧠 Warm Start: Loading current Bi-LSTM weights...")
        try:
            # Re-build and load weights to ensure metric compliance
            model = build_mirrored_brain()
            model.load_weights(PREVIOUS_MODEL, skip_mismatch=True)
            print("✅ Weights merged with new metric configuration.")
        except Exception as e:
            print(f"⚠️ Load failed ({e}). Starting fresh burn.")
            model = build_mirrored_brain()
    else:
        model = build_mirrored_brain()

    # Callbacks for Precision & Stability
    cb = [
        # Save best optimized version
        callbacks.ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='loss', verbose=1),
        # Preserve intelligence if improvement stops
        callbacks.EarlyStopping(monitor='loss', patience=10, restore_best_weights=True),
        # Smooth convergence
        callbacks.ReduceLROnPlateau(monitor='loss', factor=0.5, patience=4, min_lr=1e-7, verbose=1),
        # Emergency save heartbeat
        callbacks.ModelCheckpoint(os.path.join(BASE_DIR, "brain", "recovery_heartbeat.keras"), save_freq=10000)
    ]

    try:
        model.fit(
            X_data, y_data,
            batch_size=32768, 
            epochs=60,
            shuffle=True, 
            callbacks=cb,
            verbose=1
        )
        print("✅ SUCCESS: Optimized Neural Model Locked.")
    except KeyboardInterrupt:
        print("\n💾 Manual Break. Archiving current intelligence...")
        model.save(MODEL_SAVE_PATH)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    # Ensure oneDNN is active for i5 performance
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'
    run_burn()