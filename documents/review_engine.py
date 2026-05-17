from .models import DocumentReview


# =========================================================
# 🧠 REVIEW OUTCOME ENGINE
# =========================================================
def apply_review_outcome(document):
    """
    Evaluates all reviews and determines final outcome.

    Handles:
    ✔ Approval logic
    ✔ Rejection logic
    ✔ Multi-review thresholds
    ✔ Learning trigger (safe)
    """

    reviews = DocumentReview.objects.filter(document=document)

    approvals = reviews.filter(decision="approved").count()
    rejections = reviews.filter(decision="rejected").count()

    # =========================================================
    # 🛡️ SAFETY — ENSURE VALID REQUIRED REVIEWERS
    # =========================================================
    required = document.required_reviewers or 1

    # -----------------------------------------------------
    # ❌ ANY REJECTION → FAIL
    # -----------------------------------------------------
    if rejections > 0:
        document.review_status = "review_rejected"
        document.is_verified = False
        document.save()
        return

    # -----------------------------------------------------
    # ✅ APPROVAL THRESHOLD MET → VERIFIED
    # -----------------------------------------------------
    if approvals >= required:

        document.review_status = "review_approved"
        document.is_verified = True

        # =========================================================
        # 🧠 SAFE DATA ASSIGNMENT
        # =========================================================
        if isinstance(document.extracted_data, dict):
            document.reviewed_data = document.extracted_data
        else:
            document.reviewed_data = {}

        document.save()

        # =========================================================
        # 🧠 SAFE LEARNING TRIGGER
        # =========================================================
        if document.reviewed_data:
            from .learning import record_learning
            record_learning(document)

        return

    # -----------------------------------------------------
    # ⏳ STILL UNDER REVIEW
    # -----------------------------------------------------
    document.review_status = "under_review"
    document.save()