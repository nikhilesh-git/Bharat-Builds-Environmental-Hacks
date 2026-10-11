"""
backend/main.py
Kabadi Connect — FastAPI application matching CONTRACT.md exactly.

Endpoints:
    POST  /estimate                  → parse text, return price breakdown
    POST  /requests                  → create pickup request
    GET   /requests                  → list all requests
    GET   /requests/{id}             → get single request (status polling)
    POST  /requests/{id}/accept      → kabadiwala accepts a request

Static files:
    GET /household   → frontend/household.html
    GET /kabadi      → frontend/kabadi.html
    /static/         → frontend/app.js, frontend/style.css, etc.

AWS Lambda:
    handler = Mangum(app)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from pydantic import BaseModel, Field

from backend.agent import estimate as agent_estimate
from backend.notify import notify
from backend.storage import get_storage

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------

def err(code: str, en: str, hi: str, status: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": code, "message_en": en, "message_hi": hi},
    )

# ---------------------------------------------------------------------------
# Seed data — 6 samples matching real contract schema
# ---------------------------------------------------------------------------

_SAMPLES = [
    {
        "name": "Rajesh Kumar",
        "locality": "Malviya Nagar, Block B",
        "slot": "Today 2:00 PM - 4:00 PM",
        "original_text": "15 kg newspaper, 5 kg cardboard",
        "lang": "hi",
        "is_sample": True,
        "created_at": "2026-10-11T10:00:00+00:00",
    },
    {
        "name": "Sunita Sharma",
        "locality": "Lajpat Nagar IV",
        "slot": "Today 4:00 PM - 6:00 PM",
        "original_text": "पुराना लोहे का गेट, टूटी कुर्सी, 10 किलो लोहे के बर्तन",
        "lang": "hi",
        "is_sample": True,
        "created_at": "2026-10-11T10:30:00+00:00",
    },
    {
        "name": "Anita Patel",
        "locality": "Dwarka Sector 12",
        "slot": "Tomorrow Morning (10:00 AM - 12:00 PM)",
        "original_text": "broken laptop, 2 old mobile phones, some copper wire",
        "lang": "en",
        "is_sample": True,
        "created_at": "2026-10-11T11:00:00+00:00",
    },
    {
        "name": "Mohan Lal",
        "locality": "Rohini Sector 7",
        "slot": "Tomorrow Afternoon (2:00 PM - 4:00 PM)",
        "original_text": "30 plastic bottles, ek tuta bucket, ek aluminium ka patila",
        "lang": "hi",
        "is_sample": True,
        "created_at": "2026-10-11T11:30:00+00:00",
    },
    {
        "name": "Priya Mehta",
        "locality": "Saket, South Delhi",
        "slot": "Today 2:00 PM - 4:00 PM",
        "original_text": "old TV, keyboard, printer — office clearance e-waste",
        "lang": "en",
        "is_sample": True,
        "created_at": "2026-10-11T12:00:00+00:00",
    },
    {
        "name": "Geeta Devi",
        "locality": "Chandni Chowk",
        "slot": "Today 4:00 PM - 6:00 PM",
        "original_text": "पाँच किलो अखबार, एक थैला मिश्रित कागज़, पुरानी किताबें",
        "lang": "hi",
        "is_sample": True,
        "created_at": "2026-10-11T12:30:00+00:00",
    },
]


def _seed(storage: Any) -> None:
    if storage.count() > 0:
        logger.info("Store already has data; skipping seed.")
        return
    logger.info("Seeding %d sample requests…", len(_SAMPLES))
    for s in _SAMPLES:
        est = agent_estimate(s["original_text"], s.get("lang", "hi"))
        storage.create({
            **s,
            "items":     est["items"],
            "total_min": est["total_min"],
            "total_max": est["total_max"],
            "status":    "pending",
        })
    logger.info("Seeding complete.")

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN001
    _seed(get_storage())
    yield

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Kabadi Connect",
    description="Connecting Indian households with scrap (kabadi) collectors.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve app.js, style.css, and any other frontend assets at /static/
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class EstimateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    lang: str = Field(default="hi", pattern=r"^(en|hi)$")


class CreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    locality: str = Field(..., min_length=1)
    slot: str = Field(..., min_length=1)
    items: list[dict[str, Any]] = Field(default_factory=list)
    total_min: float = Field(default=0.0, ge=0)
    total_max: float = Field(default=0.0, ge=0)
    original_text: Optional[str] = None
    lang: str = Field(default="hi", pattern=r"^(en|hi)$")


class AcceptRequest(BaseModel):
    collector_name: str = Field(..., min_length=1)

# ---------------------------------------------------------------------------
# Static HTML pages
# ---------------------------------------------------------------------------

@app.get("/household", include_in_schema=False)
async def household_page():
    f = FRONTEND_DIR / "household.html"
    if f.exists():
        return FileResponse(str(f), media_type="text/html")
    return JSONResponse({"error": "NOT_FOUND", "message_en": "Frontend not deployed",
                         "message_hi": "फ्रंटएंड उपलब्ध नहीं"}, status_code=404)


@app.get("/kabadi", include_in_schema=False)
async def kabadi_page():
    f = FRONTEND_DIR / "kabadi.html"
    if f.exists():
        return FileResponse(str(f), media_type="text/html")
    return JSONResponse({"error": "NOT_FOUND", "message_en": "Frontend not deployed",
                         "message_hi": "फ्रंटएंड उपलब्ध नहीं"}, status_code=404)

# ---------------------------------------------------------------------------
# API — POST /estimate
# ---------------------------------------------------------------------------

@app.post("/estimate", status_code=200)
async def estimate_scrap(body: EstimateRequest) -> dict[str, Any]:
    """Parse scrap description text and return itemised price estimate."""
    if not body.text.strip():
        return err("BAD_REQUEST", "Text cannot be empty",
                   "टेक्स्ट खाली नहीं हो सकता, कृपया लिखें")
    result = agent_estimate(body.text, body.lang)
    return result

# ---------------------------------------------------------------------------
# API — POST /requests
# ---------------------------------------------------------------------------

@app.post("/requests", status_code=201)
async def create_request(body: CreateRequest) -> dict[str, Any]:
    """Create a pickup request from household."""
    storage = get_storage()
    record = storage.create({
        "name":          body.name,
        "locality":      body.locality,
        "slot":          body.slot,
        "items":         body.items,
        "total_min":     body.total_min,
        "total_max":     body.total_max,
        "original_text": body.original_text or "",
        "lang":          body.lang,
        "status":        "pending",
        "is_sample":     False,
    })
    notify("request_created", record)
    return record

# ---------------------------------------------------------------------------
# API — GET /requests
# ---------------------------------------------------------------------------

@app.get("/requests", status_code=200)
async def list_requests(
    status: Optional[str] = None,
    collector_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List all pickup requests. Polled every 5s by kabadi.html."""
    storage = get_storage()
    return storage.list(
        status=status,
        collector_name=collector_name,
        limit=limit,
        offset=offset,
    )

