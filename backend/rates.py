"""
Kabadi Connect — Material Scrap Rate Card (Approximate INR / kg or piece)
Note: All scrap prices fluctuate dynamically with local mandi / scrap yard rates.
These rates are representative approximate estimates.
"""

# Approximate market scrap rates in INR
SCRAP_RATES = {
    "newspaper": {
        "canonical_name": "अखबार (Newspaper)",
        "min_rate": 12,
        "max_rate": 15,
        "unit": "kg",
        "keywords": ["newspaper", "अखबार", "akhbaar", "paper", "raddi", "रद्दी"]
    },
    "cardboard": {
        "canonical_name": "गत्ता (Cardboard)",
        "min_rate": 8,
        "max_rate": 10,
        "unit": "kg",
        "keywords": ["cardboard", "गत्ता", "gatta", "carton", "कार्टन", "box", "boxes"]
    },
    "mixed_paper": {
        "canonical_name": "किताबें / मिश्रित कागज (Books & Mixed Paper)",
        "min_rate": 8,
        "max_rate": 12,
        "unit": "kg",
        "keywords": ["book", "books", "किताब", "किताबें", "copies", "copy", "mixed paper", "कागज"]
    },
    "pet_bottles": {
        "canonical_name": "PET प्लास्टिक बोतलें (PET Bottles)",
        "min_rate": 15,
        "max_rate": 20,
        "unit": "kg",
        "keywords": ["pet", "plastic bottle", "bottles", "बोतल", "बोतलें", "water bottle"]
    },
    "hard_plastic": {
        "canonical_name": "कठोर प्लास्टिक (Hard Plastic)",
        "min_rate": 12,
        "max_rate": 18,
        "unit": "kg",
        "keywords": ["plastic", "प्लास्टिक", "bucket", "बाल्टी", "tub", "टब", "प्लास्टिक कुर्सी", "plastic chair"]
    },
    "iron": {
        "canonical_name": "लोहा (Iron / Steel)",
        "min_rate": 26,
        "max_rate": 30,
        "unit": "kg",
        "keywords": ["iron", "लोहा", "लोहे", "loha", "steel", "स्टील", "cooler", "कूलर", "grill", "जाली", "rod", "पाइप", "कुर्सी", "chair", "अलमारी", "लोहे की कुर्सी"]
    },
    "aluminium": {
        "canonical_name": "एल्युमिनियम (Aluminium)",
        "min_rate": 100,
        "max_rate": 125,
        "unit": "kg",
        "keywords": ["aluminium", "aluminum", "एल्युमिनियम", "utensil", "बर्तन"]
    },
    "copper": {
        "canonical_name": "तांबा (Copper)",
        "min_rate": 450,
        "max_rate": 520,
        "unit": "kg",
        "keywords": ["copper", "तांबा", "tamba", "wire", "तार", "cable"]
    },
    "e_waste": {
        "canonical_name": "ई-कचरा / इलेक्ट्रॉनिक्स (E-Waste)",
        "min_rate": 20,
        "max_rate": 45,
        "unit": "kg",
        "keywords": ["e-waste", "ewaste", "ई-कचरा", "fan", "पंखा", "motor", "मोटर", "wire", "tv", "टीवी", "electronics"]
    }
}
