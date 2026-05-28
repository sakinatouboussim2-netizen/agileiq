from enum import Enum


class TicketType(str, Enum):
    EPIC = "epic"
    FEATURE = "feature"
    BUG = "bug"


class Severity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
