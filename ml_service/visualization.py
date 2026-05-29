"""Visualisations : clusters t-SNE, SHAP-like, taux d'acceptation."""

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE


def clusters_tsne_png():
    """Projection 2D t-SNE de bugs synthétiques, colorés par cluster DBSCAN."""
    bugs = [
        ("Crash au login avec un mot de passe special", "cluster_login"),
        ("Erreur lors de la connexion sur Firefox", "cluster_login"),
        ("Bug d'authentification email avec accents", "cluster_login"),
        ("Login impossible apres mise a jour", "cluster_login"),
        ("Page de connexion blanche apres clic", "cluster_login"),
        ("Export CSV des projets ne fonctionne pas", "cluster_export"),
        ("L'export Excel produit un fichier corrompu", "cluster_export"),
        ("Telechargement CSV vide pour les bugs", "cluster_export"),
        ("Bouton export grise sur la page tickets", "cluster_export"),
        ("Notification email non envoyee aux assignes", "cluster_notif"),
        ("Probleme d'envoi de notification de creation", "cluster_notif"),
        ("Email de rappel non recu par les utilisateurs", "cluster_notif"),
        ("Affichage des graphiques sur Safari iPad", "isolated_1"),
        ("Pagination cassee sur la vue calendrier", "isolated_2"),
        ("Lenteur generale sur les requetes complexes", "isolated_3"),
    ]
    texts = [b[0] for b in bugs]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    matrix = vectorizer.fit_transform(texts).toarray()

    # Clustering DBSCAN
    dbscan = DBSCAN(eps=0.85, min_samples=2, metric="cosine")
    cluster_labels = dbscan.fit_predict(matrix)

    # Projection 2D
    tsne = TSNE(n_components=2, random_state=42, perplexity=3, init="random", learning_rate="auto")
    coords = tsne.fit_transform(matrix)

    _fig, ax = plt.subplots(figsize=(11, 7.5))
    unique_labels = sorted(set(cluster_labels))
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(unique_labels), 1)))

    for label, color in zip(unique_labels, colors, strict=False):
        mask = cluster_labels == label
        if label == -1:
            ax.scatter(
                coords[mask, 0],
                coords[mask, 1],
                c="lightgray",
                s=150,
                edgecolor="black",
                label="Bug isolé (non récurrent)",
                marker="x",
                linewidth=2,
            )
        else:
            ax.scatter(
                coords[mask, 0],
                coords[mask, 1],
                c=[color],
                s=200,
                edgecolor="black",
                label=f"Cluster {label}",
                alpha=0.85,
            )

    # Annoter chaque point avec un titre court
    for i, (x, y) in enumerate(coords):
        short_title = bugs[i][0][:32] + "…" if len(bugs[i][0]) > 32 else bugs[i][0]
        ax.annotate(
            short_title,
            (x, y),
            fontsize=7.5,
            xytext=(8, 5),
            textcoords="offset points",
            color="#222",
        )

    ax.set_title(
        "Figure 6.5 — Détection des bugs récurrents (t-SNE + DBSCAN)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Dimension t-SNE 1", fontsize=10)
    ax.set_ylabel("Dimension t-SNE 2", fontsize=10)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()
    buf.seek(0)
    return buf


def explanation_png(title: str, description: str, classifier):
    """Graphique 'SHAP-like' : contribution des mots a la prediction."""
    text = f"{title} {description}".strip()
    pipeline = classifier.pipeline
    vectorizer = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]

    probabilities = pipeline.predict_proba([text])[0]
    pred_idx = int(np.argmax(probabilities))
    predicted_class = str(classifier.classes_[pred_idx])

    feature_names = vectorizer.get_feature_names_out()
    token_indices = vectorizer.transform([text]).nonzero()[1]
    coefficients = clf.coef_[pred_idx]

    contributions = [(feature_names[i], float(coefficients[i])) for i in token_indices]
    contributions.sort(key=lambda x: x[1])
    top = contributions[-7:] + contributions[:3]  # 7 positifs + 3 négatifs
    top.sort(key=lambda x: x[1])

    words = [w for w, _ in top]
    values = [v for _, v in top]
    colors = ["#C2455E" if v < 0 else "#2E7D6B" for v in values]

    _fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(words, values, color=colors, edgecolor="black")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Contribution au score (coefficient x TF-IDF)", fontsize=11)
    ax.set_title(
        f"Figure 6.8 — Explication SHAP-like\nTicket : « {title[:55]} »  →  prédit : {predicted_class}",
        fontsize=12,
        fontweight="bold",
        pad=12,
    )
    for bar, v in zip(bars, values, strict=False):
        ax.text(
            v + (0.02 if v >= 0 else -0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{v:+.2f}",
            va="center",
            ha="left" if v >= 0 else "right",
            fontsize=9,
            fontweight="bold",
        )
    ax.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()
    buf.seek(0)
    return buf


def acceptance_chart_png(stats: dict):
    """Graphique du taux d'acceptation des suggestions."""
    _fig, ax = plt.subplots(figsize=(10, 5.5))

    types = list(stats.get("by_type", {}).keys()) or ["bug", "feature", "epic"]
    accepted = [stats["by_type"].get(t, {}).get("accepted", 0) for t in types]
    modified = [stats["by_type"].get(t, {}).get("modified", 0) for t in types]
    rejected = [stats["by_type"].get(t, {}).get("rejected", 0) for t in types]

    x = np.arange(len(types))
    width = 0.25
    ax.bar(x - width, accepted, width, label="Acceptées", color="#2E7D6B")
    ax.bar(x, modified, width, label="Modifiées", color="#E0A030")
    ax.bar(x + width, rejected, width, label="Rejetées", color="#C2455E")

    ax.set_xticks(x)
    ax.set_xticklabels(types, fontsize=11)
    ax.set_ylabel("Nombre de suggestions", fontsize=11)
    ax.set_title(
        f"Figure 6.9 — Taux d'acceptation des suggestions IA\n"
        f"Total : {stats['total']}  ·  Accept. : {stats['acceptance_rate']:.0%}",
        fontsize=12,
        fontweight="bold",
        pad=12,
    )
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close()
    buf.seek(0)
    return buf
