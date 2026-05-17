"""
📦 documents/serializers.py

🧠 RESPONSIBILITY:
✔ API exposure control
✔ Safe serialization
✔ Final vs raw data separation
✔ Future-ready masking + security

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DESIGN PRINCIPLES:
✔ Never return None
✔ Always sanitize JSON fields
✔ Separate system vs user vs AI data
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = '__all__'

        read_only_fields = [
            # Core
            'id',
            'owner',
            'file_hash',
            'created_at',
            'updated_at',

            # System generated
            'owner_name',
            'document_category',
            'extracted_data',
            'raw_ai_response',
            'processing_status',
            'confidence_score',
            'variant_name',
            'suggested_category',
            'ai_confidence_score',

            # Controlled flows
            'reviewed_data'
        ]

    # =========================================================
    # 🧠 SAFE OUTPUT REPRESENTATION
    # =========================================================
    def to_representation(self, instance):
        """
        Ensures:
        ✔ Always returns dict
        ✔ No None JSON fields
        ✔ Controlled exposure of data
        """

        data = super().to_representation(instance)

        # -----------------------------------------------------
        # 🧹 SANITIZE JSON FIELDS (CRITICAL)
        # -----------------------------------------------------
        data['extracted_data'] = instance.extracted_data or {}
        data['raw_ai_response'] = instance.raw_ai_response or {}
        data['reviewed_data'] = instance.reviewed_data or {}
        data['user_corrected_data'] = instance.user_corrected_data or {}

        # -----------------------------------------------------
        # 🔥 FINAL DATA LOGIC
        # -----------------------------------------------------
        if instance.is_verified:
            data['final_data'] = data['reviewed_data']
        else:
            data['final_data'] = None

        # -----------------------------------------------------
        # 🔒 FUTURE MASKING LAYER (DISABLED FOR NOW)
        # -----------------------------------------------------
        # You can re-enable this later via settings
        #
        # if settings.MASK_SENSITIVE_DATA:
        #     data = mask_data(data)

        return data  # ✅ CRITICAL — NEVER REMOVE

    # =========================================================
    # 🧠 CREATE OVERRIDE (OWNER CONTROL)
    # =========================================================
    def create(self, validated_data):
        """
        Ensures:
        ✔ Owner always comes from request
        ✔ Prevents spoofing
        """

        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user

        return super().create(validated_data)