from datetime import datetime

DEMO_ISSUES = [
    {
        "iid": 101,
        "title": "Add CSV export feature for projects",
        "description": "Users need to export the projects list as a CSV file.",
        "state": "opened",
        "labels": ["enhancement"],
        "created_at": "2026-05-20T10:00:00Z",
    },
    {
        "iid": 102,
        "title": "Login crash on Firefox 132 with special chars",
        "description": "Reproducible 500 error when password contains accents.",
        "state": "opened",
        "labels": ["bug", "critical"],
        "created_at": "2026-05-22T14:30:00Z",
    },
    {
        "iid": 103,
        "title": "Strategic redesign of the notification system",
        "description": "Complete rework of how notifications are delivered.",
        "state": "opened",
        "labels": ["epic"],
        "created_at": "2026-05-15T09:15:00Z",
    },
    {
        "iid": 104,
        "title": "Refonte du module d authentification",
        "description": "Migration vers JWT avec gestion fine des roles et permissions.",
        "state": "opened",
        "labels": ["epic", "auth"],
        "created_at": "2026-05-18T11:00:00Z",
    },
    {
        "iid": 105,
        "title": "Ajouter un dark mode",
        "description": "Permettre aux utilisateurs de basculer en theme sombre.",
        "state": "opened",
        "labels": ["enhancement", "ui"],
        "created_at": "2026-05-25T16:45:00Z",
    },
]


def import_and_classify(classifier, gitlab_url="", project_id="", token=""):
    issues = DEMO_ISSUES
    source = "demo"
    classified = []
    counts = {}
    for issue in issues:
        result = classifier.predict(issue["title"], issue.get("description", ""))
        classified.append(
            {
                "iid": issue.get("iid", "?"),
                "title": issue["title"],
                "labels_original": issue.get("labels", []),
                "ai_classification": result["type"],
                "ai_confidence": result["confidence"],
                "language_detected": result["language_detected"],
            }
        )
        counts[result["type"]] = counts.get(result["type"], 0) + 1
    return {
        "source": source,
        "total_imported": len(classified),
        "classification_summary": counts,
        "imported_at": datetime.utcnow().isoformat() + "Z",
        "issues": classified,
    }
