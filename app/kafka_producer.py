from kafka import KafkaProducer
import pandas as pd
import time
import json

# Load formatted logs
df = pd.read_csv("data/formatted_logs.csv")
logs = df["log_text"].tolist()

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("🟢 Kafka Producer started. Streaming logs...")

index = 0
while True:
    # Cycle through the logs endlessly
    log = logs[index % len(logs)]
    producer.send("logs_topic", {"log": log})
    print(f"📤 Sent: {log}")
    
    index += 1
    time.sleep(2)  # Wait 2 seconds to simulate real-time data flow
