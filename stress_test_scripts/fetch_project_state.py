import os
import json

# --- CONFIGURATION ---
OUTPUT_FILE = "project_snapshot.json"
# Directories to ignore to save RAM and avoid binary noise
EXCLUDE_DIRS = {'venv', '.git', '__pycache__', 'node_modules', 'brain', 'logs', '.vscode', 'data'}
# Extensions to ignore (Binary, Large Data, Models)
EXCLUDE_EXTS = {'.csv', '.npy', '.keras', '.png', '.jpg', '.jpeg', '.db', '.sqlite', '.pyc', '.exe'}

def generate_snapshot():
    print("🔍 Starting Project Discovery (Python Optimized)...")
    root_dir = os.getcwd()
    print(f"📂 Target: {root_dir}")
    
    snapshot = {}
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            # Skip the output file and this script
            if file == OUTPUT_FILE or file == "fetch_project_state.py":
                continue
                
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            # Check extension
            _, ext = os.path.splitext(file)
            if ext.lower() in EXCLUDE_EXTS:
                continue
                
            print(f"📄 Reading: {relative_path}")
            
            try:
                # Read text content with UTF-8, ignoring errors for safety
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    snapshot[relative_path] = f.read()
            except Exception as e:
                print(f"⚠️  Skipping {relative_path} due to error: {e}")

    # Write the final JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2)

    print("-" * 50)
    print(f"✅ SUCCESS: Project state saved to {OUTPUT_FILE}")
    print("📎 You can now share the content of this file with me.")
    print("-" * 50)

if __name__ == "__main__":
    generate_snapshot()