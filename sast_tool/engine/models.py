from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Location:
    file: str
    line: int
    column: int


@dataclass
class Finding:
    rule_id: str
    message: str
    severity: Severity
    location: Location
    # optional fields (use later)
    snippet: Optional[str] = None
    # AI fields
    explanation: Optional[str] = None
    fix: Optional[str] = None
    fixed_code: Optional[str] = None
    confidence: float = 0.5
