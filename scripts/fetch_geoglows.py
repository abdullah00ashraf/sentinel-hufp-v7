import requests
import pandas as pd
import os

# --- TACTICAL CONFIGURATION ---
LAT = 26.85
LON = 80.94
OUTPUT_DIR = "C:/HUFP_SENTINEL_V6/data/hydrology"
FILE_NAME = "lucknow_flood_hist_19_21.csv"

def fetch_flood_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"🛡️ Sentinel V7.0: Pulling GloFAS Reanalysis for Lucknow ({LAT}, {LON})...")
    
    # Open-Meteo Flood API (No key required)
    url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": "river_discharge",
        "start_date": "2019-01-01",
        "end_date": "2021-12-31",
        "models": "seamless_v4"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Extracting the daily discharge arrays
            df = pd.DataFrame({
                "time": data["daily"]["time"],
                "river_discharge": data["daily"]["river_discharge"]
            })
            
            output_path = os.path.join(OUTPUT_DIR, FILE_NAME)
            df.to_csv(output_path, index=False)
            
            print(f"✅ MISSION SUCCESS: {len(df)} days of discharge data saved.")
            print(f"📍 Location: {output_path}")
            return True
        else:
            print(f"❌ API Breach Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Interrupted: {e}")
        return False

if __name__ == "__main__":
    fetch_flood_data()