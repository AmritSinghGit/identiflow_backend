"""
📦 intelligence/engine.py

🧠 Central Intelligence Engine

Handles:
- AI extraction
- Data enhancement
- Confidence recalculation
- Learning signals

🚨 RULE:
This is the ONLY place AI is used.
"""

from .ai import ai_extract_fields
from .confidence import calculate_confidence


def process_document_intelligence(document):
    """
    Runs AFTER upload pipeline.

    Enhances document using AI + intelligence logic.
    """

    # =========================================================
    # 📥 BASE DATA
    # =========================================================
    extracted_data = document.extracted_data or {}
    text = document.extracted_text

    # =========================================================
    # 🤖 AI EXTRACTION (ONLY IF NEEDED)
    # =========================================================
    ai_data = {}

    if should_use_ai(document, extracted_data):
        ai_data = ai_extract_fields(text)

        if isinstance(ai_data, dict):
            document.raw_ai_response = ai_data

    # =========================================================
    # 🔀 MERGE DATA (AI + RULES)
    # =========================================================
    final_data = {**ai_data, **extracted_data}

    document.extracted_data = final_data

    # =========================================================
    # 📊 RECALCULATE CONFIDENCE
    # =========================================================
    document.confidence_score = calculate_confidence(final_data)

    document.save()

    return document


def should_use_ai(document, extracted_data):
    """
    Basic AI trigger logic (we will upgrade later)
    """

    if document.confidence_score >= 0.85:
        return False

    if not extracted_data.get("name"):
        return True

    if not extracted_data.get("pan_number"):
        return True

    return True