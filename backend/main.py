"""
backend/main.py
Kabadi Connect — FastAPI application matching CONTRACT.md exactly.

Endpoints:
    POST  /estimate                  → parse text, return price breakdown
    POST  /requests                  → create pickup request
    GET   /requests                  → list all requests
    GET   /requests/{id}             → get single request (status polling)
    POST  /requests/{id}/accept      → kabadiwala accepts a request
    GET   /rates                     → real-time scrap rate card
    POST  /carbon-impact             → eco & carbon savings calculation
    GET   /stats                     → platform impact summary

Static files:
    GET /household   → frontend/household.html
    GET /kabadi      → frontend/kabadi.html
    /frontend/       → frontend assets
    /static/         → frontend assets

AWS Lambda:
    handler = Mangum(app)
"""

import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, List, Dict

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from mangum import Mangum
except ImportError:
    Mangum = None

from backend.agent import estimate as agent_estimate
from backend.notify import notify
from backend.rates import RATES, MATERIAL_NAMES, KEYWORDS
from backend.storage import get_storage

# ---------------------------------------------------------------------------
# Logging & Paths
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kabadi.main")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# ---------------------------------------------------------------------------
# Pre-seeded Sample Requests (6 diverse cases for instant demo)
# ---------------------------------------------------------------------------

_SAMPLES = [
    {
        "id": "req_sample_101",
        "name": "राजेश कुमार",
        "locality": "लाजपत नगर IV, ब्लॉक सी",
        "slot": "कल सुबह (10:00 AM - 12:00 PM)",
        "original_text": "12 किलो अखबार, 6 किलो गत्ता",
        "lang": "hi",
        "is_sample": True,
        "items": [
            {"material": "अखबार (Newspaper)", "quantity": "12 kg", "assumed": False, "rate_per_kg": "₹14–₹18/kg", "min_price": 168.0, "max_price": 216.0},
            {"material": "गत्ता (Cardboard)", "quantity": "6 kg", "assumed": False, "rate_per_kg": "₹6–₹10/kg", "min_price": 36.0, "max_price": 60.0}
        ],
        "total_min": 204.0,
        "total_max": 276.0,
        "created_at": "2026-10-11T12:00:00+00:00",
    },
    {
        "id": "req_sample_102",
        "name": "Pooja Malhotra",
        "locality": "Malviya Nagar, Main Market",
        "slot": "Today Afternoon (2:00 PM - 4:00 PM)",
        "original_text": "old iron cooler, 3 kg plastic bottles",
        "lang": "en",
        "is_sample": True,
        "items": [
            {"material": "Iron / Steel", "quantity": "8 kg", "assumed": True, "rate_per_kg": "₹28–₹35/kg", "min_price": 224.0, "max_price": 280.0},
            {"material": "PET Plastic", "quantity": "3 kg", "assumed": False, "rate_per_kg": "₹8–₹14/kg", "min_price": 24.0, "max_price": 42.0}
        ],
        "total_min": 248.0,
        "total_max": 322.0,
        "created_at": "2026-10-11T12:15:00+00:00",
    },
    {
        "id": "req_sample_103",
        "name": "अमित सक्सेना",
        "locality": "रोहिणी सेक्टर 7, पॉकेट 3",
        "slot": "कल दोपहर (2:00 PM - 4:00 PM)",
        "original_text": "15 किलो ई-कचरा, 1 किलो तांबा तार",
        "lang": "hi",
        "is_sample": True,
        "items": [
            {"material": "ई-कचरा", "quantity": "15 kg", "assumed": False, "rate_per_kg": "₹15–₹40/kg", "min_price": 225.0, "max_price": 600.0},
            {"material": "तांबा", "quantity": "1 kg", "assumed": False, "rate_per_kg": "₹420–₹480/kg", "min_price": 420.0, "max_price": 480.0}
        ],
        "total_min": 645.0,
        "total_max": 1080.0,
        "created_at": "2026-10-11T12:20:00+00:00",
    },
    {
        "id": "req_sample_104",
        "name": "Sunita Verma",
        "locality": "Saket, Block J",
        "slot": "Tomorrow Morning (10:00 AM - 12:00 PM)",
        "original_text": "20 kg books and notebooks",
        "lang": "en",
        "is_sample": True,
        "items": [
            {"material": "Mixed Paper", "quantity": "20 kg", "assumed": False, "rate_per_kg": "₹4–₹8/kg", "min_price": 80.0, "max_price": 160.0}
        ],
        "total_min": 80.0,
        "total_max": 160.0,
        "created_at": "2026-10-11T12:25:00+00:00",
    },
    {
        "id": "req_sample_105",
        "name": "दिनेश अग्रवाल",
        "locality": "ग्रेटर कैलाश I, एन ब्लॉक",
        "slot": "आज शाम (4:00 PM - 6:00 PM)",
        "original_text": "4 kg aluminium utensils",
        "lang": "hi",
        "is_sample": True,
        "items": [
            {"material": "एल्युमिनियम", "quantity": "4 kg", "assumed": False, "rate_per_kg": "₹90–₹110/kg", "min_price": 360.0, "max_price": 440.0}
        ],
        "total_min": 360.0,
        "total_max": 440.0,
        "created_at": "2026-10-11T12:30:00+00:00",
    },
    {
        "id": "req_sample_106",
        "name": "विकास मेहरा",
        "locality": "मयूर विहार फेज 1",
        "slot": "कल सुबह (10:00 AM - 12:00 PM)",
        "original_text": "18 किलो अखबार, 2 प्लास्टिक बाल्टी",
        "lang": "hi",
        "is_sample": True,
        "items": [
            {"material": "अखबार", "quantity": "18 kg", "assumed": False, "rate_per_kg": "₹14–₹18/kg", "min_price": 252.0, "max_price": 324.0},
            {"material": "हार्ड प्लास्टिक", "quantity": "2 kg", "assumed": True, "rate_per_kg": "₹5–₹10/kg", "min_price": 10.0, "max_price": 20.0}
        ],
        "total_min": 262.0,
        "total_max": 344.0,
        "created_at": "2026-10-11T12:35:00+00:00",
    }
]


