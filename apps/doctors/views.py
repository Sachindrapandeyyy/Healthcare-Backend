from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Doctor
from .serializers import DoctorSerializer

class DoctorListCreateView(generics.ListCreateAPIView):
    """
    POST /api/doctors/ - Add a new doctor (Authenticated users only)
    GET /api/doctors/ - Retrieve all doctors
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/ - Get details of a specific doctor
    PUT /api/doctors/<id>/ - Update doctor details
    DELETE /api/doctors/<id>/ - Delete a doctor record
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        doctor = self.get_object()
        doctor.delete()
        return Response(
            {"message": f"Doctor '{doctor.name}' deleted successfully."},
            status=status.HTTP_200_OK
        )
