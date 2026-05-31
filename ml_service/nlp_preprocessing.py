"""Préprocessing NLP des tickets avec spaCy (multilingue FR/EN)."""

import re

import spacy

# Chargement des modèles spaCy au démarrage
print("[ml-service] Chargement de spaCy...")
NLP_FR = spacy.load("fr_core_news_md")
NLP_EN = spacy.load("en_core_web_sm")
print("[ml-service] spaCy prêt (FR + EN).")

# Indices simples de langue
_FRENCH_INDICATORS = {
    "le",
    "la",
    "les",
    "de",
    "des",
    "un",
    "une",
    "est",
    "et",
    "ne",
    "pas",
    "ce",
    "se",
    "qui",
    "que",
    "dans",
    "pour",
    "sur",
    "avec",
    "lors",
    "lorsque",
}


def detect_language(text: str) -> str:
    """Détection rapide FR vs EN par occurrence de mots-clés."""
    words = set(re.findall(r"\b\w+\b", text.lower()))
    if len(_FRENCH_INDICATORS & words) >= 2:
        return "fr"
    return "en"


def preprocess(text: str) -> tuple[str, str]:
    """Pipeline spaCy : tokenisation, lemmatisation, suppression stopwords/ponctuation.

    Returns:
        tuple (texte_nettoye, langue_detectee)
    """
    if not text or not text.strip():
        return "", "fr"
    lang = detect_language(text)
    nlp = NLP_FR if lang == "fr" else NLP_EN
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space and len(token.text) > 1
    ]
    return " ".join(tokens), lang


def extract_entities(text: str) -> list[dict]:
    """Extraction des entités nommées par spaCy NER."""
    if not text.strip():
        return []
    lang = detect_language(text)
    nlp = NLP_FR if lang == "fr" else NLP_EN
    doc = nlp(text)
    return [
        {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
        for ent in doc.ents
    ]


def analyze(text: str) -> dict:
    """Analyse complète : préprocessing + entités + statistiques."""
    cleaned, lang = preprocess(text)
    return {
        "language": lang,
        "original_length": len(text),
        "cleaned_text": cleaned,
        "cleaned_length": len(cleaned),
        "token_count": len(cleaned.split()) if cleaned else 0,
        "entities": extract_entities(text),
    }
