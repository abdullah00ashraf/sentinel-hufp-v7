import os
import sys
import time

# Path Repair
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from core.db_manager import SentinelDB
from sqlalchemy import text

def audit_vault():
    db = SentinelDB()
    engine = db.get_engine()
    
    print("\n" + "🛡️  " + "="*45)
    print("SENTINEL V7.0 | TACTICAL DATA AUDIT")
    print("="*50)

    with engine.connect() as conn:
        # 1. Row Count Verification
        start = time.time()
        intel_count = conn.execute(text("SELECT COUNT(*) FROM intelligence_master")).scalar()
        node_count = conn.execute(text("SELECT COUNT(*) FROM tactical_nodes")).scalar()
        query_time = time.time() - start

        # 2. Storage Analysis
        db_path = os.path.join(ROOT, "tactical_db", "sentinel_v7_tactical.db")
        file_size_gb = os.path.getsize(db_path) / (1024**3)

        # 3. High-Risk Snapshot
        high_risk = conn.execute(text(
            "SELECT COUNT(*) FROM intelligence_master WHERE risk_score > 0.8"
        )).scalar()

        print(f"📍 Geospatial Nodes:      {node_count}")
        print(f"🧬 Intelligence Records:   {intel_count:,}")
        print(f"📦 Vault File Size:        {file_size_gb:.2f} GB")
        print(f"⚡ Index Speed (80M):      {query_time:.4f} seconds")
        print(f"🚨 Extreme Risk Zones:     {high_risk:,}")
        print("="*50)

        if intel_count >= 80000000:
            print("✅ VERDICT: VAULT IS FULLY POPULATED & MISSION READY.")
        else:
            print("⚠️  VERDICT: INGESTION INCOMPLETE OR DATA FRAGMENTED.")

if __name__ == "__main__":
    audit_vault()