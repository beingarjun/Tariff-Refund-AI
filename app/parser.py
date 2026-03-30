from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from typing import Iterable, List

from app.models import ExclusionRule, ShipmentRecord, TariffRate


class ParseError(ValueError):
    pass


def _parse_date(raw: str, field_name: str) -> datetime.date:
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ParseError(f"Invalid date for '{field_name}': {raw}") from exc


def _parse_float(raw: str, field_name: str) -> float:
    try:
        return float(raw.strip())
    except ValueError as exc:
        raise ParseError(f"Invalid number for '{field_name}': {raw}") from exc


def _validate_columns(actual: Iterable[str], required: List[str], source_name: str) -> None:
    actual_set = {col.strip() for col in actual}
    missing = [col for col in required if col not in actual_set]
    if missing:
        raise ParseError(f"{source_name} missing required columns: {', '.join(missing)}")


def parse_shipments(csv_text: str) -> list[ShipmentRecord]:
    reader = csv.DictReader(StringIO(csv_text))
    required = [
        "entry_id",
        "importer",
        "import_date",
        "hts_code",
        "declared_value",
        "country_of_origin",
        "duty_paid",
        "quantity",
    ]
    _validate_columns(reader.fieldnames or [], required, "shipments.csv")

    records: list[ShipmentRecord] = []
    for row in reader:
        records.append(
            ShipmentRecord(
                entry_id=row["entry_id"].strip(),
                importer=row["importer"].strip(),
                import_date=_parse_date(row["import_date"], "import_date"),
                hts_code=row["hts_code"].strip(),
                declared_value=_parse_float(row["declared_value"], "declared_value"),
                country_of_origin=row["country_of_origin"].strip(),
                duty_paid=_parse_float(row["duty_paid"], "duty_paid"),
                quantity=_parse_float(row["quantity"], "quantity"),
            )
        )
    return records


def parse_tariff_rates(csv_text: str) -> list[TariffRate]:
    reader = csv.DictReader(StringIO(csv_text))
    required = ["hts_code", "country_of_origin", "start_date", "end_date", "rate_percent"]
    _validate_columns(reader.fieldnames or [], required, "tariff_rates.csv")

    records: list[TariffRate] = []
    for row in reader:
        records.append(
            TariffRate(
                hts_code=row["hts_code"].strip(),
                country_of_origin=row["country_of_origin"].strip(),
                start_date=_parse_date(row["start_date"], "start_date"),
                end_date=_parse_date(row["end_date"], "end_date"),
                rate_percent=_parse_float(row["rate_percent"], "rate_percent"),
            )
        )
    return records


def parse_exclusions(csv_text: str) -> list[ExclusionRule]:
    reader = csv.DictReader(StringIO(csv_text))
    required = ["hts_code", "country_of_origin", "start_date", "end_date", "reason"]
    _validate_columns(reader.fieldnames or [], required, "exclusions.csv")

    records: list[ExclusionRule] = []
    for row in reader:
        records.append(
            ExclusionRule(
                hts_code=row["hts_code"].strip(),
                country_of_origin=row["country_of_origin"].strip(),
                start_date=_parse_date(row["start_date"], "start_date"),
                end_date=_parse_date(row["end_date"], "end_date"),
                reason=row["reason"].strip(),
            )
        )
    return records

