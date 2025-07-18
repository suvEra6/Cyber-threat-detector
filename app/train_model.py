import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch
import os

# ✅ Step 1: Load data
df = pd.read_csv("data/formatted_logs.csv")
input_texts = df["log_text"].tolist()
labels = df["label"].tolist()

# ✅ Step 2: Create input text WITHOUT leaking the label
# Assumes these are the columns from your formatting script
#input_texts = [
#    f"DestPort: 80, Flow Duration: {row.flow_duration}, Fwd Pkts: {row.fwd_pkts}, Bwd Pkts: {row.bwd_pkts}"
#    for row in df.itertuples()
#]



# ✅ Step 3: Split the dataset
train_texts, val_texts, train_labels, val_labels = train_test_split(
    input_texts, labels, test_size=0.2, random_state=42
)

# ✅ Step 4: Tokenize
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=256)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=256)

# ✅ Step 5: Convert to HuggingFace Dataset
train_dataset = Dataset.from_dict({**train_encodings, "label": train_labels})
val_dataset = Dataset.from_dict({**val_encodings, "label": val_labels})

# ✅ Step 6: Load model
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# ✅ Step 7: Training arguments
training_args = TrainingArguments(
    output_dir="./models",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    evaluation_strategy="epoch",
    logging_dir="./logs",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    save_total_limit=1,
)

# ✅ Step 8: Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# ✅ Step 9: Train
trainer.train()

# ✅ Step 10: Save model and tokenizer
os.makedirs("models/distilbert-anomaly", exist_ok=True)
model.save_pretrained("models/distilbert-anomaly")
tokenizer.save_pretrained("models/distilbert-anomaly")

print("✅ Model and tokenizer saved to models/distilbert-anomaly")
