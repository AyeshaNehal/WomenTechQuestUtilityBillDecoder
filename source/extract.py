import os
import json
from . import config
from . import cache
from . import preprocess
from .schema import ExtractionResult
from .providers.google import generate_structured

def load_glossary(provider: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if provider == "ALL":
        glo_ke = open(os.path.join(base_dir, 'prompts', 'glossary_ke.md')).read()
        glo_lesco = open(os.path.join(base_dir, 'prompts', 'glossary_lesco.md')).read()
        glo_iesco = open(os.path.join(base_dir, 'prompts', 'glossary_iesco.md')).read()
        return f"{glo_ke}\n{glo_lesco}\n{glo_iesco}"
    
    path = os.path.join(base_dir, 'prompts', f'glossary_{provider.lower()}.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def extract_bill_data(image_path: str, use_cache: bool = True) -> ExtractionResult:
    filename = os.path.basename(image_path)
    prefix = filename.split('_')[0].upper()
    
    if prefix == 'KESC':
        provider_glossary = load_glossary('KE')
    elif prefix in ('LESCO', 'IESCO'):
        provider_glossary = load_glossary(prefix)
    else:
        provider_glossary = load_glossary('ALL')

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
9. `total_charges` and `total_taxes` must be copied ONLY from a printed subtotal label for the charges or taxes section. Never copy `current_bill` or any other total into them. If no subtotal is printed, return null.

EXTRACTION WORKFLOW:
First, list every bill-calculation line in order within `extras.bill_calculation_lines`.
Then, map those lines into `level1.charges` and `level1.taxes` based strictly on the printed section they appear in.
Do not classify based on the line's name alone; use the printed section (charges vs taxes).

GLOSSARY (for mapping charge and tax types):
{provider_glossary}
"""

    image_bytes = preprocess.preprocess_image(image_path)
    
    cache_key = ""
    if use_cache:
        cache_key = cache.get_cache_key(
            image_bytes, 
            prompt, 
            config.MODEL_NAME, 
            config.EXTRACTION_PROMPT_VERSION
        )
        cached_result = cache.read_cache(cache_key)
        if cached_result:
            return ExtractionResult.model_validate(cached_result)

    result = generate_structured(prompt, image_bytes, ExtractionResult, task_name=config.EXTRACTION_PROMPT_VERSION)
    
    # Save to audit
    audit_path = os.path.join(config.AUDIT_DIR, f"{os.path.splitext(filename)[0]}.json")
    with open(audit_path, 'w', encoding='utf-8') as f:
        f.write(result.model_dump_json(indent=2))
        
    if use_cache and cache_key:
        cache.write_cache(cache_key, result.model_dump())
        
    return result
