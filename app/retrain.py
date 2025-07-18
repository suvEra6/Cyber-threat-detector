import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch

# Load and sample data
df = pd.read_csv("data/formatted_logs.csv")

# 🧪 Sample balanced data
ddos_df = df[df["label"] == 1].sample(5000, random_state=42)
benign_df = df[df["label"] == 0].sample(5000, random_state=42)
df_balanced = pd.concat([ddos_df, benign_df]).sample(frac=1, random_state=42)

# Split
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df_balanced["log_text"], df_balanced["label"], test_size=0.2, random_state=42
)

# Tokenize
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
train_encodings = tokenizer(train_texts.tolist(), truncation=True, padding=True, max_length=256)
val_encodings = tokenizer(val_texts.tolist(), truncation=True, padding=True, max_length=256)

# Datasets
train_dataset = Dataset.from_dict({**train_encodings, "label": train_labels.tolist()})
val_dataset = Dataset.from_dict({**val_encodings, "label": val_labels.tolist()})

# Model
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# Training args
training_args = TrainingArguments(
    output_dir="./models",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    logging_dir="./logs"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# 🔁 Train
trainer.train()

# ✅ Save model
model.save_pretrained("models/distilbert-anomaly")
tokenizer.save_pretrained("models/distilbert-anomaly")

print("✅ Model and tokenizer saved to models/distilbert-anomaly")