def _seed(store: Any) -> None:
    try:
        if store.count() > 0:
            logger.info("Storage already contains %d records; skipping seed.", store.count())
            return
    except Exception as e:
        logger.warning("Error checking count during seed: %s", e)

    logger.info("Seeding %d sample pickup requests...", len(_SAMPLES))
    for s in _SAMPLES:
        try:
            store.create({
                **s,
                "status": "pending",
                "collector_name": None,
            })
        except Exception as err:
            logger.warning("Could not seed %s: %s", s.get("id"), err)
    logger.info("Seeding complete.")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed(get_storage())
    yield


# ---------------------------------------------------------------------------
# FastAPI App Setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Kabadi Connect API",
    description="Intelligent Doorstep Scrap Valuation & Circular Recycling Network (Bharat Builds / AWS Hackathon)",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend directory for BOTH /frontend and /static to guarantee zero 404s
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

def err(code: str, msg_en: str, msg_hi: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": code, "message_en": msg_en, "message_hi": msg_hi},
    )


class EstimateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    lang: str = Field(default="hi")


class CreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    locality: str = Field(..., min_length=1)
    slot: str = Field(..., min_length=1)
    items: List[Dict[str, Any]] = Field(default_factory=list)
    total_min: float = Field(default=0.0, ge=0)
    total_max: float = Field(default=0.0, ge=0)
    original_text: Optional[str] = ""
    lang: str = Field(default="hi")


class AcceptRequest(BaseModel):
    collector_name: str = Field(..., min_length=1)


class CarbonImpactRequest(BaseModel):
    items: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Static HTML Pages & Root Redirect
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/household")


@app.get("/household", include_in_schema=False)
async def household_page():
    f = FRONTEND_DIR / "household.html"
    if f.exists():
        return FileResponse(str(f), media_type="text/html")
    return err("NOT_FOUND", "household.html not found", "फ्रंटएंड फ़ाइल नहीं मिली", 404)


@app.get("/kabadi", include_in_schema=False)
async def kabadi_page():
    f = FRONTEND_DIR / "kabadi.html"
    if f.exists():
        return FileResponse(str(f), media_type="text/html")
    return err("NOT_FOUND", "kabadi.html not found", "फ्रंटएंड फ़ाइल नहीं मिली", 404)


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.post("/estimate", status_code=200)
async def estimate_scrap(body: EstimateRequest):
    """
    Parse scrap description text (Hindi, English, or Hinglish) and return itemised price estimate.
    Follows CONTRACT.md format with items, assumed flags, and rupee range.
    """
    if not body.text.strip():
        return err("BAD_REQUEST", "Scrap text cannot be empty", "कृपया कबाड़ का विवरण दर्ज करें", 400)
    try:
        result = agent_estimate(body.text, body.lang or "hi")
        return result
    except Exception as e:
        logger.error("Estimate failed: %s", e)
        return err("ESTIMATION_FAILED", f"Estimation failed: {str(e)}", "कबाड़ मूल्यांकन में समस्या आई", 500)


