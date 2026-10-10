from rest_framework import serializers
from .models import PatientDoctorMapping
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer

class PatientSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'age', 'gender', 'contact_number']


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for viewing patient-doctor mappings.
    """
    patient = PatientSummarySerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'assigned_date', 'notes']


class PatientDoctorMappingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for assigning a doctor to a patient.
    """
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'notes', 'assigned_date']
        read_only_fields = ['id', 'assigned_date']

    def validate(self, attrs):
        request = self.context.get('request')
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Verify patient ownership if request context is provided
        if request and hasattr(request, 'user') and not request.user.is_superuser:
            if patient.created_by != request.user:
                raise serializers.ValidationError({
                    'patient': 'You can only assign doctors to patients you created.'
                })

        # Check for duplicate assignment
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['This doctor is already assigned to this patient.']
            })

        return attrs
