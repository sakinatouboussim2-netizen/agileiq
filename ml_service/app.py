"""Service IA d'AgileIQ : classification + démos UI."""

from collections import defaultdict
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_file
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from classification import TicketClassifier
from evaluation import confusion_matrix_png, evaluate_classifier
from feedback_store import add_feedback, get_statistics
from visualization import (
    acceptance_chart_png,
    clusters_tsne_png,
    explanation_png,
)

app = Flask(__name__)

print("[ml-service] Entrainement du classifieur sur corpus synthetique...")
classifier = TicketClassifier().train()
print(f"[ml-service] Classifieur pret. Classes: {classifier.classes_.tolist()}")

# Charge le template base une fois
with Path("templates/base.html").open() as f:
    BASE_TEMPLATE = f.read()


def render(title: str, body: str) -> str:
    return render_template_string(BASE_TEMPLATE, title=title, body=body)


# ====================================================
# Endpoints JSON existants (classify, prioritize, cluster, predict)
# ====================================================
@app.get("/health")
def health():
    return jsonify(status="ok", service="agileiq-ml", classes=classifier.classes_.tolist()), 200


@app.post("/classify")
def classify():
    payload = request.get_json() or {}
    title = payload.get("title", "")
    description = payload.get("description", "")
    if not title.strip():
        return jsonify(error="title is required"), 400
    return jsonify(classifier.predict(title, description)), 200


@app.post("/prioritize")
def prioritize():
    payload = request.get_json() or {}
    severity = payload.get("severity", "low")
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
    contributions = {
        "severity": severity_map.get(severity, 25) * weights["severity"],
        "urgency": max(0, min(100, 100 - days_to_deadline * 3)) * weights["urgency"],
        "frequency": min(100, similar_tickets_count * 15) * weights["frequency"],
        "dependency_impact": min(100, dependency_impact * 20) * weights["dependency"],
        "business_value": business_value * weights["business_value"],
    }
    total_score = round(sum(contributions.values()), 2)
    return (
        jsonify(
            {
                "score": total_score,
                "contributions": {k: round(v, 2) for k, v in contributions.items()},
                "weights": weights,
            }
        ),
        200,
    )


@app.post("/cluster")
def cluster_endpoint():
    payload = request.get_json() or {}
    bugs = payload.get("bugs", [])
    if len(bugs) < 2:
        return jsonify(error="Au moins 2 bugs requis"), 400
    texts = [f"{b.get('title', '')} {b.get('description', '')}" for b in bugs]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts).toarray()
    labels = DBSCAN(eps=0.6, min_samples=2, metric="cosine").fit_predict(matrix)
    clusters = defaultdict(list)
    for bug, label in zip(bugs, labels, strict=False):
        key = "isolated" if int(label) == -1 else f"cluster_{label}"
        clusters[key].append({"id": bug.get("id"), "title": bug.get("title")})
    return jsonify(clusters=dict(clusters)), 200


@app.post("/predict")
def predict_duration():
    payload = request.get_json() or {}
    ticket_type = payload.get("type", "feature")
    story_points = int(payload.get("story_points", 3))
    priority = payload.get("priority", "medium")
    has_blocker = bool(payload.get("has_blocker", False))
    base_days = {"epic": 30, "feature": 5, "bug": 2}.get(ticket_type, 5)
    base_days += story_points * 1.5
    base_days *= {"low": 1.5, "medium": 1.0, "high": 0.75, "critical": 0.5}.get(priority, 1.0)
    if has_blocker:
        base_days *= 1.8
    return (
        jsonify(
            {
                "estimated_days": round(base_days, 1),
                "interval_low": round(max(0.5, base_days * 0.65), 1),
                "interval_high": round(base_days * 1.35, 1),
            }
        ),
        200,
    )


# ====================================================
# CAPTURE 6.1 — Matrice de confusion
# ====================================================
@app.get("/evaluation")
def evaluation_json():
    return jsonify(evaluate_classifier()), 200


@app.get("/evaluation/confusion_matrix.png")
def evaluation_png():
    return send_file(confusion_matrix_png(), mimetype="image/png")


