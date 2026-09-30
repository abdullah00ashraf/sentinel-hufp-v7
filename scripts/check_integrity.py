import json
import os

def check_v6_integrity():
    base = "C:/HUFP_SENTINEL_V6"
    paths = {
        "Model": f"{base}/brain/bi_lstm_flood_model.keras",
        "Scaler": f"{base}/brain/scaler.joblib",
        "Grid": f"{base}/data/geospatial/localities.json"
    }

    print("🛡️ HUFP V6 INTEGRITY CHECK")
    print("-" * 30)

    for name, path in paths.items():
        if os.path.exists(path):
            print(f"✅ {name} found.")
        else:
            print(f"❌ MISSING {name}: {path}")

    if os.path.exists(paths["Grid"]):
        with open(paths["Grid"], 'r') as f:
            data = json.load(f)
            first_node = data[0]
            print(f"\n🛰️ Grid Sample (First Node): {first_node['name']}")
            
            # Check for keys used in sentinel.py
            required_keys = ['elevation', 'river_dist', 'lat', 'lon']
            for key in required_keys:
                if key in first_node:
                    print(f"  ✅ Key '{key}' exists.")
                else:
                    print(f"  ❌ MISSING KEY: '{key}' (The AI needs this to calculate risk!)")

if __name__ == "__main__":
    check_v6_integrity()