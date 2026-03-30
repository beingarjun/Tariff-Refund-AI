from __future__ import annotations

import csv
from io import StringIO


def build_report_csv(analysis: dict) -> str:
    fields = [
        "entry_id",
        "importer",
        "import_date",
        "hts_code",
        "country_of_origin",
        "declared_value",
        "duty_paid",
        "expected_duty",
        "refundable_amount",
        "applied_rate_percent",
        "exclusion_applied",
        "exclusion_reason",
        "confidence_score",
        "notes",
    ]

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in analysis["results"]:
        writer.writerow(row)
    return output.getvalue()

