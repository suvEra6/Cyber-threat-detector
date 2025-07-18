from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import sqlite3
import os

# Load model and tokenizer
model_path = "models/distilbert-anomaly"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)
model.eval()

# FastAPI app
app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input for /predict
class FlowInput(BaseModel):
    dest_port: int
    flow_duration: int
    fwd_pkts: int
    bwd_pkts: int

# Ensure SQLite DB
os.makedirs("logs", exist_ok=True)
db_path = "logs/predictions.db"

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            dest_port INTEGER,
            flow_duration INTEGER,
            fwd_pkts INTEGER,
            bwd_pkts INTEGER,
            prediction TEXT,
            prob REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            log TEXT,
            prediction TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

label_map = {0: "BENIGN", 1: "DDoS"}

@app.post("/predict")
async def predict_log(input: FlowInput):
    input_text = (
        f"DestPort: {input.dest_port}, Flow Duration: {input.flow_duration}, "
        f"Fwd Pkts: {input.fwd_pkts}, Bwd Pkts: {input.bwd_pkts}, "
    )

    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        prediction = torch.argmax(probs, dim=1).item()
        confidence = probs[0][prediction].item()

    label = label_map[prediction]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (
            timestamp, dest_port, flow_duration, fwd_pkts, bwd_pkts, prediction, prob
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        input.dest_port,
        input.flow_duration,
        input.fwd_pkts,
        input.bwd_pkts,
        label,
        confidence
    ))
    conn.commit()
    conn.close()

    return {"prediction": label, "confidence": round(confidence * 100, 2)}

@app.post("/alert")
async def receive_alert(request: Request):
    data = await request.json()
    print(f"🔔 Alert received: {data}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (timestamp, log, prediction)
        VALUES (?, ?, ?)
    """, (
        data.get("timestamp", datetime.now().isoformat()),
        data.get("log", "N/A"),
        data.get("prediction", "N/A")
    ))
    conn.commit()
    conn.close()

    return {"status": "received", "data": data}
