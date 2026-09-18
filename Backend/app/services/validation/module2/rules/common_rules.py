from module2.schemas import RuleDefinition, Severity


COMMON_RULES = [

    RuleDefinition(
        rule_id="COMMON-001",
        name="SUPPORTED_DOCUMENT_TYPE",
        description="Document type must be supported by the validation engine.",
        severity=Severity.HIGH,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-002",
        name="OCR_STATUS_USABLE",
        description="OCR extraction must provide usable data before deterministic validation.",
        severity=Severity.HIGH,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-003",
        name="OCR_CONFIDENCE",
        description="OCR confidence should be evaluated before relying on extracted values.",
        severity=Severity.MEDIUM,
        category="COMMON",
        notes="Prototype threshold only. Not an official government threshold."
    ),

    RuleDefinition(
        rule_id="COMMON-004",
        name="REQUIRED_FIELDS",
        description="Required fields must be available for the selected document type.",
        severity=Severity.HIGH,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-005",
        name="EMPTY_OR_INVALID_VALUES",
        description="Fields must not contain empty or obviously unusable extracted values.",
        severity=Severity.MEDIUM,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-006",
        name="DATE_FORMAT",
        description="Dates must be parseable and normalized into a standard internal representation.",
        severity=Severity.MEDIUM,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-007",
        name="DATE_LOGICAL_ORDER",
        description="Related dates must follow logical chronological ordering.",
        severity=Severity.MEDIUM,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-008",
        name="NORMALIZED_COMPARISON",
        description="Values should be normalized before comparing OCR and document representations.",
        severity=Severity.LOW,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-009",
        name="MISSING_DATA_HANDLING",
        description="Missing information should result in REVIEW or NOT_CHECKED instead of an unjustified failure.",
        severity=Severity.MEDIUM,
        category="COMMON"
    ),

    RuleDefinition(
        rule_id="COMMON-010",
        name="FIELD_CHARACTER_SANITY",
        description="Extracted values should contain characters appropriate for their expected field type.",
        severity=Severity.LOW,
        category="COMMON"
    ),
]