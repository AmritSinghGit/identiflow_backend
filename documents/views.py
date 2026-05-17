"""
📦 documents/views.py

This module handles all API endpoints related to document lifecycle.

🧠 CORE FLOW:
Upload → OCR → Extraction → AI Assist → Merge → Confidence → Store → User Confirmation

🎯 DESIGN GOALS:
- Fail-safe execution
- Clear separation of concerns
- Extendable for AI learning + human validation
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Document, UserSettings
from .serializers import DocumentSerializer

import hashlib

from .services import (
    extract_text,
    classify_document,
    extract_structured_data,
    detect_variant,
    ai_extract_fields
)


# =========================================================
# 📤 DOCUMENT UPLOAD + PROCESSING
# =========================================================
class DocumentUploadView(generics.CreateAPIView):
    """
    Handles document upload and full processing pipeline.

    Steps:
    1. Validate input
    2. Prevent duplicates
    3. Save document
    4. Run OCR
    5. Extract structured data
    6. Classify document
    7. Detect variant
    8. AI fallback (if needed)
    9. Merge data
    10. Compute confidence
    11. Store securely
    """

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # =========================================================
            # 📄 INPUT VALIDATION
            # =========================================================
            file = request.FILES.get('file')

            if not file:
                return Response(
                    {"error": "No file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # =========================================================
            # 🔒 DUPLICATE DETECTION (HASH)
            # =========================================================
            hasher = hashlib.sha256()
            for chunk in file.chunks():
                hasher.update(chunk)
            file_hash = hasher.hexdigest()

            existing_document = Document.objects.filter(
                owner=request.user,
                file_hash=file_hash
            ).first()

            if existing_document:
                return Response(
                    {
                        "message": "Duplicate document detected",
                        "existing_document_id": str(existing_document.id)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # =========================================================
            # 💾 INITIAL SAVE
            # =========================================================
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            document = serializer.save(
                owner=request.user,
                file_hash=file_hash
            )

            document.processing_status = 'processing'
            document.save()

            file_path = document.file.path

            # =========================================================
            # 🧠 USER SETTINGS (AI CONTROL)
            # =========================================================
            user_settings = UserSettings.objects.filter(user=request.user).first()
            use_ai = user_settings.use_ai if user_settings else True

            document.ai_used = use_ai

            # =========================================================
            # 🧠 STEP 1 — OCR
            # =========================================================
            text = extract_text(file_path)
            print("OCR TEXT:", text)

            document.extracted_text = text

            # =========================================================
            # 🧠 STEP 2 — RULE-BASED EXTRACTION
            # =========================================================
            structured_data = extract_structured_data(text)

            # =========================================================
            # 🧠 STEP 3 — CATEGORY CLASSIFICATION
            # =========================================================
            category, _ = classify_document(text)

            # =========================================================
            # 🧠 STEP 4 — VARIANT DETECTION
            # =========================================================
            variant, _ = detect_variant(text, category)

            if variant:
                document.variant_name = variant.name

            # =========================================================
            # 🤖 STEP 5 — AI FALLBACK (CONTROLLED)
            # =========================================================
            ai_data = {}

            try:
                if use_ai and (category == "Unknown" or len(structured_data) < 2):
                    print("Using AI fallback")

                    ai_data = ai_extract_fields(text)

                    if isinstance(ai_data, dict):
                        document.raw_ai_response = ai_data
            except Exception as e:
                print("AI ERROR:", str(e))

            # =========================================================
            # 🔀 STEP 6 — MERGE RULE + AI DATA
            # =========================================================
            final_data = structured_data.copy()

            if isinstance(ai_data, dict):
                for key, value in ai_data.items():
                    if key not in final_data or not final_data.get(key):
                        final_data[key] = value

            # =========================================================
            # 👤 STEP 7 — OWNER NAME EXTRACTION
            # =========================================================
            document.owner_name = final_data.get("name", "")

            # =========================================================
            # 🧠 STEP 8 — FINAL CATEGORY DECISION
            # =========================================================
            if category == "Unknown" and isinstance(ai_data, dict):
                document.suggested_category = ai_data.get("document_type", "")
            else:
                document.document_category = category

            # =========================================================
            # 👥 STEP 9 — RELATIONSHIP DEFAULT
            # =========================================================
            document.relationship = final_data.get("relationship", "self")

            # =========================================================
            # 📊 STEP 10 — CONFIDENCE SCORING
            # =========================================================
            confidence = 0

            if category != "Unknown":
                confidence += 0.4
            if final_data.get("pan_number"):
                confidence += 0.2
            if final_data.get("name"):
                confidence += 0.2
            if final_data.get("dob"):
                confidence += 0.1
            if variant:
                confidence += 0.1

            document.confidence_score = round(confidence, 2)

            # =========================================================
            # 🧠 STEP 11 — AI CONFIDENCE (SEPARATE TRACKING)
            # =========================================================
            ai_conf = 0

            if ai_data.get("pan_number"):
                ai_conf += 0.4
            if ai_data.get("name"):
                ai_conf += 0.3
            if ai_data.get("dob"):
                ai_conf += 0.3

            document.ai_confidence_score = ai_conf

            # =========================================================
            # 💾 STEP 12 — STORE SYSTEM OUTPUT (NO ENCRYPTION YET)
            # =========================================================
            document.extracted_data = final_data

            # =========================================================
            # ⏳ STEP 13 — WAITING FOR USER CONFIRMATION
            # =========================================================
            document.user_confirmation_status = 'pending'

            document.processing_status = 'completed'
            document.save()

            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("FULL ERROR:", str(e))
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================================================
# 📄 USER DOCUMENT LIST
# =========================================================
class UserDocumentListView(generics.ListAPIView):
    """
    Returns all documents belonging to logged-in user.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')


# =========================================================
# 🔍 DOCUMENT DETAIL
# =========================================================
class DocumentDetailView(generics.RetrieveAPIView):
    """
    Fetch single document details.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)


# =========================================================
# 🗑️ DELETE DOCUMENT
# =========================================================
class DocumentDeleteView(generics.DestroyAPIView):
    """
    Delete document owned by user.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)


# =========================================================
# ✏️ UPDATE DOCUMENT
# =========================================================
class DocumentUpdateView(generics.UpdateAPIView):
    """
    Update document metadata (not system-generated fields).
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)