"""
📦 documents/views.py

This module handles all API endpoints related to document lifecycle.

🧠 CORE FLOW (UPLOAD PIPELINE ONLY):
Upload → OCR → Extraction → Classification → Confidence → Store

🚨 IMPORTANT:
This layer DOES NOT:
- Call AI
- Make intelligence decisions
- Perform learning

Those belong to:
→ intelligence layer (separate)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .intelligence.engine import process_document_intelligence

import hashlib

from .services import (
    extract_text,
    classify_document,
    extract_structured_data,
    detect_variant,
)


# =========================================================
# 📤 DOCUMENT UPLOAD + PROCESSING (PURE INGESTION)
# =========================================================
class DocumentUploadView(generics.CreateAPIView):
    """
    Handles document upload and base processing.

    🎯 RESPONSIBILITY:
    - File validation
    - Duplicate detection
    - OCR extraction
    - Rule-based parsing
    - Classification
    - Basic confidence scoring

    ❌ DOES NOT:
    - Use AI
    - Perform learning
    - Apply encryption
    """

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # =========================================================
            # 📄 STEP 1 — INPUT VALIDATION
            # =========================================================
            file = request.FILES.get('file')

            if not file:
                return Response(
                    {"error": "No file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # =========================================================
            # 🔒 STEP 2 — DUPLICATE DETECTION (HASH)
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
            # 💾 STEP 3 — INITIAL SAVE
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
            # 🧠 STEP 4 — OCR EXTRACTION
            # =========================================================
            text = extract_text(file_path)
            print("OCR TEXT:", text)

            document.extracted_text = text

            # =========================================================
            # 🧠 STEP 5 — RULE-BASED DATA EXTRACTION
            # =========================================================
            structured_data = extract_structured_data(text)

            # =========================================================
            # 🧠 STEP 6 — DOCUMENT CLASSIFICATION
            # =========================================================
            category, _ = classify_document(text)

            # =========================================================
            # 🧠 STEP 7 — VARIANT DETECTION
            # =========================================================
            variant, _ = detect_variant(text, category)

            if variant:
                document.variant_name = variant.name

            # =========================================================
            # 🔀 STEP 8 — FINAL STRUCTURED DATA (NO AI)
            # =========================================================
            final_data = structured_data.copy()

            # =========================================================
            # 👤 STEP 9 — OWNER NAME EXTRACTION
            # =========================================================
            document.owner_name = final_data.get("name", "")

            # =========================================================
            # 🧠 STEP 10 — CATEGORY ASSIGNMENT
            # =========================================================
            document.document_category = category

            # =========================================================
            # 👥 STEP 11 — RELATIONSHIP DEFAULT
            # =========================================================
            document.relationship = final_data.get("relationship", "self")

            # =========================================================
            # 📊 STEP 12 — BASIC CONFIDENCE SCORING
            # =========================================================
            confidence = 0

            if category != "Unknown":
                confidence += 0.5

            if final_data.get("pan_number"):
                confidence += 0.2

            if final_data.get("name"):
                confidence += 0.2

            if final_data.get("dob"):
                confidence += 0.1

            document.confidence_score = round(confidence, 2)

            # =========================================================
            # 💾 STEP 13 — STORE OUTPUT
            # =========================================================
            document.extracted_data = final_data

            # =========================================================
            # ⏳ STEP 14 — INITIAL STATUS
            # =========================================================
            document.user_confirmation_status = 'pending'
            document.processing_status = 'completed'

            document.save()

            # =========================================================
            # 🔥 STEP 15 — INTELLIGENCE LAYER (POST PROCESSING)
            # =========================================================
            process_document_intelligence(document)

            # =========================================================
            # 📤 FINAL RESPONSE
            # =========================================================
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