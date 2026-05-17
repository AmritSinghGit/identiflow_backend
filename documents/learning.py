"""
📦 documents/learning.py

Handles learning signals from user/admin actions.

🧠 PURPOSE:
- Capture corrections
- Capture confirmations
- Build dataset for future AI training
"""


def record_learning(document):
    """
    Generates learning signals from document lifecycle.

    Returns:
        dict OR None
    """

    # =========================================================
    # 🧠 USER CORRECTED DATA (STRONG SIGNAL)
    # =========================================================
    if document.user_confirmation_status == 'corrected':
        return {
            "type": "correction",
            "original": document.extracted_data,
            "corrected": document.user_corrected_data,
            "category": document.document_category
        }

    # =========================================================
    # 🧠 USER CONFIRMED DATA (WEAK SIGNAL)
    # =========================================================
    if document.user_confirmation_status == 'confirmed':
        return {
            "type": "confirmation",
            "data": document.extracted_data,
            "category": document.document_category
        }

    return None