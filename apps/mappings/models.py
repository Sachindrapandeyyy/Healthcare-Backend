from django.db import models

class PatientDoctorMapping(models.Model):
    """
    Mapping model linking a Patient to an assigned Doctor.
    """
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='doctor_mappings'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='patient_mappings'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'patient_doctor_mappings'
        unique_together = ('patient', 'doctor')
        ordering = ['-assigned_date']
        verbose_name = 'Patient-Doctor Mapping'
        verbose_name_plural = 'Patient-Doctor Mappings'

    def __str__(self):
        return f"{self.patient.name} -> Dr. {self.doctor.name}"
