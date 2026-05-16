from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
import hashlib


class DocumentUploadView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]  # keep simple for now

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user, file_hash=file_hash)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserDocumentListView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user).order_by('-created_at')

class DocumentDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'   # ✅ ADD THIS

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)


