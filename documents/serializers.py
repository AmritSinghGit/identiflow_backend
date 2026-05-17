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
        🧠 FINAL API REPRESENTATION LAYER

        Responsibilities:
        ✔ Guarantees stable API structure
        ✔ Prevents None JSON corruption
        ✔ Normalizes extracted field structure
        ✔ Supports future AI metadata expansion
        ✔ Controls final verified output

        IMPORTANT:
        This layer should NEVER mutate database state.
        It only sanitizes API output.
        """

        data = super().to_representation(instance)

        # =====================================================
        # 🧹 SAFE JSON NORMALIZATION
        # =====================================================
        extracted_data = instance.extracted_data or {}
        raw_ai_response = instance.raw_ai_response or {}
        reviewed_data = instance.reviewed_data or {}
        corrected_data = instance.user_corrected_data or {}

        # Ensure dict safety
        if not isinstance(extracted_data, dict):
            extracted_data = {}

        if not isinstance(raw_ai_response, dict):
            raw_ai_response = {}

        if not isinstance(reviewed_data, dict):
            reviewed_data = {}

        if not isinstance(corrected_data, dict):
            corrected_data = {}

        # =====================================================
        # 🧠 FIELD STRUCTURE NORMALIZATION
        # =====================================================
        normalized_fields = {}

        for field_name, value in extracted_data.items():

            # -------------------------------------------------
            # ✅ ALREADY STRUCTURED
            # -------------------------------------------------
            if isinstance(value, dict):

                normalized_fields[field_name] = {
                    "value": value.get("value"),
                    "confidence": value.get("confidence", 0),
                    "source": value.get("source", "unknown"),
                    "validated": value.get("validated", False),
                    "reviewed": value.get("reviewed", False),
                }

            # -------------------------------------------------
            # 🔄 LEGACY FLAT VALUE → AUTO NORMALIZE
            # -------------------------------------------------
            else:

                normalized_fields[field_name] = {
                    "value": value,
                    "confidence": 0,
                    "source": "legacy",
                    "validated": False,
                    "reviewed": False,
                }

        # =====================================================
        # 💾 ASSIGN SANITIZED OUTPUT
        # =====================================================
        data["extracted_data"] = normalized_fields
        data["raw_ai_response"] = raw_ai_response
        data["reviewed_data"] = reviewed_data
        data["user_corrected_data"] = corrected_data

        # =====================================================
        # 🔥 FINAL VERIFIED DATA
        # =====================================================
        if instance.is_verified:

            if reviewed_data:
                data["final_data"] = reviewed_data

            else:
                data["final_data"] = normalized_fields

        else:
            data["final_data"] = None

        # =====================================================
        # 🧠 FUTURE POLICY FLAGS
        # =====================================================
        data["meta"] = {
            "ai_processed": instance.ai_used,
            "review_required": instance.required_reviewers > 0,
            "verification_status": instance.review_status,
            "confidence_score": instance.confidence_score,
        }

        # =====================================================
        # 🔒 FUTURE MASKING LAYER
        # =====================================================
        # Example:
        # if settings.MASK_SENSITIVE_DATA:
        #     data = mask_sensitive_fields(data)

        return data

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