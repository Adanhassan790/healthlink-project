from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Medication(models.Model):
    """Database of available medications"""
    FORM_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream/Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('patch', 'Patch'),
        ('suppository', 'Suppository'),
        ('powder', 'Powder'),
    ]
    
    CATEGORY_CHOICES = [
        ('antibiotic', 'Antibiotic'),
        ('painkiller', 'Painkiller/Analgesic'),
        ('antiinflammatory', 'Anti-inflammatory'),
        ('antiviral', 'Antiviral'),
        ('antifungal', 'Antifungal'),
        ('antihistamine', 'Antihistamine'),
        ('antidepressant', 'Antidepressant'),
        ('antihypertensive', 'Antihypertensive'),
        ('antidiabetic', 'Antidiabetic'),
        ('cardiovascular', 'Cardiovascular'),
        ('respiratory', 'Respiratory'),
        ('gastrointestinal', 'Gastrointestinal'),
        ('vitamin', 'Vitamin/Supplement'),
        ('hormone', 'Hormone'),
        ('sedative', 'Sedative/Sleep Aid'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    form = models.CharField(max_length=20, choices=FORM_CHOICES, default='tablet')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    strength = models.CharField(max_length=50, blank=True, help_text="e.g., 500mg, 10ml")
    manufacturer = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    requires_prescription = models.BooleanField(default=True)
    is_controlled = models.BooleanField(default=False, help_text="Controlled substance")
    common_side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        if self.strength:
            return f"{self.name} ({self.strength})"
        return self.name


class Prescription(models.Model):
    """Main prescription record"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('dispensed', 'Dispensed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    # Unique prescription number
    prescription_number = models.CharField(max_length=20, unique=True, editable=False)
    
    # Parties involved
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prescriptions_written',
        limit_choices_to={'user_type': 'doctor'}
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prescriptions_received',
        limit_choices_to={'user_type': 'patient'}
    )
    
    # Link to appointment (optional)
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions'
    )
    
    # Prescription details
    diagnosis = models.TextField(help_text="Patient diagnosis/condition")
    notes = models.TextField(blank=True, help_text="Additional notes for patient or pharmacist")
    
    # Status and dates
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid_until = models.DateField(help_text="Prescription validity date")
    dispensed_at = models.DateTimeField(null=True, blank=True)
    
    # Digital signature (simplified - could be enhanced with actual digital signatures)
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.prescription_number:
            # Generate unique prescription number: RX-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            random_suffix = uuid.uuid4().hex[:4].upper()
            self.prescription_number = f"RX-{today}-{random_suffix}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.prescription_number} - {self.patient.get_full_name()}"
    
    @property
    def is_valid(self):
        """Check if prescription is still valid"""
        return self.status == 'active' and self.valid_until >= timezone.now().date()
    
    @property
    def is_expired(self):
        """Check if prescription has expired"""
        return self.valid_until < timezone.now().date()
    
    def sign_prescription(self):
        """Doctor signs the prescription"""
        self.is_signed = True
        self.signed_at = timezone.now()
        self.status = 'active'
        self.save()
    
    def mark_dispensed(self):
        """Mark prescription as dispensed by pharmacy"""
        self.status = 'dispensed'
        self.dispensed_at = timezone.now()
        self.save()


class PrescriptionItem(models.Model):
    """Individual medication items in a prescription"""
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once daily'),
        ('twice_daily', 'Twice daily'),
        ('three_times_daily', 'Three times daily'),
        ('four_times_daily', 'Four times daily'),
        ('every_4_hours', 'Every 4 hours'),
        ('every_6_hours', 'Every 6 hours'),
        ('every_8_hours', 'Every 8 hours'),
        ('every_12_hours', 'Every 12 hours'),
        ('as_needed', 'As needed (PRN)'),
        ('once_weekly', 'Once weekly'),
        ('at_bedtime', 'At bedtime'),
        ('with_meals', 'With meals'),
        ('before_meals', 'Before meals'),
        ('after_meals', 'After meals'),
    ]
    
    DURATION_UNIT_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name='prescription_items'
    )
    
    # Dosage instructions
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet, 5ml, 2 puffs")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_value = models.PositiveIntegerField(help_text="Duration number")
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNIT_CHOICES, default='days')
    quantity = models.PositiveIntegerField(help_text="Total quantity to dispense")
    
    # Additional instructions
    special_instructions = models.TextField(blank=True, help_text="e.g., Take with food, Avoid sunlight")
    refills_allowed = models.PositiveIntegerField(default=0, help_text="Number of refills allowed")
    refills_remaining = models.PositiveIntegerField(default=0)
    
    # Substitution
    allow_generic = models.BooleanField(default=True, help_text="Allow generic substitution")
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.medication.name} - {self.dosage} {self.get_frequency_display()}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New item
            self.refills_remaining = self.refills_allowed
        super().save(*args, **kwargs)
    
    @property
    def full_instructions(self):
        """Generate full dosage instructions string"""
        instructions = f"Take {self.dosage} {self.get_frequency_display().lower()}"
        instructions += f" for {self.duration_value} {self.duration_unit}"
        if self.special_instructions:
            instructions += f". {self.special_instructions}"
        return instructions


class PrescriptionHistory(models.Model):
    """Track prescription status changes"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('signed', 'Signed by Doctor'),
        ('sent', 'Sent to Patient'),
        ('viewed', 'Viewed by Patient'),
        ('verified', 'Verified'),
        ('dispensed', 'Dispensed by Pharmacy'),
        ('refilled', 'Refilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Prescription histories'
    
    def __str__(self):
        return f"{self.prescription.prescription_number} - {self.get_action_display()}"
