"""
📦 identiflow_backend/urls.py

🧠 CENTRAL ROUTING CONFIGURATION

Defines all entry points into the backend system.

🌐 ROUTES OVERVIEW:

/                → Health check (optional, for sanity)
/admin/          → Django admin panel
/api/documents/  → Document APIs
/api/token/      → JWT login
/api/docs/       → Swagger UI (API testing)
/media/          → Uploaded files (dev only)

🎯 DESIGN PRINCIPLE:
Backend-first architecture → No frontend routes here
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import JsonResponse

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


# =========================================================
# 🏠 OPTIONAL HEALTH CHECK ENDPOINT
# =========================================================
def home(request):
    """
    Simple endpoint to confirm API is running.

    Useful for:
    - debugging
    - uptime checks
    - avoiding 404 confusion
    """
    return JsonResponse({
        "status": "IdentiFlow API is running",
        "version": "v1"
    })


# =========================================================
# 🌐 URL ROUTES
# =========================================================
urlpatterns = [

    # -----------------------------------------------------
    # 🏠 ROOT (OPTIONAL BUT RECOMMENDED)
    # -----------------------------------------------------
    path('', home),

    # -----------------------------------------------------
    # 🛠️ ADMIN PANEL
    # -----------------------------------------------------
    path('admin/', admin.site.urls),

    # -----------------------------------------------------
    # 📄 DOCUMENT APIs
    # -----------------------------------------------------
    path('api/documents/', include('documents.urls')),

    # -----------------------------------------------------
    # 🔐 AUTH (JWT)
    # -----------------------------------------------------
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # -----------------------------------------------------
    # 📊 API DOCUMENTATION
    # -----------------------------------------------------
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]


# =========================================================
# 📁 MEDIA FILES (DEV ONLY)
# =========================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)