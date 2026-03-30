"""
Модуль определения интента через Word Embeddings (spaCy + LogisticRegression).

Вместо TF-IDF каждое слово превращается в вектор из 300 чисел,
затем spaCy усредняет их в один вектор предложения.
Это позволяет понимать семантически близкие слова:
    "дождь" ~ "осадки" ~ "ливень"  (близкие векторы)
    "дождь" vs "кошка"             (далёкие векторы)
"""

import numpy as np
import joblib
import spacy

# ru_core_news_md обязательна — содержит векторы слов
nlp = spacy.load("ru_core_news_md")

# Загрузка обученного классификатора
_model = joblib.load("intent_model.pkl")


def vectorize(text: str) -> np.ndarray:
    """Преобразует текст в вектор через Word Embeddings spaCy."""
    doc = nlp(text.lower())
    return doc.vector  # shape (300,)


def predict_intent(text: str) -> str:
    """Возвращает интент для текста."""
    vec = vectorize(text).reshape(1, -1)
    return _model.predict(vec)[0]


def predict_with_confidence(text: str) -> tuple[str, float]:
    """Возвращает интент и уверенность модели (0.0 — 1.0)."""
    vec        = vectorize(text).reshape(1, -1)
    proba      = _model.predict_proba(vec)
    intent     = _model.predict(vec)[0]
    confidence = max(proba[0])
    return intent, confidence