import os
import shutil

def purge_athena_workspace():
    print("🧹 Initiating Athena Neural Core Purge...")
    
    # 1. Remove the main brain directory and all its contents
    brain_dir = "athena_brain"
    if os.path.exists(brain_dir):
        print(f"   ⏳ Deleting {brain_dir}/ and all neural weights. This may take a moment...")
        shutil.rmtree(brain_dir)
        print(f"   🗑️  Deleted directory tree: {brain_dir}/")
    else:
        print(f"   ℹ️  Directory already clean: {brain_dir}/")
        
    # 2. Remove the generated download script
    script_file = "download_athena_base.py"
    if os.path.exists(script_file):
        os.remove(script_file)
        print(f"   🗑️  Deleted script: {script_file}")
    else:
        print(f"   ℹ️  Script already clean: {script_file}")
        
    print("\n" + "="*60)
    print("✅ PURGE COMPLETE. The Athena workspace is now pristine.")
    print("We are ready to start over with a Platinum-Tier Persona.")
    print("="*60)

if __name__ == "__main__":
    purge_athena_workspace()