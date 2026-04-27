#!/usr/bin/env python
"""
Vonage Credentials Diagnostic Tool
Run this to diagnose Vonage video call issues
Usage: python diagnose_vonage.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthlink.settings')
django.setup()

print("\n" + "="*70)
print("VONAGE CREDENTIALS DIAGNOSTIC")
print("="*70 + "\n")

# Check 1: Environment Variables
print("1. Checking Environment Variables")
print("-" * 70)

vonage_api_key = os.getenv('VONAGE_API_KEY')
vonage_api_secret = os.getenv('VONAGE_API_SECRET')

if vonage_api_key:
    print(f"   [OK] VONAGE_API_KEY found (length: {len(vonage_api_key)})")
    print(f"        First 10 chars: {vonage_api_key[:10]}")
else:
    print(f"   [ERROR] VONAGE_API_KEY not set")

if vonage_api_secret:
    print(f"   [OK] VONAGE_API_SECRET found (length: {len(vonage_api_secret)})")
    print(f"         First 10 chars: {vonage_api_secret[:10]}")
else:
    print(f"   [ERROR] VONAGE_API_SECRET not set")

# Check 2: opentok Package
print("\n2. Checking opentok Package")
print("-" * 70)

try:
    import opentok
    print(f"   [OK] opentok package installed")
    try:
        print(f"        Version: {opentok.__version__}")
    except:
        print(f"        Version: unknown")
except ImportError as e:
    print(f"   [ERROR] opentok not installed: {e}")
    print(f"           Fix: pip install opentok==3.13.0")

# Check 3: Vonage Service Initialization
print("\n3. Checking Vonage Service Initialization")
print("-" * 70)

try:
    from messaging.vonage_service import ot, create_session, generate_token, get_api_key
    
    if ot:
        print(f"   [OK] Vonage OpenTok initialized successfully")
        
        # Try to test session creation
        print("\n4. Testing Session Creation")
        print("-" * 70)
        try:
            session_id = create_session()
            print(f"   [OK] Successfully created Vonage session")
            print(f"        Session ID: {session_id}")
            
            # Try to generate token
            try:
                token = generate_token(session_id, user_id='test_user')
                print(f"   [OK] Successfully generated token")
                print(f"        Token (first 30 chars): {token[:30]}...")
            except Exception as e:
                print(f"   [ERROR] Failed to generate token: {e}")
        except Exception as e:
            print(f"   [ERROR] Failed to create session: {e}")
    else:
        print(f"   [ERROR] Vonage OpenTok not initialized")
        print(f"           Reason: Credentials not configured or opentok not installed")
        
except ImportError as e:
    print(f"   [ERROR] Could not import vonage_service: {e}")
except Exception as e:
    print(f"   [ERROR] Unexpected error: {e}")

# Check 5: Database Check
print("\n5. Checking VideoCall Model")
print("-" * 70)

try:
    from messaging.models import VideoCall
    fields = [f.name for f in VideoCall._meta.get_fields()]
    if 'vonage_session_id' in fields:
        print(f"   [OK] VideoCall model has vonage_session_id field")
    else:
        print(f"   [ERROR] VideoCall model missing vonage_session_id field")
except Exception as e:
    print(f"   [ERROR] Could not check VideoCall model: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if vonage_api_key and vonage_api_secret:
    print("\n[OK] Vonage credentials are set in environment variables")
    print("    If you're still getting errors, check:")
    print("    1. Credentials are correct at https://tokbox.com/account/")
    print("    2. opentok package is installed (pip install opentok==3.13.0)")
    print("    3. Railway logs for detailed error messages")
else:
    print("\n[ERROR] Vonage credentials are NOT set")
    print("    To fix:")
    print("    1. Go to Railway Dashboard → Your Project → Settings → Environment")
    print("    2. Add: VONAGE_API_KEY = <your_api_key>")
    print("    3. Add: VONAGE_API_SECRET = <your_api_secret>")
    print("    4. Get credentials from: https://tokbox.com/account/")

print("\n")
