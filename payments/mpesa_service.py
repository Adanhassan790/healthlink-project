import base64
import requests
from datetime import datetime
from django.utils import timezone
import json
from .mpesa_config import *
from .models import MpesaTransaction

def get_mpesa_access_token():
    """Get M-Pesa API access token"""
    try:
        response = requests.get(
            MPESA_AUTH_URL,
            auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET)
        )
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def generate_password():
    """Generate Lipa Na M-Pesa Online password"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = MPESA_BUSINESS_SHORTCODE + MPESA_PASSKEY + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode()).decode()
    return encoded_string, timestamp

def initiate_stk_push(phone_number, amount, appointment, account_reference="HEALTHLINK"):
    """Initiate STK Push to customer's phone"""
    try:
        # Format phone number (2547...)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        # Get access token
        access_token = get_mpesa_access_token()
        if not access_token:
            return None, "Failed to get access token"
        
        # Generate password
        password, timestamp = generate_password()
        
        # Prepare request payload
        payload = {
            "BusinessShortCode": 174379,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": 600981,
            "PartyB": 600000,
            "PhoneNumber": 254708374149,
            "CallBackURL": MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": f"HealthLink Consultation - {appointment.doctor.get_full_name()}"
        }
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            MPESA_STK_PUSH_URL,
            json=payload,
            headers=headers
        )
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
            return transaction, response_data.get('ResponseDescription', 'Failed to initiate payment')
            
    except Exception as e:
        print(f"Error initiating STK Push: {e}")
        return None, str(e)