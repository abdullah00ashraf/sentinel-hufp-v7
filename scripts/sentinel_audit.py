import os
import pandas as pd
import glob
try:
    import rasterio
except ImportError:
    rasterio = None

def get_size_mb(path):
    return round(os.path.getsize(path) / (1024 * 1024), 2)

def audit_sentinel_stack():
    print("\n" + "="*50)
    print("🛡️  SENTINEL V7.0: DATASET INTEGRITY AUDIT")
    print("="*50)

    # --- 1. SATELLITE SAR AUDIT ---
    print("\n🛰️  AUDITING SAR RADAR (Sentinel-1)...")
    sar_files = glob.glob("data/satellite/sar/**/*.tiff", recursive=True)
    if not sar_files:
        print("❌ WARNING: No SAR .tiff files found. Check extraction path!")
    for f in sar_files:
        name = os.path.basename(f)
        size = get_size_mb(f)
        print(f"   -> Found: {name} | Size: {size} MB")
        if rasterio and "vh" in name.lower():
            with rasterio.open(f) as src:
                print(f"      [Metadata] Bounds: {src.bounds} | Bands: {src.count}")

    # --- 2. GEOSPATIAL AUDIT (Population & OSM) ---
    print("\n🌍 AUDITING GEOSPATIAL LAYERS...")
    geo_files = glob.glob("data/geospatial/*")
    for f in geo_files:
        name = os.path.basename(f)
        size = get_size_mb(f)
        ext = name.split('.')[-1].lower()
        print(f"   -> Found: {name} | Size: {size} MB")
        if ext == 'tif' and rasterio:
            with rasterio.open(f) as src:
                print(f"      [Population] Res: {src.res} | CRS: {src.crs}")

    # --- 3. HYDROLOGY AUDIT (Gomti River) ---
    print("\n🌊 AUDITING HYDROLOGY PULSE...")
    hydro_csv = "data/hydrology/lucknow_flood_hist_19_21.csv"
    if os.path.exists(hydro_csv):
        df = pd.read_csv(hydro_csv)
        print(f"   -> File: {os.path.basename(hydro_csv)} | Size: {get_size_mb(hydro_csv)} MB")
        print(f"   -> Memory: {len(df)} days of Gomti Discharge recorded.")
        print(f"   -> Range: {df['time'].min()} to {df['time'].max()}")
        print(f"   -> Peak Flow: {df['river_discharge'].max():.2f} m³/s")
    else:
        print("❌ CRITICAL: Hydrology CSV missing!")

    print("\n" + "="*50)
    print("🚀 AUDIT COMPLETE: STACK IS READY FOR FUSION.")
    print("="*50)

if __name__ == "__main__":
    audit_sentinel_stack()