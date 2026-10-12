import os
import argparse
from pathlib import Path
from source import cache, extract, validate, facts, explain, writer
import sys
import csv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run(args):
    if args.clear_cache:
        cache.clear_cache()
        print("Cache cleared.")
        
    bills_dir = Path(args.bills)
    if not bills_dir.exists():
        print(f"Bills directory not found: {bills_dir}")
        return
        
    templates_dir = None
    out_dir = None
    level2_questions = {}
    
    if args.templates:
        templates_dir = Path(args.templates)
        l2_tpl = templates_dir / 'level2.csv'
        if l2_tpl.exists():
            with open(l2_tpl, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if len(row) >= 3:
                        b_id, q_id, q_text = row[0], row[1], row[2]
                        if b_id not in level2_questions:
                            level2_questions[b_id] = []
                        level2_questions[b_id].append({'question_id': q_id, 'question': q_text})
                        
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        
    images = sorted([p for p in bills_dir.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')])
    
    if args.limit:
        images = images[:args.limit]
        
    results = {}
    level2_results = {}
    
    for img_path in images:
        bill_id = img_path.stem
        print(f"\nProcessing {bill_id}...")
        
        if args.dry_run:
            print("  Dry run, skipping API calls.")
            continue
            
        try:
            # Level 1 Extract & Validate
            res = extract.extract_bill_data(str(img_path), use_cache=not args.no_cache)
            res = validate.validate_extraction(res, str(img_path))
            results[bill_id] = res
            
            # Level 2 Facts & Explain
            if bill_id in level2_questions:
                computed_facts = facts.compute_facts(res)
                answers = explain.run_explain(level2_questions[bill_id], res, computed_facts)
                level2_results[bill_id] = answers
            
            if args.verify_rerun:
                print("  Verifying rerun...")
                res2 = extract.extract_bill_data(str(img_path), use_cache=False)
                if res.model_dump() == res2.model_dump():
                    print("  PASS: Rerun matches.")
                else:
                    print("  FAIL: Variance detected in rerun.")
                    
        except Exception as e:
            print(f"Failed to process {img_path.name}: {e}")
            results[bill_id] = None # Will cause null schema in writer
            
    if templates_dir and out_dir:
        writer.write_level1_csv(
            str(templates_dir / 'level1.csv'),
            str(out_dir / 'level1.csv'),
            results
        )
        writer.write_level2_csv(
            str(templates_dir / 'level2.csv'),
            str(out_dir / 'level2.csv'),
            level2_results
        )
        print(f"\nWrote CSVs to {out_dir}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bills', type=str, default='../train/bills')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--clear-cache', action='store_true')
    parser.add_argument('--verify-rerun', action='store_true')
    parser.add_argument('--templates', type=str)
    parser.add_argument('--out', type=str)
    
    args = parser.parse_args()
    run(args)
