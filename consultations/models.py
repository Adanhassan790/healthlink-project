from django.db import models
from users.models import CustomUser
from appointments.models import Appointment

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'doctor'},
        related_name='doctor_consultations'  # Add this
    )
    patient = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'patient'},
        related_name='patient_consultations'  # Add this
    )
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Consultation: {self.patient.username} with Dr. {self.doctor.username}"

class MedicalRecord(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='medical_records')
    record_type = models.CharField(max_length=50)  # lab_result, xray, etc.
    file = models.FileField(upload_to='medical_records/', blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.record_type} - {self.consultation.patient.username}"