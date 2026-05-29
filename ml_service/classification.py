"""Classifieur de tickets : TF-IDF + regression logistique multinomiale."""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from synthetic_data import get_training_data


class TicketClassifier:
    """Pipeline d'apprentissage et d'inference pour la classification de tickets."""

    def __init__(self) -> None:
        self.pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        min_df=1,
                        sublinear_tf=True,
                        lowercase=True,
                    ),
                ),
                (
                    "clf",
                    LogisticRegression(
                        C=1.0,
                        max_iter=1000,
                        multi_class="multinomial",
                        solver="lbfgs",
                    ),
                ),
            ]
        )
        self.classes_ = None

    def train(self):
        """Entrainement sur corpus synthetique au demarrage du service."""
        texts, labels = get_training_data()
        self.pipeline.fit(texts, labels)
        self.classes_ = self.pipeline.classes_
        return self

    def predict(self, title: str, description: str = "") -> dict:
        """Predit le type d'un ticket et retourne la confiance + explication."""
        text = f"{title} {description}".strip()
        probabilities = self.pipeline.predict_proba([text])[0]
        predicted_idx = int(np.argmax(probabilities))
        predicted_class = str(self.classes_[predicted_idx])
        confidence = float(probabilities[predicted_idx])

        # Top mots-cles ayant pese dans la decision
        vectorizer = self.pipeline.named_steps["tfidf"]
        classifier = self.pipeline.named_steps["clf"]
        feature_names = vectorizer.get_feature_names_out()
        token_indices = vectorizer.transform([text]).nonzero()[1]
        coefficients = classifier.coef_[predicted_idx]
        scored = sorted(
            ((feature_names[i], float(coefficients[i])) for i in token_indices),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        top_keywords = [w for w, _ in scored[:5]]

        return {
            "type": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": {
                str(c): round(float(p), 4)
                for c, p in zip(self.classes_, probabilities, strict=False)
            },
            "top_keywords": top_keywords,
            "explanation": (
                f"Classification automatique par TF-IDF + regression logistique "
                f"(confiance {confidence:.0%})."
            ),
        }
