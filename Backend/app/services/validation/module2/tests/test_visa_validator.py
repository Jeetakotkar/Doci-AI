import unittest

from module2.validators.visa_validator import VisaValidator


class TestVisaValidator(unittest.TestCase):

    def test_valid_visa(self):
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

        validator = VisaValidator()
        result = validator.validate(input_data, passport_data)

        self.assertEqual(result["document_type"], "VISA")
        self.assertIn(
            result["overall_status"],
            ["VALID", "REVIEW", "INVALID"]
        )

        self.assertGreater(result["summary"]["total_checks"], 0)

    def test_invalid_visa(self):
        input_data = {
            "document_type": "VISA",
            "visa_number": "",
            "visa_type": "",
            "issue_date": "2027-01-01",
            "valid_from": "2027-01-01",
            "expiry_date": "2026-01-01",
            "entry_type": "UNKNOWN",
            "stay_duration_days": -10
        }

        validator = VisaValidator()
        result = validator.validate(input_data)

        self.assertEqual(result["document_type"], "VISA")
        self.assertEqual(result["overall_status"], "INVALID")

        self.assertGreater(result["summary"]["failed"], 0)


if __name__ == "__main__":
    unittest.main()