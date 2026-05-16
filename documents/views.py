from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
import hashlib

from .services import (
    extract_text,
    classify_document,
    extract_structured_data,
    detect_variant
)


class DocumentUploadView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file')

            if not file:
                return Response(
                    {"error": "No file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 🔒 Hash
            hasher = hashlib.sha256()
            for chunk in file.chunks():
                hasher.update(chunk)
            file_hash = hasher.hexdigest()

            # 🚫 Duplicate
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

            # 💾 Save
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            document = serializer.save(owner=request.user, file_hash=file_hash)

            document.processing_status = 'processing'
            document.save()

            file_path = document.file.path

            # ===============================
            # OCR
            # ===============================
            text = extract_text(file_path)
            print("OCR TEXT:", text)

            document.extracted_text = text

            # ===============================
            # RULE EXTRACTION
            # ===============================
            structured_data = extract_structured_data(text)

            # ===============================
            # CATEGORY
            # ===============================
            category, _ = classify_document(text)

            # ===============================
            # VARIANT
            # ===============================
            variant, _ = detect_variant(text, category)

            if variant:
                document.variant_name = variant.name

            # ===============================
            # AI FALLBACK (SAFE)
            # ===============================
            from .services import ai_extract_fields

            ai_data = {}

            try:
                if category == "Unknown" or len(structured_data) < 2:
                    print("⚠️ Using AI fallback")
                    ai_data = ai_extract_fields(text)

                    if isinstance(ai_data, dict):
                        document.raw_ai_response = ai_data
            except Exception as e:
                print("AI ERROR:", str(e))

            # ===============================
            # MERGE
            # ===============================
            final_data = structured_data.copy()

            if isinstance(ai_data, dict):
                for key, value in ai_data.items():
                    if key not in final_data or not final_data.get(key):
                        final_data[key] = value

            # ===============================
            # OWNER NAME
            # ===============================
            document.owner_name = final_data.get("name", "")

            # ===============================
            # CATEGORY FINAL
            # ===============================
            if category == "Unknown" and isinstance(ai_data, dict):
                document.suggested_category = ai_data.get("document_type", "")
            else:
                document.document_category = category

            # ===============================
            # DEFAULT RELATION
            # ===============================
            document.belongs_to = document.owner.username

            # ===============================
            # CONFIDENCE
            # ===============================
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

            # ===============================
            # SAVE
            # ===============================
            document.extracted_data = final_data
            document.processing_status = 'completed'
            document.save()

            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("🚨 FULL ERROR:", str(e))
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserDocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by('-created_at')


class DocumentDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)


class DocumentDeleteView(generics.DestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)


class DocumentUpdateView(generics.UpdateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)