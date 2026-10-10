from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model with validation.
    """
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'contact_number',
            'address',
            'medical_history',
            'created_by',
            'created_by_email',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Patient name cannot be blank.")
        return value.strip()

    def validate_age(self, value):
        if value <= 0 or value > 150:
            raise serializers.ValidationError("Age must be between 1 and 150.")
        return value

    def validate_contact_number(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Contact number cannot be blank.")
        return cleaned
