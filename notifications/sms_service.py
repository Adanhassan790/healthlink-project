"""
SMS Service Module for HealthLink
Using Africa's Talking API for SMS delivery in Kenya

Setup Instructions:
1. Create an account at https://africastalking.com/
2. Get your API credentials from the dashboard
3. Add to your .env file:
   - AFRICASTALKING_USERNAME=your_username
   - AFRICASTALKING_API_KEY=your_api_key
   - SMS_SENDER_ID=HealthLink (or your approved sender ID)
4. For sandbox testing, use username='sandbox' and the sandbox API key
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Check if Africa's Talking is installed
try:
    import africastalking
    AT_AVAILABLE = True
except ImportError:
    AT_AVAILABLE = False
    logger.warning("Africa's Talking SDK not installed. Run: pip install africastalking")


class SMSService:
    """
    SMS Service using Africa's Talking API
    
    Usage:
        sms_service = SMSService()
        success, response = sms_service.send_sms("+254797123456", "Your message here")
    """
    
    def __init__(self):
        self.initialized = False
        self.sms = None
        
        if not AT_AVAILABLE:
            logger.error("Africa's Talking SDK not available")
            return
            
        # Get credentials from settings
        self.username = getattr(settings, 'AFRICASTALKING_USERNAME', None)
        self.api_key = getattr(settings, 'AFRICASTALKING_API_KEY', None)
        self.sender_id = getattr(settings, 'SMS_SENDER_ID', None)
        
        if not self.username or not self.api_key:
            logger.warning("Africa's Talking credentials not configured. SMS will not be sent.")
            return
        
        try:
            # Initialize the SDK
            africastalking.initialize(self.username, self.api_key)
            self.sms = africastalking.SMS
            self.initialized = True
            logger.info("Africa's Talking SMS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking: {e}")
    
    def format_phone_number(self, phone):
        """
        Format phone number to international format (+254...)
        
        Handles:
        - 0712345678 -> +254712345678
        - 254712345678 -> +254712345678
        - +254712345678 -> +254712345678
        - 0797123456 -> +254797123456
        """
        if not phone:
            return None
            
        # Remove any spaces, dashes, or parentheses
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Handle Kenyan numbers
        if phone.startswith('0') and len(phone) == 10:
            # Local format: 0712345678 -> +254712345678
            phone = '+254' + phone[1:]
        elif phone.startswith('254') and len(phone) == 12:
            # Without plus: 254712345678 -> +254712345678
            phone = '+' + phone
        elif phone.startswith('7') and len(phone) == 9:
            # Short format: 712345678 -> +254712345678
            phone = '+254' + phone
        elif not phone.startswith('+'):
            # Add plus if missing
            phone = '+' + phone
            
        return phone
    
    def send_sms(self, phone_number, message, sender_id=None):
        """
        Send an SMS message
        
        Args:
            phone_number: Recipient phone number (any format)
            message: Message content (max 160 chars for single SMS)
            sender_id: Optional sender ID (must be approved by Africa's Talking)
            
        Returns:
            tuple: (success: bool, response: dict or error message)
        """
        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        
        if not formatted_phone:
            return False, "Invalid phone number"
        
        if not self.initialized:
            logger.warning(f"SMS service not initialized. Would send to {formatted_phone}: {message}")
            # Log the SMS even if not sent (for testing/debugging)
            self._log_sms(formatted_phone, message, 'not_initialized', None)
            return False, "SMS service not initialized. Check configuration."
        
        try:
            # Use custom sender ID or default
            sender = sender_id or self.sender_id
            
            # Send the SMS
            if sender:
                response = self.sms.send(message, [formatted_phone], sender_id=sender)
            else:
                response = self.sms.send(message, [formatted_phone])
            
            # Log the SMS
            self._log_sms(formatted_phone, message, 'sent', response)
            
            logger.info(f"SMS sent successfully to {formatted_phone}")
            return True, response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send SMS to {formatted_phone}: {error_msg}")
            self._log_sms(formatted_phone, message, 'failed', {'error': error_msg})
            return False, error_msg
    
    def send_bulk_sms(self, phone_numbers, message, sender_id=None):
        """
        Send the same message to multiple recipients
        
        Args:
            phone_numbers: List of phone numbers
            message: Message content
            sender_id: Optional sender ID
            
        Returns:
            tuple: (success: bool, response: dict)
        """
        # Format all phone numbers
        formatted_numbers = []
        for phone in phone_numbers:
            formatted = self.format_phone_number(phone)
            if formatted:
                formatted_numbers.append(formatted)
        
        if not formatted_numbers:
            return False, "No valid phone numbers provided"
        
        if not self.initialized:
            logger.warning(f"SMS service not initialized. Would send to {formatted_numbers}")
            return False, "SMS service not initialized"
        
        try:
            sender = sender_id or self.sender_id
            
            if sender:
                response = self.sms.send(message, formatted_numbers, sender_id=sender)
            else:
                response = self.sms.send(message, formatted_numbers)
            
            # Log each SMS
            for phone in formatted_numbers:
                self._log_sms(phone, message, 'sent', response)
            
            return True, response
            
        except Exception as e:
            logger.error(f"Failed to send bulk SMS: {e}")
            return False, str(e)
    
    def _log_sms(self, phone, message, status, response):
        """Log SMS to database for tracking"""
        try:
            from .models import SMSLog
            SMSLog.objects.create(
                recipient_phone=phone,
                message=message[:500],  # Truncate if too long
                status=status,
                gateway_response=str(response) if response else None
            )
        except Exception as e:
            logger.error(f"Failed to log SMS: {e}")


# Singleton instance
_sms_service = None

def get_sms_service():
    """Get or create SMS service singleton"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service


# Convenience function for sending SMS
def send_sms(phone_number, message):
    """
    Convenience function to send an SMS
    
    Usage:
        from notifications.sms_service import send_sms
        success, response = send_sms("+254712345678", "Hello from HealthLink!")
    """
    service = get_sms_service()
    return service.send_sms(phone_number, message)


# ============================================================
# SMS NOTIFICATION TEMPLATES
# ============================================================

def send_appointment_booked_sms(patient_phone, doctor_name, appointment_date):
    """Send SMS when appointment is booked"""
    message = (
        f"HealthLink: Your appointment with Dr. {doctor_name} on "
        f"{appointment_date.strftime('%d/%m/%Y at %I:%M %p')} is pending. "
        f"Pay to confirm. Visit healthlink.co.ke"
    )
    return send_sms(patient_phone, message)


def send_appointment_confirmed_sms(patient_phone, doctor_name, appointment_date):
    """Send SMS when appointment is confirmed (after payment)"""
    message = (
        f"HealthLink: CONFIRMED! Your appointment with Dr. {doctor_name} on "
        f"{appointment_date.strftime('%d/%m/%Y at %I:%M %p')} is confirmed. "
        f"Don't forget!"
    )
    return send_sms(patient_phone, message)


def send_appointment_confirmed_to_doctor_sms(doctor_phone, patient_name, appointment_date):
    """Send SMS to doctor when appointment is confirmed"""
    message = (
        f"HealthLink: New confirmed appointment with {patient_name} on "
        f"{appointment_date.strftime('%d/%m/%Y at %I:%M %p')}. "
        f"Check dashboard for details."
    )
    return send_sms(doctor_phone, message)


def send_appointment_cancelled_sms(phone, other_party_name, appointment_date):
    """Send SMS when appointment is cancelled"""
    message = (
        f"HealthLink: Your appointment with {other_party_name} on "
        f"{appointment_date.strftime('%d/%m/%Y at %I:%M %p')} has been cancelled."
    )
    return send_sms(phone, message)


def send_appointment_reminder_sms(patient_phone, doctor_name, appointment_date):
    """Send reminder SMS 1 hour before appointment"""
    message = (
        f"HealthLink Reminder: Your appointment with Dr. {doctor_name} is in 1 hour "
        f"({appointment_date.strftime('%I:%M %p')}). Be ready!"
    )
    return send_sms(patient_phone, message)


def send_new_message_sms(recipient_phone, sender_name):
    """Send SMS when user receives a new message"""
    message = (
        f"HealthLink: New message from {sender_name}. "
        f"Login to view: healthlink.co.ke/messages"
    )
    return send_sms(recipient_phone, message)


def send_prescription_sms(patient_phone, doctor_name):
    """Send SMS when prescription is created"""
    message = (
        f"HealthLink: Dr. {doctor_name} has issued you a new prescription. "
        f"View at: healthlink.co.ke/prescriptions"
    )
    return send_sms(patient_phone, message)


def send_payment_received_sms(patient_phone, amount, mpesa_receipt):
    """Send SMS when payment is received"""
    message = (
        f"HealthLink: Payment of KES {amount} received. "
        f"M-Pesa Ref: {mpesa_receipt}. Your appointment is now confirmed."
    )
    return send_sms(patient_phone, message)


def send_video_call_sms(recipient_phone, caller_name):
    """Send SMS for incoming video call (if user is offline)"""
    message = (
        f"HealthLink: {caller_name} is calling you for a video consultation. "
        f"Open HealthLink to join."
    )
    return send_sms(recipient_phone, message)


def send_doctor_verification_sms(doctor_phone, status):
    """Send SMS when doctor verification status changes"""
    if status == 'verified':
        message = (
            "HealthLink: Congratulations! Your doctor profile has been verified. "
            "You can now receive patient appointments."
        )
    else:
        message = (
            "HealthLink: Your doctor verification was not successful. "
            "Please contact support for more information."
        )
    return send_sms(doctor_phone, message)
