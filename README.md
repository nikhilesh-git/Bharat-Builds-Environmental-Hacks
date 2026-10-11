# Kabadi Connect — Backend

A FastAPI backend for Kabadi Connect, connecting Indian households with scrap (kabadi) collectors.

---

## Project layout

```
.
├── CONTRACT.md           ← API contract (field names & endpoints — do not rename)
├── requirements.txt
├── README.md
├── frontend/
│   ├── household.html    ← served at GET /household
│   └── kabadi.html       ← served at GET /kabadi
└── backend/
    ├── __init__.py
    ├── main.py           ← FastAPI app; exports handler = Mangum(app)
    ├── storage.py        ← Storage interface + SQLite impl + get_storage()
    ├── storage_dynamo.py ← DynamoDB impl (lazy-loaded when STORAGE=dynamodb)
    ├── agent.py          ← estimate(text, lang) — rules or Strands mode
    ├── rates.py          ← INR/kg rate ranges per material
    └── notify.py         ← notification stub
```

---

## Quick start (local)

### 1. Install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the dev server

```bash
# From the project root
uvicorn backend.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3. Test the endpoints

```bash
# Create a request
curl -X POST http://localhost:8000/api/v1/request \
  -H "Content-Type: application/json" \
  -d '{
    "household_name": "Ramesh Gupta",
    "phone": "9876543210",
    "address": "B-12 Lajpat Nagar, Delhi",
    "items_description": "old newspaper, plastic bottles, broken iron rod",
    "preferred_slot": "morning",
    "lang": "hi"
  }'

# List all requests
curl http://localhost:8000/api/v1/requests

# Get by id
curl http://localhost:8000/api/v1/requests/<uuid>

# Update status
curl -X PATCH http://localhost:8000/api/v1/requests/<uuid>/status \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

---

## Environment variables

| Variable         | Default                                       | Purpose                                      |
|------------------|-----------------------------------------------|----------------------------------------------|
| `STORAGE`        | `sqlite`                                      | `sqlite` or `dynamodb`                       |
| `SQLITE_PATH`    | `kabadi.db`                                   | Path to the SQLite database file             |
| `DYNAMO_TABLE`   | `KabadiRequests`                              | DynamoDB table name (when `STORAGE=dynamodb`)|
| `AGENT_MODE`     | `rules`                                       | `rules` or `strands`                         |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20240620-v1:0` | Bedrock model (when `AGENT_MODE=strands`)    |
| `AWS_REGION`     | `ap-south-1`                                  | AWS region for Bedrock and DynamoDB          |

---

## Agent modes

### `AGENT_MODE=rules` (default)
Keyword/regex parser — no AWS credentials needed. Works offline.

### `AGENT_MODE=strands`
Uses the [Strands Agents SDK](https://strandsagents.com) with Amazon Bedrock.
Requires:
- AWS credentials configured (IAM role, `~/.aws/credentials`, or env vars)
- Bedrock model access enabled in your AWS account

If the Strands agent raises any exception, it automatically falls back to rules mode and logs a warning.

---

## AWS Lambda deployment

`backend/main.py` exports `handler = Mangum(app)`.

**Lambda configuration:**
- Handler: `backend.main.handler`
- Runtime: Python 3.12
- Package: zip the project root and include `.venv/lib/…` or use a Lambda layer

**Suggested environment variables for Lambda:**
```
STORAGE=dynamodb
DYNAMO_TABLE=KabadiRequests
AGENT_MODE=strands
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=ap-south-1
```

---

## Sample data

On first startup, 6 sample pickup requests (with `is_sample=true`) are automatically seeded if the store is empty. Seeding is idempotent — it runs only when `count() == 0`.

---

## Error format

All error responses follow the contract:

```json
{
  "error": "snake_case_code",
  "message_en": "English description",
  "message_hi": "हिंदी विवरण"
}
```

---

## Material rates reference

See [`backend/rates.py`](backend/rates.py) for the current approximate INR/kg ranges.

| Material      | Min (₹/kg) | Max (₹/kg) |
|---------------|------------|------------|
| Newspaper     | 14         | 18         |
| Cardboard     | 6          | 10         |
| Mixed Paper   | 4          | 8          |
| PET Plastic   | 8          | 14         |
| Hard Plastic  | 5          | 10         |
| Iron / Steel  | 28         | 35         |
| Aluminium     | 90         | 110        |
| Copper        | 420        | 480        |
| E-Waste       | 15         | 40         |

> All rates are approximate and vary by city, season, and vendor.
