"""Stockage en mémoire du feedback utilisateur sur les suggestions IA."""

from collections import Counter, defaultdict
from datetime import UTC, datetime

# Pré-rempli avec quelques entrées simulées pour la démo
_FEEDBACK_LOG = [
    {"ticket_type": "bug", "decision": "accepted", "at": "2026-05-25T10:14:00Z"},
    {"ticket_type": "bug", "decision": "accepted", "at": "2026-05-26T11:02:00Z"},
    {"ticket_type": "bug", "decision": "modified", "at": "2026-05-26T15:30:00Z"},
    {"ticket_type": "bug", "decision": "accepted", "at": "2026-05-27T08:55:00Z"},
    {"ticket_type": "feature", "decision": "accepted", "at": "2026-05-25T13:20:00Z"},
    {"ticket_type": "feature", "decision": "rejected", "at": "2026-05-26T09:10:00Z"},
    {"ticket_type": "feature", "decision": "accepted", "at": "2026-05-27T12:45:00Z"},
    {"ticket_type": "feature", "decision": "modified", "at": "2026-05-28T10:00:00Z"},
    {"ticket_type": "epic", "decision": "modified", "at": "2026-05-25T16:00:00Z"},
    {"ticket_type": "epic", "decision": "accepted", "at": "2026-05-28T14:15:00Z"},
]


def add_feedback(ticket_type: str, decision: str) -> None:
    _FEEDBACK_LOG.append(
        {
            "ticket_type": ticket_type,
            "decision": decision,
            "at": datetime.now(UTC).isoformat(),
        }
    )


def get_statistics() -> dict:
    total = len(_FEEDBACK_LOG)
    counts = Counter(f["decision"] for f in _FEEDBACK_LOG)
    by_type = defaultdict(lambda: {"accepted": 0, "modified": 0, "rejected": 0})
    for f in _FEEDBACK_LOG:
        by_type[f["ticket_type"]][f["decision"]] += 1
    acceptance_rate = counts.get("accepted", 0) / total if total else 0
    return {
        "total": total,
        "counts": dict(counts),
        "by_type": dict(by_type),
        "acceptance_rate": acceptance_rate,
        "recent": _FEEDBACK_LOG[-10:],
    }
