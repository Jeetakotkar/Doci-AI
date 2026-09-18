from module2.schemas import RuleDefinition, Severity


DRIVING_LICENSE_RULES = [

    RuleDefinition(
        "DL-001",
        "DL_NUMBER_PRESENT",
        "Driving licence number must be present.",
        Severity.HIGH,
        "DL_NUMBER"
    ),

    RuleDefinition(
        "DL-002",
        "DL_NUMBER_STRUCTURE",
        "Driving licence number must match the configured jurisdiction/format rule.",
        Severity.HIGH,
        "DL_NUMBER"
    ),

    RuleDefinition(
        "DL-003",
        "DL_NAME_PRESENT",
        "Licence holder name must be present.",
        Severity.HIGH,
        "NAME"
    ),

    RuleDefinition(
        "DL-004",
        "DL_DOB_VALID",
        "Date of birth must be valid and must not be in the future.",
        Severity.HIGH,
        "DOB"
    ),

    RuleDefinition(
        "DL-005",
        "DL_ISSUE_DATE_VALID",
        "Issue date must be a valid date.",
        Severity.MEDIUM,
        "ISSUE_DATE"
    ),

    RuleDefinition(
        "DL-006",
        "DL_EXPIRY_VALID",
        "Expiry date must be valid where applicable.",
        Severity.HIGH,
        "EXPIRY"
    ),

    RuleDefinition(
        "DL-007",
        "DL_DATE_ORDER",
        "Issue date must not be after expiry date.",
        Severity.HIGH,
        "DATES"
    ),

    RuleDefinition(
        "DL-008",
        "DL_CLASS_PRESENT",
        "Vehicle/category class information should be present where required.",
        Severity.MEDIUM,
        "VEHICLE_CLASS"
    ),

    RuleDefinition(
        "DL-009",
        "DL_CLASS_SUPPORTED",
        "Vehicle/category class must be recognized by the configured rule set.",
        Severity.MEDIUM,
        "VEHICLE_CLASS"
    ),

    RuleDefinition(
        "DL-010",
        "DL_INTERNAL_CONSISTENCY",
        "Core licence fields must be internally consistent.",
        Severity.HIGH,
        "CONSISTENCY"
    ),

    RuleDefinition(
        "DL-011",
        "DL_REFERENCE_STATUS",
        "Licence may be checked against an approved/local reference repository.",
        Severity.HIGH,
        "DATABASE",
        notes="Prototype uses mock/local data only."
    ),
]