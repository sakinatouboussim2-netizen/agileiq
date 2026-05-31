FROM python:3.11-slim

# Dépendances système pour spaCy et matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libfreetype6-dev libpng-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pré-télécharge les modèles spaCy (français + anglais)
RUN python -m spacy download fr_core_news_md
RUN python -m spacy download en_core_web_sm

# Pré-télécharge le modèle sentence-transformers multilingue
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8001
CMD ["python", "app.py"]
