import base64
import requests
from datetime import datetime
from django.conf import settings
from .models import MpesaTransaction
import json


def _mpesa_base_url():
    env = str(getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')).strip().lower()
    if env == 'production':
        return 'https://api.safaricom.co.ke'
    return 'https://sandbox.safaricom.co.ke'


def _format_phone_number(phone_number):
    phone_number = str(phone_number or '').strip()
    if phone_number.startswith('0'):
        return '254' + phone_number[1:]
    if phone_number.startswith('+'):
        return phone_number[1:]
    return phone_number

def get_mpesa_access_token():
    """Get M-Pesa API access token with detailed debugging"""
    try:
        # Get credentials directly from settings
        consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')

        if not consumer_key or not consumer_secret:
            return None

        auth_url = f"{_mpesa_base_url()}/oauth/v1/generate?grant_type=client_credentials"
        
        response = requests.get(auth_url, auth=(consumer_key, consumer_secret), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            return access_token
        else:
            return None
            
    except Exception as e:
        print(f"M-Pesa auth error: {e}")
        return None

def generate_password():
    """Generate Lipa Na M-Pesa Online password"""
    try:
        shortcode = getattr(settings, 'MPESA_BUSINESS_SHORTCODE', '174379')
        passkey = getattr(settings, 'MPESA_PASSKEY', '')
        
        if not shortcode or not passkey:
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = str(shortcode) + passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode()).decode()
        
        return encoded_string, timestamp
        
    except Exception as e:
        print(f"M-Pesa password generation error: {e}")
        return None, None

def initiate_stk_push(phone_number, amount, appointment, account_reference="HEALTHLINK"):
    """Initiate STK Push to customer's phone"""
    try:
        # Format phone number (2547...)
        phone_number = _format_phone_number(phone_number)
        
        # Get access token
        access_token = get_mpesa_access_token()
        if not access_token:
            return None, "Failed to get access token from M-Pesa API"
        
        # Generate password
        password, timestamp = generate_password()
        if not password:
            return None, "Failed to generate security password"
        
        # Get configuration from settings
        shortcode = getattr(settings, 'MPESA_BUSINESS_SHORTCODE', '174379')
        callback_url = getattr(settings, 'MPESA_CALLBACK_URL', '')

        if not callback_url:
            return None, "MPESA_CALLBACK_URL is missing"
        
        # Prepare request payload
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": f"HealthLink Consultation"
        }
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        stk_url = f"{_mpesa_base_url()}/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_url, json=payload, headers=headers, timeout=30)
        
        response_data = response.json()
        
        # Create transaction record
        transaction = MpesaTransaction.objects.create(
            appointment=appointment,
            user=appointment.patient,
            amount=amount,
            phone_number=phone_number,
            checkout_request_id=response_data.get('CheckoutRequestID', ''),
            merchant_request_id=response_data.get('MerchantRequestID', ''),
            status='pending'
        )
        
        if response_data.get('ResponseCode') == '0':
            return transaction, "STK Push initiated successfully"
        else:
            transaction.status = 'failed'
            transaction.result_description = response_data.get('ResponseDescription', 'Unknown error')
            transaction.save()
            error_msg = response_data.get('ResponseDescription', 'Failed to initiate payment')
            return transaction, error_msg
            
    except Exception as e:
        print(f"M-Pesa STK push error: {e}")
        return None, str(e)