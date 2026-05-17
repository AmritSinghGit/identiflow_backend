"""
📦 documents/field_intelligence.py

🧠 FIELD INTELLIGENCE ENGINE

Purpose:
✔ Fill missing fields
✔ Improve weak confidence fields
✔ Route between local AI and external AI
✔ Learn over time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 RULE:
Never overwrite high-confidence data
"""

from .services import ai_extract_fields


# =========================================================
# 🧠 MAIN FIELD ENRICHMENT FUNCTION
# =========================================================
def enrich_document_fields(document):
    """
    Enhances document fields intelligently.

    Flow:
    1. Identify missing/weak fields
    2. Try local intelligence (future)
    3. Fallback to external AI
    """

    extracted = document.extracted_data or {}

    if not isinstance(extracted, dict):
        extracted = {}

    text = document.extracted_text or ""

    # =========================================================
    # 🎯 IDENTIFY MISSING FIELDS
    # =========================================================
    missing_fields = []

    if not extracted.get("name"):
        missing_fields.append("name")

    if not extracted.get("pan_number"):
        missing_fields.append("pan_number")

    if not extracted.get("dob"):
        missing_fields.append("dob")

    # ---------------------------------------------------------
    # 🚫 NOTHING TO ENRICH
    # ---------------------------------------------------------
    if not missing_fields:
        return document

    # =========================================================
    # 🤖 AI ENRICHMENT (CONTROLLED)
    # =========================================================
    ai_data = ai_extract_fields(text)

    if not isinstance(ai_data, dict):
        return document

    # =========================================================
    # 🔀 MERGE ONLY MISSING FIELDS
    # =========================================================
    for field in missing_fields:
        if ai_data.get(field):
            extracted[field] = ai_data[field]

    document.extracted_data = extracted
    document.raw_ai_response = ai_data
    document.ai_used = True

    document.save()

    return document

def should_use_ai_for_fields(document):
    user = document.owner

    if not hasattr(user, "usersettings"):
        return True

    settings = user.usersettings

    # Level 0 → No AI
    if settings.ai_level == 0:
        return False

    # Level 1 → Only missing fields
    if settings.ai_level == 1:
        return True

    # Level 2+ → Full AI
    return True