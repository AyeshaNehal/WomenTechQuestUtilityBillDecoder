import json
import csv
import math
import argparse
from pathlib import Path

def evaluate(output_csv: str, expected_json: str, bill_id: str):
    with open(expected_json, 'r', encoding='utf-8') as f:
        expected = json.load(f)
        
    actual = None
    with open(output_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('bill_id') == bill_id:
                try:
                    actual = json.loads(row['json'])
                except:
                    print("Failed to parse JSON in output.")
                break
                
    if not actual:
        print(f"bill_id {bill_id} not found in {output_csv}")
        return
        
    # Compare
    keys_to_check = [
        "provider", "tariff", "sanctioned_load_kw", "bill_month", 
        "reading_date", "issue_date", "due_date", "previous_reading", 
        "current_reading", "units_consumed", "total_charges", 
        "total_taxes", "current_bill", "arrears", 
        "payable_within_due_date", "payable_after_due_date"
    ]
    
    score = 0
    total = len(keys_to_check) + 2 # +2 for charges list and taxes list
    
    print(f"--- Evaluation for {bill_id} ---")
    
    for k in keys_to_check:
        exp_val = expected.get(k)
        act_val = actual.get(k)
        
        if exp_val is None and act_val is None:
            score += 1
            print(f"PASS {k}: both null")
            continue
            
        if exp_val is None and act_val is not None:
            print(f"FAIL {k}: expected null, got {act_val}")
            continue
            
        if act_val is None and exp_val is not None:
            print(f"FAIL {k}: expected {exp_val}, got null")
            continue
            
        if isinstance(exp_val, (int, float)) and isinstance(act_val, (int, float)):
            if math.isclose(exp_val, act_val, abs_tol=1.0):
                score += 1
                print(f"PASS {k}: {act_val} ~= {exp_val}")
            else:
                print(f"FAIL {k}: {act_val} != {exp_val}")
        else:
            if str(exp_val).strip() == str(act_val).strip():
                score += 1
                print(f"PASS {k}: {act_val} == {exp_val}")
            else:
                print(f"FAIL {k}: {act_val} != {exp_val}")

    # Check charges and taxes arrays loosely by sum and type count
    def check_array(arr_name):
        nonlocal score
        exp_arr = expected.get(arr_name, [])
        act_arr = actual.get(arr_name, [])
        
        exp_sum = sum(x.get('amount', 0) for x in exp_arr)
        act_sum = sum(x.get('amount', 0) for x in act_arr)
        
        if math.isclose(exp_sum, act_sum, abs_tol=1.0) and len(exp_arr) == len(act_arr):
            score += 1
            print(f"PASS {arr_name}: lengths match ({len(exp_arr)}) and sums match ({act_sum} ~= {exp_sum})")
        else:
            print(f"FAIL {arr_name}: expected len {len(exp_arr)} sum {exp_sum}, got len {len(act_arr)} sum {act_sum}")

    check_array('charges')
    check_array('taxes')
    
    print(f"--- Final Score: {score}/{total} ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--expected', type=str, required=True)
    parser.add_argument('--bill-id', type=str, required=True)
    args = parser.parse_args()
    evaluate(args.output, args.expected, args.bill_id)
