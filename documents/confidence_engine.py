"""
📦 documents/confidence_engine.py

🧠 CONFIDENCE AGGREGATION ENGINE

Purpose:
✔ Calculate overall document confidence
✔ Aggregate field-level confidence
✔ Support trust routing
✔ Prepare learning signals
"""

# =========================================================
# 🧠 MAIN ENGINE
# =========================================================
def calculate_document_confidence(document):

    data = document.extracted_data or {}

    if not isinstance(data, dict):
        return 0

    scores = []

    for _, details in data.items():

        if not isinstance(details, dict):
            continue

        confidence = details.get("confidence")

        if confidence is not None:
            scores.append(confidence)

    if not scores:
        overall = 0

    else:
        overall = round(sum(scores) / len(scores), 2)

    document.confidence_score = overall
    document.ai_confidence_score = overall

    document.save()

    return overall