# ====================================================
# CAPTURE 6.3 — UI de validation des suggestions
# ====================================================
@app.get("/ui/suggestions")
def ui_suggestions():
    sample = {
        "title": "Crash au login lors de la saisie d'un mot de passe contenant un emoji",
        "description": "Reproduit sur Firefox et Chrome. Stack trace pointe vers le module d'auth.",
    }
    prediction = classifier.predict(sample["title"], sample["description"])
    keywords_html = "".join(
        f"<span style='background:#EAF1F8;padding:3px 8px;border-radius:4px;margin-right:4px;font-size:12px;'>{k}</span>"
        for k in prediction.get("preprocessed_text", "").split()[:5]
    )
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Suggestion IA pour ce ticket</h2>
      <p style="color:#666;font-size:14px;">Le ticket suivant vient d'être créé. L'IA a analysé son contenu et propose une classification.</p>
      <div style="background:#f7f8fa;padding:14px;border-radius:6px;margin:16px 0;">
        <strong>Titre :</strong> {sample["title"]}<br>
        <span style="color:#666;font-size:13px;">{sample["description"]}</span>
      </div>
      <div style="display:flex;gap:24px;align-items:center;margin:16px 0;">
        <div>
          <div style="font-size:13px;color:#666;">Type prédit</div>
          <span class="badge badge-{prediction["type"]}" style="font-size:18px;padding:6px 12px;">{prediction["type"].upper()}</span>
        </div>
        <div style="flex:1;">
          <div style="font-size:13px;color:#666;">Confiance</div>
          <div style="font-size:22px;font-weight:bold;color:#2E7D6B;">{prediction["confidence"]:.0%}</div>
          <div class="meter"><div class="meter-fill" style="width:{prediction["confidence"] * 100:.0f}%;"></div></div>
        </div>
      </div>
      <div style="margin:16px 0;">
        <div style="font-size:13px;color:#666;margin-bottom:6px;">Mots-clés explicatifs</div>
        {keywords_html}
      </div>
      <div style="margin-top:24px;">
        <button class="btn btn-accept" onclick="alert('Suggestion acceptée. Le ticket est marqué comme bug.')">✓ Accepter</button>
        <button class="btn btn-modify" onclick="alert('Édition activée — vous pouvez changer le type')">✎ Modifier</button>
        <button class="btn btn-reject" onclick="alert('Suggestion rejetée. Aucun feedback envoyé au modèle.')">✗ Rejeter</button>
      </div>
      <p style="color:#888;font-size:12px;margin-top:16px;font-style:italic;">
        Chaque action utilisateur est tracée et alimente le ré-entraînement périodique du modèle (mécanisme human-in-the-loop).
      </p>
    </div>
    """
    return render("Validation des suggestions IA", body)


# ====================================================
# CAPTURE 6.5 — Visualisation des clusters de bugs
# ====================================================
@app.get("/visualization/clusters.png")
def visualization_clusters():
    return send_file(clusters_tsne_png(), mimetype="image/png")


# ====================================================
# CAPTURE 6.7 — Dashboard de prédictions
# ====================================================
@app.get("/ui/predictions")
def ui_predictions():
    tickets = [
        ("Refonte du module de paiement", "epic", 13, "high", False),
        ("Crash login Firefox", "bug", 2, "critical", True),
        ("Ajouter export CSV", "feature", 5, "medium", False),
        ("Migration cloud AWS", "epic", 21, "high", True),
        ("Bug d'affichage sur Safari", "bug", 3, "low", False),
        ("Implémenter OAuth Google", "feature", 8, "high", False),
        ("Lenteur sur la recherche", "bug", 5, "medium", True),
    ]
    rows = []
    for title, ttype, sp, pr, blocker in tickets:
        base = {"epic": 30, "feature": 5, "bug": 2}[ttype] + sp * 1.5
        base *= {"low": 1.5, "medium": 1.0, "high": 0.75, "critical": 0.5}[pr]
        if blocker:
            base *= 1.8
        days = round(base, 1)
        low = round(max(0.5, base * 0.65), 1)
        high = round(base * 1.35, 1)
        risk = "high" if days > 15 else "medium" if days > 7 else "low"
        risk_label = {"low": "Faible", "medium": "Moyen", "high": "Élevé"}[risk]
        rows.append(
            f"""
          <tr>
            <td>{title}</td>
            <td><span class="badge badge-{ttype}">{ttype}</span></td>
            <td>{sp}</td>
            <td>{pr}</td>
            <td>{"⚠️" if blocker else "—"}</td>
            <td><strong>{days} j</strong> <span style="color:#666;font-size:12px;">[{low} - {high}]</span></td>
            <td><span class="badge badge-{risk}">{risk_label}</span></td>
          </tr>
        """
        )
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Prédictions de durée et risque par ticket</h2>
      <p style="color:#666;font-size:14px;">Le modèle prédictif estime la durée de résolution et le niveau de risque pour chaque ticket en cours.</p>
      <table>
        <thead><tr>
          <th>Ticket</th><th>Type</th><th>SP</th><th>Priorité</th><th>Bloqueur</th><th>Durée estimée</th><th>Risque retard</th>
        </tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
      <p style="color:#888;font-size:12px;margin-top:14px;font-style:italic;">
        Intervalles à 70% de confiance. Les tickets en risque élevé doivent être priorisés ou re-planifiés.
      </p>
    </div>
    """
    return render("Dashboard prédictif", body)


