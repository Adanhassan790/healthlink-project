from django.db import models
from django.contrib.auth import get_user_model
from appointments.models import Appointment

User = get_user_model()

class Conversation(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_conversations')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_conversations')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['patient', 'doctor', 'appointment']
    
    def __str__(self):
        return f"Conversation: {self.patient.username} & Dr. {self.doctor.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"