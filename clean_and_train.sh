#!/bin/bash

# --- SENTINEL V7.0 SYSTEM PURGE ---
echo "🛡️  Sentinel V7.0 | Initiating System Purge..."

# 1. Clear Python Bytecode
echo "🧹 Removing Python __pycache__ folders..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# 2. Clear Specific Training Logs & Metrics
echo "🧹 Purging stale training logs and CSV metrics..."
rm -f neural_deep_burn.log
rm -f deep_metrics_v7.csv

# 3. Remove Heartbeat Recovery (Force Fresh Start if desired)
# Note: Delete this line if you want to keep your current progress
echo "🧹 Removing heartbeat recovery files..."
rm -f brain/heartbeat_recovery.keras

# 4. Clear Keras/TensorFlow local metadata
if [ -d "$HOME/.keras" ]; then
    echo "🧹 Cleaning Keras metadata cache..."
    rm -rf "$HOME/.keras/cache/*"
fi

# 5. Optional: System Memory Flush (Requires sudo/admin on Linux/WSL)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🧠 Flushing system RAM buffers..."
    sync; echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1
fi

echo "✨ System status: OPTIMAL. Starting Architecture Audit..."

# --- EXECUTION ---
# 1. Run the system test first to ensure environment integrity
python test_sentinel_v7.py

# 2. If test passes, launch the Ultra Training
if [ $? -eq 0 ]; then
    echo "✅ Audit passed. Launching Deep Training Engine..."
    python deep_train_v7_ultra.py
else
    echo "❌ System Audit Failed. Aborting training to prevent data corruption."
  
    exit 1
fi