from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Provider(str, Enum):
    KE = "KE"
    LESCO = "LESCO"
    IESCO = "IESCO"

class ChargeType(str, Enum):
    energy = "energy"
    fixed = "fixed"
    fpa = "fpa"
    quarterly_adjustment = "quarterly_adjustment"
    surcharge = "surcharge"
    meter_rent = "meter_rent"
    subsidy = "subsidy"
    other = "other"

class TaxType(str, Enum):
    gst = "gst"
    electricity_duty = "electricity_duty"
    income_tax = "income_tax"
    municipal_tax = "municipal_tax"
    other_tax = "other_tax"

class Charge(BaseModel):
    type: ChargeType
    amount: float

class Tax(BaseModel):
    type: TaxType
    amount: float

class Level1(BaseModel):
    provider: Optional[Provider] = None
    tariff: Optional[str] = None
    sanctioned_load_kw: Optional[float] = None
    bill_month: Optional[str] = None
    reading_date: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    units_consumed: Optional[float] = None
    charges: List[Charge] = Field(default_factory=list)
    total_charges: Optional[float] = None
    taxes: List[Tax] = Field(default_factory=list)
    total_taxes: Optional[float] = None
    current_bill: Optional[float] = None
    arrears: Optional[float] = None
    payable_within_due_date: Optional[float] = None
    payable_after_due_date: Optional[float] = None

class UsageHistory(BaseModel):
    month: str
    units: float

class BillingHistoryRow(BaseModel):
    month: str
    units: Optional[float] = None
    amount_billed: Optional[float] = None
    amount_paid: Optional[float] = None

class LineItem(BaseModel):
    name: str
    section: str
    units: Optional[float] = None
    rate: Optional[float] = None
    amount: float

class LatePaymentLine(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None

class PercentageSplit(BaseModel):
    category: str
    percentage: float
    amount: Optional[float] = None

class TariffSlab(BaseModel):
    slab_name: str
    units: float
    rate: float
    amount: float

class PrintedTotal(BaseModel):
    description: str
    amount: float

class Extras(BaseModel):
    usage_history: List[UsageHistory] = Field(default_factory=list)
    billing_history_rows: List[BillingHistoryRow] = Field(default_factory=list)
    bill_calculation_lines: List[LineItem] = Field(default_factory=list)
    late_payment_lines: List[LatePaymentLine] = Field(default_factory=list)
    printed_percentage_splits: List[PercentageSplit] = Field(default_factory=list)
    message_board_text: Optional[str] = None
    mdi_readings: Optional[float] = None
    tariff_slab_details: List[TariffSlab] = Field(default_factory=list)
    printed_totals: List[PrintedTotal] = Field(default_factory=list)

class ExtractionResult(BaseModel):
    level1: Level1
    extras: Extras
