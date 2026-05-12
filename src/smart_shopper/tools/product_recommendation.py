"""Demo product recommendation tool for the SmartShopper agent."""

from __future__ import annotations

import re
from typing import Any


PRODUCT_CATALOG: list[dict[str, Any]] = [
    {
        "name": "SonicMeet H350",
        "category": "headphone",
        "price": 449_000,
        "tags": ["meeting", "wireless", "noise cancelling", "work"],
        "description": "Headphone wireless dengan mikrofon jernih untuk meeting.",
    },
    {
        "name": "BassLite Earbuds 2",
        "category": "earbuds",
        "price": 299_000,
        "tags": ["music", "compact", "commute", "wireless"],
        "description": "Earbuds ringan untuk musik harian dan perjalanan.",
    },
    {
        "name": "ChargeMax 20K",
        "category": "powerbank",
        "price": 329_000,
        "tags": ["travel", "fast charging", "usb-c", "phone"],
        "description": "Powerbank 20.000 mAh dengan fast charging USB-C.",
    },
    {
        "name": "PocketCharge 10K Slim",
        "category": "powerbank",
        "price": 189_000,
        "tags": ["travel", "slim", "budget", "phone"],
        "description": "Powerbank tipis untuk kebutuhan darurat harian.",
    },
    {
        "name": "KeyPro K87",
        "category": "keyboard",
        "price": 579_000,
        "tags": ["work", "gaming", "mechanical", "typing"],
        "description": "Keyboard mekanikal TKL untuk mengetik dan gaming ringan.",
    },
    {
        "name": "ViewClear Webcam FHD",
        "category": "webcam",
        "price": 399_000,
        "tags": ["meeting", "work", "video", "streaming"],
        "description": "Webcam Full HD dengan autofocus untuk panggilan video.",
    },
]


CATEGORY_KEYWORDS = {
    "headphone": ["headphone", "headset", "meeting", "rapat"],
    "earbuds": ["earbuds", "tws", "musik", "commute"],
    "powerbank": ["powerbank", "charger", "baterai", "cas"],
    "keyboard": ["keyboard", "mekanikal", "typing", "mengetik"],
    "webcam": ["webcam", "kamera", "video call", "streaming"],
}


def _extract_budget(query: str) -> int | None:
    normalized = query.lower().replace(".", "").replace(",", "")
    match = re.search(r"(?:di bawah|dibawah|maks|max|budget|<=?)\s*(\d+)\s*(juta|jt|ribu|rb|k)?", normalized)
    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)
    if unit in {"juta", "jt"}:
        return amount * 1_000_000
    if unit in {"ribu", "rb", "k"} or amount < 10_000:
        return amount * 1_000
    return amount


def _score_product(product: dict[str, Any], query: str, budget: int | None) -> int:
    terms = query.lower()
    score = 0

    if product["category"] in terms:
        score += 4

    for category, keywords in CATEGORY_KEYWORDS.items():
        if product["category"] == category and any(keyword in terms for keyword in keywords):
            score += 3

    for tag in product["tags"]:
        if tag in terms:
            score += 2

    if budget is not None:
        score += 3 if product["price"] <= budget else -5

    return score


def recommend_products(query: str) -> dict[str, Any]:
    """Recommend products from a local demo catalog based on user needs and budget.

    Args:
        query: User request describing product category, use case, budget, or specs.
    """

    budget = _extract_budget(query)
    scored_products = [
        (product, _score_product(product, query, budget)) for product in PRODUCT_CATALOG
    ]
    ranked = sorted(scored_products, key=lambda item: item[1], reverse=True)
    matches = [product for product, score in ranked if score > 0][:3]

    if not matches:
        matches = [product for product, _score in ranked[:3]]

    recommendations = [
        {
            "name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "reason": product["description"],
        }
        for product in matches
    ]

    top = recommendations[0]
    return {
        "status": "success",
        "query": query,
        "budget_detected": budget,
        "recommendations": recommendations,
        "buying_suggestion": (
            f"Pilihan utama: {top['name']} karena paling sesuai dengan kebutuhan "
            f"yang terdeteksi. Cek ulang stok, garansi, dan ulasan sebelum checkout."
        ),
    }
