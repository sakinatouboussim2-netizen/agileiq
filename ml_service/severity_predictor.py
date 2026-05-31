import numpy as np
from sklearn.linear_model import LogisticRegression

from classification import EMBEDDING_MODEL
from nlp_preprocessing import preprocess

TRAINING_BUGS = [
    ("Crash total application au demarrage", "critical"),
    ("Application inutilisable apres deploiement", "critical"),
    ("Perte de donnees utilisateurs en base", "critical"),
    ("Faille de securite acces non autorise", "critical"),
    ("Erreur 500 sur tous les endpoints API", "critical"),
    ("Crash login Firefox specifique", "major"),
    ("Export CSV produit fichier vide", "major"),
    ("Notifications email non envoyees", "major"),
    ("Bug authentification avec accents", "major"),
    ("Lenteur generale interface", "minor"),
    ("Pagination cassee mode calendrier", "minor"),
    ("Couleur des badges incorrecte", "minor"),
    ("Typo dans le message d erreur", "trivial"),
    ("Renommer un libelle dans le menu", "trivial"),
]


class SeverityPredictor:
    def __init__(self):
        self.embedder = EMBEDDING_MODEL
        self.clf = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")
        self._train()

    def _train(self):
        texts = [preprocess(t)[0] for t, _ in TRAINING_BUGS]
        labels = [s for _, s in TRAINING_BUGS]
        embeddings = self.embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        self.clf.fit(embeddings, labels)
        self.classes_ = self.clf.classes_

    def predict(self, title: str, description: str = "") -> dict:
        text = preprocess(f"{title} {description}")[0]
        embedding = self.embedder.encode([text], show_progress_bar=False, convert_to_numpy=True)
        probabilities = self.clf.predict_proba(embedding)[0]
        pred_idx = int(np.argmax(probabilities))
        predicted = str(self.classes_[pred_idx])
        confidence = float(probabilities[pred_idx])
        return {
            "predicted_severity": predicted,
            "confidence": round(confidence, 4),
            "probabilities": {
                str(c): round(float(p), 4) for c, p in zip(self.classes_, probabilities)
            },
            "is_critical": predicted in ("critical", "major"),
            "recommended_action": (
                "Traiter en priorite immediate"
                if predicted in ("critical", "major")
                else "Traiter dans le sprint courant"
            ),
        }