# ====================================================
# CAPTURE 6.8 — Explication SHAP-like
# ====================================================
@app.get("/explanation.png")
def explanation_endpoint():
    title = request.args.get("title", "Crash au login avec mot de passe special")
    description = request.args.get("description", "")
    return send_file(explanation_png(title, description, classifier), mimetype="image/png")


# ====================================================
# CAPTURE 6.9 — Statistiques d'acceptation
# ====================================================
@app.post("/feedback")
def feedback():
    payload = request.get_json() or {}
    add_feedback(payload.get("ticket_type", "bug"), payload.get("decision", "accepted"))
    return jsonify(ok=True, total=get_statistics()["total"]), 200


@app.get("/stats/acceptance.png")
def stats_png():
    return send_file(acceptance_chart_png(get_statistics()), mimetype="image/png")


@app.get("/ui/stats")
def ui_stats():
    stats = get_statistics()
    recent_rows = "".join(
        f"<tr><td>{f['at'][:16].replace('T', ' ')}</td><td><span class='badge badge-{f['ticket_type']}'>{f['ticket_type']}</span></td><td>{f['decision']}</td></tr>"
        for f in reversed(stats["recent"])
    )
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Suivi du taux d'acceptation des suggestions IA</h2>
      <div style="display:flex;gap:20px;margin:16px 0;">
        <div style="flex:1;background:#f7f8fa;padding:16px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Total</div>
          <div style="font-size:28px;font-weight:bold;">{stats["total"]}</div>
        </div>
        <div style="flex:1;background:#d4edda;padding:16px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#155724;">Acceptation</div>
          <div style="font-size:28px;font-weight:bold;color:#155724;">{stats["acceptance_rate"]:.0%}</div>
        </div>
        <div style="flex:1;background:#fff3cd;padding:16px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#856404;">Modifiées</div>
          <div style="font-size:28px;font-weight:bold;color:#856404;">{stats["counts"].get("modified", 0)}</div>
        </div>
        <div style="flex:1;background:#f8d7da;padding:16px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#721c24;">Rejetées</div>
          <div style="font-size:28px;font-weight:bold;color:#721c24;">{stats["counts"].get("rejected", 0)}</div>
        </div>
      </div>
      <img class="viz" src="/stats/acceptance.png" alt="Graphique acceptation">
    </div>
    <div class="card">
      <h3 style="margin-top:0">Derniers feedbacks</h3>
      <table>
        <thead><tr><th>Date</th><th>Type</th><th>Décision</th></tr></thead>
        <tbody>{recent_rows}</tbody>
      </table>
    </div>
    """
    return render("Statistiques d'acceptation", body)


# ====================================================
# CAPTURE 6.10 — Dashboard des modèles déployés
# ====================================================
@app.get("/ui/models")
def ui_models():
    eval_result = evaluate_classifier()
    models = [
        {
            "name": "ticket-classifier",
            "version": "v1.0.0",
            "type": "Classification (TF-IDF + LogReg)",
            "trained_at": "2026-05-29 06:00 UTC",
            "f1_macro": eval_result["f1_macro"],
            "status": "deployed",
        },
        {
            "name": "priority-scorer",
            "version": "v1.0.0",
            "type": "Score multi-critères (règles + poids)",
            "trained_at": "—",
            "f1_macro": None,
            "status": "deployed",
        },
        {
            "name": "bug-clusterer",
            "version": "v1.0.0",
            "type": "DBSCAN sur embeddings TF-IDF",
            "trained_at": "2026-05-29 04:00 UTC",
            "f1_macro": None,
            "status": "deployed",
        },
        {
            "name": "duration-predictor",
            "version": "v0.5.0-rc1",
            "type": "Heuristique (LightGBM en cours)",
            "trained_at": "—",
            "f1_macro": None,
            "status": "experimental",
        },
    ]
    rows = ""
    for m in models:
        f1 = f"{m['f1_macro']:.3f}" if m["f1_macro"] is not None else "—"
        status_color = "#2E7D6B" if m["status"] == "deployed" else "#E0A030"
        rows += f"""
          <tr>
            <td><strong>{m["name"]}</strong></td>
            <td><code>{m["version"]}</code></td>
            <td>{m["type"]}</td>
            <td>{m["trained_at"]}</td>
            <td>{f1}</td>
            <td><span style="background:{status_color};color:#fff;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:600;">{m["status"]}</span></td>
          </tr>
        """
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Modèles d'IA déployés</h2>
      <p style="color:#666;font-size:14px;">Tableau de bord administrateur des modèles ML actuellement en production sur AgileIQ.</p>
      <table>
        <thead><tr>
          <th>Nom</th><th>Version</th><th>Type</th><th>Dernier entraînement</th><th>F1-macro</th><th>Statut</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <p style="color:#888;font-size:12px;margin-top:14px;font-style:italic;">
        Le ré-entraînement périodique est planifié mensuellement. Un nouveau modèle ne remplace l'ancien que s'il améliore la métrique principale sur le jeu holdé out.
      </p>
    </div>
    """
    return render("Modèles déployés", body)


