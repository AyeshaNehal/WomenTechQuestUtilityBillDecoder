import os
from pathlib import Path
from source import extract, validate, cache, config
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def format_value(v):
    if v is None: return "null"
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)

def run():
    bills_dir = Path("train/bills")
    images = sorted([p for p in bills_dir.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')])
    
    api_calls = 0
    
    for img_path in images:
        print(f"\nProcessing {img_path.name}...")
        try:
            # Check if cache exists
            import hashlib
            from source.preprocess import preprocess_image
            image_bytes = preprocess_image(str(img_path))
            
            # Reconstruct prompt to check cache key
            filename = os.path.basename(str(img_path))
            prefix = filename.split('_')[0].upper()
            if prefix == 'KESC': provider_glossary = extract.load_glossary('KE')
            elif prefix in ('LESCO', 'IESCO'): provider_glossary = extract.load_glossary(prefix)
            else: provider_glossary = extract.load_glossary('ALL')

            prompt = f"""
You are a highly accurate utility bill extraction assistant. 
Extract the details from this electricity bill.
IMPORTANT RULES:
1. Extract values EXACTLY AS PRINTED. If a field like current_bill, arrears, or any other is blank or not printed, return null, not 0 and not a computed value.
2. Amounts must be pure numbers in PKR. Strip 'Rs.' and commas. 
3. Credits (e.g. '38209CR') and subsidies MUST be negative.
4. Record dates as YYYY-MM-DD or YYYY-MM (e.g. 22nd Sep 2026 -> 2026-09-22, MAR 2026 -> 2026-03).
5. Exclude ALL personal identifiers (names, addresses, CNIC, account/reference/consumer/meter numbers).
6. Copy tariff text exactly as printed, including letter case and brackets.
7. Any charge line labelled FPA or FCA, or described as fuel price/cost adjustment anywhere on the bill, MUST be type 'fpa', never 'other'.
8. Use null for unavailable values (blank, covered by grey box, unreadable). Do not guess.

EXTRACTION WORKFLOW:
First, list every bill-calculation line in order within `extras.bill_calculation_lines`.
Then, map those lines into `level1.charges` and `level1.taxes` based strictly on the printed section they appear in.
Do not classify based on the line's name alone; use the printed section (charges vs taxes).

GLOSSARY (for mapping charge and tax types):
{provider_glossary}
"""
            cache_key = cache.get_cache_key(image_bytes, prompt, config.MODEL_NAME, config.EXTRACTION_PROMPT_VERSION)
            if not cache.read_cache(cache_key):
                api_calls += 1

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
            
    print(f"\nTotal API Calls made: {api_calls}")

if __name__ == '__main__':
    run()
