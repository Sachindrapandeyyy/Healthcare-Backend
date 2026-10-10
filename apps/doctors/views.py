from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer

class DoctorListCreateView(generics.ListCreateAPIView):
    """
    POST /api/doctors/ - Add a new doctor (Authenticated users only)
    GET /api/doctors/ - Retrieve paginated directory of all doctors
    Supports filtering by specialization, search by name/specialization/email, and ordering.
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['specialization']
    search_fields = ['name', 'specialization', 'email', 'phone']
    ordering_fields = ['name', 'experience_years', 'created_at']
    ordering = ['name']


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/ - Get details of a specific doctor
    PUT /api/doctors/<id>/ - Update doctor details
    DELETE /api/doctors/<id>/ - Soft-delete a doctor record
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        doctor = self.get_object()
        doctor.delete()
        return Response(
            {"message": f"Doctor '{doctor.name}' record deleted successfully."},
            status=status.HTTP_200_OK
        )
