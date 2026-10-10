from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from apps.common.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health & Diagnostics
    path('api/health/', HealthCheckView.as_view(), name='health-check'),

    # OpenAPI 3.0 Documentation & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Application APIs
    path('api/auth/', include('apps.accounts.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('api/doctors/', include('apps.doctors.urls')),
    path('api/mappings/', include('apps.mappings.urls')),
]
