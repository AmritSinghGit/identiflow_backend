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
            'owner_name',
            'document_category',
            'extracted_data',
            'raw_ai_response',
            'processing_status',
            'confidence_score',
            'variant_name',
            'suggested_category',
            'review_status',
            'reviewed_data',
            'ai_confidence_score',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # 🔥 FINAL DATA LOGIC (IMPORTANT)
        if instance.review_status == 'approved':
            data['final_data'] = instance.reviewed_data
        else:
            data['final_data'] = None

        # 🔍 Optional: show masked preview (we'll enhance later)
        extracted = data.get("extracted_data", {})

        if "pan_number" in extracted:
            pan = extracted["pan_number"]
            if isinstance(pan, str) and len(pan) >= 4:
                extracted["pan_number"] = pan[:2] + "XXXXX" + pan[-2:]

        if "name" in extracted:
            name = extracted["name"]
            if isinstance(name, str) and len(name) > 1:
                extracted["name"] = name[0] + "***"

        data["extracted_data"] = extracted

        return data

    def create(self, validated_data):
        # Owner always comes from request, not user input
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user

        return super().create(validated_data)