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

    # Verified by Uploader Yes
    is_verified = models.BooleanField(default=False)

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
    reviewed_data = models.JSONField(default=dict, blank=True)

    # =========================================================
    # 🔍 REVIEW WORKFLOW SYSTEM (CRITICAL FOR SCALE)
    # =========================================================
    review_status = models.CharField(
        max_length=30,
        choices=[
            ('pending', 'Pending'),
            ('user_confirmed', 'User Confirmed'),
            ('under_review', 'Under Review'),
            ('review_approved', 'Review Approved'),
            ('review_rejected', 'Review Rejected'),
            ('high_risk_review', 'High Risk Review')
        ],
        default='pending'
    )

    # Number of reviewers required (dynamic based on confidence)
    required_reviewers = models.IntegerField(default=1)

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
# ⚙️ USER SETTINGS (AI CONTROL + SECURITY POLICY)
# =========================================================
class UserSettings(models.Model):
    """
    Stores per-user system preferences.

    🧠 PURPOSE:
    - Control AI usage (cost optimization)
    - Enable/disable specific AI features
    - Control encryption behavior

    🎯 WHY THIS MATTERS:
    - AI is expensive → must be configurable
    - Different users = different needs
    - Enables future SaaS pricing tiers
    """

    # =========================================================
    # 📊 CONFIDENCE THRESHOLD (USER OVERRIDE)
    # =========================================================
    confidence_threshold = models.FloatField(default=0.85)

    """
    Defines what user considers "high confidence".

    Used to:
    - Skip AI if confidence ≥ threshold
    - Trigger AI if below threshold

    Default = system standard (0.85)
    """

    # =========================================================
    # 🧠 DOCUMENT REVIEW (MULTI-REVIEW SYSTEM)
    # =========================================================
class DocumentReview(models.Model):
    """
    Stores reviewer decisions for documents.

    Enables:
    - Multi-review workflows
    - Audit logs
    - Conflict resolution
    """

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )

    decision = models.CharField(
        max_length=20,
        choices=[
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ]
    )

    comments = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document.id} - {self.decision} by {self.reviewer.username}"

    # =========================================================
    # 🧠 AI USAGE LEVEL (COST CONTROL)
    # =========================================================
    AI_LEVEL_CHOICES = [
        (0, "No AI"),         # Fully rule-based system
        (1, "Light AI"),      # Only fill missing fields
        (2, "Full AI"),       # Full extraction + classification
        (3, "Advanced AI"),   # Future: reasoning, relationships
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Overall AI level (primary control)
    ai_level = models.IntegerField(choices=AI_LEVEL_CHOICES, default=2)

    # =========================================================
    # 🎛️ FEATURE-LEVEL AI CONTROLS
    # =========================================================
    use_ai_extraction = models.BooleanField(default=True)
    use_ai_classification = models.BooleanField(default=True)
    use_ai_relationship = models.BooleanField(default=False)

    """
    These allow fine-grained control:
    - extraction → fill missing data
    - classification → detect document type
    - relationship → infer "wife", "father", etc.
    """

    # =========================================================
    # 🔐 SECURITY CONTROL
    # =========================================================
    enable_encryption = models.BooleanField(default=False)

    """
    If enabled:
    - sensitive fields will be encrypted AFTER approval
    """

    def __str__(self):
        return self.user.username