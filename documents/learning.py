"""
📦 documents/learning.py

🧠 LEARNING ENGINE (CORE INTELLIGENCE LAYER)

This module is responsible for converting VERIFIED document data
into structured intelligence for future AI improvements.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 OBJECTIVES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Learn ONLY from verified data
✔ Build category intelligence
✔ Discover and evolve document fields
✔ Generate high-quality training dataset
✔ Enable future ML + AI improvements

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 GOLDEN RULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEVER learn from unverified data.
This ensures:
✔ No noise
✔ No corrupted learning
✔ High-quality dataset
"""

from .models import DocumentCategory, DocumentField


# =========================================================
# 🧠 MAIN ENTRY POINT
# =========================================================
def record_learning(document):
    """
    Entry point for learning system.

    Called ONLY AFTER:
    ✔ Reviewer approval
    ✔ OR trusted system verification

    This is where intelligence starts accumulating.
    """

    # -----------------------------------------------------
    # 🚫 SAFETY CHECK — DO NOT LEARN FROM NOISE
    # -----------------------------------------------------
    if not document.is_verified:
        return

    final_data = document.reviewed_data

    if not isinstance(final_data, dict):
        return  # 🚫 skip invalid data safely

    # -----------------------------------------------------
    # 📊 CATEGORY LEARNING
    # -----------------------------------------------------
    learn_category(document)

    # -----------------------------------------------------
    # 🧩 FIELD LEARNING (DYNAMIC SCHEMA)
    # -----------------------------------------------------
    learn_fields(document, final_data)

    # -----------------------------------------------------
    # 🧠 DATASET LOGGING (CRITICAL FOR FUTURE AI)
    # -----------------------------------------------------
    log_learning_event(document, final_data)


# =========================================================
# 📊 CATEGORY LEARNING
# =========================================================
def learn_category(document):
    """
    Tracks how frequently a category is used.

    Future impact:
    ✔ Improves classification confidence
    ✔ Enables ranking models
    ✔ Helps identify dominant document types
    """

    try:
        category = DocumentCategory.objects.get(
            name=document.document_category
        )

        category.usage_count += 1
        category.save()

    except DocumentCategory.DoesNotExist:
        # Category not yet registered (safe fail)
        pass


# =========================================================
# 🧩 FIELD LEARNING (IMPORTANT)
# =========================================================
def learn_fields(document, data):
    """
    Dynamically learns which fields belong to which category.

    Example:
    PAN → name, dob, pan_number

    Future impact:
    ✔ Auto-schema evolution
    ✔ Better extraction
    ✔ Field validation rules
    ✔ AI fine-tuning signals
    """

    category = DocumentCategory.objects.filter(
        name=document.document_category
    ).first()

    if not category:
        return

    for field_name in (data or {}).keys():

        field, created = DocumentField.objects.get_or_create(
            name=field_name,
            category=category,
        )

        # 🔮 FUTURE ENHANCEMENTS:
        # - field frequency tracking
        # - confidence scoring per field
        # - validation rule generation


# =========================================================
# 🧠 LEARNING DATA LOGGER
# =========================================================
def log_learning_event(document, data):
    """
    Logs structured learning data.

    This becomes your:
    ✔ Training dataset
    ✔ Debugging tool
    ✔ Analytics base
    """

    payload = {
        "document_id": str(document.id),
        "category": document.document_category,
        "final_data": data,
        "confidence_score": document.confidence_score,
        "ai_used": document.ai_used,
        "review_status": document.review_status,
    }

    print("\n========== VERIFIED LEARNING EVENT ==========")
    print(payload)
    print("============================================\n")