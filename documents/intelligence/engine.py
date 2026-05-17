"""
📦 documents/intelligence/engine.py

🧠 CENTRAL INTELLIGENCE ENGINE

Handles:
- AI extraction
- Data enhancement (merge AI + rule-based)
- Confidence recalculation
- AI usage tracking
- Debug visibility

🚨 RULES:
- This is the ONLY place AI is used
- Views should NEVER contain intelligence logic
- Database always stores FULL (unmasked) data
"""

from .ai import ai_extract_fields
from .confidence import calculate_confidence


# =========================================================
# 🧠 MAIN ENTRY POINT
# =========================================================
def process_document_intelligence(document):
    """
    Runs AFTER upload pipeline.

    Enhances document using AI + intelligence logic.

    FLOW:
    1. Get extracted data
    2. Decide AI usage
    3. Run AI (if needed)
    4. Merge results
    5. Recalculate confidence
    6. Store results
    """

    # =========================================================
    # 📥 STEP 1 — BASE DATA
    # =========================================================
    extracted_data = document.extracted_data or {}
    text = document.extracted_text or ""

    # =========================================================
    # 🤖 STEP 2 — DECIDE AI USAGE
    # =========================================================
    use_ai = should_use_ai(document, extracted_data)

    ai_data = {}

    # =========================================================
    # 🤖 STEP 3 — AI EXECUTION
    # =========================================================
    if use_ai:
        ai_data = ai_extract_fields(text)

        if isinstance(ai_data, dict):
            document.raw_ai_response = ai_data
            document.ai_used = True
        else:
            document.ai_used = False
    else:
        document.ai_used = False

    # =========================================================
    # 🔀 STEP 4 — MERGE DATA
    # =========================================================
    final_data = {**ai_data, **extracted_data}

    document.extracted_data = final_data

    # =========================================================
    # 📊 STEP 5 — CONFIDENCE (CENTRALIZED)
    # =========================================================
    document.confidence_score = calculate_confidence(final_data)

    # =========================================================
    # 🧠 STEP 6 — DEBUG (REMOVE IN PROD LATER)
    # =========================================================
    print("\n===== INTELLIGENCE ENGINE =====")
    print("Use AI:", use_ai)
    print("Extracted Data:", extracted_data)
    print("AI Data:", ai_data)
    print("Final Data:", final_data)
    print("Confidence:", document.confidence_score)
    print("AI Used:", document.ai_used)
    print("================================\n")

    # =========================================================
    # 💾 STEP 7 — SAVE
    # =========================================================
    document.save()

    return document


# =========================================================
# 🧠 AI DECISION ENGINE (TEMP VERSION)
# =========================================================
def should_use_ai(document, extracted_data):
    """
    Determines whether AI should be used.

    CURRENT LOGIC (TEMP):
    - Skip AI if confidence is already high
    - Use AI if key fields are missing

    ⚠️ This will later become:
    - User-controlled
    - Category-based
    - Learning-driven
    """

    # ---------------------------------------------------------
    # HIGH CONFIDENCE → SKIP AI
    # ---------------------------------------------------------
    if document.confidence_score >= 0.85:
        return False

    # ---------------------------------------------------------
    # MISSING IMPORTANT FIELDS → USE AI
    # ---------------------------------------------------------
    if not extracted_data.get("name"):
        return True

    if not extracted_data.get("pan_number"):
        return True

    # ---------------------------------------------------------
    # DEFAULT → USE AI
    # ---------------------------------------------------------
    return True