"""
📦 documents/field_confidence.py

🧠 FIELD CONFIDENCE ENGINE

Purpose:
✔ Assign confidence per field
✔ Prepare structured AI-ready data
✔ Enable selective AI targeting

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
from datetime import datetime


# =========================================================
# 🧠 MAIN ENGINE
# =========================================================
def build_field_confidence(document):

    raw_data = document.extracted_data or {}

    if not isinstance(raw_data, dict):
        raw_data = {}

    structured = {}

    # =====================================================
    # 👤 NAME
    # =====================================================
    name = raw_data.get("name")

    confidence = 0.0

    if name and len(str(name).split()) >= 2:
        confidence = 0.9

    structured["name"] = {
        "value": name,
        "confidence": confidence,
        "source": "ocr"
    }

    # =====================================================
    # 🪪 PAN
    # =====================================================
    pan = raw_data.get("pan_number")

    confidence = 0.0

    if pan and re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', str(pan)):
        confidence = 0.99

    structured["pan_number"] = {
        "value": pan,
        "confidence": confidence,
        "source": "ocr"
    }

    # =====================================================
    # 📅 DOB
    # =====================================================
    dob = raw_data.get("dob")

    confidence = 0.0

    if dob:

        try:

            parsed = datetime.strptime(str(dob), "%d/%m/%Y")

            if parsed.year > 1900:
                confidence = 0.9

        except Exception:
            pass

    structured["dob"] = {
        "value": dob,
        "confidence": confidence,
        "source": "ocr"
    }

    # =====================================================
    # 💾 SAVE
    # =====================================================
    document.extracted_data = structured

    document.save()

    return document