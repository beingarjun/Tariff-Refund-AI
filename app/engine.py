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
    tariff_rates: list[TariffRate],
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
        matched_rate = _find_matching_rate(shipment, tariff_rates)

        notes = []
        exclusion_applied = exclusion is not None
        exclusion_reason = exclusion.reason if exclusion else None
        confidence_score = 0.6

        if exclusion:
            expected_duty = 0.0
            applied_rate = 0.0
            notes.append("Exclusion rule matched")
            confidence_score = 0.95
        elif matched_rate:
            applied_rate = matched_rate.rate_percent
            expected_duty = shipment.declared_value * (applied_rate / 100.0)
            notes.append("Tariff rate matched")
            confidence_score = 0.9
        else:
            applied_rate = 0.0
            expected_duty = shipment.duty_paid
            notes.append("No matching tariff rate; assumed paid amount as expected")
            confidence_score = 0.5

        refundable = max(0.0, shipment.duty_paid - expected_duty)
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

