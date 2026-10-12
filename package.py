import os
import zipfile
import shutil
from pathlib import Path

def package():
    print("Building your-submission.zip...")
    

    zip_name = 'wtq2026Karachi_AyeshaNehal.zip'
    if os.path.exists(zip_name):
        os.remove(zip_name)
        
    def should_exclude(path_str):
        path_str = path_str.replace('\\', '/')
        if path_str.endswith('/.env') or path_str == '.env': return True
        if path_str.endswith('/usage_report.json') or path_str == 'usage_report.json': return True
        
        folders_to_exclude = ['cache', 'audit', '__pycache__', '.pytest_cache', 'venv']
        parts = path_str.split('/')
        for ex in folders_to_exclude:
            if ex in parts:
                return True
                
        if path_str.startswith('train/bills/') or path_str.startswith('test/bills/'): return True
        if 'tests/fixtures' in path_str: return True
        
        return False

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder in ['source', 'output', 'demo']:
            if not os.path.exists(folder): continue
            for root, dirs, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    if not should_exclude(full_path):
                        zf.write(full_path, full_path)
                        
    print("\n=== Zip Contents ===")
    with zipfile.ZipFile(zip_name, 'r') as zf:
        for info in zf.infolist():
            print(f"{info.file_size:10d}  {info.filename}")

    size_bytes = os.path.getsize(zip_name)
    size_mb = size_bytes / (1024 * 1024)
    print(f"\n=== File Size Check ===")
    print(f"Size: {size_mb:.2f} MB")
    
    if size_mb > 15.0:
        print("[WARNING] Zip file exceeds 15 MB (expected if including video).")
    else:
        print("[PASS] Zip file is under 15 MB.")

if __name__ == '__main__':
    package()
