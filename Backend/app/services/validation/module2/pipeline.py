from module2.validators.passport_validator import PassportValidator
from module2.validators.visa_validator import VisaValidator
from module2.validators.aadhaar_validator import AadhaarValidator


def run_validation(
    input_data: dict,
    passport_data: dict | None = None
) -> dict:
    document_type = input_data.get("document_type", "").upper()

    if document_type == "PASSPORT":
        validator = PassportValidator()
        return validator.validate(input_data)

    if document_type == "VISA":
        validator = VisaValidator()
        return validator.validate(
            input_data,
            passport_data
        )

    if document_type == "AADHAAR":
        validator = AadhaarValidator()
        return validator.validate(input_data)

    return {
        "document_type": document_type,
        "overall_status": "REVIEW",
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 1,
            "not_checked": 0
        },
        "checks": [
            {
                "rule_id": "PIPE-001",
                "status": "WARNING",
                "severity": "MEDIUM",
                "message": f"No validator implemented for {document_type}.",
                "field": "document_type"
            }
        ]
    }