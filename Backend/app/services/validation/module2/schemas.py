from dataclasses import dataclass
from enum import Enum
from typing import Any


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_CHECKED = "NOT_CHECKED"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class OverallStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    name: str
    description: str
    severity: Severity
    category: str
    enabled: bool = True
    notes: str = ""


@dataclass
class ValidationCheck:
    rule_id: str
    status: CheckStatus
    severity: Severity
    message: str
    field: str | None = None
    details: Any = None