"""
📦 documents/views.py

🧠 DOCUMENT PIPELINE (MODULAR AI ARCHITECTURE)

Flow:
Upload
→ OCR
→ Extraction
→ Validation
→ Field Confidence
→ AI Targeting
→ Classification
→ Variant Detection
→ Trust Routing
→ Response

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Clean architecture
✔ AI-ready
✔ Learning-ready
✔ Scalable pipeline
✔ Modular intelligence
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Document, DocumentReview
from .serializers import DocumentSerializer

from .review_engine import apply_review_outcome

import hashlib
import traceback

from .services import (
    extract_text,
    classify_document,
    extract_structured_data,
    detect_variant,
)

from .validation import validate_document_data
from .field_confidence import build_field_confidence


# =========================================================
# 📤 DOCUMENT UPLOAD PIPELINE
# =========================================================
class DocumentUploadView(generics.CreateAPIView):

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):

        try:

            # =====================================================
            # 📄 STEP 1 — FILE VALIDATION
            # =====================================================
            file = request.FILES.get("file")

            if not file:
                return Response(
                    {"error": "No file provided"},
                    status=400
                )

            # =====================================================
            # 🔒 STEP 2 — FILE HASH
            # =====================================================
            hasher = hashlib.sha256()

            for chunk in file.chunks():
                hasher.update(chunk)

            file_hash = hasher.hexdigest()

            # Duplicate detection
            if Document.objects.filter(
                owner=request.user,
                file_hash=file_hash
            ).exists():

                return Response(
                    {"error": "Duplicate document"},
                    status=400
                )

            # =====================================================
            # 💾 STEP 3 — INITIAL SAVE
            # =====================================================
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            document = serializer.save(
                owner=request.user,
                file_hash=file_hash
            )

            document.processing_status = "processing"
            document.save()

            # =====================================================
            # 🧠 STEP 4 — OCR
            # =====================================================
            file_path = document.file.path

            text = extract_text(file_path) or ""

            document.extracted_text = text
            document.save()

            # =====================================================
            # 🧠 STEP 5 — RULE EXTRACTION
            # =====================================================
            structured_data = extract_structured_data(text) or {}

            document.extracted_data = structured_data
            document.save()

            # =====================================================
            # 🧠 STEP 6 — VALIDATION ENGINE
            # =====================================================
            validate_document_data(document)

            # =====================================================
            # 🧠 STEP 7 — FIELD CONFIDENCE ENGINE
            # =====================================================
            print("\nCALLING FIELD CONFIDENCE ENGINE")

            from .field_confidence import build_field_confidence

            build_field_confidence(document)

            print("\nFIELD CONFIDENCE ENGINE FINISHED")
            print(document.extracted_data)

            # =====================================================
            # 🧠 STEP 8 — AI TARGETING ENGINE
            # =====================================================
            # run_ai_targeting(document)

            # =====================================================
            # 🧠 STEP 9 — DOCUMENT CLASSIFICATION
            # =====================================================
            category, category_confidence = classify_document(text)

            document.document_category = category

            # =====================================================
            # 🧠 STEP 10 — VARIANT DETECTION
            # =====================================================
            variant, _ = detect_variant(text, category)

            if variant:
                document.variant_name = variant.name

            print("\nDEBUG EXTRACTED DATA")
            print(document.extracted_data)
            print(type(document.extracted_data))

            # =====================================================
            # 👤 STEP 11 — OWNER NAME
            # =====================================================
            name_data = document.extracted_data.get("name", {})

            if isinstance(name_data, dict):
                document.owner_name = name_data.get("value", "")
            else:
                document.owner_name = str(name_data)

            # =====================================================
            # 👥 STEP 12 — RELATIONSHIP
            # =====================================================
            relationship_data = document.extracted_data.get("relationship", {})

            if isinstance(relationship_data, dict):
                document.relationship = relationship_data.get("value", "self")
            else:
                document.relationship = str(relationship_data or "self")

            # =====================================================
            # 🧠 STEP 13 — TRUST DECISION
            # =====================================================
            threshold = 0.85

            if document.confidence_score < threshold:

                document.required_reviewers = 1
                document.review_status = "under_review"

            else:

                document.required_reviewers = 0
                document.review_status = "user_confirmation_pending"

            # =====================================================
            # 📊 STEP 14 — FINAL STATUS
            # =====================================================
            document.user_confirmation_status = "pending"
            document.processing_status = "completed"

            document.save()

            # =====================================================
            # 🧹 STEP 15 — SANITIZE NULL JSON FIELDS
            # =====================================================
            if document.extracted_data is None:
                document.extracted_data = {}

            if document.raw_ai_response is None:
                document.raw_ai_response = {}

            if document.reviewed_data is None:
                document.reviewed_data = {}

            if document.user_corrected_data is None:
                document.user_corrected_data = {}

            document.save()

            # =====================================================
            # 📤 FINAL RESPONSE
            # =====================================================
            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            print("\nFULL TRACEBACK")
            traceback.print_exc()

            return Response(
                {
                    "error": "Something went wrong",
                    "details": str(e)
                },
                status=500
            )


# =========================================================
# 📄 USER DOCUMENT LIST
# =========================================================
class UserDocumentListView(generics.ListAPIView):

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        ).order_by("-created_at")


# =========================================================
# 🔍 DOCUMENT DETAIL
# =========================================================
class DocumentDetailView(generics.RetrieveAPIView):

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "id"

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        )


# =========================================================
# 🗑️ DOCUMENT DELETE
# =========================================================
class DocumentDeleteView(generics.DestroyAPIView):

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "id"

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        )


# =========================================================
# ✏️ DOCUMENT UPDATE
# =========================================================
class DocumentUpdateView(generics.UpdateAPIView):

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "id"

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        )


# =========================================================
# 🧠 USER CONFIRMATION
# =========================================================
class DocumentConfirmView(generics.UpdateAPIView):

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = "id"

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        )

    def update(self, request, *args, **kwargs):

        document = self.get_object()

        action = request.data.get("action")
        corrected_data = request.data.get("data", {})

        if action == "confirm":

            document.reviewed_data = document.extracted_data

        elif action == "correct":

            document.reviewed_data = corrected_data
            document.user_corrected_data = corrected_data

        else:

            return Response(
                {"error": "Invalid action"},
                status=400
            )

        document.user_confirmation_status = action
        document.is_verified = True

        document.save()

        from .learning import record_learning
        record_learning(document)

        return Response(
            DocumentSerializer(document).data
        )


# =========================================================
# 🧠 REVIEW ACTION
# =========================================================
class DocumentReviewActionView(generics.CreateAPIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):

        document = Document.objects.filter(id=id).first()

        if not document:

            return Response(
                {"error": "Document not found"},
                status=404
            )

        decision = request.data.get("decision")
        comments = request.data.get("comments", "")

        if decision not in ["approved", "rejected"]:

            return Response(
                {"error": "Invalid decision"},
                status=400
            )

        DocumentReview.objects.create(
            document=document,
            reviewer=request.user,
            decision=decision,
            comments=comments
        )

        # 🧠 APPLY REVIEW OUTCOME
        apply_review_outcome(document)

        return Response(
            {"message": "Review submitted"}
        )