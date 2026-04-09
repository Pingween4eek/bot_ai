import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)

MODEL_NAME = "DeepPavlov/rubert-base-cased"
OUTPUT_DIR = "intent_model"
NUM_EPOCHS = 4
BATCH_SIZE = 8

df = pd.read_csv("dataset.csv")

label2id = {label: idx for idx, label in enumerate(df["intent"].unique())}
id2label  = {idx: label for label, idx in label2id.items()}

df["label"] = df["intent"].map(label2id)

print("Интенты и их ID:")
for label, idx in label2id.items():
    print(f"  {idx}: {label}")

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["text"].tolist(),
    df["label"].tolist(),
    test_size=0.2,
    random_state=42,
)
print(f"\nТrain: {len(train_texts)}, Val: {len(val_texts)}")

print("\nЗагрузка токенайзера...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def tokenize(texts: list[str]) -> dict:
    return tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )


train_encodings = tokenize(train_texts)
val_encodings   = tokenize(val_texts)

class IntentDataset(torch.utils.data.Dataset):

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels    = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = IntentDataset(train_encodings, train_labels)
val_dataset   = IntentDataset(val_encodings,   val_labels)

print("Загрузка RuBERT...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label2id),   # количество интентов
    id2label=id2label,
    label2id=label2id,
)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    logging_dir="./logs",
    logging_steps=10,
    learning_rate=2e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

print("\nНачало обучения...")
trainer.train()

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"\nМодель сохранена в папку: {OUTPUT_DIR}/")

print("\n--- Проверка ---")
model.eval()
test_phrases = [
    "привет",
    "как поживаешь",
    "пока",
    "погода завтра в Москве",
    "сколько сейчас время",
    "будут ли осадки завтра",
]
for phrase in test_phrases:
    inputs = tokenizer(phrase, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits          = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()
    proba           = torch.softmax(logits, dim=1)
    confidence      = proba[0][predicted_class].item()
    intent          = id2label[predicted_class]
    print(f"  {phrase!r:35} -> {intent:12} ({confidence:.2f})")