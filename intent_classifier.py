import joblib
import spacy

nlp = spacy.load("ru_core_news_sm")

_pipeline = joblib.load("intent_model.pkl")


def preprocess(text: str) -> str:
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and token.lemma_.strip()
    ]
    return " ".join(tokens) or text.lower()


def predict_intent(text: str) -> str:
    processed = preprocess(text)
    return _pipeline.predict([processed])[0]


def predict_with_confidence(text: str) -> tuple[str, float]:
    processed  = preprocess(text)
    vector     = _pipeline.named_steps["tfidf"].transform([processed])
    proba      = _pipeline.named_steps["clf"].predict_proba(vector)
    confidence = max(proba[0])
    intent     = _pipeline.named_steps["clf"].predict(vector)[0]
    return intent, confidence
