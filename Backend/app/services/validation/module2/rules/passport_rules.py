from module2.schemas import RuleDefinition, Severity


PASSPORT_RULES = [

    # ============================================================
    # PASSPORT NUMBER
    # ============================================================

    RuleDefinition(
        rule_id="PAS-NUM-001",
        name="PASSPORT_NUMBER_PRESENT",
        description="Passport number must be present.",
        severity=Severity.HIGH,
        category="PASSPORT_NUMBER"
    ),

    RuleDefinition(
        rule_id="PAS-NUM-002",
        name="PASSPORT_NUMBER_STRUCTURE",
        description="Passport number must follow the configured document-number structure.",
        severity=Severity.HIGH,
        category="PASSPORT_NUMBER",
        notes=(
            "Keep this configurable. Do not assume a single pattern "
            "covers every passport generation or document type."
        )
    ),

    RuleDefinition(
        rule_id="PAS-NUM-003",
        name="PASSPORT_NUMBER_NORMALIZATION",
        description="Passport number must be normalized before comparison.",
        severity=Severity.LOW,
        category="PASSPORT_NUMBER"
    ),


    # ============================================================
    # NAME
    # ============================================================

    RuleDefinition(
        rule_id="PAS-NAME-001",
        name="PASSPORT_NAME_PRESENT",
        description="Passport holder name must be present.",
        severity=Severity.HIGH,
        category="NAME"
    ),

    RuleDefinition(
        rule_id="PAS-NAME-002",
        name="PASSPORT_NAME_SANITY",
        description="Passport holder name must contain plausible textual content.",
        severity=Severity.MEDIUM,
        category="NAME"
    ),

    RuleDefinition(
        rule_id="PAS-NAME-003",
        name="NAME_VISUAL_MRZ_MATCH",
        description="Visual name and MRZ name must agree after appropriate normalization.",
        severity=Severity.HIGH,
        category="NAME"
    ),

    RuleDefinition(
        rule_id="PAS-NAME-004",
        name="MRZ_NAME_STRUCTURE",
        description="MRZ name field must follow the expected MRZ name representation.",
        severity=Severity.MEDIUM,
        category="NAME"
    ),


    # ============================================================
    # NATIONALITY
    # ============================================================

    RuleDefinition(
        rule_id="PAS-NAT-001",
        name="NATIONALITY_PRESENT",
        description="Nationality must be present.",
        severity=Severity.HIGH,
        category="NATIONALITY"
    ),

    RuleDefinition(
        rule_id="PAS-NAT-002",
        name="NATIONALITY_CODE",
        description="Nationality must use a recognized three-letter country/reference code.",
        severity=Severity.HIGH,
        category="NATIONALITY"
    ),

    RuleDefinition(
        rule_id="PAS-NAT-003",
        name="NATIONALITY_VISUAL_MRZ_MATCH",
        description="Visual nationality and MRZ nationality must agree.",
        severity=Severity.HIGH,
        category="NATIONALITY"
    ),


    # ============================================================
    # DATE OF BIRTH
    # ============================================================

    RuleDefinition(
        rule_id="PAS-DOB-001",
        name="DOB_PARSEABLE",
        description="Date of birth must be a valid calendar date.",
        severity=Severity.HIGH,
        category="DATE_OF_BIRTH"
    ),

    RuleDefinition(
        rule_id="PAS-DOB-002",
        name="DOB_NOT_FUTURE",
        description="Date of birth cannot be in the future.",
        severity=Severity.HIGH,
        category="DATE_OF_BIRTH"
    ),

    RuleDefinition(
        rule_id="PAS-DOB-003",
        name="DOB_BEFORE_EXPIRY",
        description="Date of birth must precede passport expiry.",
        severity=Severity.MEDIUM,
        category="DATE_OF_BIRTH"
    ),

    RuleDefinition(
        rule_id="PAS-DOB-004",
        name="DOB_VISUAL_MRZ_MATCH",
        description="Visual date of birth must match MRZ date of birth.",
        severity=Severity.HIGH,
        category="DATE_OF_BIRTH"
    ),

    RuleDefinition(
        rule_id="PAS-DOB-005",
        name="DOB_MRZ_CHECK_DIGIT",
        description="MRZ date-of-birth check digit must be valid.",
        severity=Severity.HIGH,
        category="DATE_OF_BIRTH"
    ),

    RuleDefinition(
        rule_id="PAS-DOB-006",
        name="DOB_REASONABLE_RANGE",
        description="Extremely implausible dates should be flagged for review.",
        severity=Severity.LOW,
        category="DATE_OF_BIRTH",
        notes="Do not automatically classify unusual age as fraud."
    ),


    # ============================================================
    # EXPIRY
    # ============================================================

    RuleDefinition(
        rule_id="PAS-EXP-001",
        name="EXPIRY_PARSEABLE",
        description="Passport expiry date must be a valid calendar date.",
        severity=Severity.HIGH,
        category="DATE_OF_EXPIRY"
    ),

    RuleDefinition(
        rule_id="PAS-EXP-002",
        name="EXPIRY_STATUS",
        description="Passport expiry must be evaluated against the screening date.",
        severity=Severity.HIGH,
        category="DATE_OF_EXPIRY"
    ),

    RuleDefinition(
        rule_id="PAS-EXP-003",
        name="EXPIRY_VISUAL_MRZ_MATCH",
        description="Visual expiry date must match MRZ expiry date.",
        severity=Severity.HIGH,
        category="DATE_OF_EXPIRY"
    ),

    RuleDefinition(
        rule_id="PAS-EXP-004",
        name="EXPIRY_MRZ_CHECK_DIGIT",
        description="MRZ expiry-date check digit must be valid.",
        severity=Severity.HIGH,
        category="DATE_OF_EXPIRY"
    ),


    # ============================================================
    # SEX / GENDER
    # ============================================================

    RuleDefinition(
        rule_id="PAS-SEX-001",
        name="SEX_VALUE_SUPPORTED",
        description="Sex marker must use a supported document representation.",
        severity=Severity.MEDIUM,
        category="SEX"
    ),

    RuleDefinition(
        rule_id="PAS-SEX-002",
        name="SEX_VISUAL_MRZ_MATCH",
        description="Visual sex marker and MRZ sex marker must agree when both are available.",
        severity=Severity.HIGH,
        category="SEX"
    ),


    # ============================================================
    # MRZ STRUCTURE
    # ============================================================

    RuleDefinition(
        rule_id="PAS-MRZ-001",
        name="MRZ_PRESENT",
        description="Expected passport MRZ must be available for validation.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-002",
        name="MRZ_LINE_STRUCTURE",
        description="Passport MRZ must follow the expected two-line TD3 structure.",
        severity=Severity.HIGH,
        category="MRZ",
        notes="Based on ICAO Doc 9303 passport MRZ structure."
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-003",
        name="MRZ_CHARACTER_SET",
        description="MRZ must contain characters allowed by the MRZ character set.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-004",
        name="MRZ_FIELD_POSITIONS",
        description="MRZ fields must occur in their expected positions and lengths.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-005",
        name="MRZ_PASSPORT_NUMBER_CHECK_DIGIT",
        description="Passport-number MRZ check digit must be valid.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-006",
        name="MRZ_DOB_CHECK_DIGIT",
        description="Date-of-birth MRZ check digit must be valid.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-007",
        name="MRZ_EXPIRY_CHECK_DIGIT",
        description="Expiry-date MRZ check digit must be valid.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-008",
        name="MRZ_COMPOSITE_CHECK_DIGIT",
        description="MRZ composite check digit must be valid.",
        severity=Severity.HIGH,
        category="MRZ"
    ),


    # ============================================================
    # MRZ ↔ VISUAL DATA
    # ============================================================

    RuleDefinition(
        rule_id="PAS-MRZ-009",
        name="MRZ_PASSPORT_NUMBER_MATCH",
        description="MRZ passport number must match the extracted passport number.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-010",
        name="MRZ_NATIONALITY_MATCH",
        description="MRZ nationality must match the extracted nationality.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-011",
        name="MRZ_DOB_MATCH",
        description="MRZ date of birth must match the extracted date of birth.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-012",
        name="MRZ_EXPIRY_MATCH",
        description="MRZ expiry date must match the extracted expiry date.",
        severity=Severity.HIGH,
        category="MRZ"
    ),

    RuleDefinition(
        rule_id="PAS-MRZ-013",
        name="MRZ_SEX_MATCH",
        description="MRZ sex marker must match the extracted sex value.",
        severity=Severity.HIGH,
        category="MRZ"
    ),


    # ============================================================
    # INTERNAL CONSISTENCY
    # ============================================================

    RuleDefinition(
        rule_id="PAS-CONS-001",
        name="IDENTITY_FIELDS_INTERNAL_CONSISTENCY",
        description="Core identity fields must not contradict one another.",
        severity=Severity.HIGH,
        category="CONSISTENCY"
    ),

    RuleDefinition(
        rule_id="PAS-CONS-002",
        name="DOCUMENT_DATE_CONSISTENCY",
        description="Passport dates must satisfy their logical chronological relationships.",
        severity=Severity.MEDIUM,
        category="CONSISTENCY"
    ),


    # ============================================================
    # REFERENCE / DATABASE CHECKS
    # ============================================================

    RuleDefinition(
        rule_id="PAS-DB-001",
        name="DOCUMENT_STATUS_LOOKUP",
        description="Passport number may be checked against an approved reference repository.",
        severity=Severity.HIGH,
        category="DATABASE",
        notes="Prototype uses local mock data only."
    ),

    RuleDefinition(
        rule_id="PAS-DB-002",
        name="REVOKED_DOCUMENT",
        description="A reference record marked as revoked must be flagged.",
        severity=Severity.CRITICAL,
        category="DATABASE",
        notes="Prototype/mock rule. Production requires authorized integration."
    ),

    RuleDefinition(
        rule_id="PAS-DB-003",
        name="LOST_OR_STOLEN_DOCUMENT",
        description="A reference record marked lost or stolen must be flagged.",
        severity=Severity.CRITICAL,
        category="DATABASE",
        notes="Prototype/mock rule. Production requires authorized integration."
    ),
]