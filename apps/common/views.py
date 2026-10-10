from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status, serializers
from django.db import connection
from drf_spectacular.utils import extend_schema, inline_serializer

class HealthCheckView(APIView):
    """
    GET /api/health/
    Health check endpoint for Kubernetes, Docker, and Load Balancers.
    Verifies service availability and database connectivity.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Service Health Check",
        description="Public health check probe verifying API and database operational status.",
        responses={200: inline_serializer(
            name='HealthCheckResponse',
            fields={
                'status': serializers.CharField(),
                'database': serializers.CharField(),
                'service': serializers.CharField(),
                'version': serializers.CharField(),
            }
        )}
    )
    def get(self, request):
        db_status = "connected"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            db_status = f"error: {str(e)}"
            return Response({
                "status": "degraded",
                "database": db_status
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({
            "status": "healthy",
            "database": db_status,
            "service": "Healthcare Backend API",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)
