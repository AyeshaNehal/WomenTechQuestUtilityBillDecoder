import pytest
import csv
import io
import json
from source.schema import Provider, ChargeType, TaxType, Level1, ExtractionResult, Extras, Charge
from source.facts import compute_facts
from source.safe_eval import safe_eval
from source.writer import write_level1_csv

def test_enum_mapping():
    assert Provider.KE == "KE"
    assert ChargeType.fpa == "fpa"
    assert TaxType.gst == "gst"

def test_validation_level1():
    # Number/date parsing is handled by pydantic automatically, but we can verify our models
    l1 = Level1(
        provider="KE",
        bill_month="2026-04",
        issue_date="2026-04-07",
        units_consumed=151.0,
        charges=[Charge(type="energy", amount=1054.0)],
        total_charges=1054.0
    )
    assert l1.provider == Provider.KE
    assert l1.units_consumed == 151.0
    assert l1.charges[0].amount == 1054.0

def test_facts_computation():
    res = ExtractionResult(
        level1=Level1(
            current_bill=1000.0,
            total_taxes=150.0,
            units_consumed=100.0,
            charges=[Charge(type="energy", amount=500.0)],
            total_charges=500.0,
            payable_within_due_date=1000.0,
            payable_after_due_date=1100.0
        ),
        extras=Extras(
            usage_history=[{"month": "Jan", "units": 250.0}, {"month": "Feb", "units": 150.0}]
        )
    )
    facts = compute_facts(res)
    assert facts['tax_share_of_current_bill'] == 0.15
    assert facts['average_cost_per_unit'] == 10.0
    assert facts['usage_max'] == 250.0
    assert facts['months_above_200'] == 1
    assert facts['late_payment_surcharge'] == 100.0

def test_safe_evaluator_valid():
    context = {'facts': {'usage_avg': 100}, 'level1': {'current_bill': 500}}
    # Math operations
    assert safe_eval("level1['current_bill'] / facts['usage_avg']", context) == 5.0
    assert safe_eval("max([10, 20, 30])", context) == 30
    assert safe_eval("round(10.555, 1)", context) == 10.6

def test_safe_evaluator_unsafe():
    context = {}
    # __import__ should fail
    res = safe_eval("__import__('os').system('echo 1')", context)
    assert "Error" in res or "not allowed" in res
    
    # open should fail
    res = safe_eval("open('test.txt', 'w')", context)
    assert "Error" in res or "not allowed" in res
    
    # exec should fail
    res = safe_eval("exec('a = 1')", context)
    assert "Error" in res or "not allowed" in res

def test_writer_csv_roundtrip(tmp_path):
    template = tmp_path / "level1_template.csv"
    with open(template, "w", newline="") as f:
        f.write("bill_id,json\ntest_001,\n")
        
    output = tmp_path / "level1_out.csv"
    
    res = ExtractionResult(
        level1=Level1(provider="KE", current_reading=9301.0, units_consumed=5.0), # 9301.0 should become 9301
        extras=Extras()
    )
    results = {"test_001": res}
    
    write_level1_csv(str(template), str(output), results)
    
    # Read it back
    with open(output, "r", newline="") as f:
        reader = list(csv.reader(f))
        assert reader[0] == ["bill_id", "json"]
        
        # Verify JSON survives quoting and whole numbers are ints
        row = reader[1]
        assert row[0] == "test_001"
        data = json.loads(row[1])
        assert data["provider"] == "KE"
        assert data["current_reading"] == 9301 # no .0
        assert data["units_consumed"] == 5
