from module2.validators.passport_validator import PassportValidator


def test_valid_passport():
    passport = {
        "document_type": "PASSPORT",
        "passport_number": "P1234567",
        "name": "DOE<<JOHN",
        "nationality": "IND",
        "date_of_birth": "1995-05-20",
        "expiry_date": "2030-05-19",
        "sex": "M",
        "mrz": [
            "P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            "P1234567<1IND9505209M3005198<<<<<<<<<<<<<<04",
        ],
    }

    validator = PassportValidator()
    result = validator.validate(passport)

    print("\nVALID PASSPORT RESULT")
    print(result)

    assert result["overall_status"] in {
        "VALID",
        "REVIEW",
    }


def test_passport_number_mismatch():
    passport = {
        "document_type": "PASSPORT",
        "passport_number": "P1234567",
        "name": "DOE<<JOHN",
        "nationality": "IND",
        "date_of_birth": "1995-05-20",
        "expiry_date": "2030-05-19",
        "sex": "M",
        "mrz": [
            "P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            "P9999999<8IND9505205M3005198<<<<<<<<<<<<<<04",
        ],
    }

    validator = PassportValidator()
    result = validator.validate(passport)

    print("\nPASSPORT NUMBER MISMATCH RESULT")
    print(result)

    failed_rules = [
        check["rule_id"]
        for check in result["checks"]
        if check["status"] == "FAIL"
    ]

    assert "PAS-MRZ-009" in failed_rules


def test_future_date_of_birth():
    passport = {
        "document_type": "PASSPORT",
        "passport_number": "P1234567",
        "name": "DOE<<JOHN",
        "nationality": "IND",
        "date_of_birth": "2035-01-01",
        "expiry_date": "2040-01-01",
        "sex": "M",
        "mrz": [],
    }

    validator = PassportValidator()
    result = validator.validate(passport)

    print("\nFUTURE DOB RESULT")
    print(result)

    failed_rules = [
        check["rule_id"]
        for check in result["checks"]
        if check["status"] == "FAIL"
    ]

    assert "PAS-DOB-002" in failed_rules


def test_missing_mrz():
    passport = {
        "document_type": "PASSPORT",
        "passport_number": "P1234567",
        "name": "DOE<<JOHN",
        "nationality": "IND",
        "date_of_birth": "1995-05-20",
        "expiry_date": "2030-05-19",
        "sex": "M",
    }

    validator = PassportValidator()
    result = validator.validate(passport)

    print("\nMISSING MRZ RESULT")
    print(result)

    failed_rules = [
        check["rule_id"]
        for check in result["checks"]
        if check["status"] == "FAIL"
    ]

    assert "PAS-MRZ-001" in failed_rules