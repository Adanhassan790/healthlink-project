#!/usr/bin/env python
"""Test Zegocloud configuration and token generation"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("ZEGOCLOUD CONFIGURATION TEST")
print("=" * 60)

# Test 1: Verify configuration
print("\n1. Checking Zegocloud Configuration...")
from messaging.zegocloud_service import verify_zegocloud_setup, get_app_id

status = verify_zegocloud_setup()
print(f"   ✓ Configured: {status['configured']}")
print(f"   ✓ App ID Set: {status['app_id_set']}")
print(f"   ✓ Server Secret Set: {status['server_secret_set']}")

if not status['configured']:
    print(f"   ⚠ ERROR: {status['error_message']}")
    sys.exit(1)

# Test 2: Get App ID
print("\n2. Getting App ID...")
app_id = get_app_id()
print(f"   ✓ App ID: {app_id}")

# Test 3: Generate test token
print("\n3. Testing Token Generation...")
from messaging.zegocloud_service import generate_access_token

try:
    token_data = generate_access_token(
        user_id="test_user_123",
        session_id="test_room_456",
        expiration_seconds=3600
    )
    print(f"   ✓ Token generated successfully!")
    print(f"   ✓ Token length: {len(token_data['access_token'])} chars")
    print(f"   ✓ Expires in: {token_data['expires_in']} seconds")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ZEGOCLOUD SETUP COMPLETE AND VERIFIED!")
print("=" * 60)
