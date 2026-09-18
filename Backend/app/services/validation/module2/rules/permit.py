from module2.schemas import RuleDefinition, Severity


PERMIT_RULES = [

    RuleDefinition(
        "PERMIT-001",
        "PERMIT_NUMBER_PRESENT",
        "Permit number must be present.",
        Severity.HIGH,
        "PERMIT_NUMBER"
    ),

    RuleDefinition(
        "PERMIT-002",
        "PERMIT_NUMBER_STRUCTURE",
        "Permit number must match the configured permit-type format.",
        Severity.MEDIUM,
        "PERMIT_NUMBER"
    ),

    RuleDefinition(
        "PERMIT-003",
        "PERMIT_TYPE_PRESENT",
        "Permit type must be present.",
        Severity.HIGH,
        "PERMIT_TYPE"
    ),

    RuleDefinition(
        "PERMIT-004",
        "PERMIT_TYPE_SUPPORTED",
        "Permit type must exist in the configured permit registry.",
        Severity.HIGH,
        "PERMIT_TYPE"
    ),

    RuleDefinition(
        "PERMIT-005",
        "PERMIT_HOLDER_PRESENT",
        "Permit holder identity must be present.",
        Severity.HIGH,
        "HOLDER"
    ),

    RuleDefinition(
        "PERMIT-006",
        "PERMIT_ISSUE_DATE_VALID",
        "Issue date must be a valid date.",
        Severity.MEDIUM,
        "DATES"
    ),

    RuleDefinition(
        "PERMIT-007",
        "PERMIT_EXPIRY_VALID",
        "Expiry date must be valid where applicable.",
        Severity.HIGH,
        "DATES"
    ),

    RuleDefinition(
        "PERMIT-008",
        "PERMIT_DATE_ORDER",
        "Issue date must not be after expiry date.",
        Severity.HIGH,
        "DATES"
    ),

    RuleDefinition(
        "PERMIT-009",
        "PERMIT_SCOPE_SUPPORTED",
        "Permit scope, region, or purpose must conform to configured values where applicable.",
        Severity.MEDIUM,
        "SCOPE"
    ),

    RuleDefinition(
        "PERMIT-010",
        "PERMIT_INTERNAL_CONSISTENCY",
        "Permit fields must be internally consistent.",
        Severity.HIGH,
        "CONSISTENCY"
    ),

    RuleDefinition(
        "PERMIT-011",
        "PERMIT_REFERENCE_STATUS",
        "Permit may be checked against an approved/local reference repository.",
        Severity.HIGH,
        "DATABASE",
        notes="Prototype uses mock/local data only."
    ),
]