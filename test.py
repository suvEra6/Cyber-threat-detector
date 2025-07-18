import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

tokenizer = DistilBertTokenizer.from_pretrained("models/distilbert-anomaly")
model = DistilBertForSequenceClassification.from_pretrained("models/distilbert-anomaly")

input_text = "DestPort: 80, Flow Duration: 80034360, Fwd Pkts: 8, Bwd Pkts: 4"
inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)
probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

prediction = probs.argmax(dim=1).item()
print("Prediction:", "DDoS" if prediction == 1 else "BENIGN")
print("Probabilities:", probs.tolist())