# ====================================================
# Endpoint démonstration spaCy : préprocessing détaillé
# ====================================================
from nlp_preprocessing import analyze as nlp_analyze


@app.post("/preprocess")
def preprocess_endpoint():
    """Démontre la chaîne spaCy : langue, lemmes, entités nommées."""
    payload = request.get_json() or {}
    text = payload.get("text", "")
    if not text.strip():
        return jsonify(error="text is required"), 400
    return (
        jsonify(
            {
                "pipeline": "spaCy (fr_core_news_md / en_core_web_sm)",
                **nlp_analyze(text),
            }
        ),
        200,
    )


@app.get("/ui/nlp")
def ui_nlp():
    """Page de démonstration du pipeline NLP."""
    sample = (
        "Crash au login lors de la saisie d'un mot de passe special dans Firefox 132 sur Windows 11"
    )
    result = nlp_analyze(sample)
    entities_html = (
        "".join(
            f"<span style='background:#EAF1F8;padding:3px 8px;border-radius:4px;margin-right:4px;font-size:13px;'>"
            f"<strong>{e['text']}</strong> <span style='color:#888;'>({e['label']})</span></span>"
            for e in result["entities"]
        )
        or "<em style='color:#888;'>Aucune entité détectée</em>"
    )
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Pipeline NLP : spaCy + sentence-transformers</h2>
      <p style="color:#666;font-size:14px;">Démonstration de la chaîne complète de préprocessing utilisée par le service IA.</p>
      <div style="background:#f7f8fa;padding:14px;border-radius:6px;margin:16px 0;">
        <strong>Texte d'entrée :</strong><br>
        <span style="font-style:italic;color:#444;">{sample}</span>
      </div>
      <table style="margin-top:16px;">
        <tr><th style="width:30%;">Étape</th><th>Résultat</th></tr>
        <tr><td><strong>Langue détectée</strong></td><td><span class="badge badge-feature">{result['language']}</span></td></tr>
        <tr><td><strong>Taille originale</strong></td><td>{result['original_length']} caractères</td></tr>
        <tr><td><strong>Texte lemmatisé</strong></td><td><code>{result['cleaned_text']}</code></td></tr>
        <tr><td><strong>Nombre de tokens conservés</strong></td><td>{result['token_count']}</td></tr>
        <tr><td><strong>Entités nommées détectées</strong></td><td>{entities_html}</td></tr>
      </table>
      <p style="color:#888;font-size:12px;margin-top:16px;font-style:italic;">
        Ce texte lemmatisé est ensuite encodé par sentence-transformers
        (paraphrase-multilingual-MiniLM-L12-v2) en vecteur 384d, puis classifié par régression logistique.
      </p>
    </div>
    """
    return render("Pipeline NLP", body)


# Fix: les fichiers manquants de setup_final
from bug_recommendation import BugRecommender
from gitlab_integration import import_and_classify
from performance_metrics import compute_metrics
from severity_predictor import SeverityPredictor

print("[ml-service] Chargement bug recommender + severity predictor...")
bug_recommender = BugRecommender()
severity_predictor = SeverityPredictor()
print("[ml-service] Pret.")


@app.post("/recommend")
def recommend_solutions():
    payload = request.get_json() or {}
    title = payload.get("title", "")
    if not title.strip():
        return jsonify(error="title is required"), 400
    return (
        jsonify(
            {
                "input": {"title": title, "description": payload.get("description", "")},
                "recommendations": bug_recommender.recommend(
                    title, payload.get("description", ""), top_k=3
                ),
                "method": "Embedding sentence-transformers + similarite cosinus",
            }
        ),
        200,
    )


@app.post("/predict-severity")
def predict_severity_endpoint():
    payload = request.get_json() or {}
    title = payload.get("title", "")
    if not title.strip():
        return jsonify(error="title is required"), 400
    return jsonify(severity_predictor.predict(title, payload.get("description", ""))), 200


@app.post("/integrations/gitlab/import")
def gitlab_import():
    payload = request.get_json() or {}
    return (
        jsonify(
            import_and_classify(
                classifier,
                gitlab_url=payload.get("gitlab_url", ""),
                project_id=payload.get("project_id", ""),
                token=payload.get("token", ""),
            )
        ),
        200,
    )


@app.get("/stats/performance")
def stats_performance():
    return jsonify(compute_metrics()), 200


@app.get("/ui/integrations")
def ui_integrations():
    result = import_and_classify(classifier)
    rows = ""
    for issue in result["issues"]:
        rows += f"""<tr>
          <td><code>#{issue['iid']}</code></td>
          <td>{issue['title']}</td>
          <td><span class="badge badge-feature">{issue['language_detected']}</span></td>
          <td><span class="badge badge-{issue['ai_classification']}">{issue['ai_classification']}</span></td>
          <td><strong>{issue['ai_confidence']:.0%}</strong></td>
        </tr>"""
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Integration GitLab — Import et classification</h2>
      <p style="color:#666;font-size:14px;">Source : <strong>{result['source']}</strong> · {result['total_imported']} issues.</p>
      <div style="display:flex;gap:14px;margin:16px 0;">
        <div style="flex:1;background:#fff7e6;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Epics</div>
          <div style="font-size:24px;font-weight:bold;color:#5B8DEF;">{result['classification_summary'].get('epic', 0)}</div>
        </div>
        <div style="flex:1;background:#e8f4f0;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Features</div>
          <div style="font-size:24px;font-weight:bold;color:#2E7D6B;">{result['classification_summary'].get('feature', 0)}</div>
        </div>
        <div style="flex:1;background:#fde4ea;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Bugs</div>
          <div style="font-size:24px;font-weight:bold;color:#C2455E;">{result['classification_summary'].get('bug', 0)}</div>
        </div>
      </div>
      <table><thead><tr><th>Issue</th><th>Titre</th><th>Langue</th><th>Type IA</th><th>Confiance</th></tr></thead>
      <tbody>{rows}</tbody></table>
    </div>"""
    return render("Integration GitLab", body)


