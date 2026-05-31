import numpy as np

from classification import EMBEDDING_MODEL
from nlp_preprocessing import preprocess
from resolved_bugs import get_all_resolved


class BugRecommender:
    def __init__(self):
        self.embedder = EMBEDDING_MODEL
        self.resolved = get_all_resolved()
        self._index = self._build_index()

    def _build_index(self):
        texts = [preprocess(f"{b['title']} {b['description']}")[0] for b in self.resolved]
        return self.embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    def recommend(self, title: str, description: str = "", top_k: int = 3) -> list:
        query_text = preprocess(f"{title} {description}")[0]
        query_emb = self.embedder.encode(
            [query_text], show_progress_bar=False, convert_to_numpy=True
        )[0]
        norms = np.linalg.norm(self._index, axis=1) * np.linalg.norm(query_emb)
        scores = np.dot(self._index, query_emb) / (norms + 1e-9)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {
                "id": self.resolved[i]["id"],
                "title": self.resolved[i]["title"],
                "resolution": self.resolved[i]["resolution"],
                "severity": self.resolved[i]["severity_resolved"],
                "similarity": float(round(scores[i], 4)),
                "resolved_at": self.resolved[i]["resolved_at"],
            }
            for i in top_indices
        ]
