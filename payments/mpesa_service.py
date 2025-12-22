import base64
import requests
from datetime import datetime
from django.conf import settings
from .models import MpesaTransaction
import json

def get_mpesa_access_token():
    """Get M-Pesa API access token with detailed debugging"""
    try:
        # Get credentials directly from settings
        consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        
        print(f"🔑 Attempting authentication with Consumer Key: {consumer_key}")
        print(f"🔑 Consumer Secret starts with: {consumer_secret[:10]}...")
        
        auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        response = requests.get(auth_url, auth=(consumer_key, consumer_secret), timeout=30)
        
        print(f"📡 Auth Response Status: {response.status_code}")
        print(f"📡 Auth Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            print(f"✅ SUCCESS: Access token received: {access_token[:20]}...")
            return access_token
        else:
            print(f"❌ FAILED: Auth failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR in get_mpesa_access_token: {e}")
        return None

def generate_password():
    """Generate Lipa Na M-Pesa Online password"""
    try:
        shortcode = getattr(settings, 'MPESA_BUSINESS_SHORTCODE', '174379')
        passkey = getattr(settings, 'MPESA_PASSKEY', '')
        
        print(f"🔐 Generating password with Shortcode: {shortcode}")
        print(f"🔐 Passkey starts with: {passkey[:10]}...")
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = str(shortcode) + passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode()).decode()
        
        print(f"✅ Password generated successfully with timestamp: {timestamp}")
        return encoded_string, timestamp
        
    except Exception as e:
        print(f"❌ ERROR in generate_password: {e}")
        return None, None

def initiate_stk_push(phone_number, amount, appointment, account_reference="HEALTHLINK"):
    """Initiate STK Push to customer's phone"""
    try:
        # Format phone number (2547...)
        original_phone = phone_number
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        print(f"📱 Phone number formatted: {original_phone} -> {phone_number}")
        print(f"💰 Amount: {amount}")
        
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
        
        print(f"🔗 Callback URL: {callback_url}")
        print(f"🏢 Business Shortcode: {shortcode}")
        
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
        
        print(f"📦 STK Push Payload: {json.dumps(payload, indent=2)}")
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_url, json=payload, headers=headers, timeout=30)
        
        print(f"📡 STK Push Response Status: {response.status_code}")
        print(f"📡 STK Push Response: {response.text}")
        
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
            print("✅ STK Push initiated successfully!")
            return transaction, "STK Push initiated successfully"
        else:
            transaction.status = 'failed'
            transaction.result_description = response_data.get('ResponseDescription', 'Unknown error')
            transaction.save()
            error_msg = response_data.get('ResponseDescription', 'Failed to initiate payment')
            print(f"❌ STK Push failed: {error_msg}")
            return transaction, error_msg
            
    except Exception as e:
        print(f"❌ ERROR in initiate_stk_push: {e}")
        return None, str(e)