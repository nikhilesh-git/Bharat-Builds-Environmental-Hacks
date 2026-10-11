# Kabadi Connect — API & Architecture Contract

This document is the **Single Source of Truth** for Kabadi Connect across all three teammates (A: Backend & Agent, B: Frontend & Demo, C: AWS & Infra).

---

## 1. System Overview & Deployment
- **Backend**: FastAPI (Python 3.12) with Mangum ASGI handler for AWS Lambda Function URL.
- **Frontend**: Plain HTML5 + Vanilla ES6 JavaScript + Tailwind CSS via CDN. Served directly by FastAPI at `/household` and `/kabadi` without build tools or CORS issues.
- **URLs**: All frontend API calls use **relative paths** (`/estimate`, `/requests`, etc.).
- **Agent Modes**:
  - `AGENT_MODE=strands`: AWS Strands Agents SDK using Amazon Bedrock with `lookup_rate(material)` tool.
  - `AGENT_MODE=rules`: Fallback regex/keyword matcher over the exact same rate card.

---

## 2. API Endpoints

### 2.1 Scrap Estimation
- **Endpoint**: `POST /estimate`
- **Description**: Parses user text (Hindi, English, or Hinglish) and estimates scrap item weights and price ranges.
- **Request Body**:
```json
{
  "text": "10 kg newspaper, 5 beer bottles, old iron chair",
  "lang": "hi"
}
```

- **Success Response (200 OK)**:
```json
{
  "items": [
    {
      "material": "अखबार (Newspaper)",
      "quantity": "10 kg",
      "assumed": false,
      "rate_per_kg": "₹12 - ₹15/kg",
      "min_price": 120,
      "max_price": 150
    },
    {
      "material": "लोहा (Iron)",
      "quantity": "5 kg",
      "assumed": true,
      "rate_per_kg": "₹26 - ₹30/kg",
      "min_price": 130,
      "max_price": 150
    }
  ],
  "total_min": 250,
  "total_max": 300,
  "currency": "INR",
  "notes": "rates are approximate"
}
```

---

### 2.2 Create Pickup Request
- **Endpoint**: `POST /requests`
- **Description**: Household submits an estimated scrap pickup request.
- **Request Body**:
```json
{
  "name": "Sunita Sharma",
  "locality": "Lajpat Nagar IV",
  "slot": "Tomorrow 10:00 AM - 12:00 PM",
  "items": [
    {
      "material": "अखबार (Newspaper)",
      "quantity": "10 kg",
      "assumed": false,
      "rate_per_kg": "₹12 - ₹15/kg",
      "min_price": 120,
      "max_price": 150
    }
  ],
  "total_min": 120,
  "total_max": 150,
  "original_text": "10 kg newspaper",
  "lang": "hi"
}
```

- **Success Response (201 Created / 200 OK)**:
```json
{
  "id": "req_8f1a23bc",
  "status": "pending",
  "name": "Sunita Sharma",
  "locality": "Lajpat Nagar IV",
  "slot": "Tomorrow 10:00 AM - 12:00 PM",
  "items": [ ... ],
  "total_min": 120,
  "total_max": 150,
  "collector_name": null,
  "is_sample": false,
  "created_at": "2026-10-11T17:30:00Z"
}
```

---

### 2.3 Get Specific Request (Status Polling)
- **Endpoint**: `GET /requests/{id}`
- **Description**: Household frontend polls this endpoint every 5 seconds until accepted.
- **Success Response (200 OK)**:
```json
{
  "id": "req_8f1a23bc",
  "status": "pending",
  "name": "Sunita Sharma",
  "locality": "Lajpat Nagar IV",
  "slot": "Tomorrow 10:00 AM - 12:00 PM",
  "items": [ ... ],
  "total_min": 120,
  "total_max": 150,
  "collector_name": null,
  "is_sample": false,
  "created_at": "2026-10-11T17:30:00Z"
}
```
*When accepted by a kabadiwala:*
```json
{
  "id": "req_8f1a23bc",
  "status": "accepted",
  "name": "Sunita Sharma",
  "locality": "Lajpat Nagar IV",
  "slot": "Tomorrow 10:00 AM - 12:00 PM",
  "items": [ ... ],
  "total_min": 120,
  "total_max": 150,
  "collector_name": "Ramesh Kumar",
  "is_sample": false,
  "created_at": "2026-10-11T17:30:00Z"
}
```

---

### 2.4 List All Requests (Kabadiwala Board)
- **Endpoint**: `GET /requests`
- **Description**: Returns all requests (open & accepted) for the Kabadiwala view. Polled every 5 seconds.
- **Success Response (200 OK)**:
```json
[
  {
    "id": "sample_1",
    "status": "pending",
    "name": "Rajesh Kumar",
    "locality": "Malviya Nagar, Block B",
    "slot": "Today 2:00 PM - 4:00 PM",
    "items": [
      {
        "material": "अखबार (Newspaper)",
        "quantity": "15 kg",
        "assumed": false,
        "rate_per_kg": "₹12 - ₹15/kg",
        "min_price": 180,
        "max_price": 225
      }
    ],
    "total_min": 180,
    "total_max": 225,
    "collector_name": null,
    "is_sample": true,
    "created_at": "2026-10-11T16:00:00Z"
  }
]
```

---

### 2.5 Accept Pickup Request
- **Endpoint**: `POST /requests/{id}/accept`
- **Description**: Kabadiwala accepts an open pickup request.
- **Request Body**:
```json
{
  "collector_name": "Ramesh Kumar"
}
```

- **Success Response (200 OK)**:
```json
{
  "id": "req_8f1a23bc",
  "status": "accepted",
  "collector_name": "Ramesh Kumar",
  "message_en": "Request accepted successfully",
  "message_hi": "अनुरोध सफलतापूर्वक स्वीकार किया गया"
}
```

---

### 2.6 Standard Error Format
All 4xx and 5xx errors return:
```json
{
  "error": "BAD_REQUEST",
  "message_en": "Text cannot be empty",
  "message_hi": "कबाड़ का विवरण खाली नहीं हो सकता"
}
```

---

## 3. UI/UX Rules & Requirements
1. **Hindi First**: The interface defaults to Hindi (`hi`) with a dynamic toggle button to switch to English (`en`).
2. **Mobile First & High Contrast**: Large touch buttons (min 48px height), clear borders, high legibility.
3. **No Build Step**: Tailwind CSS loaded via CDN, vanilla JavaScript, vanilla CSS helpers.
4. **Resilience**: The frontend polls every 5 seconds with graceful error recovery and loading skeleton states.