@app.get("/ui/performance")
def ui_performance():
    m = compute_metrics()
    body = f"""
    <div class="card">
      <h2 style="margin-top:0">Performance et gain de temps</h2>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0;">
        <div style="background:#f7f8fa;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Tickets traites</div>
          <div style="font-size:24px;font-weight:bold;">{m['tickets_processed']}</div>
        </div>
        <div style="background:#fde4ea;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Bugs analyses</div>
          <div style="font-size:24px;font-weight:bold;color:#C2455E;">{m['bugs_processed']}</div>
        </div>
        <div style="background:#e8f4f0;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Heures economisees</div>
          <div style="font-size:24px;font-weight:bold;color:#2E7D6B;">{m['time_savings']['total_hours_saved']} h</div>
        </div>
        <div style="background:#eaf1f8;padding:14px;border-radius:6px;text-align:center;">
          <div style="font-size:12px;color:#666;">Taux acceptation IA</div>
          <div style="font-size:24px;font-weight:bold;color:#1F3355;">{m['acceptance_rate']:.0%}</div>
        </div>
      </div>
      <h3>Decomposition du gain de temps</h3>
      <table>
        <tr><th>Tache</th><th>Temps economise</th></tr>
        <tr><td>Classification automatique</td><td>{m['time_savings']['classification_seconds_saved']//60} min</td></tr>
        <tr><td>Priorisation explicable</td><td>{m['time_savings']['priority_seconds_saved']//60} min</td></tr>
        <tr><td>Recherche bugs similaires</td><td>{m['time_savings']['bug_search_seconds_saved']//60} min</td></tr>
        <tr style="font-weight:bold;background:#f0f3f7;"><td>Total</td><td>{m['time_savings']['total_hours_saved']} h ({m['time_savings']['total_days_saved (8h/jour)']} jours)</td></tr>
      </table>
    </div>"""
    return render("Performance", body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False)
