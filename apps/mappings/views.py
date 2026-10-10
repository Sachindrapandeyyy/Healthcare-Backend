from rest_framework import status, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from .models import PatientDoctorMapping
from apps.patients.models import Patient
from .serializers import (
    PatientDoctorMappingSerializer,
    PatientDoctorMappingCreateSerializer
)

class MappingListCreateView(APIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient
    GET /api/mappings/ - Retrieve all patient-doctor mappings
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PatientDoctorMappingCreateSerializer

    @extend_schema(
        operation_id="mappings_list_all",
        summary="List all patient-doctor mappings",
        description="Retrieves all active patient-doctor mappings belonging to the user's patients.",
        responses={200: PatientDoctorMappingSerializer(many=True)}
    )
    def get(self, request):
        if request.user.is_superuser:
            mappings = PatientDoctorMapping.objects.all().select_related('patient', 'doctor')
        else:
            mappings = PatientDoctorMapping.objects.filter(
                patient__created_by=request.user
            ).select_related('patient', 'doctor')

        serializer = PatientDoctorMappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="mappings_create",
        summary="Assign doctor to patient",
        description="Creates an assignment mapping between a doctor and a patient created by the current user.",
        request=PatientDoctorMappingCreateSerializer,
        responses={201: PatientDoctorMappingSerializer}
    )
    def post(self, request):
        serializer = PatientDoctorMappingCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        mapping = serializer.save()
        return Response(
            PatientDoctorMappingSerializer(mapping).data,
            status=status.HTTP_201_CREATED
        )


class MappingDetailDeleteView(APIView):
    """
    GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient
    DELETE /api/mappings/<id>/ - Remove a doctor from a patient (by mapping id or patient id + doctor_id)
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        operation_id="mappings_get_doctors_by_patient",
        summary="Get doctors assigned to patient",
        description="Retrieves all doctor assignments for a specified patient ID.",
        responses={200: PatientDoctorMappingSerializer(many=True)}
    )
    def get(self, request, id):
        """
        Retrieve all doctors assigned to the specified patient.
        """
        try:
            if request.user.is_superuser:
                patient = Patient.objects.get(id=id)
            else:
                patient = Patient.objects.get(id=id, created_by=request.user)
        except Patient.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_404_NOT_FOUND,
                    'error': f"Patient with ID {id} not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor', 'patient')
        serializer = PatientDoctorMappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="mappings_remove_doctor",
        summary="Remove doctor assignment",
        description="Deletes or unassigns a mapping by mapping ID.",
        responses={200: inline_serializer(
            name='MappingDeleteResponse',
            fields={'message': serializers.CharField()}
        )}
    )
    def delete(self, request, id):
        """
        Delete a mapping. Checks for mapping id first, then patient id + doctor_id.
        """
        mapping_query = PatientDoctorMapping.objects.filter(id=id)
        if not request.user.is_superuser:
            mapping_query = mapping_query.filter(patient__created_by=request.user)
        mapping_obj = mapping_query.first()

        if not mapping_obj:
            doctor_id = request.query_params.get('doctor_id') or request.data.get('doctor_id')
            if doctor_id:
                fallback_query = PatientDoctorMapping.objects.filter(patient_id=id, doctor_id=doctor_id)
                if not request.user.is_superuser:
                    fallback_query = fallback_query.filter(patient__created_by=request.user)
                mapping_obj = fallback_query.first()

        if not mapping_obj:
            return Response(
                {
                    'success': False,
                    'status_code': status.HTTP_404_NOT_FOUND,
                    'error': f"Mapping with ID {id} not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        mapping_obj.delete()
        return Response(
            {'message': 'Doctor removed from patient successfully.'},
            status=status.HTTP_200_OK
        )
