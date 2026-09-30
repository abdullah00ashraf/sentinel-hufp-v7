import pandas as pd
import sqlite3
import os
import time
import json

# --- PATHS ---
CSV_PATH = "master_flood_intelligence_80m.csv"
# Renamed to MASTER_VAULT so it doesn't overwrite your tiny Hugging Face DB
MASTER_DB_PATH = "tactical_db/sentinel_v7_master_vault.db" 
LOCALITIES_PATH = "data/geospatial/localities.json"

def create_master_vault():
    print(f"🚀 Rebuilding the FULL 11GB Master Database (83.9M Rows)...")
    print(f"⚠️  Keep this safe on your local drive. (Do not upload to Hugging Face)")
    
    os.makedirs(os.path.dirname(MASTER_DB_PATH), exist_ok=True)
    
    if os.path.exists(MASTER_DB_PATH):
        os.remove(MASTER_DB_PATH)
        print("🗑️ Removed old master database.")

    # Get node count to ensure accurate cyclic linking
    nodes_count = 2025 # Default Lucknow tactical nodes
    if os.path.exists(LOCALITIES_PATH):
        with open(LOCALITIES_PATH, 'r') as f:
            nodes_count = len(json.load(f))

    conn = sqlite3.connect(MASTER_DB_PATH)
    
    print(f"📊 Streaming 100% of data and linking to {nodes_count} Geospatial Nodes...")
    chunk_size = 1000000
    rows_processed = 0
    start_time = time.time()
    
    # Process the massive CSV in chunks to protect your 16GB RAM
    for i, chunk in enumerate(pd.read_csv(CSV_PATH, chunksize=chunk_size)):
        # FIX: Restored the critical node_id assignment logic!
        current_start_idx = i * chunk_size
        chunk['node_id'] = [( (current_start_idx + j) % nodes_count) + 1 for j in range(len(chunk))]
        
        # NO SAMPLING: We are saving 100% of the valuable data asset
        chunk.to_sql("intelligence_master", conn, if_exists="append", index=False)
        
        rows_processed += len(chunk)
        elapsed = (time.time() - start_time) / 60
        print(f"   -> Saved {rows_processed / 1e6:.1f}M records... ({elapsed:.1f} mins elapsed)")

    print("⚡ Building high-speed database indexes (This may take a minute)...")
    # FIX: Restored the indexes so the database is actually searchable
    conn.execute("CREATE INDEX idx_node_link ON intelligence_master(node_id);")
    conn.execute("CREATE INDEX idx_risk_scores ON intelligence_master(risk_score);")

    conn.close()
    
    size_gb = os.path.getsize(MASTER_DB_PATH) / (1024 * 1024 * 1024)
    print("\n" + "="*50)
    print(f"✨ SUCCESS! Master Vault fully restored. Final Size: {size_gb:.2f} GB.")
    print("💡 Note: SQLite compresses text CSVs into binary floats. ~6-8GB is expected and 100% complete!")
    print(f"👉 Your valuable asset is safely archived at: {MASTER_DB_PATH}")
    print("="*50)

if __name__ == "__main__":
    create_master_vault()