import math
from typing import List, Tuple
from .schema import ExtractionResult

def validate_extraction(result: ExtractionResult, image_path: str = None) -> ExtractionResult:
    # Advisory checks
    warnings = []
    
    l1 = result.level1
    
    # Check charges sum
    if l1.charges and l1.total_charges is not None:
        sum_charges = sum(c.amount for c in l1.charges)
        if not math.isclose(sum_charges, l1.total_charges, abs_tol=1.0):
            warnings.append(f"sum(charges) {sum_charges} != total_charges {l1.total_charges}")
            
    # Check taxes sum
    if l1.taxes and l1.total_taxes is not None:
        sum_taxes = sum(t.amount for t in l1.taxes)
        if not math.isclose(sum_taxes, l1.total_taxes, abs_tol=1.0):
            warnings.append(f"sum(taxes) {sum_taxes} != total_taxes {l1.total_taxes}")
            
    # Check units consumed
    if l1.current_reading is not None and l1.previous_reading is not None and l1.units_consumed is not None:
        diff = l1.current_reading - l1.previous_reading
        if not math.isclose(diff, l1.units_consumed, abs_tol=1.0):
            warnings.append(f"current - previous ({diff}) != units_consumed ({l1.units_consumed})")
            
    # Check payable amounts
    if l1.payable_after_due_date is not None and l1.payable_within_due_date is not None:
        if l1.payable_after_due_date < l1.payable_within_due_date:
            warnings.append(f"payable_after {l1.payable_after_due_date} < payable_within {l1.payable_within_due_date}")

    if warnings:
        print(f"Validation warnings for {image_path}:")
        for w in warnings:
            print(f"  - {w}")
        # TODO: Implement 1 targeted re-read if needed
        # We never overwrite printed values with math, so we just log it.
        
    return result
