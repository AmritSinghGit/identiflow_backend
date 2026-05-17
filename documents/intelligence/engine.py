"""
📦 intelligence/engine.py

🧠 CENTRAL INTELLIGENCE ENGINE

Handles:
✔ AI extraction
✔ Data enhancement
✔ Confidence recalculation
✔ Safe processing pipeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 RULE:
This is the ONLY place where AI is used.
Must NEVER crash the system.
"""

from .ai import ai_extract_fields
from .confidence import calculate_confidence


# =========================================================
# 🧠 MAIN INTELLIGENCE PROCESSOR
# =========================================================
def process_document_intelligence(document):
    """
    Runs AFTER upload pipeline.

    Enhances document using AI + rule-based logic.
    """

    # =========================================================
    # 🛡️ SAFE BASE DATA HANDLING
    # =========================================================
    extracted_data = document.extracted_data or {}

    if not isinstance(extracted_data, dict):
        extracted_data = {}

    text = document.extracted_text or ""

    # =========================================================
    # 🤖 AI EXTRACTION (SAFE)
    # =========================================================
    ai_data = {}

    if should_use_ai(document, extracted_data):

        ai_response = ai_extract_fields(text)

        # -----------------------------------------------------
        # 🛡️ SAFE AI RESPONSE HANDLING
        # -----------------------------------------------------
        if isinstance(ai_response, dict):
            ai_data = ai_response
            document.raw_ai_response = ai_response
            document.ai_used = True
        else:
            ai_data = {}
            document.ai_used = False

    # =========================================================
    # 🔀 SAFE DATA MERGE
    # =========================================================
    if not isinstance(ai_data, dict):
        ai_data = {}

    final_data = {**ai_data, **extracted_data}

    document.extracted_data = final_data

    # =========================================================
    # 📊 SAFE CONFIDENCE CALCULATION
    # =========================================================
    try:
        document.confidence_score = calculate_confidence(final_data)
    except Exception:
        document.confidence_score = 0.0

    document.save()

    return document


# =========================================================
# 🧠 AI USAGE DECISION ENGINE
# =========================================================
def should_use_ai(document, extracted_data):
    """
    Determines whether AI should be used.

    Future-ready:
    ✔ Will use user settings
    ✔ Will use cost optimization
    ✔ Will use learning signals
    """

    # -----------------------------------------------------
    # 🛡️ SAFETY CHECK
    # -----------------------------------------------------
    if not isinstance(extracted_data, dict):
        return True

    # -----------------------------------------------------
    # 📊 HIGH CONFIDENCE → SKIP AI
    # -----------------------------------------------------
    if document.confidence_score >= 0.85:
        return False

    # -----------------------------------------------------
    # 🔍 MISSING CRITICAL FIELDS → USE AI
    # -----------------------------------------------------
    if not extracted_data.get("name"):
        return True

    if not extracted_data.get("pan_number"):
        return True

    # -----------------------------------------------------
    # DEFAULT → USE AI
    # -----------------------------------------------------
    return True