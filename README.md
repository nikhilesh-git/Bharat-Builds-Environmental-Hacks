# ♻️ कबाड़ी कनेक्ट (Kabadi Connect)

> **AI-Powered Doorstep Scrap Valuation & Circular Recycling Network**  
> *Track: Waste and Energy Track — Bharat Builds / AWS Hackathon*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_Python_3.12-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![AWS](https://img.shields.io/badge/Cloud-AWS_Lambda_%2B_Bedrock-FF9900.svg?logo=amazon-aws)](https://aws.amazon.com)
[![Tailwind](https://img.shields.io/badge/Frontend-Tailwind_CSS_CDN-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com)
[![Language](https://img.shields.io/badge/Language-Hindi_%2B_English-blue.svg)](#features)

---

## 📌 Problem & Impact

In India, over **62 million tonnes of municipal waste** is generated annually, with millions of tonnes of valuable recyclable materials (paper, cardboard, plastics, metals, e-waste) ending up in landfills. 

While the informal recycling sector—led by local **Kabadiwalas**—recovers a massive portion of recyclable waste, the system suffers from:
1. **Zero Price Transparency**: Households have no reliable way to know what their scrap is worth.
2. **Friction in Coordination**: Households can't reliably schedule pickups, while collectors waste fuel and time wandering neighborhoods looking for scrap.
3. **Language Barriers**: Digital platforms often ignore vernacular Indian languages.

**Kabadi Connect** solves this by combining **Amazon Bedrock generative AI** with a **real-time circular pickup loop**:
- Households type or speak what scrap they have in Hindi or English.
- The AI agent parses natural language, looks up fair market rates, and flags assumed quantities.
- A doorstep pickup is scheduled, broadcasting the request to local collectors in real-time.

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph Frontend["Frontend (Zero Build, Vanilla JS + Tailwind)"]
        H[Household View /household] -->|POST /estimate| API[FastAPI Backend]
        H -->|POST /requests| API
        H -.->|Poll GET /requests/:id (every 5s)| API
        K[Collector View /kabadi] -.->|Poll GET /requests (every 5s)| API
        K -->|POST /requests/:id/accept| API
    end

    subgraph Backend["FastAPI on AWS Lambda (Mangum)"]
        API --> Agent{Agent Controller}
        Agent -->|AGENT_MODE=strands| Bedrock[Amazon Bedrock + Strands SDK]
        Agent -->|AGENT_MODE=rules / Fallback| Rules[Regex Rate Estimator]
        API --> Storage[Storage Layer]
        API --> Notify[Notify Layer]
    end

    subgraph AWS["AWS Cloud Infrastructure"]
        Storage -->|Production| DDB[(Amazon DynamoDB)]
        Storage -->|Local Dev| SQL[(SQLite kabadi.db)]
        Notify -->|Production| SNS[Amazon SNS Topic]
        Notify -->|Local Dev| Log[Local Logger]
    end
```

---

## ☁️ AWS Services Used

| AWS Service | Role in Kabadi Connect |
|---|---|
| **AWS Bedrock & Strands Agents SDK** | Powers the intelligent scrap valuation agent using open-source Strands SDK, parsing unstructured Hindi/English text and using the `@tool lookup_rate` function. |
| **AWS Lambda & Function URL** | Serverless execution of the FastAPI app via `Mangum`, eliminating server management, stage prefixes, and CORS complexity. |
| **Amazon DynamoDB** | Fast on-demand NoSQL storage for scrap pickup requests, customer details, and live collector status. |
| **Amazon SNS** | Notification delivery broadcasting new requests and status updates to registered collectors and households. |

---

## ✨ Features

- **🌐 Hindi-First with Instant Toggle**: Built natively with Devanagari typography (`Noto Sans Devanagari`) and an instant header toggle to English (`app.js` translation dictionary).
- **🎙️ Speech-to-Text Input**: Integrated `webkitSpeechRecognition` with `hi-IN` language support and live listening animations.
- **⚖️ Smart "Assumed (अनुमानित)" Detection**: If a household writes *"old iron cooler"* or *"broken chair"* without specifying weight, the agent flags the item as **Assumed** and estimates reasonable scrap weight.
- **⏱️ 5-Second Real-Time Polling**:
  - Household status card polls `GET /requests/{id}` and updates automatically when accepted: *"🎉 रमेश कुमार कल सुबह (10:00 AM - 12:00 PM) पर आ रहे हैं"*.
  - Collector portal polls `GET /requests` to live-sync available pickups in the locality.
- **📱 Mobile-First & Accessible**: Big touch targets (48px+ minimum height), high-contrast elements, and zero build step.

---

## 📂 Project Structure

```
├── CONTRACT.md              # Single source of truth API contract across all teammates
├── DEMO_SCRIPT.md           # 3-minute video recording script & 10-input test suite
├── .env.example             # Environment configuration template
├── .gitignore               # Excludes secrets, credentials, and SQLite databases
├── backend/
│   ├── main.py              # FastAPI app, static HTML routes, and Mangum handler
│   ├── agent.py             # Strands Bedrock agent with rules-mode fallback
│   ├── rates.py             # Approximate scrap rates card (INR/kg)
│   ├── storage.py           # SQLite local storage + 6 pre-seeded sample requests
│   ├── storage_dynamo.py    # DynamoDB storage implementation
│   ├── notify.py            # SNS & logger notification service
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── household.html       # Household scrap estimation & pickup booking screen
    ├── kabadi.html          # Collector partner dashboard & acceptance board
    ├── app.js               # Translation engine, speech recognition, and API logic
    └── style.css            # Typography, radar pulse, and touch target styling
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/gnshx/Bharat-Builds-Environmental-Hacks.git
cd Bharat-Builds-Environmental-Hacks
```

### 2. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Environment configuration
```bash
cp .env.example .env
```
*(By default, `STORAGE=sqlite`, `NOTIFY=log`, and `AGENT_MODE=rules` allow full local execution without AWS credentials).*

### 4. Run the application
```bash
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8080 --ws none
```

- **Household Screen**: [http://localhost:8080/household](http://localhost:8080/household)
- **Collector Portal**: [http://localhost:8080/kabadi](http://localhost:8080/kabadi)
- **Interactive Swagger Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## 🎬 3-Minute Demo Video Guide

Check [`DEMO_SCRIPT.md`](file:///home/ganesh/Desktop/aws/DEMO_SCRIPT.md) for the timed script and the 10-input test matrix covering Hindi, English, code-switched Hinglish, and edge cases.
