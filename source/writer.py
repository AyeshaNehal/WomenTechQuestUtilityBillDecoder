import csv
import json
import math
from typing import Dict, Any

def format_number(v: Any) -> Any:
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
        if v.is_integer():
            return int(v)
    return v

def clean_dict(d: dict) -> dict:
    cleaned = {}
    for k, v in d.items():
        if isinstance(v, dict):
            cleaned[k] = clean_dict(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_dict(i) if isinstance(i, dict) else format_number(i) for i in v]
        else:
            cleaned[k] = format_number(v)
    return cleaned

def write_level1_csv(template_path: str, output_path: str, results: Dict[str, Any]):
    with open(template_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL)
        
        header = next(reader)
        writer.writerow(header)
        
        for row in reader:
            if not row: continue
            bill_id = row[0]
            if bill_id in results and results[bill_id]:
                # Force all keys to be present, null if missing, numbers as ints if whole
                l1_dict = results[bill_id].level1.model_dump(exclude_unset=False, exclude_none=False)
                cleaned = clean_dict(l1_dict)
                json_str = json.dumps(cleaned, separators=(',', ':'))
                writer.writerow([bill_id, json_str])
            else:
                # Full null schema
                from source.schema import Level1
                null_dict = Level1().model_dump()
                cleaned = clean_dict(null_dict)
                writer.writerow([bill_id, json.dumps(cleaned, separators=(',', ':'))])

def write_level2_csv(template_path: str, output_path: str, results: Dict[str, Dict[str, str]]):
    with open(template_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL)
        
        header = next(reader)
        writer.writerow(header)
        
        for row in reader:
            if not row or len(row) < 3: continue
            bill_id = row[0]
            q_id = row[1]
            question = row[2]
            
            ans = "Information unavailable."
            if bill_id in results and q_id in results[bill_id]:
                ans = results[bill_id][q_id]
                
            writer.writerow([bill_id, q_id, question, ans])
