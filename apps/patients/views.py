from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer

class PatientListCreateView(generics.ListCreateAPIView):
    """
    POST /api/patients/ - Add a new patient (Authenticated users only)
    GET /api/patients/ - Retrieve paginated patients created by the authenticated user
    Supports filtering by gender, search by name/contact, and ordering.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['gender']
    search_fields = ['name', 'contact_number', 'address']
    ordering_fields = ['name', 'age', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Patient.objects.none()
        if not self.request.user.is_authenticated:
            return Patient.objects.none()
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/ - Get details of a specific patient
    PUT /api/patients/<id>/ - Update patient details
    DELETE /api/patients/<id>/ - Soft-delete a patient record
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Patient.objects.none()
        if not self.request.user.is_authenticated:
            return Patient.objects.none()
        return Patient.objects.filter(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        patient.delete()
        return Response(
            {"message": f"Patient '{patient.name}' record deleted successfully."},
            status=status.HTTP_200_OK
        )
