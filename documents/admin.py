from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "document_type", "is_verified", "created_at")
    search_fields = ("owner__username", "document_type")
    list_filter = ("is_verified", "document_type")