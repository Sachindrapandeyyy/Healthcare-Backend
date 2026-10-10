from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor model with validation.
    """
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'phone',
            'email',
            'experience_years',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return value.strip()

    def validate_specialization(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Specialization cannot be blank.")
        return value.strip()

    def validate_email(self, value):
        cleaned_email = value.lower().strip()
        instance = getattr(self, 'instance', None)
        query = Doctor.objects.filter(email__iexact=cleaned_email)
        if instance:
            query = query.exclude(pk=instance.pk)
        if query.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return cleaned_email

    def validate_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError("Experience years cannot be negative.")
        return value
