from django.urls import path
from .views import DocumentUploadView, UserDocumentListView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('', UserDocumentListView.as_view(), name='document-list'),
]