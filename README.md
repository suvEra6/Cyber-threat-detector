 Cyber Threat Detector

---

##  Intro

Network logs are noisy. Sifting through them for threats? Even noisier. So I decided to hand the job to a fine-tuned language model (because AI doesn’t complain about overtime).

Cyber Threat Detector is your smart, always-on buddy that sniffs out DDoS attacks in real time. Built with FastAPI, Kafka, HuggingFace Transformers, and a sprinkle of DevOps fairy dust (Docker), it processes logs, classifies threats, and logs it all so you can sip your coffee without worrying about packet floods.

Whether you're learning, building, or just tired of staring at logs that look like digital soup, this project has your back.

---

##  What It Does

* Listens to network traffic in real time (Kafka consumer-style)
* Uses a custom-trained DistilBERT model to classify logs as BENIGN or DDoS
* Sends predictions to a FastAPI backend and stores them in a SQLite database
* Optionally provides a frontend where you can manually submit logs for prediction
* Runs in Docker for smooth orchestration and deployment

##  Project Structure

```
cyber-threat-detector/
│
├── app/                          # Main application logic
│   ├-- main.py                   # FastAPI backend (predicts and logs to DB)
│   ├-- log_stream_predictor.py   # Kafka consumer + BERT predictions
│   ├-- train_model.py            # Script to train DistilBERT
│   ├-- preprocess.py             # Log preprocessing for training
│   └-- kafka_producer.py         # (Optional) another log-sender
│
├── models/                       # Pretrained model directory (distilbert-anomaly/)
│
├── logs/                         # Stores predictions.log and SQLite DB
│
├── frontend/                     # Optional frontend to submit logs
│   └-- index.html
│
├── log_sender.py                 # Sends test logs to Kafka topic
├── requirements.txt              # Python deps
├── Dockerfile                    # Builds FastAPI service
├── dockerfile.consumer           # Dockerfile for log_stream_predictor
├── docker-compose.yml            # Spins everything up
├── .dockerignore
└── README.md                     # You’re reading this 
```

##  How to Run It (Your Cyber Senses, Now Online)

### 1. Clone the Repo (a.k.a. bring it home)

```bash
git clone https://github.com/yourusername/cyber-threat-detector.git
cd cyber-threat-detector
```

### 2. Build & Start the Stack with Docker 

Make sure Docker Desktop is running. Then:

```bash
docker-compose up --build
```

This will spin up:

* Kafka in KRaft mode (no Zookeeper drama )
* FastAPI backend for predictions (/predict)
* Kafka consumer running log\_stream\_predictor.py

Grab a coffee  while Kafka boots. First-time build may take a minute.

### 3. Send Some Test Logs (Let the logs flow)

```bash
python log_sender.py
```

This will send logs like:

```
 Log: DDOS attack detected on port 443
 Prediction: DDoS
```

### 4. Try the Frontend (Optional, but flashy )

* Open frontend/index.html in your browser
* Enter log details
* Click Predict to see real-time classification

### 5. Check the Results

*  Console: Real-time logs and predictions
*  logs/predictions.log: Logs every prediction
*  logs/predictions.db: SQLite DB for predictions (use DB browser!)

### 6. Bonus: API Endpoint

```http
POST http://localhost:8000/predict
```

Payload:

```json
{
  "dest_port": 443,
  "flow_duration": 123456,
  "fwd_pkts": 5,
  "bwd_pkts": 1
}
```

Response:

```json
{
  "prediction": "DDoS",
  "confidence": 94.3
}
```

###  Sample Input & Output

Input:

```
DestPort: 80, Flow Duration: 3200000, Fwd Pkts: 3, Bwd Pkts: 2
```

Output:

```
 Log: DestPort: 80, Flow Duration: 3200000, Fwd Pkts: 3, Bwd Pkts: 2
 Prediction: BENIGN
```

---

##  Model Training

Trained on CICDDoS2019 logs with labels.

To retrain:

```bash
python app/train_model.py
```

To preprocess before that:

```bash
python app/preprocess.py
```

Output will land in models/distilbert-anomaly.

##  How It Works (Nutshell Edition)

1. Kafka Producer ➔ sends logs to logs\_topic
2. Kafka Consumer ➔ reads logs, sends them through DistilBERT
3. Predictions go to SQLite & logs/predictions.log
4. FastAPI exposes a /predict endpoint
5. You interact via browser or HTTP tools (Postman, curl, etc.)

##  Future Work ("maybe later, maybe never")

* Alerting system (Slack, email)
* More attack types (BotNet, PortScan, etc.)
* Swap SQLite with PostgreSQL
* Live dashboard (charts, trends)
* Real frontend (React, Svelte, etc.)

##  FAQ

Q: Can I run this on a Raspberry Pi?
A: Maybe. If you believe in magic and have lots of RAM.

Q: Does it detect all threats?
A: Right now, just DDoS. But easy to extend!

Q: Why use DistilBERT?
A: Because logs are weird text, and BERT loves weird text.

##  Cleanup

When you're done:

```bash
docker-compose down -v
docker system prune -a --volumes
```

##  Contributions?

PRs welcome! Got ideas for improvements? Fork away!

##  License

MIT. Use it, remix it, break it (and maybe fix it).

##  Done!

Congrats, you've built a real-time cyber threat detector. High-five! 
![WhatsApp Image 2025-08-05 at 16 24 18_0da263a8](https://github.com/user-attachments/assets/de3f0d2c-9803-4a80-9991-b4a561538289)


