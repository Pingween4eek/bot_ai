import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "intent_model"

print("Загрузка BERT модели...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

id2label = model.config.id2label
print(f"Модель загружена. Интенты: {list(id2label.values())}")


_bert_cache: dict[str, tuple[str, float]] = {}


def predict_with_confidence(text: str) -> tuple[str, float]:
    if text in _bert_cache:
        return _bert_cache[text]

    # Токенизация
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits          = outputs.logits
    proba           = torch.softmax(logits, dim=1)
    predicted_class = torch.argmax(logits, dim=1).item()
    confidence      = proba[0][predicted_class].item()
    intent          = id2label[predicted_class]

    result = (intent, confidence)
    _bert_cache[text] = result
    return result


def predict_intent(text: str) -> str:
    intent, _ = predict_with_confidence(text)
    return intent