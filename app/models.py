from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class ShipmentRecord:
    entry_id: str
    importer: str
    import_date: date
    hts_code: str
    declared_value: float
    country_of_origin: str
    duty_paid: float
    quantity: float


@dataclass(frozen=True)
class TariffRate:
    hts_code: str
    country_of_origin: str
    start_date: date
    end_date: date
    rate_percent: float


@dataclass(frozen=True)
class ExclusionRule:
    hts_code: str
    country_of_origin: str
    start_date: date
    end_date: date
    reason: str


@dataclass(frozen=True)
class RefundResult:
    entry_id: str
    importer: str
    import_date: date
    hts_code: str
    country_of_origin: str
    declared_value: float
    duty_paid: float
    expected_duty: float
    refundable_amount: float
    previous_rate_percent: float
    present_rate_percent: float
    rate_reduction_percent_points: float
    return_percentage: float
    applied_rate_percent: float
    exclusion_applied: bool
    exclusion_reason: Optional[str]
    confidence_score: float
    notes: str
