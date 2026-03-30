import pandas as pd
import numpy as np
import joblib
import spacy
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

nlp = spacy.load("ru_core_news_md")


def vectorize(text: str) -> np.ndarray:
    doc = nlp(text.lower())
    return doc.vector


data   = pd.read_csv("dataset.csv")
texts  = data["text"].tolist()
labels = data["intent"].tolist()

print("Векторизация через Word Embeddings")
X = np.array([vectorize(text) for text in texts])
y = labels
print(f"Матрица: {X.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Обучение на векторах слов")
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"\nAccuracy: {accuracy:.2%}")
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(model, "intent_model.pkl")
print("Модель сохранена: intent_model.pkl")

print("\n--- Проверка фраз ---")
test_phrases = [
    "как поживаешь",
    "пока",
    "привет",
    "погода завтра в Москве",
    "сколько сейчас время",
    "будут ли осадки завтра",
    "что нового",
    "нужен ли зонт",
]
for phrase in test_phrases:
    vec    = vectorize(phrase).reshape(1, -1)
    intent = model.predict(vec)[0]
    conf   = max(model.predict_proba(vec)[0])
    print(f"  {phrase!r:35} -> {intent:12} ({conf:.2f})")