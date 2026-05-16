from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = [
            'id',
            'owner',
            'file_hash',
            'created_at',
            'updated_at',
            'file'
            'owner_name',
            'document_category',
            'extracted_data',
            'processing_status',
        ]