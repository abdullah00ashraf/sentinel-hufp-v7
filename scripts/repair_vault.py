import sqlite3
import os

# Path to your database
DB_PATH = os.path.join("tactical_db", "sentinel_v7_tactical.db")

def repair_vault():
    if not os.path.exists(DB_PATH):
        print("❌ Database not found at path. Check your directory.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🛠️  SENTINEL V7.0 | Schema Repair Unit")
    print("="*40)

    try:
        # 1. Add the missing node_id column
        print("-> Adding 'node_id' column to intelligence_master...")
        cursor.execute("ALTER TABLE intelligence_master ADD COLUMN node_id INTEGER;")
        
        # 2. Add an index for high-speed map joins
        print("-> Creating tactical index for 80M-row joins...")
        cursor.execute("CREATE INDEX idx_node_link ON intelligence_master(node_id);")
        
        # 3. Optional: Link existing 80M rows to nodes (Demo Logic)
        # Since we have 2,025 nodes, we'll distribute the 80M rows across them
        print("-> Linking existing records to geospatial nodes (this is fast)...")
        cursor.execute("UPDATE intelligence_master SET node_id = (id % 2025) + 1 WHERE node_id IS NULL;")
        
        conn.commit()
        print("="*40)
        print("✅ REPAIR COMPLETE: Vault is now mission-compliant.")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  Column 'node_id' already exists. No action needed.")
        else:
            print(f"❌ SQLite Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    repair_vault()