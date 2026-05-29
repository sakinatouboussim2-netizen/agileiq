"""Évaluation du classifieur : confusion matrix, F1-score, rapport."""

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from synthetic_data import get_training_data

CLASSES = ["bug", "epic", "feature"]


def evaluate_classifier():
    """Refait l'entrainement sur train/test split et retourne les metriques."""
    texts, labels = get_training_data()
    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.30,
        random_state=42,
        stratify=labels,
    )
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            (
                "clf",
                LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs", multi_class="multinomial"),
            ),
        ]
    )
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)
    cm = confusion_matrix(y_test, y_pred, labels=CLASSES)
    return {
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "f1_per_class": dict(
            zip(CLASSES, f1_score(y_test, y_pred, labels=CLASSES, average=None), strict=False)
        ),
        "confusion_matrix": cm.tolist(),
        "labels": CLASSES,
        "test_size": len(y_test),
        "train_size": len(y_train),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }


def confusion_matrix_png():
    """Genere la matrice de confusion sous forme d'image PNG."""
    result = evaluate_classifier()
    cm = np.array(result["confusion_matrix"])
    f1_macro = result["f1_macro"]

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title(
        f"Matrice de confusion — classifieur AgileIQ\nF1-macro = {f1_macro:.3f}",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set_xticks(range(len(CLASSES)))
    ax.set_yticks(range(len(CLASSES)))
    ax.set_xticklabels(CLASSES, fontsize=11)
    ax.set_yticklabels(CLASSES, fontsize=11)
    ax.set_xlabel("Classe prédite", fontsize=11, fontweight="bold")
    ax.set_ylabel("Classe réelle", fontsize=11, fontweight="bold")

    thresh = cm.max() / 2.0
    for i in range(len(CLASSES)):
        for j in range(len(CLASSES)):
            ax.text(
                j,
                i,
                format(cm[i, j], "d"),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=14,
                fontweight="bold",
            )

    # F1 per class en dessous
    f1_per_class = result["f1_per_class"]
    text = "  ".join(f"F1({c}) = {f:.2f}" for c, f in f1_per_class.items())
    fig.text(0.5, 0.02, text, ha="center", fontsize=10, style="italic", color="#444")

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white")
    plt.close()
    buf.seek(0)
    return buf
