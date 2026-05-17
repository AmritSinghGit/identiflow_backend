"""
📦 documents/validation.py

🧠 VALIDATION ENGINE

Purpose:
✔ Validate extracted data
✔ Improve confidence scoring
✔ Detect anomalies
✔ Prepare data for AI + review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 RULE:
Validation NEVER modifies data blindly.
It only:
✔ flags
✔ scores
✔ suggests
"""

import re
from datetime import datetime


# =========================================================
# 🧠 MAIN VALIDATION ENTRY POINT
# =========================================================
def validate_document_data(document):
    """
    Runs validation checks and updates confidence score.
    """

    data = document.extracted_data or {}

    if not isinstance(data, dict):
        data = {}

    validation_results = {
        "pan_valid": False,
        "dob_valid": False,
        "name_valid": False,
    }

    score = 0

    # =========================================================
    # 🪪 PAN VALIDATION
    # =========================================================
    pan = data.get("pan_number")

    if pan and re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
        validation_results["pan_valid"] = True
        score += 0.4

    # =========================================================
    # 📅 DOB VALIDATION
    # =========================================================
    dob = data.get("dob")

    if dob:
        try:
            parsed_dob = datetime.strptime(dob, "%d/%m/%Y")

            if parsed_dob.year > 1900 and parsed_dob.year < datetime.now().year:
                validation_results["dob_valid"] = True
                score += 0.2

        except Exception:
            pass

    # =========================================================
    # 👤 NAME VALIDATION
    # =========================================================
    name = data.get("name")

    if name and len(name.split()) >= 2 and len(name) > 5:
        validation_results["name_valid"] = True
        score += 0.2

    # =========================================================
    # 🧠 CATEGORY CONFIDENCE BOOST
    # =========================================================
    if document.document_category != "Unknown":
        score += 0.2

    # =========================================================
    # 🧠 FINAL CONFIDENCE
    # =========================================================
    document.confidence_score = round(score, 2)

    # Store validation results (future AI learning)
    document.ai_confidence_score = score

    document.save()

    return document