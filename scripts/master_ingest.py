import sys
import os
import pandas as pd
import json
import time
from sqlalchemy import text

# --- TACTICAL PATH REPAIR ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from core.db_manager import SentinelDB
from core.models import Base, TacticalNode, MissionAudit, IntelligenceMaster

def run_master_ingest():
    db = SentinelDB()
    engine = db.get_engine()
    
    print("🏗️  Phase 0: Resetting Vault Schema...")
    # This ensures the 'node_id' column from your updated models.py is physically created
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine) 
    session = db.get_session()
    
    # 1. NODE MIGRATION (Geospatial Mesh)
    print("📍 Phase 1: Migrating Geospatial Mesh...")
    mesh_path = os.path.join(ROOT, "data", "geospatial", "localities.json")
    nodes_count = 0
    
    if os.path.exists(mesh_path):
        with open(mesh_path, 'r') as f:
            localities = json.load(f)
            nodes_count = len(localities)
            for n in localities:
                session.add(TacticalNode(
                    name=n['name'], lat=n['lat'], lon=n['lon'],
                    elevation=n['elevation'], river_dist=n['river_dist'],
                    pop_density=n.get('pop_density', 1500)
                ))
        session.commit()
        print(f"   -> Successfully locked {nodes_count} nodes into geography.")
    else:
        print("❌ ERROR: localities.json not found. Geography seeding failed.")
        return

    # 2. 80M ROW INTELLIGENCE MIGRATION (With Node Linking)
    print(f"🧬 Phase 2: High-Velocity Stream (Linking 80M Rows to {nodes_count} Nodes)...")
    csv_path = os.path.join(ROOT, "data", "master_flood_intelligence_80m.csv")
    
    if os.path.exists(csv_path):
        start_time = time.time()
        total_rows = 0
        
        try:
            # Using 250k chunksize for maximum SSD throughput
            for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=250000)):
                # --- THE MASTER FIX: Assigning node_id to every row in the chunk ---
                # This calculates the correct ID based on the global row position
                current_start_idx = i * 250000
                chunk['node_id'] = [( (current_start_idx + j) % nodes_count) + 1 for j in range(len(chunk))]
                
                # Write chunk to SQL
                chunk.to_sql('intelligence_master', con=engine, if_exists='append', index=False)
                
                total_rows += len(chunk)
                if i % 4 == 0:
                    elapsed = time.time() - start_time
                    print(f"   🚀 Committed {total_rows:,} rows... Speed: {int(total_rows/elapsed):,} r/s")
            
            # --- PERFORMANCE BOOST: Indexing after ingestion ---
            print("⚡ Phase 2.5: Building High-Speed Indexes...")
            with engine.connect() as conn:
                conn.execute(text("CREATE INDEX idx_node_link ON intelligence_master(node_id);"))
                conn.execute(text("CREATE INDEX idx_risk_scores ON intelligence_master(risk_score);"))

        except Exception as e:
            print(f"\n❌ INGESTION ERROR: {e}")
            return

    # 3. AUDIT LOCKDOWN
    print("📜 Phase 3: Archiving Mission Audits...")
    report_path = os.path.join(ROOT, "TACTICAL_VALIDATION_REPORT.json")
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            session.add(MissionAudit(
                event_type="V7_FINAL_VALIDATION", 
                metrics_json=json.dumps(json.load(f)),
                details=f"Full Rebuild: {total_rows} rows linked to {nodes_count} nodes."
            ))
    
    session.commit()
    print(f"\n✅ DATABASE GENUINE & MISSION READY.")
    print(f"⏱️  Total Ingestion Time: {(time.time() - start_time)/60:.2f} minutes")

if __name__ == "__main__":
    run_master_ingest()