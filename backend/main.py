"""
Kabadi Connect — Main FastAPI Application
Serves API endpoints and static frontend for /household and /kabadi.
Exports handler = Mangum(app) for AWS Lambda Function URL.
"""

import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.storage import get_storage
from backend.agent import estimate
from backend.notify import notify

app = FastAPI(title="Kabadi Connect API", version="1.0.0")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount frontend directory for static assets (style.css, app.js)
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

# Initialize storage instance
storage = get_storage()


# Request / Response Schemas
class EstimateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    lang: Optional[str] = "hi"


class CreatePickupRequest(BaseModel):
    name: str = Field(..., min_length=1)
    locality: str = Field(..., min_length=1)
    slot: str = Field(..., min_length=1)
    items: List[Dict[str, Any]]
    total_min: int
    total_max: int
    original_text: Optional[str] = ""
    lang: Optional[str] = "hi"


class AcceptPickupRequest(BaseModel):
    collector_name: str = Field(..., min_length=1)


# Static HTML Routes
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/household")


@app.get("/household", include_in_schema=False)
async def serve_household():
    html_file = FRONTEND_DIR / "household.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="household.html not found")
    return FileResponse(str(html_file), media_type="text/html")


@app.get("/kabadi", include_in_schema=False)
async def serve_kabadi():
    html_file = FRONTEND_DIR / "kabadi.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="kabadi.html not found")
    return FileResponse(str(html_file), media_type="text/html")


# API Endpoints
@app.post("/estimate")
async def api_estimate(payload: EstimateRequest):
    try:
        result = estimate(payload.text, payload.lang or "hi")
        return result
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ESTIMATION_FAILED",
                "message_en": f"Failed to estimate scrap: {str(e)}",
                "message_hi": "कबाड़ का अनुमान लगाने में समस्या आई। कृपया पुनः प्रयास करें।"
            }
        )


@app.post("/requests", status_code=status.HTTP_201_CREATED)
async def api_create_request(payload: CreatePickupRequest):
    req_id = f"req_{uuid.uuid4().hex[:8]}"
    request_data = {
        "id": req_id,
        "status": "pending",
        "name": payload.name,
        "locality": payload.locality,
        "slot": payload.slot,
        "items": payload.items,
        "total_min": payload.total_min,
        "total_max": payload.total_max,
        "collector_name": None,
        "is_sample": False,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    saved = storage.save(request_data)
    notify("request_created", saved)
    return saved


@app.get("/requests/{request_id}")
async def api_get_request(request_id: str):
    req = storage.get(request_id)
    if not req:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "NOT_FOUND",
                "message_en": "Request not found",
                "message_hi": "अनुरोध नहीं मिला"
            }
        )
    return req


@app.get("/requests")
async def api_list_requests():
    return storage.list_all()


@app.post("/requests/{request_id}/accept")
async def api_accept_request(request_id: str, payload: AcceptPickupRequest):
    req = storage.get(request_id)
    if not req:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "NOT_FOUND",
                "message_en": "Request not found",
                "message_hi": "अनुरोध नहीं मिला"
            }
        )

    updated = storage.update_status(request_id, "accepted", payload.collector_name)
    notify("request_accepted", updated)
    return {
        "id": request_id,
        "status": "accepted",
        "collector_name": payload.collector_name,
        "message_en": "Pickup accepted successfully",
        "message_hi": "पिकअप अनुरोध सफलतापूर्वक स्वीकार किया गया"
    }


# Mangum handler for AWS Lambda Function URL
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    handler = None
