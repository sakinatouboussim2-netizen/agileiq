"""Service IA d'AgileIQ : classification, priorisation, clustering, prediction."""

from collections import defaultdict
from datetime import UTC, datetime

from flask import Flask, jsonify, request
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from classification import TicketClassifier

app = Flask(__name__)

# ====================================================
# Entrainement au demarrage
# ====================================================
print("[ml-service] Entrainement du classifieur sur corpus synthetique...")
classifier = TicketClassifier().train()
print(f"[ml-service] Classifieur pret. Classes: {classifier.classes_.tolist()}")


@app.get("/health")
def health():
    return jsonify(status="ok", service="agileiq-ml", classes=classifier.classes_.tolist()), 200


# ====================================================
# 1. CLASSIFICATION
# ====================================================
@app.post("/classify")
def classify():
    payload = request.get_json() or {}
    title = payload.get("title", "")
    description = payload.get("description", "")
    if not title.strip():
        return jsonify(error="title is required"), 400
    result = classifier.predict(title, description)
    return jsonify(result), 200


# ====================================================
# 2. PRIORISATION (score multi-criteres explicite)
# ====================================================
@app.post("/prioritize")
def prioritize():
    """Calcule un score de priorite explicite et decompose par critere."""
    payload = request.get_json() or {}
    severity = payload.get("severity", "low")  # low/medium/high/critical
    days_to_deadline = int(payload.get("days_to_deadline", 30))
    similar_tickets_count = int(payload.get("similar_tickets_count", 0))
    dependency_impact = int(payload.get("dependency_impact", 0))
    business_value = int(payload.get("business_value", 50))

    weights = {
        "severity": 0.30,
        "urgency": 0.20,
        "frequency": 0.15,
        "dependency": 0.20,
        "business_value": 0.15,
    }

    severity_map = {"low": 25, "medium": 50, "high": 75, "critical": 100}
    severity_score = severity_map.get(severity, 25)
    urgency_score = max(0, min(100, 100 - (days_to_deadline * 3)))
    frequency_score = min(100, similar_tickets_count * 15)
    dependency_score = min(100, dependency_impact * 20)

    contributions = {
        "severity": severity_score * weights["severity"],
        "urgency": urgency_score * weights["urgency"],
        "frequency": frequency_score * weights["frequency"],
        "dependency_impact": dependency_score * weights["dependency"],
        "business_value": business_value * weights["business_value"],
    }
    total_score = round(sum(contributions.values()), 2)

    return (
        jsonify(
            {
                "score": total_score,
                "contributions": {k: round(v, 2) for k, v in contributions.items()},
                "weights": weights,
                "explanation": (
                    f"Score {total_score:.0f}/100 = severite ({contributions['severity']:.0f}) "
                    f"+ urgence ({contributions['urgency']:.0f}) "
                    f"+ recurrence ({contributions['frequency']:.0f}) "
                    f"+ dependances ({contributions['dependency_impact']:.0f}) "
                    f"+ valeur metier ({contributions['business_value']:.0f})"
                ),
            }
        ),
        200,
    )


# ====================================================
# 3. CLUSTERING (detection de bugs similaires)
# ====================================================
@app.post("/cluster")
def cluster():
    """Regroupe des bugs similaires par DBSCAN sur leurs embeddings TF-IDF."""
    payload = request.get_json() or {}
    bugs = payload.get("bugs", [])  # liste de {id, title, description}
    if len(bugs) < 2:
        return jsonify(error="Au moins 2 bugs requis pour le clustering"), 400

    texts = [f"{b.get('title', '')} {b.get('description', '')}" for b in bugs]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts).toarray()

    dbscan = DBSCAN(eps=0.6, min_samples=2, metric="cosine")
    labels = dbscan.fit_predict(matrix)

    clusters = defaultdict(list)
    for bug, label in zip(bugs, labels, strict=False):
        cluster_id = int(label)
        bug_summary = {"id": bug.get("id"), "title": bug.get("title")}
        if cluster_id == -1:
            clusters["isolated"].append(bug_summary)
        else:
            clusters[f"cluster_{cluster_id}"].append(bug_summary)

    return (
        jsonify(
            {
                "total_bugs": len(bugs),
                "n_clusters": len([k for k in clusters if k != "isolated"]),
                "n_isolated": len(clusters.get("isolated", [])),
                "clusters": dict(clusters),
                "explanation": (
                    "Clustering DBSCAN (cosine, eps=0.6) sur embeddings TF-IDF. "
                    "Les bugs marques 'isolated' n'ont pas de doublon proche."
                ),
            }
        ),
        200,
    )


# ====================================================
# 4. PREDICTION DE DUREE (heuristique fondee sur le type)
# ====================================================
@app.post("/predict")
def predict_duration():
    """Estime la duree de resolution + intervalle de confiance."""
    payload = request.get_json() or {}
    ticket_type = payload.get("type", "feature")
    story_points = int(payload.get("story_points", 3))
    priority = payload.get("priority", "medium")
    has_blocker = bool(payload.get("has_blocker", False))

    base_days = {"epic": 30, "feature": 5, "bug": 2}.get(ticket_type, 5)
    base_days += story_points * 1.5

    priority_factor = {"low": 1.5, "medium": 1.0, "high": 0.75, "critical": 0.5}
    base_days *= priority_factor.get(priority, 1.0)

    if has_blocker:
        base_days *= 1.8

    estimated_days = round(base_days, 1)
    confidence_interval_days = round(base_days * 0.35, 1)

    return (
        jsonify(
            {
                "estimated_days": estimated_days,
                "interval_low": round(max(0.5, estimated_days - confidence_interval_days), 1),
                "interval_high": round(estimated_days + confidence_interval_days, 1),
                "explanation": (
                    f"Heuristique : base ({ticket_type}) + story points + priorite "
                    f"+ facteur bloqueur. Intervalle a 70% de confiance."
                ),
                "predicted_at": datetime.now(UTC).isoformat(),
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False)
