import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

def preprocess(text: str) -> str:
    return text.lower().strip()


# Загрузка датасета
data   = pd.read_csv("dataset.csv")
texts  = data["text"].tolist()
labels = data["intent"].tolist()

processed_texts = [preprocess(t) for t in texts]

# Разделение на train/test
X_train, X_test, y_train, y_test = train_test_split(
    processed_texts, labels, test_size=0.2, random_state=42
)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("clf",   LogisticRegression(max_iter=1000)),
])

print("Обучение модели...")
pipeline.fit(X_train, y_train)

accuracy = pipeline.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2%}")
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(pipeline, "intent_model.pkl")
print("Модель сохранена: intent_model.pkl")
