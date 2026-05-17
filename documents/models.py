"""
📦 documents/models.py

This module defines the core data architecture for the document intelligence system.

🧠 DESIGN PRINCIPLES:
- Separate system output, AI output, user input, and final trusted data
- Enable human-in-the-loop learning
- Keep structure scalable for AI training and enterprise use
- Avoid mixing responsibilities across fields
"""

from django.db import models
from django.contrib.auth.models import User
import uuid


# =========================================================
# 📄 CORE DOCUMENT MODEL
# =========================================================
class Document(models.Model):
    """
    Represents a single uploaded document.

    This is the central model of the system.

    🧠 FLOW:
    Upload → OCR → Extraction → AI → User Confirmation → Final Data

    We store multiple layers of truth:
    - extracted_data (system)
    - raw_ai_response (AI)
    - user_corrected_data (human)
    - reviewed_data (final trusted)
    """

    # =========================================================
    # 🆔 PRIMARY IDENTIFIER
    # =========================================================
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # 👤 OWNERSHIP
    # =========================================================
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    # Name extracted from document (not system user name)
    owner_name = models.CharField(max_length=255, blank=True)

    # =========================================================
    # 📄 FILE STORAGE
    # =========================================================
    file = models.FileField(upload_to="documents/%Y/%m/%d/")

    # =========================================================
    # 🧠 DOCUMENT CLASSIFICATION
    # =========================================================
    document_category = models.CharField(
        max_length=100,
        default="Unknown"
    )

    # AI-suggested category if system is unsure
    suggested_category = models.CharField(max_length=100, blank=True)

    # Variant (e.g., PAN_V1, PAN_QR, etc.)
    variant_name = models.CharField(max_length=100, blank=True)

    # =========================================================
    # 🧠 SYSTEM OUTPUT (RULE-BASED)
    # =========================================================
    extracted_text = models.TextField(blank=True)

    # Structured data extracted via rules
    extracted_data = models.JSONField(default=dict, blank=True)

    # =========================================================
    # 🤖 AI OUTPUT
    # =========================================================
    # Raw AI response stored for:
    # - audit
    # - training
    # - debugging
    raw_ai_response = models.JSONField(default=dict, blank=True)

    # Confidence from rule-based system
    confidence_score = models.FloatField(default=0.0)

    # Confidence from AI extraction
    ai_confidence_score = models.FloatField(default=0.0)

    # =========================================================
    # 👤 USER INTERACTION LAYER
    # =========================================================
    user_confirmation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),     # User has not confirmed yet
            ('confirmed', 'Confirmed'), # User accepted system output
            ('corrected', 'Corrected')  # User modified data
        ],
        default='pending'
    )

    # Stores user corrections (ground truth for learning)
    user_corrected_data = models.JSONField(default=dict, blank=True)

    # Relationship of document owner to user
    # Example: self, wife, father, etc.
    relationship = models.CharField(max_length=100, blank=True)

    # =========================================================
    # ✅ FINAL TRUSTED DATA
    # =========================================================
    """
    This is the MOST IMPORTANT layer.

    It represents:
    - Verified
    - Approved
    - Trusted data

    This is what downstream systems should use.
    """
    reviewed_data = models.JSONField(default=dict, blank=True)

    # =========================================================
    # ⚙️ SETTINGS SNAPSHOT (IMPORTANT FOR AUDIT)
    # =========================================================
    # Whether AI was used for this document
    ai_used = models.BooleanField(default=True)

    # Whether encryption was enabled at time of processing
    encryption_enabled = models.BooleanField(default=False)

    # =========================================================
    # 📌 METADATA
    # =========================================================
    title = models.CharField(max_length=255, blank=True)

    # High-level type grouping (Identity, Financial, etc.)
    document_type = models.CharField(max_length=100, blank=True)

    # Hash for duplicate detection
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)

    # =========================================================
    # ⚙️ PROCESSING STATUS
    # =========================================================
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    # =========================================================
    # 🕒 TIMESTAMPS
    # =========================================================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # =========================================================
    # 🔍 STRING REPRESENTATION
    # =========================================================
    def __str__(self):
        return f"{self.owner.username} - {self.title or self.file.name}"


# =========================================================
# 📂 DOCUMENT CATEGORY (ADMIN CONTROLLED)
# =========================================================
class DocumentCategory(models.Model):
    """
    Defines document types (PAN, Aadhaar, etc.)

    Used for:
    - classification
    - learning
    - AI guidance
    """

    name = models.CharField(max_length=100, unique=True)

    # Keywords used for classification
    keywords = models.JSONField(default=list, blank=True)

    # Tracks how often this category is used
    usage_count = models.IntegerField(default=0)

    # Minimum confidence required for auto-classification
    confidence_threshold = models.FloatField(default=0.7)

    def __str__(self):
        return self.name


# =========================================================
# 🔀 DOCUMENT VARIANTS
# =========================================================
class DocumentVariant(models.Model):
    """
    Represents variations of a document type.

    Example:
    - PAN_V1
    - PAN_QR
    - DL_MH
    """

    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    # Keywords specific to this variant
    keywords = models.JSONField(default=list, blank=True)

    # Extraction rules specific to variant
    extraction_rules = models.JSONField(default=dict, blank=True)

    # Boost confidence when matched
    confidence_boost = models.FloatField(default=0.1)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# =========================================================
# 🧩 DYNAMIC FIELD DEFINITIONS
# =========================================================
class DocumentField(models.Model):
    """
    Defines fields dynamically per category.

    Example:
    PAN → pan_number, name, dob
    """

    name = models.CharField(max_length=100)

    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)

    # Regex validation for field
    validation_regex = models.CharField(max_length=255, blank=True)

    # Whether field is mandatory
    required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# =========================================================
# ⚙️ USER SETTINGS (CONTROL AI + SECURITY)
# =========================================================
class UserSettings(models.Model):
    """
    Stores per-user preferences.

    Allows:
    - Turning AI ON/OFF
    - Enabling encryption
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    use_ai = models.BooleanField(default=True)
    enable_encryption = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username