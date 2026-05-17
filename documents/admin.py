"""
📦 documents/admin.py

This module defines the Django Admin interface.

🧠 PURPOSE:
- Review extracted document data
- Compare system vs AI vs user corrections
- Approve final trusted data
- Generate learning signals

🎯 ADMIN = CONTROL CENTER of intelligence system
"""

from django.contrib import admin
from .models import (
    Document,
    DocumentCategory,
    DocumentVariant,
    DocumentField
)

from .learning import record_learning


# =========================================================
# ✅ ADMIN ACTION — APPROVE DOCUMENTS
# =========================================================
def approve_documents(modeladmin, request, queryset):
    """
    Approves selected documents.

    🧠 LOGIC:
    - If user corrected → trust corrected data
    - If user confirmed → trust extracted data
    - Save result into reviewed_data (final truth)

    🚀 ALSO:
    - Emits learning signals for future model improvement
    """

    for doc in queryset:

        # ===============================
        # 🧠 DETERMINE FINAL DATA
        # ===============================
        if doc.user_confirmation_status == 'corrected':
            doc.reviewed_data = doc.user_corrected_data

        elif doc.user_confirmation_status == 'confirmed':
            doc.reviewed_data = doc.extracted_data

        # ===============================
        # 📚 LEARNING SIGNAL CAPTURE
        # ===============================
        learning_data = record_learning(doc)

        if learning_data:
            print("LEARNING SIGNAL:", learning_data)

        doc.save()


approve_documents.short_description = "✅ Approve selected documents"


# =========================================================
# 📄 DOCUMENT ADMIN (CORE REVIEW PANEL)
# =========================================================
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for reviewing documents.

    🧠 VIEW LAYERS:
    - System output (OCR + extraction)
    - AI output
    - User corrections
    - Final trusted data
    """

    # =========================================================
    # 📋 LIST VIEW
    # =========================================================
    list_display = (
        'id',
        'owner',
        'document_category',
        'user_confirmation_status',
        'confidence_score',
        'ai_confidence_score',
        'created_at'
    )

    list_filter = (
        'document_category',
        'user_confirmation_status',
        'created_at'
    )

    search_fields = (
        'owner__username',
        'owner_name',
        'document_category'
    )

    # =========================================================
    # 🔒 READ-ONLY SYSTEM FIELDS
    # =========================================================
    readonly_fields = (
        'extracted_text',
        'extracted_data',
        'raw_ai_response',
        'confidence_score',
        'ai_confidence_score'
    )

    # =========================================================
    # 🧠 FIELD ORGANIZATION (CRITICAL FOR UX)
    # =========================================================
    fieldsets = (
        ("📄 Basic Info", {
            "fields": ("owner", "title", "file")
        }),

        ("🧠 System Extraction", {
            "fields": ("extracted_text", "extracted_data")
        }),

        ("🤖 AI Output", {
            "fields": ("raw_ai_response", "ai_confidence_score")
        }),

        ("👤 User Input", {
            "fields": ("user_confirmation_status", "user_corrected_data", "relationship")
        }),

        ("✅ Final Trusted Data", {
            "fields": ("reviewed_data",)
        }),

        ("📊 Classification", {
            "fields": ("document_category", "suggested_category", "variant_name")
        }),

        ("⚙️ Metadata", {
            "fields": ("confidence_score", "processing_status")
        }),
    )

    # =========================================================
    # ⚡ ACTIONS
    # =========================================================
    actions = [approve_documents]


# =========================================================
# 📂 DOCUMENT CATEGORY ADMIN
# =========================================================
@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    """
    Admin for managing document categories.
    """

    list_display = ('name', 'usage_count', 'confidence_threshold')
    search_fields = ('name',)


# =========================================================
# 🔀 DOCUMENT VARIANT ADMIN
# =========================================================
@admin.register(DocumentVariant)
class DocumentVariantAdmin(admin.ModelAdmin):
    """
    Admin for managing document variants (layouts).
    """

    list_display = ('name', 'category', 'confidence_boost')
    list_filter = ('category',)


# =========================================================
# 🧩 DOCUMENT FIELD ADMIN
# =========================================================
@admin.register(DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    """
    Admin for dynamic fields used in extraction/validation.
    """

    list_display = ('name', 'category', 'required')
    list_filter = ('category',)