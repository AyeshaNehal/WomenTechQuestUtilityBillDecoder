import os
import sys
import re
import csv
import json
import argparse
from pathlib import Path

def fail(msg):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)

def run_preflight(out_dir: Path, tpl_dir: Path):
    source_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 1. API key pattern check in source/
    print("Checking for exposed API keys...")
    key_pattern = re.compile(r'AIzaSy[A-Za-z0-9_-]{33}')
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.md') or file == '.env.example':
                path = Path(root) / file
                content = path.read_text(encoding='utf-8')
                if key_pattern.search(content):
                    fail(f"API key pattern found in {path.relative_to(source_dir)}")

    # 2. .env.example check
    print("Checking .env.example...")
    env_example = source_dir / '.env.example'
    if not env_example.exists():
        fail(".env.example is missing.")
    env_content = env_example.read_text()
    if 'MODEL_PROVIDER=google' not in env_content:
        fail("MODEL_PROVIDER=google missing from .env.example")
    if 'MODEL_NAME=gemini-3.5-flash-lite' not in env_content:
        fail("MODEL_NAME=gemini-3.5-flash-lite missing from .env.example")
    if 'API_KEY=' not in env_content or 'AIzaSy' in env_content:
        fail("API_KEY= must be a placeholder without real secrets in .env.example")

    # 3. requirements.txt fully pinned check
    print("Checking requirements.txt pinning...")
    req_txt = source_dir / 'requirements.txt'
    if not req_txt.exists():
        fail("requirements.txt missing.")
    for line in req_txt.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            if '==' not in line:
                fail(f"Unpinned requirement found: {line}")

    # 4. CSV output checks
    print("Checking CSV row counts and schema...")
    l1_out = out_dir / 'level1.csv'
    l2_out = out_dir / 'level2.csv'
    l1_tpl = tpl_dir / 'level1.csv'
    l2_tpl = tpl_dir / 'level2.csv'
    
    for f in [l1_out, l2_out, l1_tpl, l2_tpl]:
        if not f.exists():
            fail(f"Missing file: {f}")

    def read_csv(path):
        with open(path, 'r', encoding='utf-8') as f:
            return list(csv.reader(f))

    tpl_l1_data = read_csv(l1_tpl)
    tpl_l2_data = read_csv(l2_tpl)
    out_l1_data = read_csv(l1_out)
    out_l2_data = read_csv(l2_out)

    if len(tpl_l1_data) != len(out_l1_data):
        fail(f"level1.csv row count mismatch. Expected {len(tpl_l1_data)}, got {len(out_l1_data)}")
    if len(tpl_l2_data) != len(out_l2_data):
        fail(f"level2.csv row count mismatch. Expected {len(tpl_l2_data)}, got {len(out_l2_data)}")

    # Check identical headers and structure
    if tpl_l1_data[0] != out_l1_data[0]:
        fail("level1.csv header does not match template")
    if tpl_l2_data[0] != out_l2_data[0]:
        fail("level2.csv header does not match template")

    # Required Level 1 schema fields
    required_l1_keys = [
        "provider", "tariff", "sanctioned_load_kw", "bill_month", "reading_date", 
        "issue_date", "due_date", "previous_reading", "current_reading", 
        "units_consumed", "charges", "total_charges", "taxes", "total_taxes", 
        "current_bill", "arrears", "payable_within_due_date", "payable_after_due_date"
    ]

    for i in range(1, len(tpl_l1_data)):
        if out_l1_data[i][0] != tpl_l1_data[i][0]:
            fail(f"level1.csv bill_id mismatch at row {i+1}")
        
        json_str = out_l1_data[i][1].strip()
        if not json_str:
            fail(f"Empty json cell in level1.csv row {i+1}")
            
        try:
            data = json.loads(json_str)
            for k in required_l1_keys:
                if k not in data:
                    fail(f"Missing schema field '{k}' in level1 JSON for {out_l1_data[i][0]}")
        except json.JSONDecodeError:
            fail(f"Invalid JSON in level1.csv row {i+1}")

    for i in range(1, len(tpl_l2_data)):
        # Check bill_id, question_id, question
        if out_l2_data[i][:3] != tpl_l2_data[i][:3]:
            fail(f"level2.csv bill_id/q_id/question mismatch at row {i+1}")
            
        ans = out_l2_data[i][3].strip()
        if not ans:
            fail(f"Empty answer cell in level2.csv row {i+1}")

    print("[PASS] All preflight checks passed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, required=True)
    parser.add_argument('--templates', type=str, required=True)
    args = parser.parse_args()
    
    run_preflight(Path(args.out), Path(args.templates))
