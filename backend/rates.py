"""
backend/rates.py
Approximate scrap material rates in INR per kg for Indian kabadi market.
All values are approximate and may vary by city, season, and vendor.
"""

# Each entry: (min_inr_per_kg, max_inr_per_kg)
RATES: dict[str, tuple[float, float]] = {
    "newspaper":    (14.0, 18.0),   # approx INR 14-18 / kg
    "cardboard":    (6.0,  10.0),   # approx INR 6-10 / kg
    "mixed_paper":  (4.0,  8.0),    # approx INR 4-8 / kg
    "pet":          (8.0,  14.0),   # PET bottles; approx INR 8-14 / kg
    "hard_plastic": (5.0,  10.0),   # hard/rigid plastic; approx INR 5-10 / kg
    "iron":         (28.0, 35.0),   # iron / mild steel; approx INR 28-35 / kg
    "aluminium":    (90.0, 110.0),  # aluminium; approx INR 90-110 / kg
    "copper":       (420.0, 480.0), # copper; approx INR 420-480 / kg
    "e_waste":      (15.0, 40.0),   # mixed e-waste; approx INR 15-40 / kg
}

# Human-readable display names
MATERIAL_NAMES: dict[str, dict[str, str]] = {
    "newspaper":    {"en": "Newspaper",     "hi": "अखबार"},
    "cardboard":    {"en": "Cardboard",     "hi": "गत्ता"},
    "mixed_paper":  {"en": "Mixed Paper",   "hi": "मिश्रित कागज"},
    "pet":          {"en": "PET Plastic",   "hi": "पीईटी प्लास्टिक"},
    "hard_plastic": {"en": "Hard Plastic",  "hi": "हार्ड प्लास्टिक"},
    "iron":         {"en": "Iron / Steel",  "hi": "लोहा / स्टील"},
    "aluminium":    {"en": "Aluminium",     "hi": "एल्युमिनियम"},
    "copper":       {"en": "Copper",        "hi": "तांबा"},
    "e_waste":      {"en": "E-Waste",       "hi": "ई-कचरा"},
}

# Keywords / aliases that map to canonical material keys
KEYWORDS: dict[str, list[str]] = {
    "newspaper":    ["newspaper", "news paper", "akhbar", "अखबार", "paper"],
    "cardboard":    ["cardboard", "card board", "gatta", "गत्ता", "box", "boxes"],
    "mixed_paper":  ["mixed paper", "paper", "copy", "notebook", "books"],
    "pet":          ["pet", "plastic bottle", "bottle", "bottles", "water bottle"],
    "hard_plastic": ["plastic", "hard plastic", "bucket", "tub", "chair", "container"],
    "iron":         ["iron", "steel", "rod", "loha", "लोहा", "scrap metal", "metal"],
    "aluminium":    ["aluminium", "aluminum", "can", "cans", "foil"],
    "copper":       ["copper", "wire", "tambe", "तांबा"],
    "e_waste":      ["ewaste", "e-waste", "e waste", "electronic", "laptop",
                     "computer", "mobile", "phone", "tv", "television",
                     "monitor", "printer", "keyboard"],
}
