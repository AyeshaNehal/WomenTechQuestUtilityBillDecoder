import os
from pathlib import Path
from source import extract, validate
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def format_value(v):
    if v is None: return "null"
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)

def run():
    bills_dir = Path("train/bills")
    # IESCO_0004.jpg is cached from previous run, let's process the others
    images = [p for p in bills_dir.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    
    for img_path in images:
        if img_path.name == "IESCO_0004.jpg":
            print(f"\nSkipping {img_path.name} (already processed and reviewed).")
            continue
            
        print(f"\nProcessing {img_path.name}...")
        try:
            result = extract.extract_bill_data(str(img_path), use_cache=True)
            result = validate.validate_extraction(result, str(img_path))
            
            l1 = result.level1
            
            print(f"| Field | Extracted Value |")
            print(f"|---|---|")
            print(f"| Provider | {format_value(l1.provider)} |")
            print(f"| Tariff | {format_value(l1.tariff)} |")
            print(f"| Sanctioned Load | {format_value(l1.sanctioned_load_kw)} |")
            print(f"| Bill Month | {format_value(l1.bill_month)} |")
            print(f"| Reading Date | {format_value(l1.reading_date)} |")
            print(f"| Issue Date | {format_value(l1.issue_date)} |")
            print(f"| Due Date | {format_value(l1.due_date)} |")
            print(f"| Previous Reading | {format_value(l1.previous_reading)} |")
            print(f"| Current Reading | {format_value(l1.current_reading)} |")
            print(f"| Units Consumed | {format_value(l1.units_consumed)} |")
            
            for i, c in enumerate(l1.charges):
                print(f"| Charge {i+1} ({c.type}) | {format_value(c.amount)} |")
            
            print(f"| Total Charges | {format_value(l1.total_charges)} |")
            
            for i, t in enumerate(l1.taxes):
                print(f"| Tax {i+1} ({t.type}) | {format_value(t.amount)} |")
                
            print(f"| Total Taxes | {format_value(l1.total_taxes)} |")
            print(f"| Current Bill | {format_value(l1.current_bill)} |")
            print(f"| Arrears | {format_value(l1.arrears)} |")
            print(f"| Payable Within Due Date | {format_value(l1.payable_within_due_date)} |")
            print(f"| Payable After Due Date | {format_value(l1.payable_after_due_date)} |")
            
        except Exception as e:
            print(f"Failed to process {img_path.name}: {e}")

if __name__ == '__main__':
    run()
