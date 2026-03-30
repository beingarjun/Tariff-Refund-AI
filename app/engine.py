from __future__ import annotations

from dataclasses import asdict
from datetime import date

from app.models import ExclusionRule, RefundResult, ShipmentRecord, TariffRate


def _is_date_in_range(value: date, start: date, end: date) -> bool:
    return start <= value <= end


def _find_matching_rate(shipment: ShipmentRecord, tariff_rates: list[TariffRate]) -> TariffRate | None:
    for rate in tariff_rates:
        if (
            rate.hts_code == shipment.hts_code
            and rate.country_of_origin.lower() == shipment.country_of_origin.lower()
            and _is_date_in_range(shipment.import_date, rate.start_date, rate.end_date)
        ):
            return rate
    return None


def _find_matching_exclusion(shipment: ShipmentRecord, exclusions: list[ExclusionRule]) -> ExclusionRule | None:
    for exclusion in exclusions:
        if (
            exclusion.hts_code == shipment.hts_code
            and exclusion.country_of_origin.lower() == shipment.country_of_origin.lower()
            and _is_date_in_range(shipment.import_date, exclusion.start_date, exclusion.end_date)
        ):
            return exclusion
    return None


def _round_currency(value: float) -> float:
    return round(value + 1e-9, 2)


def analyze_refunds(
    shipments: list[ShipmentRecord],
    previous_tariff_rates: list[TariffRate],
    present_tariff_rates: list[TariffRate],
    exclusions: list[ExclusionRule] | None = None,
) -> dict:
    exclusions = exclusions or []
    results: list[RefundResult] = []

    total_paid = 0.0
    total_expected = 0.0
    total_refundable = 0.0
    likely_refunds = 0

    for shipment in shipments:
        total_paid += shipment.duty_paid
        exclusion = _find_matching_exclusion(shipment, exclusions)
        previous_rate = _find_matching_rate(shipment, previous_tariff_rates)
        present_rate = _find_matching_rate(shipment, present_tariff_rates)

        notes = []
        exclusion_applied = exclusion is not None
        exclusion_reason = exclusion.reason if exclusion else None
        confidence_score = 0.7

        if exclusion:
            prev_rate_percent = previous_rate.rate_percent if previous_rate else 0.0
            present_rate_percent = 0.0
            notes.append("Exclusion rule matched")
            confidence_score = 0.95
        elif previous_rate and present_rate:
            prev_rate_percent = previous_rate.rate_percent
            present_rate_percent = present_rate.rate_percent
            notes.append("Previous and present tariff rates matched")
            confidence_score = 0.9
        elif present_rate:
            prev_rate_percent = 0.0
            present_rate_percent = present_rate.rate_percent
            notes.append("Only present tariff rate matched")
            confidence_score = 0.75
        elif previous_rate:
            prev_rate_percent = previous_rate.rate_percent
            present_rate_percent = previous_rate.rate_percent
            notes.append("Present tariff missing; reused previous rate")
            confidence_score = 0.65
        else:
            prev_rate_percent = 0.0
            present_rate_percent = 0.0
            notes.append("No matching tariff rate; assumed paid amount as expected")
            confidence_score = 0.5

        applied_rate = present_rate_percent
        rate_reduction_points = max(0.0, prev_rate_percent - present_rate_percent)

        expected_duty = shipment.declared_value * (present_rate_percent / 100.0)
        if not present_rate and not exclusion:
            expected_duty = shipment.duty_paid

        refundable_by_rate = shipment.declared_value * (rate_reduction_points / 100.0)
        refundable_by_paid = max(0.0, shipment.duty_paid - expected_duty)
        refundable = min(refundable_by_rate, refundable_by_paid) if rate_reduction_points > 0 else refundable_by_paid

        if prev_rate_percent > 0:
            return_percentage = (rate_reduction_points / prev_rate_percent) * 100.0
        else:
            return_percentage = 0.0

        if refundable > 0:
            likely_refunds += 1

        expected_duty = _round_currency(expected_duty)
        refundable = _round_currency(refundable)

        total_expected += expected_duty
        total_refundable += refundable

        results.append(
            RefundResult(
                entry_id=shipment.entry_id,
                importer=shipment.importer,
                import_date=shipment.import_date,
                hts_code=shipment.hts_code,
                country_of_origin=shipment.country_of_origin,
                declared_value=_round_currency(shipment.declared_value),
                duty_paid=_round_currency(shipment.duty_paid),
                expected_duty=expected_duty,
                refundable_amount=refundable,
                previous_rate_percent=_round_currency(prev_rate_percent),
                present_rate_percent=_round_currency(present_rate_percent),
                rate_reduction_percent_points=_round_currency(rate_reduction_points),
                return_percentage=_round_currency(return_percentage),
                applied_rate_percent=_round_currency(applied_rate),
                exclusion_applied=exclusion_applied,
                exclusion_reason=exclusion_reason,
                confidence_score=round(confidence_score, 2),
                notes="; ".join(notes),
            )
        )

    ordered = sorted(results, key=lambda row: row.refundable_amount, reverse=True)

    return {
        "summary": {
            "shipment_count": len(shipments),
            "likely_refund_entries": likely_refunds,
            "total_duty_paid": _round_currency(total_paid),
            "total_expected_duty": _round_currency(total_expected),
            "total_potential_refund": _round_currency(total_refundable),
        },
        "results": [
            {
                **asdict(row),
                "import_date": row.import_date.isoformat(),
            }
            for row in ordered
        ],
    }
