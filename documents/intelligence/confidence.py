"""
📦 intelligence/confidence.py

Centralized confidence scoring.
"""


def calculate_confidence(data):
    """
    Calculates confidence based on available fields.
    """

    score = 0

    if data.get("name"):
        score += 0.3

    if data.get("pan_number"):
        score += 0.3

    if data.get("dob"):
        score += 0.2

    if data.get("document_type"):
        score += 0.2

    return round(score, 2)