from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer

class PatientListCreateView(generics.ListCreateAPIView):
    """
    POST /api/patients/ - Add a new patient (Authenticated users only)
    GET /api/patients/ - Retrieve all patients created by the authenticated user
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/ - Get details of a specific patient
    PUT /api/patients/<id>/ - Update patient details
    DELETE /api/patients/<id>/ - Delete a patient record
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        patient.delete()
        return Response(
            {"message": f"Patient '{patient.name}' deleted successfully."},
            status=status.HTTP_200_OK
        )
