from django.db import models
from django.conf import settings
from apps.common.models import SoftDeleteModel

class Patient(SoftDeleteModel):
    """
    Patient model associated with the user who created the record.
    Supports soft-deletion for healthcare audit compliance.
    """
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    name = models.CharField(max_length=255, db_index=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=25, db_index=True)
    address = models.TextField()
    medical_history = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.name} (Age: {self.age})"
