import os
from django.conf import settings

# M-Pesa Daraja API Configuration
MPESA_ENVIRONMENT = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')  # or 'production'

# Sandbox Credentials (You'll get these from developer.safaricom.co.ke)
MPESA_CONSUMER_KEY = getattr(settings, 'MPESA_CONSUMER_KEY', 'your_consumer_key_here')
MPESA_CONSUMER_SECRET = getattr(settings, 'MPESA_CONSUMER_SECRET', 'your_consumer_secret_here')

# Business Shortcode (Paybill or Till Number)
MPESA_BUSINESS_SHORTCODE = getattr(settings, 'MPESA_BUSINESS_SHORTCODE', '174379')  # Sandbox: 174379

# Lipa Na M-Pesa Online Passkey
MPESA_PASSKEY = getattr(settings, 'MPESA_PASSKEY', 'your_passkey_here')

# API URLs
if MPESA_ENVIRONMENT == 'production':
    MPESA_BASE_URL = 'https://api.safaricom.co.ke'
else:
    MPESA_BASE_URL = 'https://sandbox.safaricom.co.ke'

MPESA_AUTH_URL = f"{MPESA_BASE_URL}/oauth/v1/generate"
MPESA_STK_PUSH_URL = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"

# Callback URL (You'll need to set up ngrok for local development)
MPESA_CALLBACK_URL = getattr(settings, 'MPESA_CALLBACK_URL', 'https://your-domain.com/mpesa/callback/')