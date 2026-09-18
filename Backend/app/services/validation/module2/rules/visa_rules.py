from module2.schemas import RuleDefinition, Severity


VISA_RULES = [

    RuleDefinition(
        "VISA-001",
        "VISA_NUMBER_PRESENT",
        "Visa number must be present.",
        Severity.HIGH,
        "VISA_NUMBER"
    ),

    RuleDefinition(
        "VISA-002",
        "VISA_NUMBER_STRUCTURE",
        "Visa number must follow the configured visa-number structure.",
        Severity.MEDIUM,
        "VISA_NUMBER"
    ),

    RuleDefinition(
        "VISA-003",
        "VISA_TYPE_PRESENT",
        "Visa type/category must be present.",
        Severity.HIGH,
        "VISA_TYPE"
    ),

    RuleDefinition(
        "VISA-004",
        "VISA_TYPE_SUPPORTED",
        "Visa type must exist in the configured visa category registry.",
        Severity.HIGH,
        "VISA_TYPE"
    ),

    RuleDefinition(
        "VISA-005",
        "VISA_DATES_PARSEABLE",
        "Visa validity dates must be valid calendar dates.",
        Severity.HIGH,
        "DATES"
    ),

    RuleDefinition(
        "VISA-006",
        "VISA_VALIDITY_ORDER",
        "Visa start/valid-from date must not be after the end/valid-until date.",
        Severity.HIGH,
        "DATES"
    ),

    RuleDefinition(
        "VISA-007",
        "VISA_CURRENT_VALIDITY",
        "Visa validity must be evaluated against the screening/travel date.",
        Severity.HIGH,
        "DATES"
    ),

    RuleDefinition(
        "VISA-008",
        "VISA_ENTRY_TYPE",
        "Entry type must use a recognized representation.",
        Severity.MEDIUM,
        "ENTRIES"
    ),

    RuleDefinition(
        "VISA-009",
        "VISA_STAY_DURATION",
        "Permitted stay duration must be consistent with the configured visa category.",
        Severity.HIGH,
        "STAY"
    ),

    RuleDefinition(
        "VISA-010",
        "VISA_PASSPORT_NUMBER_MATCH",
        "Visa passport number must match the referenced passport number.",
        Severity.HIGH,
        "CROSS_DOCUMENT"
    ),

    RuleDefinition(
        "VISA-011",
        "VISA_NAME_MATCH",
        "Visa holder name must match the referenced passport identity.",
        Severity.HIGH,
        "CROSS_DOCUMENT"
    ),

    RuleDefinition(
        "VISA-012",
        "VISA_NATIONALITY_MATCH",
        "Visa nationality should match passport nationality where applicable.",
        Severity.MEDIUM,
        "CROSS_DOCUMENT"
    ),

    RuleDefinition(
        "VISA-013",
        "VISA_PASSPORT_VALIDITY",
        "Visa/passport validity relationship must satisfy the configured rule set.",
        Severity.HIGH,
        "CROSS_DOCUMENT"
    ),

    RuleDefinition(
        "VISA-014",
        "VISA_CATEGORY_RULESET",
        "Category-specific visa rules must be applied instead of one universal rule.",
        Severity.HIGH,
        "CATEGORY"
    ),

    RuleDefinition(
        "VISA-015",
        "VISA_REFERENCE_STATUS",
        "Visa may be checked against an approved/local reference repository.",
        Severity.HIGH,
        "DATABASE",
        notes="Prototype uses mock/local data only."
    ),
]