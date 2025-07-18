from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',  # Match docker-compose port for Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

sample_logs = [
    {"log": "User logged in from IP 192.168.1.1"},
    {"log": "DDOS attack detected on port 443"},
    {"log": "System health check passed"},
    {"log": "Suspicious activity from multiple IPs within 1 second"},
    {"log": "Normal traffic observed"},
]

for log in sample_logs:
    print(f"📤 Sending: {log['log']}")
    producer.send("logs_topic", value=log)
    time.sleep(1)  # small delay to simulate streaming

producer.flush()
producer.close()
print("✅ All logs sent.")
