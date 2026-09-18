from module2.schemas import RuleDefinition, Severity


# Aadhaar-specific deterministic validation rules.
#
# IMPORTANT:
# - These rules validate extracted/document-presented data.
# - A valid 12-digit Aadhaar number or valid checksum does NOT by itself
#   prove that the Aadhaar document is genuine.
# - UIDAI Secure QR / Offline e-KYC signature verification is treated as
#   a separate authenticity check.
# - Online Aadhaar authentication/e-KYC requires an authorized integration
#   and is therefore not implemented here.
#
# Official references:
#   UIDAI Secure QR Code / Offline Verification
#   UIDAI Paperless Offline e-KYC
#
# Prototype implementation should keep external verification behind an
# adapter/interface so it can be added later without changing these rules.


AADHAAR_RULES = [

    # ------------------------------------------------------------------
    # Aadhaar number
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-NUM-001",
        "AADHAAR_NUMBER_PRESENT",
        "Aadhaar number must be present when the presented document exposes it.",
        Severity.HIGH,
        "AADHAAR_NUMBER"
    ),

    RuleDefinition(
        "AADHAAR-NUM-002",
        "AADHAAR_NUMBER_LENGTH",
        "Aadhaar number must contain exactly 12 digits after removing permitted display separators.",
        Severity.HIGH,
        "AADHAAR_NUMBER"
    ),

    RuleDefinition(
        "AADHAAR-NUM-003",
        "AADHAAR_NUMBER_DIGITS_ONLY",
        "Aadhaar number must contain numeric digits only after normalization.",
        Severity.HIGH,
        "AADHAAR_NUMBER"
    ),

    RuleDefinition(
        "AADHAAR-NUM-004",
        "AADHAAR_NUMBER_VERHOEFF_CHECKSUM",
        "Aadhaar number checksum must satisfy the Verhoeff validation algorithm.",
        Severity.HIGH,
        "AADHAAR_NUMBER",
        notes="Checksum validation detects number-entry errors; it does not establish document authenticity."
    ),

    RuleDefinition(
        "AADHAAR-NUM-005",
        "AADHAAR_NUMBER_NOT_REPEATED_PATTERN",
        "Obvious repeated/sequential placeholder patterns should be flagged for review.",
        Severity.MEDIUM,
        "AADHAAR_NUMBER",
        notes="Heuristic only; never treat this alone as proof of fraud."
    ),

    RuleDefinition(
        "AADHAAR-NUM-006",
        "AADHAAR_NUMBER_MASKING_HANDLING",
        "Masked Aadhaar representations must be recognized and must not be treated as a complete Aadhaar number.",
        Severity.MEDIUM,
        "AADHAAR_NUMBER",
        notes="For example, only the visible final digits may be available on a masked presentation."
    ),


    # ------------------------------------------------------------------
    # Identity / demographic fields
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-ID-001",
        "AADHAAR_NAME_PRESENT",
        "Aadhaar holder name must be present when available on the presented form.",
        Severity.HIGH,
        "NAME"
    ),

    RuleDefinition(
        "AADHAAR-ID-002",
        "AADHAAR_NAME_SANITY",
        "Name must contain plausible textual content after OCR normalization.",
        Severity.MEDIUM,
        "NAME"
    ),

    RuleDefinition(
        "AADHAAR-ID-003",
        "AADHAAR_NAME_CHARACTER_SANITY",
        "Name should not contain obvious OCR corruption or unsupported control/special characters.",
        Severity.LOW,
        "NAME"
    ),

    RuleDefinition(
        "AADHAAR-ID-004",
        "AADHAAR_DOB_VALID",
        "Full date of birth, when supplied, must be a valid calendar date and must not be in the future.",
        Severity.HIGH,
        "DATE_OF_BIRTH"
    ),

    RuleDefinition(
        "AADHAAR-ID-005",
        "AADHAAR_YOB_VALID",
        "Year of birth, when only year is supplied, must be a valid four-digit year and must not be in the future.",
        Severity.HIGH,
        "YEAR_OF_BIRTH"
    ),

    RuleDefinition(
        "AADHAAR-ID-006",
        "AADHAAR_DOB_YOB_CONSISTENCY",
        "If both full DOB and year of birth are available from different representations, they must agree.",
        Severity.HIGH,
        "DATE_OF_BIRTH"
    ),

    RuleDefinition(
        "AADHAAR-ID-007",
        "AADHAAR_GENDER_SUPPORTED",
        "Gender value must match the supported representation for the source.",
        Severity.MEDIUM,
        "GENDER",
        notes="Do not assume one OCR spelling/format is universal across all Aadhaar representations."
    ),

    RuleDefinition(
        "AADHAAR-ID-008",
        "AADHAAR_GENDER_CONSISTENCY",
        "Gender values extracted from multiple document representations must agree.",
        Severity.MEDIUM,
        "GENDER"
    ),


    # ------------------------------------------------------------------
    # Address
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-ADDR-001",
        "AADHAAR_ADDRESS_PRESENT",
        "Address should be available when the presented Aadhaar representation is expected to contain address information.",
        Severity.MEDIUM,
        "ADDRESS"
    ),

    RuleDefinition(
        "AADHAAR-ADDR-002",
        "AADHAAR_PINCODE_FORMAT",
        "Indian PIN code, when present, must contain exactly six digits.",
        Severity.MEDIUM,
        "ADDRESS"
    ),

    RuleDefinition(
        "AADHAAR-ADDR-003",
        "AADHAAR_ADDRESS_SANITY",
        "Address should contain plausible textual/location information and should not be obviously corrupted.",
        Severity.LOW,
        "ADDRESS"
    ),

    RuleDefinition(
        "AADHAAR-ADDR-004",
        "AADHAAR_STATE_SANITY",
        "State/UT value, when extracted, should match the configured India state/UT reference data.",
        Severity.MEDIUM,
        "ADDRESS",
        notes="Use a versioned local reference dataset."
    ),


    # ------------------------------------------------------------------
    # Document representation / format
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-DOC-001",
        "AADHAAR_REPRESENTATION_SUPPORTED",
        "Presented Aadhaar representation must be identified as an expected form such as Aadhaar letter, e-Aadhaar, Aadhaar PVC, mAadhaar, or another configured representation.",
        Severity.MEDIUM,
        "DOCUMENT"
    ),

    RuleDefinition(
        "AADHAAR-DOC-002",
        "AADHAAR_NO_EXPIRY_ASSUMPTION",
        "Aadhaar should not be processed using passport-style expiry validation.",
        Severity.MEDIUM,
        "DOCUMENT",
        notes="Do not require an expiry date for Aadhaar."
    ),

    RuleDefinition(
        "AADHAAR-DOC-003",
        "AADHAAR_REQUIRED_FIELDS",
        "Required fields must be determined from the specific Aadhaar representation rather than one universal field list.",
        Severity.HIGH,
        "DOCUMENT"
    ),

    RuleDefinition(
        "AADHAAR-DOC-004",
        "AADHAAR_OCR_CONSISTENCY",
        "Repeated/extracted text representations should be internally consistent after normalization.",
        Severity.HIGH,
        "DOCUMENT"
    ),


    # ------------------------------------------------------------------
    # Secure QR Code
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-QR-001",
        "AADHAAR_SECURE_QR_PRESENT",
        "If a Secure QR Code is expected on the presented representation, the QR data should be detected/readable.",
        Severity.HIGH,
        "SECURE_QR"
    ),

    RuleDefinition(
        "AADHAAR-QR-002",
        "AADHAAR_QR_SIGNATURE_VALID",
        "UIDAI digital signature associated with the Secure QR Code must validate.",
        Severity.CRITICAL,
        "SECURE_QR",
        notes="Actual cryptographic verification requires the appropriate UIDAI public-key/certificate chain."
    ),

    RuleDefinition(
        "AADHAAR-QR-003",
        "AADHAAR_QR_DATA_INTEGRITY",
        "Demographic information obtained from the Secure QR Code must pass its integrity/authenticity verification.",
        Severity.CRITICAL,
        "SECURE_QR"
    ),

    RuleDefinition(
        "AADHAAR-QR-004",
        "AADHAAR_QR_DOCUMENT_MATCH",
        "Secure QR demographic data must match the visible/OCR-extracted Aadhaar data.",
        Severity.HIGH,
        "SECURE_QR"
    ),

    RuleDefinition(
        "AADHAAR-QR-005",
        "AADHAAR_QR_PHOTO_MATCH",
        "Photographic information obtained from a verified Secure QR Code may be compared with the document photo.",
        Severity.HIGH,
        "SECURE_QR",
        notes="Actual face comparison belongs to Module 4; Module 2 should only record the verification dependency/result when integrated."
    ),


    # ------------------------------------------------------------------
    # Offline e-KYC XML
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-EKYC-001",
        "AADHAAR_OFFLINE_EKYC_PRESENT",
        "Offline Paperless e-KYC XML must be recognized when supplied as the verification source.",
        Severity.HIGH,
        "OFFLINE_EKYC"
    ),

    RuleDefinition(
        "AADHAAR-EKYC-002",
        "AADHAAR_OFFLINE_EKYC_SIGNATURE",
        "The Offline e-KYC XML digital signature must validate using the appropriate UIDAI verification certificate.",
        Severity.CRITICAL,
        "OFFLINE_EKYC",
        notes="Cryptographic implementation should be isolated in a dedicated verification adapter."
    ),

    RuleDefinition(
        "AADHAAR-EKYC-003",
        "AADHAAR_OFFLINE_EKYC_DATA_INTEGRITY",
        "Signed Offline e-KYC demographic/photo data must pass integrity verification.",
        Severity.CRITICAL,
        "OFFLINE_EKYC"
    ),

    RuleDefinition(
        "AADHAAR-EKYC-004",
        "AADHAAR_OFFLINE_EKYC_REFERENCE_ID",
        "Offline e-KYC reference ID must be structurally valid for the supported XML version.",
        Severity.MEDIUM,
        "OFFLINE_EKYC"
    ),

    RuleDefinition(
        "AADHAAR-EKYC-005",
        "AADHAAR_OFFLINE_EKYC_DOCUMENT_MATCH",
        "Verified Offline e-KYC data must match the OCR-extracted/presented document data where comparison is applicable.",
        Severity.HIGH,
        "OFFLINE_EKYC"
    ),


    # ------------------------------------------------------------------
    # External / authorized verification
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-EXT-001",
        "AADHAAR_AUTHORIZATION_STATUS",
        "Online Aadhaar authentication/e-KYC must only be performed through an authorized integration.",
        Severity.CRITICAL,
        "EXTERNAL_VERIFICATION",
        notes="Do not implement direct CIDR access, unofficial APIs, scraping, or credential workarounds."
    ),

    RuleDefinition(
        "AADHAAR-EXT-002",
        "AADHAAR_ONLINE_AUTH_RESULT",
        "If an authorized authentication result is supplied, its result must be incorporated into validation.",
        Severity.HIGH,
        "EXTERNAL_VERIFICATION",
        notes="Future adapter/interface."
    ),

    RuleDefinition(
        "AADHAAR-EXT-003",
        "AADHAAR_CONSENT_AND_PURPOSE",
        "Authorized Aadhaar authentication must be associated with the required lawful purpose and informed consent where applicable.",
        Severity.HIGH,
        "EXTERNAL_VERIFICATION",
        notes="Process/compliance check; not an OCR check."
    ),


    # ------------------------------------------------------------------
    # Local/mock reference database
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-DB-001",
        "AADHAAR_REFERENCE_LOOKUP",
        "Aadhaar-related status may be evaluated against an approved/local reference source when such data is legitimately available.",
        Severity.HIGH,
        "DATABASE",
        notes="Prototype should use mock data only. Do not claim live UIDAI database access."
    ),

    RuleDefinition(
        "AADHAAR-DB-002",
        "AADHAAR_REFERENCE_STATUS",
        "Any returned reference status must be handled explicitly rather than inferred from the Aadhaar number alone.",
        Severity.HIGH,
        "DATABASE"
    ),


    # ------------------------------------------------------------------
    # Privacy / data handling
    # ------------------------------------------------------------------

    RuleDefinition(
        "AADHAAR-PRIV-001",
        "AADHAAR_DATA_MINIMIZATION",
        "Validation should process and retain only fields required for the screening workflow.",
        Severity.HIGH,
        "PRIVACY"
    ),

    RuleDefinition(
        "AADHAAR-PRIV-002",
        "AADHAAR_SENSITIVE_DATA_PROTECTION",
        "Aadhaar data must be protected in logs, storage, APIs, and debugging output.",
        Severity.HIGH,
        "PRIVACY"
    ),

    RuleDefinition(
        "AADHAAR-PRIV-003",
        "AADHAAR_NO_CORE_BIOMETRIC_STORAGE",
        "Core biometric information must not be stored by this document-validation module.",
        Severity.CRITICAL,
        "PRIVACY",
        notes="Face matching belongs to Module 4 and must follow the applicable legal/technical controls."
    ),
]
