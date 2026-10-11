"""
backend/agent.py
Estimate engine for Kabadi Connect.

Public API:
    estimate(text, lang) -> dict matching EstimateResult in CONTRACT.md:
    {
      "items": [{"material", "quantity", "assumed", "rate_per_kg",
                 "min_price", "max_price"}, ...],
      "total_min": float,
      "total_max": float,
      "currency": "INR",
      "notes": str
    }

Environment variables:
    AGENT_MODE        "rules" (default) | "strands"
    BEDROCK_MODEL_ID  e.g. "anthropic.claude-3-5-sonnet-20240620-v1:0"
    AWS_REGION        e.g. "ap-south-1"
"""

import json
import logging
import os
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from backend.rates import KEYWORDS, MATERIAL_NAMES, RATES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ItemLine(BaseModel):
    material: str
    quantity: str = ""
    assumed: bool = False
    rate_per_kg: str = ""
    min_price: float = Field(default=0.0, ge=0)
    max_price: float = Field(default=0.0, ge=0)


class EstimateResult(BaseModel):
    items: list[ItemLine] = Field(default_factory=list)
    total_min: float = Field(default=0.0, ge=0)
    total_max: float = Field(default=0.0, ge=0)
    currency: str = "INR"
    notes: str = "rates are approximate"


# ---------------------------------------------------------------------------
# Rules-based parser
# ---------------------------------------------------------------------------

_NUMBER_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilo|किलो|किग्रा|gram|gm|piece|pieces|bag|bags|box|boxes)?",
    re.I | re.UNICODE,
)
_WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5,
    "पांच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
}

_DEFAULT_QTY_MIN = 2.0
_DEFAULT_QTY_MAX = 5.0


def _extract_qty(text: str) -> tuple[float, float]:
    nums = [float(m.group(1)) for m in _NUMBER_RE.finditer(text)]
    for word, val in _WORD_NUMS.items():
        if word in text.lower():
            nums.append(float(val))
    if not nums:
        return _DEFAULT_QTY_MIN, _DEFAULT_QTY_MAX
    total = sum(nums)
    return max(0.5, total * 0.8), total * 1.3


def _rules_estimate(text: str, lang: str) -> EstimateResult:
    text_lower = text.lower()
    found: list[str] = []
    for material, kw_list in KEYWORDS.items():
        if any(kw in text_lower for kw in kw_list):
            if material not in found:
                found.append(material)

    if not found:
        found = ["mixed_paper"]

    qty_min, qty_max = _extract_qty(text)
    per_min = round(qty_min / len(found), 2)
    per_max = round(qty_max / len(found), 2)

    lines: list[ItemLine] = []
    total_min = 0.0
    total_max = 0.0

    for mat in found:
        r_min, r_max = RATES[mat]
        mat_name = MATERIAL_NAMES[mat].get(lang, MATERIAL_NAMES[mat]["en"])
        assumed = qty_min == _DEFAULT_QTY_MIN and qty_max == _DEFAULT_QTY_MAX
        price_min = round(per_min * r_min, 2)
        price_max = round(per_max * r_max, 2)
        total_min += price_min
        total_max += price_max
        lines.append(ItemLine(
            material=mat_name,
            quantity=f"{per_min}–{per_max} kg",
            assumed=assumed,
            rate_per_kg=f"₹{r_min}–₹{r_max}/kg",
            min_price=price_min,
            max_price=price_max,
        ))

    if lang == "hi":
        notes = "सभी दरें अनुमानित हैं"
    else:
        notes = "rates are approximate"

    return EstimateResult(
        items=lines,
        total_min=round(total_min, 2),
        total_max=round(total_max, 2),
        currency="INR",
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Strands agent
# ---------------------------------------------------------------------------

def _strands_estimate(text: str, lang: str) -> EstimateResult:
    from strands import Agent, tool  # noqa: PLC0415
    from strands.models import BedrockModel  # noqa: PLC0415

    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
    region = os.environ.get("AWS_REGION", "ap-south-1")

    @tool
    def lookup_rate(material: str) -> str:
        """
        Look up the approximate INR per kg rate range for a kabadi (scrap) material.
        Valid keys: newspaper, cardboard, mixed_paper, pet, hard_plastic, iron,
        aluminium, copper, e_waste.
        Returns JSON: {material, rate_min_inr_per_kg, rate_max_inr_per_kg}
        """
        key = material.lower().replace(" ", "_").replace("-", "_")
        if key in RATES:
            r_min, r_max = RATES[key]
            return json.dumps({"material": key, "rate_min_inr_per_kg": r_min, "rate_max_inr_per_kg": r_max})
        for canonical, kw_list in KEYWORDS.items():
            if any(kw in key for kw in kw_list) or key in canonical:
                r_min, r_max = RATES[canonical]
                return json.dumps({"material": canonical, "rate_min_inr_per_kg": r_min, "rate_max_inr_per_kg": r_max})
        return json.dumps({"error": f"Unknown material: {material}"})

    system_prompt = (
        "You are a kabadi (scrap dealer) assistant for India.\n"
        "Given a household's scrap description (in Hindi, English, or Hinglish),\n"
        "identify all materials, look up their rates using the lookup_rate tool,\n"
        "estimate weights, and return ONLY valid JSON (no markdown):\n"
        "{\n"
        '  "items": [\n'
        "    {\n"
        '      "material": "<name in ' + lang + ' language>",\n'
        '      "quantity": "<e.g. 10 kg>",\n'
        '      "assumed": <true if weight was guessed>,\n'
        '      "rate_per_kg": "<e.g. ₹14–₹18/kg>",\n'
        '      "min_price": <float>,\n'
        '      "max_price": <float>\n'
        "    }\n"
        "  ],\n"
        '  "total_min": <float>,\n'
        '  "total_max": <float>,\n'
        '  "currency": "INR",\n'
        f'  "notes": "<short note in {lang}>"\n'
        "}"
    )

    model = BedrockModel(model_id=model_id, region_name=region)
    agent = Agent(model=model, tools=[lookup_rate], system_prompt=system_prompt)
    result = agent(f"Scrap items: {text}\nRespond in: {lang}")

    raw = str(result).strip()
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON in agent response: {raw[:200]}")
    return EstimateResult(**json.loads(json_match.group()))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def estimate(text: str, lang: str = "hi") -> dict[str, Any]:
    """
    Estimate scrap value. Returns dict matching CONTRACT.md EstimateResult.
    AGENT_MODE=strands uses Bedrock; falls back to rules on any error.
    """
    mode = os.environ.get("AGENT_MODE", "rules").lower()
    result: EstimateResult

    if mode == "strands":
        try:
            result = _strands_estimate(text, lang)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Strands failed (%s: %s); falling back to rules.", type(exc).__name__, exc)
            result = _rules_estimate(text, lang)
    else:
        result = _rules_estimate(text, lang)

    try:
        validated = EstimateResult(**result.model_dump())
    except ValidationError as exc:
        logger.error("EstimateResult validation error: %s", exc)
        validated = result

    return validated.model_dump()
