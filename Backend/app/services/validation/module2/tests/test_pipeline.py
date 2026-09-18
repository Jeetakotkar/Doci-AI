import unittest

from app.services.validation.module2.pipeline import run_validation


class TestPipeline(unittest.TestCase):

    def test_passport(self):
        input_data = {
            "document_type": "PASSPORT",
            "passport_number": "P1234567",
            "name": "DOE<<JOHN",
            "nationality": "IND",
            "date_of_birth": "1995-05-20",
            "expiry_date": "2030-05-19",
            "sex": "M",
            "mrz": [
                "P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P1234567<1IND9505209M3005198<<<<<<<<<<<<<<01"
            ]
        }

        result = run_validation(input_data)

        self.assertEqual(result["document_type"], "PASSPORT")
        self.assertIn(
            result["overall_status"],
            ["VALID", "REVIEW", "INVALID"]
        )

    def test_visa(self):
        input_data = {
            "document_type": "VISA",
            "visa_number": "V12345678",
            "visa_type": "TOURIST",
            "issue_date": "2026-01-01",
            "valid_from": "2026-01-01",
            "expiry_date": "2026-12-31",
            "entry_type": "MULTIPLE",
            "stay_duration_days": 90,
            "passport_number": "P1234567",
            "name": "DOE<<JOHN",
            "nationality": "IND"
        }

        passport_data = {
            "passport_number": "P1234567",
            "name": "DOE<<JOHN",
            "nationality": "IND",
            "expiry_date": "2030-05-19"
        }

        result = run_validation(
            input_data,
            passport_data
        )

        self.assertEqual(result["document_type"], "VISA")

        self.assertIn(
            result["overall_status"],
            ["VALID", "REVIEW", "INVALID"]
        )

        self.assertGreater(
            result["summary"]["total_checks"],
            0
        )


if __name__ == "__main__":
    unittest.main()