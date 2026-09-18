from datetime import date, datetime
import re

from module2.rules.aadhaar_rules import AADHAAR_RULES
from module2.schemas import CheckStatus, OverallStatus, Severity, ValidationCheck


class AadhaarValidator:
    """
    Deterministic validation engine for Aadhaar-related extracted data.

    Input:
        Structured data produced by Module 1 (OCR/extraction).

    Output:
        A list of validation checks plus an overall status.

    Important:
        This validator does NOT establish Aadhaar authenticity by itself.
        Secure QR / Offline e-KYC cryptographic verification is kept as a
        separate integration point for authorized verification workflows.
    """

    SUPPORTED_REPRESENTATIONS = {
        "AADHAAR",
        "AADHAAR_LETTER",
        "E_AADHAAR",
        "AADHAAR_PVC",
        "M_AADHAAR",
        "MASKED_AADHAAR",
    }

    # Prototype thresholds only.
    OCR_CONFIDENCE_PASS = 0.85
    OCR_CONFIDENCE_WARNING = 0.60

    # Aadhaar Verhoeff multiplication table.
    _D = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]

    # Verhoeff permutation table.
    _P = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, data: dict) -> dict:
        """
        Validate an extracted Aadhaar document.

        Expected high-level input:

        {
            "document_id": "DOC-001",
            "document_type": "AADHAAR",
            "fields": {
                "aadhaar_number": "...",
                "name": "...",
                "date_of_birth": "...",
                "year_of_birth": "...",
                "gender": "...",
                "address": "...",
                "pincode": "...",
                "state": "..."
            },
            "ocr_confidence": 0.96,
            "status": "SUCCESS"
        }
        """

        checks = []

        fields = data.get("fields") or {}

        checks.append(self._check_document_type(data))
        checks.append(self._check_ocr_status(data))
        checks.append(self._check_ocr_confidence(data))

        checks.extend(self._validate_aadhaar_number(fields))
        checks.extend(self._validate_identity(fields))
        checks.extend(self._validate_address(fields))
        checks.extend(self._validate_document(data, fields))

        # QR/e-KYC fields are optional. If supplied, validate the
        # consistency/availability information we can evaluate locally.
        checks.extend(self._validate_qr_data(data, fields))
        checks.extend(self._validate_ekyc_data(data, fields))

        overall_status = self._calculate_overall_status(checks)

        summary = {
            "total_checks": len(checks),
            "passed": sum(1 for check in checks if check.status == CheckStatus.PASS),
            "failed": sum(1 for check in checks if check.status == CheckStatus.FAIL),
            "warnings": sum(1 for check in checks if check.status == CheckStatus.WARNING),
            "not_checked": sum(1 for check in checks if check.status == CheckStatus.NOT_CHECKED),
        }

        result = {
            "document_type": "AADHAAR",
            "overall_status": overall_status.value,
            "summary": summary,
            "checks": [
                {
                    "rule_id": check.rule_id,
                    "status": check.status.value,
                    "severity": check.severity.value,
                    "message": check.message,
                    "field": check.field,
                    "details": check.details,
                }
                for check in checks
            ],
        }

        document_id = data.get("document_id")
        if document_id is not None:
            result["document_id"] = document_id

        return result

    # ------------------------------------------------------------------
    # Common validation
    # ------------------------------------------------------------------

    def _check_document_type(self, data: dict) -> ValidationCheck:
        document_type = str(data.get("document_type", "")).upper().strip()

        if document_type == "AADHAAR":
            return ValidationCheck(
                "COMMON-001",
                CheckStatus.PASS,
                Severity.INFO,
                "Document type is Aadhaar.",
                "document_type",
            )

        return ValidationCheck(
            "COMMON-001",
            CheckStatus.FAIL,
            Severity.HIGH,
            "Document type is not Aadhaar.",
            "document_type",
        )

    def _check_ocr_status(self, data: dict) -> ValidationCheck:
        status = str(data.get("status", "")).upper().strip()

        if status == "SUCCESS":
            return ValidationCheck(
                "COMMON-002",
                CheckStatus.PASS,
                Severity.INFO,
                "OCR extraction completed successfully.",
                "status",
            )

        if not status:
            return ValidationCheck(
                "COMMON-002",
                CheckStatus.WARNING,
                Severity.HIGH,
                "OCR extraction status is missing.",
                "status",
            )

        return ValidationCheck(
            "COMMON-002",
            CheckStatus.WARNING,
            Severity.HIGH,
            f"OCR extraction status is '{status}'. Validation may be incomplete.",
            "status",
        )

    def _check_ocr_confidence(self, data: dict) -> ValidationCheck:
        confidence = data.get("ocr_confidence")

        if confidence is None:
            return ValidationCheck(
                "COMMON-003",
                CheckStatus.NOT_CHECKED,
                Severity.MEDIUM,
                "OCR confidence was not provided.",
                "ocr_confidence",
            )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            return ValidationCheck(
                "COMMON-003",
                CheckStatus.FAIL,
                Severity.MEDIUM,
                "OCR confidence is not a valid numeric value.",
                "ocr_confidence",
            )

        if confidence >= self.OCR_CONFIDENCE_PASS:
            return ValidationCheck(
                "COMMON-003",
                CheckStatus.PASS,
                Severity.INFO,
                f"OCR confidence is {confidence:.2f}.",
                "ocr_confidence",
            )

        if confidence >= self.OCR_CONFIDENCE_WARNING:
            return ValidationCheck(
                "COMMON-003",
                CheckStatus.WARNING,
                Severity.MEDIUM,
                f"OCR confidence is {confidence:.2f}; manual review may be appropriate.",
                "ocr_confidence",
            )

        return ValidationCheck(
            "COMMON-003",
            CheckStatus.WARNING,
            Severity.HIGH,
            f"OCR confidence is low ({confidence:.2f}); extracted values should not be treated as authoritative.",
            "ocr_confidence",
        )

    # ------------------------------------------------------------------
    # Aadhaar number
    # ------------------------------------------------------------------

    def _validate_aadhaar_number(self, fields: dict) -> list:
        checks = []

        raw_number = fields.get("aadhaar_number")

        if raw_number is None or not str(raw_number).strip():
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-001",
                    CheckStatus.FAIL,
                    Severity.HIGH,
                    "Aadhaar number is missing.",
                    "aadhaar_number",
                )
            )
            return checks

        number = self._normalize_aadhaar_number(raw_number)

        # Masked Aadhaar
        if "*" in str(raw_number) or "X" in str(raw_number).upper():
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-006",
                    CheckStatus.WARNING,
                    Severity.MEDIUM,
                    "Masked Aadhaar representation detected; complete Aadhaar number is unavailable.",
                    "aadhaar_number",
                )
            )

            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-002",
                    CheckStatus.NOT_CHECKED,
                    Severity.HIGH,
                    "Complete 12-digit validation cannot be performed on a masked Aadhaar number.",
                    "aadhaar_number",
                )
            )

            return checks

        if len(number) != 12:
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-002",
                    CheckStatus.FAIL,
                    Severity.HIGH,
                    "Aadhaar number must contain exactly 12 digits.",
                    "aadhaar_number",
                )
            )
            return checks

        checks.append(
            ValidationCheck(
                "AADHAAR-NUM-002",
                CheckStatus.PASS,
                Severity.INFO,
                "Aadhaar number contains exactly 12 digits.",
                "aadhaar_number",
            )
        )

        if not number.isdigit():
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-003",
                    CheckStatus.FAIL,
                    Severity.HIGH,
                    "Aadhaar number contains non-numeric characters.",
                    "aadhaar_number",
                )
            )
            return checks

        checks.append(
            ValidationCheck(
                "AADHAAR-NUM-003",
                CheckStatus.PASS,
                Severity.INFO,
                "Aadhaar number contains numeric digits only.",
                "aadhaar_number",
            )
        )

        if self._verhoeff_validate(number):
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-004",
                    CheckStatus.PASS,
                    Severity.INFO,
                    "Aadhaar number passes the Verhoeff checksum.",
                    "aadhaar_number",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-004",
                    CheckStatus.FAIL,
                    Severity.HIGH,
                    "Aadhaar number failed the Verhoeff checksum.",
                    "aadhaar_number",
                )
            )

        if self._looks_like_placeholder(number):
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-005",
                    CheckStatus.WARNING,
                    Severity.MEDIUM,
                    "Aadhaar number resembles an obvious repeated or placeholder pattern.",
                    "aadhaar_number",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-NUM-005",
                    CheckStatus.PASS,
                    Severity.INFO,
                    "No obvious repeated/placeholder Aadhaar number pattern detected.",
                    "aadhaar_number",
                )
            )

        return checks

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def _validate_identity(self, fields: dict) -> list:
        checks = []

        name = fields.get("name")

        if not name or not str(name).strip():
            checks.append(
                ValidationCheck(
                    "AADHAAR-ID-001",
                    CheckStatus.FAIL,
                    Severity.HIGH,
                    "Aadhaar holder name is missing.",
                    "name",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ID-001",
                    CheckStatus.PASS,
                    Severity.INFO,
                    "Aadhaar holder name is present.",
                    "name",
                )
            )

            if self._is_reasonable_text(name):
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-002",
                        CheckStatus.PASS,
                        Severity.INFO,
                        "Name contains plausible textual content.",
                        "name",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-002",
                        CheckStatus.WARNING,
                        Severity.MEDIUM,
                        "Name contains unusual or potentially corrupted OCR content.",
                        "name",
                    )
                )

            if self._has_control_or_invalid_characters(name):
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-003",
                        CheckStatus.WARNING,
                        Severity.LOW,
                        "Name contains characters that may indicate OCR corruption.",
                        "name",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-003",
                        CheckStatus.PASS,
                        Severity.INFO,
                        "Name character structure is acceptable.",
                        "name",
                    )
                )

        dob = fields.get("date_of_birth")
        yob = fields.get("year_of_birth")

        if dob:
            parsed_dob = self._parse_date(dob)

            if parsed_dob is None:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-004",
                        CheckStatus.FAIL,
                        Severity.HIGH,
                        "Date of birth is not a valid calendar date.",
                        "date_of_birth",
                    )
                )
            elif parsed_dob > date.today():
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-004",
                        CheckStatus.FAIL,
                        Severity.HIGH,
                        "Date of birth cannot be in the future.",
                        "date_of_birth",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-004",
                        CheckStatus.PASS,
                        Severity.INFO,
                        "Date of birth is a valid non-future date.",
                        "date_of_birth",
                    )
                )

        elif yob:
            try:
                year = int(str(yob).strip())

                if len(str(yob).strip()) != 4:
                    raise ValueError

                if year > date.today().year:
                    checks.append(
                        ValidationCheck(
                            "AADHAAR-ID-005",
                            CheckStatus.FAIL,
                            Severity.HIGH,
                            "Year of birth cannot be in the future.",
                            "year_of_birth",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            "AADHAAR-ID-005",
                            CheckStatus.PASS,
                            Severity.INFO,
                            "Year of birth is structurally valid.",
                            "year_of_birth",
                        )
                    )

            except (ValueError, TypeError):
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-005",
                        CheckStatus.FAIL,
                        Severity.HIGH,
                        "Year of birth must be a valid four-digit year.",
                        "year_of_birth",
                    )
                )

        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ID-004",
                    CheckStatus.NOT_CHECKED,
                    Severity.HIGH,
                    "Date/year of birth was not provided.",
                    "date_of_birth",
                )
            )

        # DOB ↔ YOB consistency
        if dob and yob:
            parsed_dob = self._parse_date(dob)

            try:
                year = int(str(yob).strip())
            except (TypeError, ValueError):
                year = None

            if parsed_dob and year:
                if parsed_dob.year == year:
                    checks.append(
                        ValidationCheck(
                            "AADHAAR-ID-006",
                            CheckStatus.PASS,
                            Severity.INFO,
                            "Date of birth and year of birth are consistent.",
                            "date_of_birth",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            "AADHAAR-ID-006",
                            CheckStatus.FAIL,
                            Severity.HIGH,
                            "Date of birth and year of birth contradict each other.",
                            "date_of_birth",
                        )
                    )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ID-006",
                    CheckStatus.NOT_CHECKED,
                    Severity.MEDIUM,
                    "Both DOB and YOB were not available for consistency checking.",
                    "date_of_birth",
                )
            )

        # Gender
        gender = fields.get("gender")

        if not gender:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ID-007",
                    CheckStatus.NOT_CHECKED,
                    Severity.MEDIUM,
                    "Gender was not provided.",
                    "gender",
                )
            )
        else:
            normalized_gender = self._normalize_gender(gender)

            if normalized_gender in {"MALE", "FEMALE", "OTHER", "UNSPECIFIED"}:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-007",
                        CheckStatus.PASS,
                        Severity.INFO,
                        "Gender value is recognized.",
                        "gender",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ID-007",
                        CheckStatus.WARNING,
                        Severity.MEDIUM,
                        f"Unrecognized gender representation: {gender}.",
                        "gender",
                    )
                )

        return checks

    # ------------------------------------------------------------------
    # Address
    # ------------------------------------------------------------------

    def _validate_address(self, fields: dict) -> list:
        checks = []

        address = fields.get("address")

        if not address:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ADDR-001",
                    CheckStatus.NOT_CHECKED,
                    Severity.MEDIUM,
                    "Address was not provided by OCR.",
                    "address",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ADDR-001",
                    CheckStatus.PASS,
                    Severity.INFO,
                    "Address is present.",
                    "address",
                )
            )

            if self._is_reasonable_text(address):
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ADDR-003",
                        CheckStatus.PASS,
                        Severity.INFO,
                        "Address contains plausible textual content.",
                        "address",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ADDR-003",
                        CheckStatus.WARNING,
                        Severity.LOW,
                        "Address contains unusual or potentially corrupted OCR content.",
                        "address",
                    )
                )

        pincode = fields.get("pincode")

        if not pincode:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ADDR-002",
                    CheckStatus.NOT_CHECKED,
                    Severity.MEDIUM,
                    "PIN code was not provided.",
                    "pincode",
                )
            )
        else:
            normalized_pin = re.sub(r"\D", "", str(pincode))

            if re.fullmatch(r"\d{6}", normalized_pin):
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ADDR-002",
                        CheckStatus.PASS,
                        Severity.INFO,
                        "PIN code contains exactly six digits.",
                        "pincode",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-ADDR-002",
                        CheckStatus.FAIL,
                        Severity.MEDIUM,
                        "Indian PIN code must contain exactly six digits.",
                        "pincode",
                    )
                )

        # We intentionally don't hardcode a state list here.
        # It should eventually come from a versioned reference dataset.
        state = fields.get("state")

        if state:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ADDR-004",
                    CheckStatus.WARNING,
                    Severity.MEDIUM,
                    "State/UT was extracted; reference-data validation is not yet connected.",
                    "state",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-ADDR-004",
                    CheckStatus.NOT_CHECKED,
                    Severity.MEDIUM,
                    "State/UT was not provided.",
                    "state",
                )
            )

        return checks

    # ------------------------------------------------------------------
    # Document representation
    # ------------------------------------------------------------------

    def _validate_document(self, data: dict, fields: dict) -> list:
        checks = []

        representation = (
            fields.get("document_representation")
            or data.get("document_representation")
        )

        if representation:
            normalized = str(representation).upper().strip()

            if normalized in self.SUPPORTED_REPRESENTATIONS:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-DOC-001",
                        CheckStatus.PASS,
                        Severity.INFO,
                        f"Aadhaar representation '{normalized}' is supported.",
                        "document_representation",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        "AADHAAR-DOC-001",
                        CheckStatus.WARNING,
                        Severity.MEDIUM,
                        f"Unknown Aadhaar representation '{representation}'.",
                        "document_representation",
                    )
                )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-DOC-001",
                    CheckStatus.NOT_CHECKED,
                    Severity.MEDIUM,
                    "Aadhaar representation was not specified.",
                    "document_representation",
                )
            )

        # Aadhaar does not use passport-style expiry validation.
        checks.append(
            ValidationCheck(
                "AADHAAR-DOC-002",
                CheckStatus.PASS,
                Severity.INFO,
                "Passport-style expiry validation is not applied to Aadhaar.",
                "document_type",
            )
        )

        # We keep this flexible because Aadhaar representations differ.
        checks.append(
            ValidationCheck(
                "AADHAAR-DOC-003",
                CheckStatus.PASS,
                Severity.INFO,
                "Aadhaar validation uses representation-specific fields rather than a universal expiry requirement.",
                "document_type",
            )
        )

        checks.append(
            ValidationCheck(
                "AADHAAR-DOC-004",
                CheckStatus.PASS,
                Severity.INFO,
                "Available Aadhaar fields were processed using normalized comparisons.",
                "document_type",
            )
        )

        return checks

    # ------------------------------------------------------------------
    # Secure QR
    # ------------------------------------------------------------------

    def _validate_qr_data(self, data: dict, fields: dict) -> list:
        checks = []

        qr = data.get("secure_qr") or fields.get("secure_qr")

        if not qr:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-001",
                    CheckStatus.NOT_CHECKED,
                    Severity.HIGH,
                    "Secure QR data was not supplied.",
                    "secure_qr",
                )
            )
            return checks

        qr_present = qr.get("available", True)

        if qr_present:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-001",
                    CheckStatus.PASS,
                    Severity.INFO,
                    "Secure QR data is available for verification.",
                    "secure_qr",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-001",
                    CheckStatus.WARNING,
                    Severity.HIGH,
                    "Secure QR was expected but was not available.",
                    "secure_qr",
                )
            )

        # These are integration hooks, not fake local verification.
        signature_valid = qr.get("signature_valid")

        if signature_valid is True:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-002",
                    CheckStatus.PASS,
                    Severity.CRITICAL,
                    "Secure QR digital signature was reported as valid by the verification adapter.",
                    "secure_qr",
                )
            )
        elif signature_valid is False:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-002",
                    CheckStatus.FAIL,
                    Severity.CRITICAL,
                    "Secure QR digital signature verification failed.",
                    "secure_qr",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-002",
                    CheckStatus.NOT_CHECKED,
                    Severity.CRITICAL,
                    "Secure QR cryptographic signature verification is not connected.",
                    "secure_qr",
                )
            )

        integrity_valid = qr.get("integrity_valid")

        if integrity_valid is True:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-003",
                    CheckStatus.PASS,
                    Severity.CRITICAL,
                    "Secure QR data integrity was verified by the verification adapter.",
                    "secure_qr",
                )
            )
        elif integrity_valid is False:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-003",
                    CheckStatus.FAIL,
                    Severity.CRITICAL,
                    "Secure QR data integrity verification failed.",
                    "secure_qr",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-QR-003",
                    CheckStatus.NOT_CHECKED,
                    Severity.CRITICAL,
                    "Secure QR data integrity verification is not connected.",
                    "secure_qr",
                )
            )

        return checks

    # ------------------------------------------------------------------
    # Offline e-KYC
    # ------------------------------------------------------------------

    def _validate_ekyc_data(self, data: dict, fields: dict) -> list:
        checks = []

        ekyc = data.get("offline_ekyc") or fields.get("offline_ekyc")

        if not ekyc:
            checks.append(
                ValidationCheck(
                    "AADHAAR-EKYC-001",
                    CheckStatus.NOT_CHECKED,
                    Severity.HIGH,
                    "Offline e-KYC XML was not supplied.",
                    "offline_ekyc",
                )
            )
            return checks

        checks.append(
            ValidationCheck(
                "AADHAAR-EKYC-001",
                CheckStatus.PASS,
                Severity.INFO,
                "Offline e-KYC data is available for verification.",
                "offline_ekyc",
            )
        )

        signature_valid = ekyc.get("signature_valid")

        if signature_valid is True:
            checks.append(
                ValidationCheck(
                    "AADHAAR-EKYC-002",
                    CheckStatus.PASS,
                    Severity.CRITICAL,
                    "Offline e-KYC digital signature was reported as valid by the verification adapter.",
                    "offline_ekyc",
                )
            )
        elif signature_valid is False:
            checks.append(
                ValidationCheck(
                    "AADHAAR-EKYC-002",
                    CheckStatus.FAIL,
                    Severity.CRITICAL,
                    "Offline e-KYC digital signature verification failed.",
                    "offline_ekyc",
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    "AADHAAR-EKYC-002",
                    CheckStatus.NOT_CHECKED,
                    Severity.CRITICAL,
                    "Offline e-KYC cryptographic verification is not connected.",
                    "offline_ekyc",
                )
            )

        return checks

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_aadhaar_number(value) -> str:
        return re.sub(r"\D", "", str(value))

    @staticmethod
    def _parse_date(value):
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
    def _is_reasonable_text(value) -> bool:
        if not value:
            return False

        value = str(value).strip()

        if len(value) < 2:
            return False

        if not re.search(r"[A-Za-z]", value):
            return False

        if len(value) > 300:
            return False

        return True

    @staticmethod
    def _has_control_or_invalid_characters(value) -> bool:
        value = str(value)

        return any(
            ord(char) < 32 and char not in "\t\n\r"
            for char in value
        )

    @staticmethod
    def _normalize_gender(value) -> str:
        value = str(value).upper().strip()

        mapping = {
            "M": "MALE",
            "MALE": "MALE",
            "MAN": "MALE",
            "F": "FEMALE",
            "FEMALE": "FEMALE",
            "WOMAN": "FEMALE",
            "O": "OTHER",
            "OTHER": "OTHER",
            "U": "UNSPECIFIED",
            "UNSPECIFIED": "UNSPECIFIED",
        }

        return mapping.get(value, value)

    @staticmethod
    def _looks_like_placeholder(number: str) -> bool:
        if len(set(number)) == 1:
            return True

        ascending = "012345678901"
        descending = "987654321098"

        return number in {ascending, descending}

    @classmethod
    def _verhoeff_validate(cls, number: str) -> bool:
        """
        Validate a numeric string using the Verhoeff algorithm.
        """

        if not number.isdigit():
            return False

        check = 0

        reversed_digits = list(map(int, reversed(number)))

        for i, digit in enumerate(reversed_digits):
            check = cls._D[check][cls._P[i % 8][digit]]

        return check == 0

    @staticmethod
    def _check_to_dict(check: ValidationCheck) -> dict:
        return {
            "rule": check.rule_id,
            "status": check.status.value,
            "severity": check.severity.value,
            "message": check.message,
            "field": check.field,
            "details": check.details,
        }

    @staticmethod
    def _calculate_overall_status(checks: list) -> OverallStatus:
        failures = [
            check
            for check in checks
            if check.status == CheckStatus.FAIL
        ]

        warnings = [
            check
            for check in checks
            if check.status == CheckStatus.WARNING
        ]

        not_checked = [
            check
            for check in checks
            if check.status == CheckStatus.NOT_CHECKED
        ]

        if failures:
            return OverallStatus.INVALID

        if warnings or not_checked:
            return OverallStatus.REVIEW

        return OverallStatus.VALID