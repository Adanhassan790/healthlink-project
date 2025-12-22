from django.db import models
from users.models import CustomUser
from django.conf import settings


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    category = models.CharField(
        max_length=50, 
        choices=[
            ('general', 'General'),
            ('pain', 'Pain'),
            ('fever', 'Fever/Infection'),
            ('respiratory', 'Respiratory'),
            ('digestive', 'Digestive'),
            ('neurological', 'Neurological'),
            ('skin', 'Skin'),
            ('mental', 'Mental Health'),
            ('cardiac', 'Cardiac'),
        ],
        default='general'
    )
    body_part = models.CharField(max_length=100, blank=True, default='')
    severity_options = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.name


class Disease(models.Model):  
    name = models.CharField(max_length=100, default='')
    specialty = models.CharField(max_length=100, default='General Medicine')
    common_symptoms = models.ManyToManyField(Symptom, related_name='diseases', blank=True)
    
    def __str__(self):
        return self.name


class SymptomChoice(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='')
    
    def __str__(self):
        return f"{self.symptom.name}: {self.description}"


class TriageSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_type = models.CharField(
        max_length=20, 
        choices=[
            ('form', 'Form-based'),
            ('chat', 'Chat-based')
        ],
        default='form'
    )
    selected_symptoms = models.ManyToManyField('SymptomChoice', blank=True)
    symptom_details = models.JSONField(default=dict, blank=True)
    additional_notes = models.TextField(blank=True, default='')
    predicted_specialty = models.CharField(max_length=100, default='General Medicine')
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    conversation_history = models.JSONField(default=list, blank=True)
    
    # ✅ FIXED: Because this model is inside the symptoms app
    symptoms = models.ManyToManyField('Symptom', related_name='triage_sessions', blank=True)

    def __str__(self):
        if self.user:
            return f"Triage: {self.user.username} - {self.predicted_specialty}"
        return f"Triage: Anonymous - {self.predicted_specialty}"
    
    
from django.db import models
from django.conf import settings


class SavedAssessment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_assessments'
    )
    predicted_specialty = models.CharField(max_length=100)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    symptoms_text = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.predicted_specialty} ({self.confidence}%)"

    class Meta:
        ordering = ['-created_at']
