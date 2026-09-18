from module2.schemas import RuleDefinition, Severity


NATIONAL_ID_RULES = [

    RuleDefinition(
        "NID-001",
        "ID_NUMBER_PRESENT",
        "National ID number must be present.",
        Severity.HIGH,
        "ID_NUMBER"
    ),

    RuleDefinition(
        "NID-002",
        "ID_NUMBER_STRUCTURE",
        "ID number must match the configured document-specific structure.",
        Severity.HIGH,
        "ID_NUMBER"
    ),

    RuleDefinition(
        "NID-003",
        "ID_NAME_PRESENT",
        "ID holder name must be present.",
        Severity.HIGH,
        "NAME"
    ),

    RuleDefinition(
        "NID-004",
        "ID_NAME_SANITY",
        "ID holder name must contain plausible textual content.",
        Severity.MEDIUM,
        "NAME"
    ),

    RuleDefinition(
        "NID-005",
        "ID_DOB_VALID",
        "Date of birth must be valid and must not be in the future.",
        Severity.HIGH,
        "DOB"
    ),

    RuleDefinition(
        "NID-006",
        "ID_EXPIRY_VALID",
        "Expiry must be valid where the specific ID type has an expiry.",
        Severity.MEDIUM,
        "EXPIRY"
    ),

    RuleDefinition(
        "NID-007",
        "ID_DATE_ORDER",
        "Issue and validity dates must be logically ordered.",
        Severity.MEDIUM,
        "DATES"
    ),

    RuleDefinition(
        "NID-008",
        "ID_INTERNAL_CONSISTENCY",
        "Identity fields must be internally consistent.",
        Severity.HIGH,
        "CONSISTENCY"
    ),

    RuleDefinition(
        "NID-009",
        "AUTHORIZED_VERIFICATION",
        "Official digital/offline verification may be performed through an authorized adapter.",
        Severity.HIGH,
        "EXTERNAL_VERIFICATION",
        notes="Do not implement unofficial authentication or scraping."
    ),

    RuleDefinition(
        "NID-010",
        "ID_REFERENCE_STATUS",
        "ID may be checked against an approved/local reference repository.",
        Severity.HIGH,
        "DATABASE"
    ),
]