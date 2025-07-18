import json
import torch
import os
import time
import requests
from datetime import datetime
from kafka import KafkaConsumer
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Load model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("models/distilbert-anomaly")
model = DistilBertForSequenceClassification.from_pretrained("models/distilbert-anomaly")
model.eval()

kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
alert_endpoint = os.getenv("ALERT_ENDPOINT", "http://fastapi:8000/alert")

print("🚀 Log stream consumer starting...")

# Retry logic in case Kafka is not ready
max_retries = 10
for attempt in range(max_retries):
    try:
        consumer = KafkaConsumer(
            'logs_topic',
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='alert-group'
        )
        print("🟢 Connected to Kafka. Listening for logs...")
        break
    except Exception:
        print(f"⏳ Kafka not ready, retrying in 5 seconds... ({attempt+1}/{max_retries})")
        time.sleep(5)
else:
    print("❌ Failed to connect to Kafka after retries.")
    exit(1)

# Consume and predict
for msg in consumer:
    print("📨 Message received")
    try:
        decoded = json.loads(msg.value.decode("utf-8"))
        log_text = decoded.get("log", "")
        print(f"🔍 Log: {log_text}")

        inputs = tokenizer(log_text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            prediction = torch.argmax(outputs.logits, dim=1).item()

        label = "DDoS" if prediction == 1 else "BENIGN"
        print(f"📌 Prediction: {label}")

        # Log to file
        with open("predictions.log", "a") as f:
            f.write(f"{datetime.now()} | {log_text} | Prediction: {label}\n")

        # Send alert if DDoS
        if label == "DDoS":
            alert_data = {
                "timestamp": str(datetime.now()),
                "log": log_text,
                "prediction": label
            }
            try:
                response = requests.post(alert_endpoint, json=alert_data)
                print(f"🔔 Alert sent: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Failed to send alert: {e}")

    except Exception as e:
        print(f"❌ Error processing log: {e}")
