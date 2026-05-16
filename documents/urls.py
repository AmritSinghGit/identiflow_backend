from django.urls import path
from .views import (
    DocumentUploadView,
    UserDocumentListView,
    DocumentDetailView,
    DocumentDeleteView,
    DocumentUpdateView
)

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('', UserDocumentListView.as_view(), name='document-list'),
    path('<uuid:id>/', DocumentDetailView.as_view(), name='document-detail'),
    path('<uuid:id>/delete/', DocumentDeleteView.as_view(), name='document-delete'),
    path('<uuid:id>/update/', DocumentUpdateView.as_view(), name='document-update'),
]