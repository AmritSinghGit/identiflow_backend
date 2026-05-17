"""
📦 documents/ai_targeting.py

🧠 AI TARGETING ENGINE

Purpose:
✔ Identify weak fields
✔ Call AI only where needed
✔ Merge results safely

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 RULE:
AI must NEVER overwrite strong data
"""

from .services import ai_extract_fields


CONFIDENCE_THRESHOLD = 0.7


# =========================================================
# 🧠 MAIN TARGETING FUNCTION
# =========================================================
def run_ai_targeting(document):

    data = document.extracted_data or {}

    if not isinstance(data, dict):
        return document

    text = document.extracted_text or ""

    # =========================================================
    # 🎯 FIND WEAK FIELDS
    # =========================================================
    weak_fields = []

    for field, details in data.items():
        if not isinstance(details, dict):
            continue

        if details.get("confidence", 0) < CONFIDENCE_THRESHOLD:
            weak_fields.append(field)

    # ---------------------------------------------------------
    # 🚫 NOTHING TO FIX
    # ---------------------------------------------------------
    if not weak_fields:
        document.ai_used = False
        document.save()
        return document

    # =========================================================
    # 🤖 CALL AI
    # =========================================================
    ai_data = ai_extract_fields(text)

    if not isinstance(ai_data, dict):
        return document

    # =========================================================
    # 🔀 MERGE ONLY WEAK FIELDS
    # =========================================================
    for field in weak_fields:
        if ai_data.get(field):
            data[field] = {
                "value": ai_data[field],
                "confidence": 0.85,
                "source": "ai"
            }

    document.extracted_data = data
    document.raw_ai_response = ai_data
    document.ai_used = True

    document.save()

    return document