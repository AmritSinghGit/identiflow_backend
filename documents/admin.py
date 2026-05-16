from django.contrib import admin
from .models import (
    Document,
    DocumentCategory,
    DocumentVariant,
    DocumentField
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'document_category', 'created_at')


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'usage_count')


@admin.register(DocumentVariant)
class DocumentVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'confidence_boost')


@admin.register(DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'required')