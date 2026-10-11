"""
Kabadi Connect — Agent Estimator
Supports:
1. AGENT_MODE=strands: AWS Strands Agents SDK with BedrockModel and lookup_rate tool
2. AGENT_MODE=rules: Deterministic regex/keyword parser over the exact same scrap rate card
Automatic fallback to rules mode on any Bedrock/Strands exception.
"""

import os
import re
import logging
from typing import List, Dict, Any
from backend.rates import SCRAP_RATES

logger = logging.getLogger("kabadi.agent")


def lookup_rate(material: str) -> Dict[str, Any]:
    """Lookup rate for a scrap material in approximate INR."""
    material_clean = material.lower().strip()
    for key, data in SCRAP_RATES.items():
        if key in material_clean:
            return data
        for kw in data["keywords"]:
            if kw.lower() in material_clean:
                return data
    # Fallback generic mixed scrap
    return {
        "canonical_name": material.title(),
        "min_rate": 10,
        "max_rate": 15,
        "unit": "kg"
    }


def estimate_rules(text: str, lang: str = "hi") -> Dict[str, Any]:
    """Deterministic regex & keyword parser for scrap estimation."""
    text_lower = text.lower()
    items = []
    total_min = 0
    total_max = 0

    # Pattern for matching quantity + material
    # e.g., "10 kg newspaper", "5 किलो अखबार", "8 bottles", "एक पुरानी लोहे की कुर्सी"
    found_materials = set()

    for key, data in SCRAP_RATES.items():
        for kw in data["keywords"]:
            kw_esc = re.escape(kw.lower())
            # Match quantity preceding or succeeding keyword
            pattern = rf'(\d+[\.\d]*)\s*(?:kg|kilo|किलो|किग्रा|लीटर|l|बोतल|bottles|pcs|piece)?\s*{kw_esc}|{kw_esc}\s*(\d+[\.\d]*)?\s*(?:kg|kilo|किलो|किग्रा)?'
            match = re.search(pattern, text_lower)
            if match and key not in found_materials:
                found_materials.add(key)
                qty_val = match.group(1) or match.group(2)
                assumed = False

                if qty_val:
                    qty_num = float(qty_val)
                    qty_str = f"{int(qty_num) if qty_num.is_integer() else qty_num} kg"
                else:
                    # Quantity not explicitly mentioned, assume standard default weight
                    assumed = True
                    if key in ["iron", "aluminium"]:
                        qty_num = 4.0
                    elif key in ["pet_bottles", "hard_plastic"]:
                        qty_num = 2.0
                    elif key in ["copper"]:
                        qty_num = 1.0
                    elif key in ["cardboard", "newspaper"]:
                        qty_num = 5.0
                    elif key in ["e_waste"]:
                        qty_num = 8.0
                    else:
                        qty_num = 3.0
                    qty_str = f"{int(qty_num)} kg"

                min_price = int(qty_num * data["min_rate"])
                max_price = int(qty_num * data["max_rate"])
                total_min += min_price
                total_max += max_price

                rate_str = f"₹{data['min_rate']} - ₹{data['max_rate']}/kg"

                items.append({
                    "material": data["canonical_name"],
                    "quantity": qty_str,
                    "assumed": assumed,
                    "rate_per_kg": rate_str,
                    "min_price": min_price,
                    "max_price": max_price
                })
                break

    # If no recognized keywords matched, provide a safe fallback estimate
    if not items:
        default_rate = SCRAP_RATES["cardboard"]
        items.append({
            "material": "मिश्रित कबाड़ (General Scrap)",
            "quantity": "5 kg",
            "assumed": True,
            "rate_per_kg": "₹10 - ₹15/kg",
            "min_price": 50,
            "max_price": 75
        })
        total_min = 50
        total_max = 75

    return {
        "items": items,
        "total_min": total_min,
        "total_max": total_max,
        "currency": "INR",
        "notes": "rates are approximate / दरें अनुमानित हैं"
    }


def estimate_strands(text: str, lang: str = "hi") -> Dict[str, Any]:
    """Strands SDK integration with Amazon Bedrock."""
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if not model_id:
        raise ValueError("BEDROCK_MODEL_ID not configured")

    # Dynamically import strands when available
    from strands_agents import Agent, BedrockModel, tool
    from pydantic import BaseModel, Field

    class ScrapItem(BaseModel):
        material: str
        quantity: str
        assumed: bool
        rate_per_kg: str
        min_price: int
        max_price: int

    class ScrapEstimateResponse(BaseModel):
        items: List[ScrapItem]
        total_min: int
        total_max: int
        currency: str = "INR"

    model = BedrockModel(model_id=model_id, region=aws_region)
    agent = Agent(
        model=model,
        tools=[lookup_rate],
        system_prompt="You are an expert Indian Kabadiwala scrap valuation assistant. Return structured JSON with materials, quantities, assumed flags, and price ranges."
    )
    result = agent.run(f"User scrap description: {text}. Language: {lang}")
    return result


def estimate(text: str, lang: str = "hi") -> Dict[str, Any]:
    """Main estimation dispatch with safety net."""
    mode = os.environ.get("AGENT_MODE", "rules").lower()
    if mode == "strands":
        try:
            return estimate_strands(text, lang)
        except Exception as e:
            logger.warning(f"Strands agent failed or not configured, falling back to rules: {e}")
            return estimate_rules(text, lang)
    return estimate_rules(text, lang)
