import sqlite3

DB_PATH = r"C:\HUFP_SENTINEL_V6\tactical_db\sentinel_v7_tactical.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table exists and print its columns
    cursor.execute("PRAGMA table_info(intelligence_master);")
    columns = cursor.fetchall()
    
    if not columns:
        print("Table 'intelligence_master' not found! Here are the tables that DO exist:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(f" -> {t[0]}")
    else:
        print("✅ Table 'intelligence_master' found. Here are the EXACT column names:")
        for col in columns:
            print(f" -> {col[1]} (Type: {col[2]})")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")