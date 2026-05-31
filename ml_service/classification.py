"""Classifieur AgileIQ : spaCy → sentence-transformers → LogReg."""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

from nlp_preprocessing import preprocess
from synthetic_data import get_training_data

# Chargement du modèle d'embedding multilingue au démarrage
print("[ml-service] Chargement de sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)...")
EMBEDDING_MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_DIM = EMBEDDING_MODEL.get_sentence_embedding_dimension()
print(f"[ml-service] sentence-transformers prêt (dimension = {EMBEDDING_DIM}).")


class TicketClassifier:
    """Pipeline : spaCy lemmatisation → embeddings 384d → régression logistique."""

    def __init__(self) -> None:
        self.classifier = LogisticRegression(
            C=1.0,
            max_iter=1000,
            solver="lbfgs",
            multi_class="multinomial",
        )
        self.classes_ = None
        self.embedder = EMBEDDING_MODEL

    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        """Préprocessing spaCy puis embedding par batch."""
        cleaned = [preprocess(t)[0] for t in texts]
        return self.embedder.encode(
            cleaned,
            show_progress_bar=False,
            convert_to_numpy=True,
            batch_size=16,
        )

    def train(self):
        """Entrainement sur le corpus synthétique."""
        texts, labels = get_training_data()
        print(f"[ml-service] Entrainement sur {len(texts)} exemples...")
        embeddings = self._embed_batch(texts)
        self.classifier.fit(embeddings, labels)
        self.classes_ = self.classifier.classes_
        print(f"[ml-service] Classifieur entraîné. Classes : {self.classes_.tolist()}")
        return self

    def predict(self, title: str, description: str = "") -> dict:
        """Prédit le type d'un ticket et retourne confiance, langue, explication."""
        text = f"{title} {description}".strip()
        cleaned, language = preprocess(text)
        embedding = self.embedder.encode(
            [cleaned],
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        probabilities = self.classifier.predict_proba(embedding)[0]
        pred_idx = int(np.argmax(probabilities))
        predicted_class = str(self.classes_[pred_idx])
        confidence = float(probabilities[pred_idx])

        return {
            "type": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": {
                str(c): round(float(p), 4) for c, p in zip(self.classes_, probabilities)
            },
            "language_detected": language,
            "preprocessed_text": cleaned,
            "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
            "embedding_dim": int(embedding.shape[1]),
            "explanation": (
                f"Classification par embeddings sentence-transformers ({EMBEDDING_DIM}d) "
                f"+ régression logistique (confiance {confidence:.0%}, langue {language})."
            ),
        }
