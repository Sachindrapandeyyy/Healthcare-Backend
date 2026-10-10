from django.db import models
from apps.common.models import SoftDeleteModel

class Doctor(SoftDeleteModel):
    """
    Doctor model storing medical practitioner information.
    Supports soft-deletion for medical staff retention compliance.
    """
    name = models.CharField(max_length=255, db_index=True)
    specialization = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=25)
    email = models.EmailField(unique=True, db_index=True)
    experience_years = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctors'
        ordering = ['name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
