from django.db import models
from django.contrib.auth.models import User
import uuid


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 👤 Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    owner_name = models.CharField(max_length=255, blank=True)

    # 📄 File
    file = models.FileField(upload_to="documents/%Y/%m/%d/")

    # 🧠 Classification
    document_category = models.CharField(max_length=100, default="Unknown")
    suggested_category = models.CharField(max_length=100, blank=True)
    variant_name = models.CharField(max_length=100, blank=True)

    # 🧠 Extraction
    extracted_text = models.TextField(blank=True)
    extracted_data = models.JSONField(default=dict, blank=True)
    raw_ai_response = models.JSONField(default=dict, blank=True)

    # 📊 Intelligence
    confidence_score = models.FloatField(default=0.0)

    # 👥 Relationship (future)
    belongs_to = models.CharField(max_length=255, blank=True)

    # 📌 Metadata
    title = models.CharField(max_length=255, blank=True)
    document_type = models.CharField(max_length=100, blank=True)

    # 🔒 Integrity
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)

    # ✅ Status
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

    is_verified = models.BooleanField(default=False)

    # 🕒 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username} - {self.title or self.file.name}"


# 📂 Category (Admin-controlled intelligence)
class DocumentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keywords = models.JSONField(default=list, blank=True)
    usage_count = models.IntegerField(default=0)
    confidence_threshold = models.FloatField(default=0.7)

    def __str__(self):
        return self.name


# 🔀 Variants (layout / format differences)
class DocumentVariant(models.Model):
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    keywords = models.JSONField(default=list, blank=True)
    extraction_rules = models.JSONField(default=dict, blank=True)

    confidence_boost = models.FloatField(default=0.1)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# 🧩 Dynamic Fields (for learning system)
class DocumentField(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)

    validation_regex = models.CharField(max_length=255, blank=True)
    required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category.name} - {self.name}"