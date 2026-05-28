from enum import StrEnum


class TicketType(StrEnum):
    EPIC = "epic"
    FEATURE = "feature"
    BUG = "bug"


class Severity(StrEnum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