# ---------------------------------------------------------------------------
# API — GET /requests/{id}
# ---------------------------------------------------------------------------

@app.get("/requests/{request_id}", status_code=200)
async def get_request(request_id: str) -> Any:
    """Get a single request by id. Polled every 5s by household.html."""
    storage = get_storage()
    record = storage.get(request_id)
    if record is None:
        return err("NOT_FOUND", "Request not found", "अनुरोध नहीं मिला", 404)
    return record

# ---------------------------------------------------------------------------
# API — POST /requests/{id}/accept
# ---------------------------------------------------------------------------

@app.post("/requests/{request_id}/accept", status_code=200)
async def accept_request(request_id: str, body: AcceptRequest) -> Any:
    """Kabadiwala accepts an open pickup request."""
    storage = get_storage()
    existing = storage.get(request_id)
    if existing is None:
        return err("NOT_FOUND", "Request not found", "अनुरोध नहीं मिला", 404)
    if existing["status"] != "pending":
        return err(
            "ALREADY_ACCEPTED",
            "This request has already been accepted",
            "यह अनुरोध पहले ही स्वीकार किया जा चुका है",
            409,
        )
    updated = storage.accept(request_id, body.collector_name)
    if updated:
        notify("request_accepted", updated)
    return {
        "id":             request_id,
        "status":         "accepted",
        "collector_name": body.collector_name,
        "message_en":     "Request accepted successfully",
        "message_hi":     "अनुरोध सफलतापूर्वक स्वीकार किया गया",
    }

# ---------------------------------------------------------------------------
# AWS Lambda handler
# ---------------------------------------------------------------------------

handler = Mangum(app)
