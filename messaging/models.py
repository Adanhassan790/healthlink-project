from django.db import models
from django.contrib.auth import get_user_model
from appointments.models import Appointment
import uuid

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


class VideoCall(models.Model):
    """Model to track video calls between doctor and patient"""
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('ongoing', 'Ongoing'),
        ('ended', 'Ended'),
        ('missed', 'Missed'),
        ('declined', 'Declined'),
    ]
    
    # Unique room ID for the call
    room_id = models.CharField(max_length=100, unique=True, editable=False)
    
    # Vonage Video API session ID
    vonage_session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    # Participants
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='video_calls')
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_made')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_received')
    
    # Call details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    started_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Peer IDs for WebRTC connection
    caller_peer_id = models.CharField(max_length=100, null=True, blank=True)
    receiver_peer_id = models.CharField(max_length=100, null=True, blank=True)
    
    # WebRTC Signaling Data - stored as JSON strings
    caller_offer = models.TextField(null=True, blank=True)  # SDP offer from caller
    receiver_answer = models.TextField(null=True, blank=True)  # SDP answer from receiver
    caller_ice_candidates = models.TextField(null=True, blank=True)  # JSON array of ICE candidates
    receiver_ice_candidates = models.TextField(null=True, blank=True)  # JSON array of ICE candidates
    
    # Call recording
    recording_enabled = models.BooleanField(default=False)  # Whether call was recorded
    recording_url = models.URLField(null=True, blank=True)  # URL to recorded call (if available)
    
    # Call duration in seconds
    duration = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-started_at']
    
    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = f"hl-call-{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Call {self.room_id} - {self.caller} to {self.receiver}"
    
    @property
    def duration_formatted(self):
        """Return duration as mm:ss format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"