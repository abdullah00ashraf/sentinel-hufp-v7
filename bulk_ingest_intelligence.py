import os
import pandas as pd
from sqlalchemy import create_engine

# --- PATH CONFIG ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = f"sqlite:///{os.path.join(ROOT_DIR, 'tactical_db', 'sentinel_v7_tactical.db')}"
CSV_PATH = os.path.join(ROOT_DIR, "data", "master_flood_intelligence_80m.csv")

def run_heavy_ingestion():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found!")
        return

    print("🧬 Phase: High-Velocity Intelligence Migration...")
    engine = create_engine(DB_PATH)
    
    # We use a 100k chunk size to keep memory usage at ~500MB
    chunk_size = 100000
    total_rows = 0

    try:
        # Stream the CSV into the 'intelligence_master' table
        for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=chunk_size)):
            # Mapping CSV columns to DB columns automatically
            chunk.to_sql('intelligence_master', con=engine, if_exists='append', index=False)
            total_rows += len(chunk)
            
            if i % 10 == 0:
                print(f"   -> Progress: {total_rows:,} rows successfully indexed...")

        print(f"\n✅ SUCCESS: {total_rows:,} intelligence records are now searchable in SQL.")
    except Exception as e:
        print(f"❌ CRITICAL INGESTION FAILURE: {e}")

if __name__ == "__main__":
    run_heavy_ingestion()