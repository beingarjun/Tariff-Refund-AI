import unittest
from datetime import date

from app.engine import analyze_refunds
from app.models import ExclusionRule, ShipmentRecord, TariffRate


class TestRefundEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.shipments = [
            ShipmentRecord(
                entry_id="E-001",
                importer="Acme Imports",
                import_date=date(2025, 1, 10),
                hts_code="8501.10.40",
                declared_value=10000.0,
                country_of_origin="CN",
                duty_paid=3500.0,
                quantity=50,
            )
        ]
        self.rates = [
            TariffRate(
                hts_code="8501.10.40",
                country_of_origin="CN",
                start_date=date(2024, 1, 1),
                end_date=date(2025, 12, 31),
                rate_percent=35.0,
            )
        ]
        self.present_rates = [
            TariffRate(
                hts_code="8501.10.40",
                country_of_origin="CN",
                start_date=date(2024, 1, 1),
                end_date=date(2025, 12, 31),
                rate_percent=20.0,
            )
        ]

    def test_refund_with_matching_rate(self) -> None:
        output = analyze_refunds(self.shipments, self.rates, self.present_rates, [])
        self.assertEqual(output["summary"]["shipment_count"], 1)
        self.assertEqual(output["summary"]["total_expected_duty"], 2000.0)
        self.assertEqual(output["summary"]["total_potential_refund"], 1500.0)
        self.assertEqual(output["results"][0]["refundable_amount"], 1500.0)
        self.assertEqual(output["results"][0]["return_percentage"], 42.86)

    def test_exclusion_overrides_rate(self) -> None:
        exclusions = [
            ExclusionRule(
                hts_code="8501.10.40",
                country_of_origin="CN",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 6, 30),
                reason="Temporary exclusion",
            )
        ]
        output = analyze_refunds(self.shipments, self.rates, self.present_rates, exclusions)
        self.assertEqual(output["summary"]["total_expected_duty"], 0.0)
        self.assertEqual(output["summary"]["total_potential_refund"], 3500.0)
        self.assertTrue(output["results"][0]["exclusion_applied"])
        self.assertEqual(output["results"][0]["return_percentage"], 100.0)

    def test_no_matching_rate_defaults_to_no_refund(self) -> None:
        output = analyze_refunds(self.shipments, [], [], [])
        self.assertEqual(output["summary"]["total_potential_refund"], 0.0)
        self.assertEqual(output["results"][0]["expected_duty"], 3500.0)


if __name__ == "__main__":
    unittest.main()
