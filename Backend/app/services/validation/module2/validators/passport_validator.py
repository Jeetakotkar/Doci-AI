# backend/module2/validators/passport_validator.py

from datetime import date, datetime
from typing import Any

from module2.schemas import (
    CheckStatus,
    OverallStatus,
    Severity,
    ValidationCheck,
)


class PassportValidator:
    """
    Module 2 - Passport Validation

    Responsibility:
        Validate already-extracted passport information.

    This validator does NOT:
        - perform OCR
        - perform face recognition
        - inspect image pixels
        - detect photo manipulation
        - directly access government databases
        - declare a document definitively fake

    It produces deterministic, explainable validation results.
    """

    MRZ_LINE_LENGTH = 44
    MRZ_LINE_COUNT = 2

    MRZ_ALLOWED_CHARACTERS = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    )

    # ICAO MRZ check-digit character weights.
    MRZ_WEIGHTS = [7, 3, 1]

    SUPPORTED_SEX_VALUES = {"M", "F", "X", "<"}

    def __init__(self):
        self.checks: list[ValidationCheck] = []

    # ---------------------------------------------------------
    # PUBLIC ENTRY POINT
    # ---------------------------------------------------------

    def validate(self, passport_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate a passport record produced by Module 1.

        Expected input example:

        {
            "document_type": "PASSPORT",
            "passport_number": "P1234567",
            "name": "DOE<<JOHN",
            "nationality": "IND",
            "date_of_birth": "1995-05-20",
            "expiry_date": "2030-05-19",
            "sex": "M",
            "mrz": [
                "P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P1234567<8IND9505205M3005198<<<<<<<<<<<<<<04"
            ]
        }
        """

        self.checks = []

        # Basic document validation
        self._validate_document_type(passport_data)
        self._validate_required_fields(passport_data)

        # Individual field validation
        self._validate_passport_number(passport_data)
        self._validate_name(passport_data)
        self._validate_nationality(passport_data)
        self._validate_date_of_birth(passport_data)
        self._validate_expiry_date(passport_data)
        self._validate_sex(passport_data)

        # MRZ validation
        mrz = passport_data.get("mrz")

        if mrz:
            self._validate_mrz(mrz, passport_data)
        else:
            self._add_check(
                rule_id="PAS-MRZ-001",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Machine-readable zone (MRZ) is missing.",
                field="mrz",
            )

        return self._build_result()

    # ---------------------------------------------------------
    # BASIC VALIDATION
    # ---------------------------------------------------------

    def _validate_document_type(self, data: dict[str, Any]) -> None:
        document_type = self._normalize(data.get("document_type"))

        if document_type == "PASSPORT":
            self._add_check(
                rule_id="COMMON-001",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Document type is supported.",
                field="document_type",
            )
        else:
            self._add_check(
                rule_id="COMMON-001",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Input document is not identified as a passport.",
                field="document_type",
            )

    def _validate_required_fields(self, data: dict[str, Any]) -> None:
        required_fields = [
            "passport_number",
            "name",
            "nationality",
            "date_of_birth",
            "expiry_date",
            "sex",
        ]

        missing = [
            field
            for field in required_fields
            if not self._has_value(data.get(field))
        ]

        if not missing:
            self._add_check(
                rule_id="COMMON-004",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="All required passport fields are present.",
            )
            return

        self._add_check(
            rule_id="COMMON-004",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            message="Required passport fields are missing.",
            details={"missing_fields": missing},
        )

    # ---------------------------------------------------------
    # PASSPORT NUMBER
    # ---------------------------------------------------------

    def _validate_passport_number(self, data: dict[str, Any]) -> None:
        passport_number = self._normalize(
            data.get("passport_number")
        )

        if not passport_number:
            return

        if not self._is_reasonable_passport_number(passport_number):
            self._add_check(
                rule_id="PAS-NUM-002",
                status=CheckStatus.FAIL,
                severity=Severity.MEDIUM,
                message="Passport number contains invalid characters or has an unreasonable length.",
                field="passport_number",
                details={"value": passport_number},
            )
            return

        self._add_check(
            rule_id="PAS-NUM-002",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Passport number has a structurally reasonable format.",
            field="passport_number",
        )

    # ---------------------------------------------------------
    # NAME
    # ---------------------------------------------------------

    def _validate_name(self, data: dict[str, Any]) -> None:
        name = self._normalize(data.get("name"))

        if not name:
            return

        # Allow letters, spaces, hyphens, apostrophes and <.
        allowed = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            " -'<"
        )

        invalid_chars = sorted(
            {char for char in name if char not in allowed}
        )

        if invalid_chars:
            self._add_check(
                rule_id="PAS-NAME-002",
                status=CheckStatus.FAIL,
                severity=Severity.MEDIUM,
                message="Passport name contains unexpected characters.",
                field="name",
                details={"invalid_characters": invalid_chars},
            )
        else:
            self._add_check(
                rule_id="PAS-NAME-002",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Passport name has a reasonable character structure.",
                field="name",
            )

    # ---------------------------------------------------------
    # NATIONALITY
    # ---------------------------------------------------------

    def _validate_nationality(self, data: dict[str, Any]) -> None:
        nationality = self._normalize(data.get("nationality"))

        if not nationality:
            return

        if len(nationality) != 3 or not nationality.isalpha():
            self._add_check(
                rule_id="PAS-NAT-002",
                status=CheckStatus.FAIL,
                severity=Severity.MEDIUM,
                message="Nationality should contain a three-letter country code.",
                field="nationality",
                details={"value": nationality},
            )
            return

        self._add_check(
            rule_id="PAS-NAT-002",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Nationality uses a three-letter code.",
            field="nationality",
        )

    # ---------------------------------------------------------
    # DATE OF BIRTH
    # ---------------------------------------------------------

    def _validate_date_of_birth(self, data: dict[str, Any]) -> None:
        dob = self._parse_date(data.get("date_of_birth"))

        if dob is None:
            self._add_check(
                rule_id="PAS-DOB-001",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Date of birth could not be parsed.",
                field="date_of_birth",
            )
            return

        self._add_check(
            rule_id="PAS-DOB-001",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Date of birth is parseable.",
            field="date_of_birth",
        )

        if dob > date.today():
            self._add_check(
                rule_id="PAS-DOB-002",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Date of birth is in the future.",
                field="date_of_birth",
            )
        else:
            self._add_check(
                rule_id="PAS-DOB-002",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Date of birth is not in the future.",
                field="date_of_birth",
            )

    # ---------------------------------------------------------
    # EXPIRY DATE
    # ---------------------------------------------------------

    def _validate_expiry_date(self, data: dict[str, Any]) -> None:
        expiry = self._parse_date(data.get("expiry_date"))

        if expiry is None:
            self._add_check(
                rule_id="PAS-EXP-001",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Passport expiry date could not be parsed.",
                field="expiry_date",
            )
            return

        self._add_check(
            rule_id="PAS-EXP-001",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Passport expiry date is parseable.",
            field="expiry_date",
        )

        if expiry < date.today():
            self._add_check(
                rule_id="PAS-EXP-002",
                status=CheckStatus.WARNING,
                severity=Severity.MEDIUM,
                message="Passport is expired.",
                field="expiry_date",
                details={
                    "expired_on": expiry.isoformat()
                },
            )
        else:
            self._add_check(
                rule_id="PAS-EXP-002",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Passport is currently within its stated validity period.",
                field="expiry_date",
            )

    # ---------------------------------------------------------
    # SEX
    # ---------------------------------------------------------

    def _validate_sex(self, data: dict[str, Any]) -> None:
        sex = self._normalize(data.get("sex"))

        if sex in self.SUPPORTED_SEX_VALUES:
            self._add_check(
                rule_id="PAS-SEX-001",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Sex field contains a supported MRZ-compatible value.",
                field="sex",
            )
        else:
            self._add_check(
                rule_id="PAS-SEX-001",
                status=CheckStatus.FAIL,
                severity=Severity.MEDIUM,
                message="Sex field contains an unsupported value.",
                field="sex",
                details={"value": sex},
            )

    # ---------------------------------------------------------
    # MRZ
    # ---------------------------------------------------------

    def _validate_mrz(
        self,
        mrz: Any,
        passport_data: dict[str, Any],
    ) -> None:

        if not isinstance(mrz, list) or len(mrz) != self.MRZ_LINE_COUNT:
            self._add_check(
                rule_id="PAS-MRZ-002",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Passport MRZ must contain exactly two lines.",
                field="mrz",
            )
            return

        line1 = str(mrz[0]).strip().upper()
        line2 = str(mrz[1]).strip().upper()

        # Structure
        if (
            len(line1) != self.MRZ_LINE_LENGTH
            or len(line2) != self.MRZ_LINE_LENGTH
        ):
            self._add_check(
                rule_id="PAS-MRZ-002",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="Passport TD3 MRZ lines must each contain 44 characters.",
                field="mrz",
                details={
                    "line1_length": len(line1),
                    "line2_length": len(line2),
                },
            )
            return

        self._add_check(
            rule_id="PAS-MRZ-002",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="MRZ has the expected two-line TD3 structure.",
            field="mrz",
        )

        # Character validation
        invalid_chars = sorted(
            {
                char
                for line in (line1, line2)
                for char in line
                if char not in self.MRZ_ALLOWED_CHARACTERS
            }
        )

        if invalid_chars:
            self._add_check(
                rule_id="PAS-MRZ-003",
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message="MRZ contains characters outside the allowed ICAO MRZ character set.",
                field="mrz",
                details={"invalid_characters": invalid_chars},
            )
            return

        self._add_check(
            rule_id="PAS-MRZ-003",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="MRZ character set is structurally valid.",
            field="mrz",
        )

        # Parse line 2
        mrz_passport_number = line2[0:9]
        passport_number_check_digit = line2[9]

        mrz_nationality = line2[10:13]

        mrz_dob = line2[13:19]
        dob_check_digit = line2[19]

        mrz_sex = line2[20]

        mrz_expiry = line2[21:27]
        expiry_check_digit = line2[27]

        # Composite field according to TD3 layout
        composite_data = (
            line2[0:10]
            + line2[13:20]
            + line2[21:43]
        )

        composite_check_digit = line2[43]

        # Check digits
        self._validate_mrz_check_digit(
            field="passport_number",
            value=mrz_passport_number,
            expected_digit=passport_number_check_digit,
            rule_id="PAS-MRZ-005",
        )

        self._validate_mrz_check_digit(
            field="date_of_birth",
            value=mrz_dob,
            expected_digit=dob_check_digit,
            rule_id="PAS-MRZ-006",
        )

        self._validate_mrz_check_digit(
            field="expiry_date",
            value=mrz_expiry,
            expected_digit=expiry_check_digit,
            rule_id="PAS-MRZ-007",
        )

        self._validate_mrz_check_digit(
            field="composite",
            value=composite_data,
            expected_digit=composite_check_digit,
            rule_id="PAS-MRZ-008",
        )

        # Cross-check visual fields against MRZ
        self._compare_passport_number(
            passport_data.get("passport_number"),
            mrz_passport_number,
        )

        self._compare_nationality(
            passport_data.get("nationality"),
            mrz_nationality,
        )

        self._compare_dob(
            passport_data.get("date_of_birth"),
            mrz_dob,
        )

        self._compare_expiry(
            passport_data.get("expiry_date"),
            mrz_expiry,
        )

        self._compare_sex(
            passport_data.get("sex"),
            mrz_sex,
        )

        self._compare_name(
            passport_data.get("name"),
            line1[5:44],
        )

    # ---------------------------------------------------------
    # MRZ CHECK DIGIT
    # ---------------------------------------------------------

    def _validate_mrz_check_digit(
        self,
        field: str,
        value: str,
        expected_digit: str,
        rule_id: str,
    ) -> None:

        if not expected_digit.isdigit():
            self._add_check(
                rule_id=rule_id,
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message=f"MRZ check digit for {field} is not numeric.",
                field=field,
            )
            return

        calculated = self._calculate_mrz_check_digit(value)

        if calculated == int(expected_digit):
            self._add_check(
                rule_id=rule_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message=f"MRZ check digit for {field} is valid.",
                field=field,
                details={
                    "calculated": calculated,
                    "provided": int(expected_digit),
                },
            )
        else:
            self._add_check(
                rule_id=rule_id,
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message=f"MRZ check digit for {field} is invalid.",
                field=field,
                details={
                    "calculated": calculated,
                    "provided": int(expected_digit),
                },
            )

    @classmethod
    def _calculate_mrz_check_digit(cls, value: str) -> int:
        """
        ICAO MRZ check digit calculation.

        Character values:
            0-9 -> numeric value
            A-Z -> 10-35
            <   -> 0

        Weights:
            7, 3, 1 repeating
        """

        total = 0

        for index, character in enumerate(value):
            character = character.upper()

            if character.isdigit():
                numeric_value = int(character)

            elif "A" <= character <= "Z":
                numeric_value = ord(character) - ord("A") + 10

            elif character == "<":
                numeric_value = 0

            else:
                raise ValueError(
                    f"Invalid MRZ character: {character}"
                )

            weight = cls.MRZ_WEIGHTS[index % 3]
            total += numeric_value * weight

        return total % 10

    # ---------------------------------------------------------
    # VISUAL <-> MRZ COMPARISONS
    # ---------------------------------------------------------

    def _compare_passport_number(
        self,
        visual_value: Any,
        mrz_value: str,
    ) -> None:

        visual = self._normalize(visual_value)
        mrz = mrz_value.replace("<", "")

        if visual == mrz:
            status = CheckStatus.PASS
            severity = Severity.INFO
            message = "Passport number matches the MRZ."
        else:
            status = CheckStatus.FAIL
            severity = Severity.HIGH
            message = "Passport number does not match the MRZ."

        self._add_check(
            rule_id="PAS-MRZ-009",
            status=status,
            severity=severity,
            message=message,
            field="passport_number",
            details={
                "visual": visual,
                "mrz": mrz,
            },
        )

    def _compare_nationality(
        self,
        visual_value: Any,
        mrz_value: str,
    ) -> None:

        visual = self._normalize(visual_value)
        mrz = self._normalize(mrz_value)

        self._comparison_check(
            rule_id="PAS-MRZ-010",
            field="nationality",
            visual=visual,
            mrz=mrz,
            message_prefix="Nationality",
        )

    def _compare_dob(
        self,
        visual_value: Any,
        mrz_value: str,
    ) -> None:

        visual_date = self._parse_date(visual_value)

        if visual_date is None:
            return

        expected_mrz = visual_date.strftime("%y%m%d")

        self._comparison_check(
            rule_id="PAS-MRZ-011",
            field="date_of_birth",
            visual=expected_mrz,
            mrz=mrz_value,
            message_prefix="Date of birth",
        )

    def _compare_expiry(
        self,
        visual_value: Any,
        mrz_value: str,
    ) -> None:

        visual_date = self._parse_date(visual_value)

        if visual_date is None:
            return

        expected_mrz = visual_date.strftime("%y%m%d")

        self._comparison_check(
            rule_id="PAS-MRZ-012",
            field="expiry_date",
            visual=expected_mrz,
            mrz=mrz_value,
            message_prefix="Expiry date",
        )

    def _compare_sex(
        self,
        visual_value: Any,
        mrz_value: str,
    ) -> None:

        visual = self._normalize(visual_value)

        # Normalize common visual representations.
        if visual in {"MALE", "MAN"}:
            visual = "M"
        elif visual in {"FEMALE", "WOMAN"}:
            visual = "F"

        self._comparison_check(
            rule_id="PAS-MRZ-013",
            field="sex",
            visual=visual,
            mrz=mrz_value,
            message_prefix="Sex",
        )

    def _compare_name(
        self,
        visual_value: Any,
        mrz_name: str,
    ) -> None:

        if not self._has_value(visual_value):
            return

        visual = self._normalize_name_for_comparison(
            str(visual_value)
        )

        mrz = self._normalize_name_for_comparison(
            mrz_name
        )

        if visual == mrz:
            self._add_check(
                rule_id="PAS-NAME-003",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="Name is consistent with the MRZ representation.",
                field="name",
            )
        else:
            self._add_check(
                rule_id="PAS-NAME-003",
                status=CheckStatus.WARNING,
                severity=Severity.MEDIUM,
                message="Name does not exactly match the normalized MRZ representation.",
                field="name",
                details={
                    "visual": visual,
                    "mrz": mrz,
                },
            )

    def _comparison_check(
        self,
        rule_id: str,
        field: str,
        visual: str,
        mrz: str,
        message_prefix: str,
    ) -> None:

        if visual == mrz:
            self._add_check(
                rule_id=rule_id,
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message=f"{message_prefix} matches the MRZ.",
                field=field,
            )
        else:
            self._add_check(
                rule_id=rule_id,
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                message=f"{message_prefix} does not match the MRZ.",
                field=field,
                details={
                    "visual": visual,
                    "mrz": mrz,
                },
            )

    # ---------------------------------------------------------
    # RESULT BUILDING
    # ---------------------------------------------------------

    def _build_result(self) -> dict[str, Any]:
        failures = [
            check
            for check in self.checks
            if check.status == CheckStatus.FAIL
        ]

        warnings = [
            check
            for check in self.checks
            if check.status == CheckStatus.WARNING
        ]

        if any(
            check.severity in {
                Severity.HIGH,
                Severity.CRITICAL,
            }
            for check in failures
        ):
            overall_status = OverallStatus.INVALID
        elif failures:
            overall_status = OverallStatus.INVALID
        elif warnings:
            overall_status = OverallStatus.REVIEW
        else:
            overall_status = OverallStatus.VALID

        return {
            "document_type": "PASSPORT",
            "overall_status": overall_status.value,
            "summary": {
                "total_checks": len(self.checks),
                "passed": sum(
                    c.status == CheckStatus.PASS
                    for c in self.checks
                ),
                "failed": sum(
                    c.status == CheckStatus.FAIL
                    for c in self.checks
                ),
                "warnings": sum(
                    c.status == CheckStatus.WARNING
                    for c in self.checks
                ),
                "not_checked": sum(
                    c.status == CheckStatus.NOT_CHECKED
                    for c in self.checks
                ),
            },
            "checks": [
                {
                    "rule_id": check.rule_id,
                    "status": check.status.value,
                    "severity": check.severity.value,
                    "message": check.message,
                    "field": check.field,
                    "details": check.details,
                }
                for check in self.checks
            ],
        }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _add_check(
        self,
        rule_id: str,
        status: CheckStatus,
        severity: Severity,
        message: str,
        field: str | None = None,
        details: Any = None,
    ) -> None:

        self.checks.append(
            ValidationCheck(
                rule_id=rule_id,
                status=status,
                severity=severity,
                message=message,
                field=field,
                details=details,
            )
        )

    @staticmethod
    def _normalize(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip().upper()

    @staticmethod
    def _has_value(value: Any) -> bool:
        return value is not None and str(value).strip() != ""

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if value is None:
            return None

        if isinstance(value, date):
            return value

        value = str(value).strip()

        formats = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def _is_reasonable_passport_number(value: str) -> bool:
        """
        Deliberately broad.

        Different countries and passport generations can use
        different passport-number formats.

        Country-specific rules can be added later through
        configuration rather than hardcoding one global pattern.
        """

        if not 6 <= len(value) <= 15:
            return False

        return value.isalnum()

    @staticmethod
    def _normalize_name_for_comparison(value: str) -> str:
        value = value.upper().strip()

        value = value.replace("<", " ")

        # Collapse repeated spaces.
        return " ".join(value.split())