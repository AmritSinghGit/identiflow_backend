from rest_framework import generics, permissions
from .models import Document
from .serializers import DocumentSerializer
import hashlib


class DocumentUploadView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')

        hasher = hashlib.sha256()
        for chunk in file.chunks():
            hasher.update(chunk)

        file_hash = hasher.hexdigest()

        serializer.save(owner=self.request.user, file_hash=file_hash)