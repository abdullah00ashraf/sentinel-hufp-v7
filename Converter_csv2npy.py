import pandas as pd
import numpy as np
import os
import sys

# --- CONFIG ---
CSV_PATH = "master_flood_intelligence_80m.csv"
OUT_X = "brain/features_80m.npy"
OUT_Y = "brain/labels_80m.npy"

if not os.path.exists("brain"): os.makedirs("brain")

print("🚀 Starting High-Speed Binary Conversion...")
print("📦 This process saves hours of training time later.")

# --- SMART HEADER DISCOVERY ---
def discover_neural_mapping(file_path):
    """Detects actual CSV headers to prevent KeyErrors and maps the 8-factor vector."""
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        sys.exit(1)
        
    # Read only the header to inspect column names
    df_sample = pd.read_csv(file_path, nrows=0)
    actual_cols = df_sample.columns.tolist()
    # Normalize for searching (lower + strip spaces)
    cols = [c.lower().strip() for c in actual_cols]

    mapping = {
        'elev': next((actual_cols[i] for i, c in enumerate(cols) if 'elev' in c), None),
        'dist': next((actual_cols[i] for i, c in enumerate(cols) if 'dist' in c), None),
        'rain': next((actual_cols[i] for i, c in enumerate(cols) if any(k in c for k in ['rain', 'precip'])), None),
        'runoff': next((actual_cols[i] for i, c in enumerate(cols) if 'runoff' in c), None),
        'soil': next((actual_cols[i] for i, c in enumerate(cols) if any(k in c for k in ['soil', 'moist'])), None),
        'discharge': next((actual_cols[i] for i, c in enumerate(cols) if any(k in c for k in ['disch', 'river'])), None),
        'pop': next((actual_cols[i] for i, c in enumerate(cols) if any(k in c for k in ['pop', 'dens'])), None),
        'sar': next((actual_cols[i] for i, c in enumerate(cols) if any(k in c for k in ['sar', 'vh'])), None),
        'target': next((actual_cols[i] for i, c in enumerate(cols) if any(k in c for k in ['risk', 'flood', 'label', 'target', 'score'])), None)
    }
    
    # Fallback for target if keyword matching fails
    if not mapping['target']: 
        mapping['target'] = actual_cols[-1]
    
    # Filter features that exist in the CSV
    features = [mapping[k] for k in ['elev', 'dist', 'rain', 'runoff', 'soil', 'discharge', 'pop', 'sar'] if mapping[k]]
    return features, mapping['target']

try:
    FEATURE_COLS, TARGET_COL = discover_neural_mapping(CSV_PATH)
    print(f"✅ Intelligence Mapping: Features={FEATURE_COLS}, Target='{TARGET_COL}'")
except Exception as e:
    print(f"❌ Mapping Failed: {e}")
    sys.exit(1)

# Use a large chunk size to speed up conversion
chunk_size = 1000000 
X_list = []
y_list = []

# Process in chunks to respect your 16GB RAM
for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=chunk_size)):
    # Slice the chunk using the discovered column names
    X_list.append(chunk[FEATURE_COLS].values.astype('float32'))
    y_list.append(chunk[TARGET_COL].values.astype('float32'))
    print(f"✅ Processed { (i+1)*chunk_size / 1e6 }M rows...")

print("💾 Writing Binary Vault to disk...")
# Concatenate and save as high-speed .npy files
np.save(OUT_X, np.concatenate(X_list, axis=0))
np.save(OUT_Y, np.concatenate(y_list, axis=0))

print(f"✨ DONE! Created {OUT_X} and {OUT_Y}")
print("🗑️  You can now delete the .csv if you want to save space.")