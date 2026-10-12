from typing import Dict, Any
from source.schema import ExtractionResult

def compute_facts(result: ExtractionResult) -> Dict[str, Any]:
    l1 = result.level1
    ext = result.extras
    
    facts = {}
    
    # Safely compute percentages and averages
    if l1.current_bill and l1.current_bill > 0:
        facts['tax_share_of_current_bill'] = (l1.total_taxes or 0) / l1.current_bill
    else:
        facts['tax_share_of_current_bill'] = 0.0

    if l1.units_consumed and l1.units_consumed > 0:
        facts['average_cost_per_unit'] = (l1.current_bill or 0) / l1.units_consumed
        facts['average_energy_cost_per_unit'] = sum(c.amount for c in l1.charges if c.type == 'energy') / l1.units_consumed
    else:
        facts['average_cost_per_unit'] = 0.0
        facts['average_energy_cost_per_unit'] = 0.0

    # Charge shares
    total_chg = l1.total_charges or 0
    if total_chg > 0:
        for c in l1.charges:
            facts[f'share_of_charge_{c.type}'] = facts.get(f'share_of_charge_{c.type}', 0) + (c.amount / total_chg)
            
    # Usage history stats
    if ext.usage_history:
        units = [u.units for u in ext.usage_history]
        facts['usage_max'] = max(units)
        facts['usage_min'] = min(units)
        facts['usage_avg'] = sum(units) / len(units)
        facts['months_above_200'] = sum(1 for u in units if u > 200)
        facts['months_above_300'] = sum(1 for u in units if u > 300)
        
        # Change vs last month (assuming last in history is last month)
        if len(units) >= 1:
            last_month_units = units[-1]
            current = l1.units_consumed or 0
            facts['usage_change_vs_last_month'] = current - last_month_units

    # Late payment difference
    if l1.payable_after_due_date is not None and l1.payable_within_due_date is not None:
        facts['late_payment_surcharge'] = l1.payable_after_due_date - l1.payable_within_due_date
    else:
        facts['late_payment_surcharge'] = None

    return facts
