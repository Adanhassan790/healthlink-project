from django.db import models
from users.models import CustomUser

class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class TriageSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    symptoms = models.ManyToManyField(Symptom)
    additional_notes = models.TextField(blank=True)
    predicted_specialty = models.CharField(max_length=100)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Triage for {self.user.username if self.user else 'Anonymous'} - {self.predicted_specialty}"

class Disease(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    common_symptoms = models.ManyToManyField(Symptom)
    
    def __str__(self):
        return self.name