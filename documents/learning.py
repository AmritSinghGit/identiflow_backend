"""
📦 documents/learning.py

🧠 LEARNING ENGINE (FOUNDATION)

This module captures VERIFIED data and converts it into
structured intelligence for future AI improvement.

🚨 GOLDEN RULE:
We ONLY learn from VERIFIED documents.

This ensures:
✔ No garbage learning
✔ High-quality dataset
✔ Future ML readiness
"""

from .models import Document, DocumentCategory, DocumentField


# =========================================================
# 🧠 MAIN ENTRY POINT
# =========================================================
def record_learning(document):
    """
    Called AFTER:
    - reviewer approval
    - OR trusted user confirmation

    This function builds long-term intelligence.
    """

    # -----------------------------------------------------
    # 🚫 SAFETY CHECK
    # -----------------------------------------------------
    if not document.is_verified:
        return  # NEVER learn from unverified data

    final_data = document.reviewed_data or {}

    # -----------------------------------------------------
    # 📊 CATEGORY LEARNING
    # -----------------------------------------------------
    update_category_learning(document)

    # -----------------------------------------------------
    # 🧩 FIELD LEARNING
    # -----------------------------------------------------
    update_field_learning(document, final_data)

    # -----------------------------------------------------
    # 🧠 DATASET LOGGING (VERY IMPORTANT)
    # -----------------------------------------------------
    log_learning_event(document, final_data)


# =========================================================
# 📊 CATEGORY LEARNING
# =========================================================
def update_category_learning(document):
    """
    Tracks category usage frequency.

    Helps:
    - improve classification
    - build ranking models later
    """

    try:
        category = DocumentCategory.objects.get(
            name=document.document_category
        )
        category.usage_count += 1
        category.save()
    except DocumentCategory.DoesNotExist:
        pass


# =========================================================
# 🧩 FIELD LEARNING (DYNAMIC SYSTEM)
# =========================================================
def update_field_learning(document, data):
    """
    Learns which fields belong to which category.

    Example:
    PAN → name, dob, pan_number

    This enables:
    - dynamic schema evolution
    - validation building
    - better extraction later
    """

    category = get_category(document.document_category)

    if not category:
        return

    for field_name in data.keys():

        field, created = DocumentField.objects.get_or_create(
            name=field_name,
            category=category,
        )

        # 🔮 Future:
        # - add frequency count
        # - add confidence tracking
        # - build validation rules


# =========================================================
# 🔧 HELPER
# =========================================================
def get_category(name):
    return DocumentCategory.objects.filter(name=name).first()


# =========================================================
# 🧠 LEARNING DATASET LOGGER
# =========================================================
def log_learning_event(document, data):
    """
    Logs structured learning data.

    This becomes your future training dataset.
    """

    payload = {
        "document_id": str(document.id),
        "category": document.document_category,
        "final_data": data,
        "confidence": document.confidence_score,
        "ai_used": document.ai_used,
        "review_status": document.review_status,
    }

    print("\n===== VERIFIED LEARNING EVENT =====")
    print(payload)
    print("==================================\n")