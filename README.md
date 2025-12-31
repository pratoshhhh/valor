# VALOR – VA Disability Reporting & Health Evidence Platform

VALOR is a veteran-focused health documentation and reporting system designed to make VA disability claims faster, clearer, and easier to approve. The platform continuously collects and organizes health and exposure data from service environments, transforming it into VA-ready medical evidence and AI-assisted disability reports. It does so through by tracking IoT sensors and environmental monitors. The platform processes battlefield health data through a Kafka streaming pipeline, stores it in Firestore, and provides commanders with a real-time dashboard for generating AI-powered VA disability reports.

**Live Demo:** [https://valorstream-demo-1.web.app](https://valorstream-demo-1.web.app)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

### AI-Powered Analytics
- **VA Report Generation** - AI-powered disability claim reports using Google Gemini
- **PDF Export** - Professional multi-page VA reports with medical analysis
- **Predictive Analytics** - Risk assessment and health score calculation

### Real-Time Monitoring
- **Live Health Alerts** - Monitor critical events (burn pit exposure, cardiac events, heat stress)
- **Interactive Dashboard** - Real-time stats with 10-second polling intervals
- **Alert Management** - Filter, search, and resolve health alerts
- **Data Visualization** - Charts and graphs for health trends

### Data Pipeline
- **Kafka Streaming** - Real-time battlefield sensor data processing
- **Event Processing** - Avro schema-based message serialization
- **Firestore Storage** - Scalable NoSQL database for soldier records
- **Cloud Functions** - Serverless API endpoints

---

## Architecture

```
┌─────────────────┐
│  IoT Sensors    │
│  (Biometric &   │
│  Environmental) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│    Producer     │────▶│ Kafka Topic  │────▶│    Consumer     │
│  (Python/Avro)  │     │ (Confluent)  │     │  (Python/Avro)  │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
                                            ┌─────────────────┐
                                            │   Firestore     │
                                            │   Database      │
                                            └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Cloud Functions │
                                            │   (6 APIs)      │
                                            └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ React Dashboard │
                                            │ (Firebase Host) │
                                            └─────────────────┘
```

---

## Tech Stack

### Frontend
- **React 18** - UI framework
- **React Router 6** - Navigation
- **Chart.js** - Data visualization
- **Lucide React** - Icons
- **Bootstrap 5** - UI components

### Backend
- **Google Cloud Functions** - Serverless APIs (Python 3.11)
- **Firestore** - NoSQL database
- **Cloud Storage** - PDF storage
- **Gemini AI** - Report generation

### Data Pipeline
- **Confluent Kafka** - Message streaming
- **Avro** - Schema serialization
- **Python 3.11** - Producer/Consumer

### Deployment
- **Firebase Hosting** - Frontend hosting
- **Google Cloud Platform** - Cloud infrastructure
- **GitHub** - Version control

---

## Project Structure

```
valor/
├── backend/
│   └── functions/                # Cloud Functions (Python APIs)
│       ├── main.py
│       ├── requirements.txt
│       └── deploy.sh
├── bin/                          # (likely build / utility scripts)
├── config/                       # Config files used by services
├── consumers/                    # Kafka consumers
├── firestore/                    # Firestore-related setup/scripts
├── infrastructure/
│   └── scripts/                  # Scripts for deployment/infrastructure tasks
├── ksql/                         # ksqlDB scripts for Kafka streams
├── monitoring/                   # Monitoring/config tooling
├── producers/                    # Kafka producers
├── schemas/                      # Avro schemas for events
├── scripts/                      # Misc scripts
├── utils/                        # Utility modules
├── valor-dashboard/              # React frontend for dashboard
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   ├── firebase.json
│   └── README.md
├── .gitignore
├── LICENSE
├── README.md
├── initialize_firestore.py       # Script to initialize Firestore data
└── inspect_firestore.py          # Script to inspect Firestore contents
---

```

## Prerequisites

- **Node.js** (v16+)
- **Python** (3.11+)
- **Google Cloud Account**
- **Confluent Kafka Account** (optional)
- **Firebase CLI**
- **Git**

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/pratoshhhh/valor.git
cd valor
```

### 2. Frontend Setup

```bash
cd valor-dashboard
npm install
```

### 3. Backend Setup (Optional - for local development)

```bash
cd ../valor
pip install -r requirements.txt --break-system-packages
```

### 4. Firebase Setup

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize project (if not already done)
firebase init
```

---

## Configuration

### 1. Environment Variables

Create `valorstream/config/config.py`:

```python
# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'your-kafka-server.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'your-api-key',
    'sasl.password': 'your-api-secret',
}

# Schema Registry
SCHEMA_REGISTRY_CONFIG = {
    'url': 'https://your-schema-registry.confluent.cloud',
    'basic.auth.user.info': 'your-sr-key:your-sr-secret'
}

# GCP Configuration
GCP_PROJECT_ID = 'valorstream-demo-1'
```

### 2. Firebase Configuration

Update `valor-dashboard/src/services/api.js` with your Cloud Function URLs:

```javascript
const API_BASE = {
  ingestEvents: 'https://ingest-events-xxxxx.a.run.app',
  generateVAReport: 'https://generate-va-report-xxxxx.a.run.app',
  getConfluentMetrics: 'https://get-confluent-metrics-xxxxx.a.run.app',
  getSoldierSummary: 'https://get-soldier-summary-xxxxx.a.run.app',
  getHealthAlerts: 'https://get-health-alerts-xxxxx.a.run.app',
  resolveAlert: 'https://resolve-alert-xxxxx.a.run.app'
};
```

### 3. Initialize Firestore

```bash
python initialize_firestore.py
```

This creates:
- 5 soldiers in `soldiers` collection
- Health score and deployment data
- Initial service records

---

## Running the System

### Development Mode

#### 1. Start Frontend (Local)

```bash
cd valor-dashboard
npm start
# Opens http://localhost:3000
```

**Login Credentials:**
- Username: `admin`
- Password: `valor2024`

#### 2. Start Producer (Optional - for real-time data)

```bash
cd producer
python3 enhanced_producer.py
```

#### 3. Start Consumer (Optional - for real-time data)

```bash
cd consumer
python3 enhanced_consumer.py
```

### Production Mode

Visit deployed site: https://valorstream-demo-1.web.app

---

## 🚀 Deployment

### Deploy Frontend to Firebase

```bash
cd valor-dashboard

# Build production app
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

### Deploy Cloud Functions

```bash
cd backend/functions

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key"

# Deploy all functions
./infrastructure/scripts/deploy.sh

# Or deploy individually
gcloud functions deploy get-health-alerts \
  --gen2 \
  --runtime=python311 \
  --region=us-east1 \
  --source=. \
  --entry-point=get_health_alerts \
  --trigger-http \
  --allow-unauthenticated
```

### Create Cloud Storage Bucket (for VA Reports)

```bash
gsutil mb gs://valorstream-reports
gsutil iam ch allUsers:objectViewer gs://valorstream-reports
```

---

## API Documentation

### Health Alerts

**GET** `https://get-health-alerts-xxxxx.a.run.app`

Returns all health alerts from Firestore.

**Response:**
```json
{
  "status": "success",
  "alerts": [
    {
      "event_id": "evt_001",
      "soldier_id": "SGT_JOHNSON_001",
      "event_type": "BURN_PIT_EXPOSURE",
      "severity": "CRITICAL",
      "timestamp": "2025-12-31T10:30:00",
      "location": "Forward Operating Base Delta",
      "status": "pending"
    }
  ]
}
```

### Resolve Alert

**POST** `https://resolve-alert-xxxxx.a.run.app`

**Request:**
```json
{
  "alert_id": "evt_001",
  "resolution_notes": "Resolved by operator"
}
```

### Generate VA Report

**POST** `https://generate-va-report-xxxxx.a.run.app`

**Request:**
```json
{
  "soldier_id": "SGT_JOHNSON_001"
}
```

**Response:**
```json
{
  "status": "success",
  "soldier_id": "SGT_JOHNSON_001",
  "report_url": "https://storage.googleapis.com/.../report.pdf",
  "report_id": "rpt_abc123",
  "generated_at": "2025-12-31T10:45:00"
}
```

### Get Soldier Summary

**GET** `https://get-soldier-summary-xxxxx.a.run.app?soldier_id=SGT_JOHNSON_001`

Returns soldier details, health score, and recent alerts.

### Get Confluent Metrics

**GET** `https://get-confluent-metrics-xxxxx.a.run.app`

Returns Kafka cluster health, topics, and consumer groups.

### Ingest Events

**POST** `https://ingest-events-xxxxx.a.run.app`

Manually ingest battlefield events (alternative to Kafka pipeline).

---

## Usage

### Dashboard Overview

1. **Login** at https://valorstream-demo-1.web.app
2. **Dashboard** - View real-time stats and charts
3. **Health Alerts** - Monitor and resolve critical alerts
4. **Soldiers** - Browse soldier directory
5. **Soldier Profile** - Click any soldier to view details
6. **VA Reports** - Generate AI-powered VA disability reports
7. **Confluent Metrics** - Monitor Kafka pipeline
8. **Devices** - Track IoT sensors and monitors

### Generate VA Report

1. Go to **Soldiers** page
2. Click on a soldier (e.g., SGT_JOHNSON_001)
3. Click **"Generate VA Report"** button
4. Wait 30-90 seconds for AI analysis
5. Download PDF report

### Search Functionality

- **Navbar Search:** Type soldier name or ID, press Enter
- **Alerts Search:** Filter by soldier ID or event type
- **Soldiers Search:** Filter by name, rank, or unit

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---


**Quick Fixes:**
- **Empty Dashboard:** Run `python initialize_firestore.py`
- **CORS Errors:** Check Cloud Function CORS headers
- **Login Issues:** Use `admin` / `valor2024`
- **Build Errors:** Delete `node_modules/` and `npm install`

---

## License

MIT License

---


## Acknowledgments

- Google Cloud Platform for infrastructure
- Confluent for Kafka streaming
- Anthropic for Claude AI assistance
- React community for excellent documentation

---

**VALOR** - Protecting those who protect us 🇺🇸
