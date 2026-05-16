from django.db import models
from django.contrib.auth.models import User
import uuid


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")

    file = models.FileField(upload_to="documents/%Y/%m/%d/")

    title = models.CharField(max_length=255, blank=True)
    document_type = models.CharField(max_length=100, blank=True)
    belongs_to = models.CharField(max_length=255, blank=True)
    extracted_text = models.TextField(blank=True)

    is_verified = models.BooleanField(default=False)

    file_hash = models.CharField(max_length=64, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username} - {self.title or self.file.name}"