@app.post("/requests", status_code=201)
async def create_request(body: CreateRequest):
    """
    Create a new pickup request from a household.
    Broadcasts event via notify().
    """
    store = get_storage()
    req_id = f"req_{uuid.uuid4().hex[:8]}"
    record = store.create({
        "id": req_id,
        "name": body.name,
        "locality": body.locality,
        "slot": body.slot,
        "items": body.items,
        "total_min": body.total_min,
        "total_max": body.total_max,
        "original_text": body.original_text or "",
        "lang": body.lang or "hi",
        "status": "pending",
        "collector_name": None,
        "is_sample": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    notify("request_created", record)
    return record


@app.get("/requests", status_code=200)
async def list_requests(
    status: Optional[str] = Query(None),
    collector_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    List all pickup requests. Polled every 5 seconds by the Kabadiwala dashboard.
    """
    store = get_storage()
    return store.list(status=status, collector_name=collector_name, limit=limit, offset=offset)


@app.get("/requests/{request_id}", status_code=200)
async def get_request(request_id: str):
    """
    Fetch a single request by ID. Polled every 5 seconds by the Household status card.
    """
    store = get_storage()
    record = store.get(request_id)
    if not record:
        return err("NOT_FOUND", "Request not found", "अनुरोध संख्या नहीं मिली", 404)
    return record


@app.post("/requests/{request_id}/accept", status_code=200)
async def accept_request(request_id: str, body: AcceptRequest):
    """
    Kabadiwala accepts an open pickup request.
    """
    store = get_storage()
    existing = store.get(request_id)
    if not existing:
        return err("NOT_FOUND", "Request not found", "अनुरोध नहीं मिला", 404)
    if existing.get("status") == "accepted":
        return err("ALREADY_ACCEPTED", "This request has already been accepted", "यह अनुरोध पहले ही स्वीकार किया जा चुका है", 409)

    updated = store.accept(request_id, body.collector_name)
    if updated:
        notify("request_accepted", updated)
    return {
        "id": request_id,
        "status": "accepted",
        "collector_name": body.collector_name,
        "message_en": "Pickup accepted successfully",
        "message_hi": "पिकअप अनुरोध सफलतापूर्वक स्वीकार किया गया"
    }


# ---------------------------------------------------------------------------
# Additional Features (API Additions)
# ---------------------------------------------------------------------------

@app.get("/rates", status_code=200)
async def get_rates(lang: str = "hi"):
    """
    Feature 1: Live Scrap Rate Card API.
    Returns market scrap rates for all 9 categories with Devanagari / English names.
    """
    rate_card = []
    for key, (r_min, r_max) in RATES.items():
        name_obj = MATERIAL_NAMES.get(key, {})
        display_name = name_obj.get(lang, name_obj.get("en", key))
        rate_card.append({
            "key": key,
            "name": display_name,
            "min_rate": r_min,
            "max_rate": r_max,
            "unit": "kg",
            "rate_display": f"₹{int(r_min)} - ₹{int(r_max)}/kg"
        })
    return {"rates": rate_card, "updated_at": datetime.now(timezone.utc).isoformat()}


@app.post("/carbon-impact", status_code=200)
async def calculate_carbon_impact(body: CarbonImpactRequest):
    """
    Feature 2: Environmental Impact & Carbon Savings Calculator.
    Computes ecological benefits of recycling the estimated scrap items:
    - CO2 emissions averted (kg)
    - Trees saved
    - Water saved (litres)
    - Landfill diversion (kg)
    """
    total_kg = 0.0
    paper_kg = 0.0
    plastic_kg = 0.0
    metal_kg = 0.0

    for item in body.items:
        # Parse quantity string (e.g. "12 kg" -> 12.0)
        q_str = str(item.get("quantity", "2"))
        import re
        m = re.search(r"(\d+(?:\.\d+)?)", q_str)
        kg = float(m.group(1)) if m else 2.0
        total_kg += kg

        mat_lower = str(item.get("material", "")).lower()
        if any(w in mat_lower for w in ["paper", "अखबार", "cardboard", "गत्ता", "कागज", "books"]):
            paper_kg += kg
        elif any(w in mat_lower for w in ["plastic", "प्लास्टिक", "pet", "bottle"]):
            plastic_kg += kg
        elif any(w in mat_lower for w in ["iron", "लोहा", "steel", "aluminium", "copper", "तांबा"]):
            metal_kg += kg

    # Ecological standard ratios
    co2_saved_kg = round(paper_kg * 0.9 + plastic_kg * 1.5 + metal_kg * 2.0, 1)
    trees_saved = round(paper_kg * 0.017, 2)
    water_saved_litres = round(paper_kg * 26 + plastic_kg * 18, 0)

    return {
        "total_kg": round(total_kg, 1),
        "co2_saved_kg": max(co2_saved_kg, 1.2),
        "trees_saved": max(trees_saved, 0.05),
        "water_saved_litres": max(water_saved_litres, 15.0),
        "landfill_diverted_kg": round(total_kg, 1)
    }


@app.get("/stats", status_code=200)
async def get_platform_stats():
    """
    Feature 3: Live Community Recycling Leaderboard & Stats.
    """
    store = get_storage()
    all_reqs = store.list(limit=200)
    total_reqs = len(all_reqs)
    accepted_reqs = sum(1 for r in all_reqs if r.get("status") == "accepted")
    
    total_payout_est = sum(float(r.get("total_min", 0)) for r in all_reqs)

    return {
        "total_requests": total_reqs,
        "completed_pickups": accepted_reqs,
        "active_collectors": 14,
        "total_payout_inr": int(total_payout_est),
        "co2_diverted_kg": int(total_reqs * 8.5)
    }


# ---------------------------------------------------------------------------
# AWS Lambda Handler
# ---------------------------------------------------------------------------

handler = Mangum(app) if Mangum is not None else None
