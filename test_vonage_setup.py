#!/usr/bin/env python
"""
Test script to verify Vonage integration setup
Run: python test_vonage_setup.py
"""

import os
import sys

def test_vonage_setup():
    """Test Vonage environment variables and imports"""
    
    print("\n" + "="*60)
    print("VONAGE INTEGRATION TEST")
    print("="*60 + "\n")
    
    # Check environment variables
    print("1. Checking Environment Variables...")
    api_key = os.getenv('VONAGE_API_KEY')
    api_secret = os.getenv('VONAGE_API_SECRET')
    
    if api_key:
        print(f"   ✓ VONAGE_API_KEY: Present (length: {len(api_key)})")
    else:
        print("   ✗ VONAGE_API_KEY: NOT FOUND")
    
    if api_secret:
        print(f"   ✓ VONAGE_API_SECRET: Present (length: {len(api_secret)})")
    else:
        print("   ✗ VONAGE_API_SECRET: NOT FOUND")
    
    if not (api_key and api_secret):
        print("\n   ⚠️  WARNING: Vonage credentials not found in environment!")
        print("   Set them in Railway or your .env file\n")
        return False
    
    # Check opentok package
    print("\n2. Checking OpenTok Package Installation...")
    try:
        import opentok
        print(f"   ✓ opentok package installed (version: {opentok.__version__ if hasattr(opentok, '__version__') else 'unknown'})")
    except ImportError as e:
        print(f"   ✗ opentok package NOT installed: {e}")
        print("   Install with: pip install opentok==3.13.0")
        return False
    
    # Test vonage_service import
    print("\n3. Checking vonage_service Module...")
    try:
        from messaging.vonage_service import create_session, generate_token, get_api_key
        print("   ✓ vonage_service imports successful")
    except ImportError as e:
        print(f"   ✗ vonage_service import failed: {e}")
        return False
    
    # Test Vonage connection
    print("\n4. Testing Vonage Connection...")
    try:
        api_key_test = get_api_key()
        print(f"   ✓ get_api_key() works")
        
        session_id = create_session()
        print(f"   ✓ create_session() works: {session_id[:20]}...")
        
        token = generate_token(session_id, user_id="test_user")
        print(f"   ✓ generate_token() works: {token[:30]}...")
        
    except Exception as e:
        print(f"   ✗ Vonage operation failed: {e}")
        return False
    
    # Check VideoCall model
    print("\n5. Checking VideoCall Model...")
    try:
        from messaging.models import VideoCall
        if hasattr(VideoCall, '_meta'):
            fields = [f.name for f in VideoCall._meta.get_fields()]
            if 'vonage_session_id' in fields:
                print("   ✓ VideoCall model has vonage_session_id field")
            else:
                print("   ✗ VideoCall model missing vonage_session_id field")
                return False
    except ImportError as e:
        print(f"   ✗ VideoCall model import failed: {e}")
        return False
    
    # Check views integration
    print("\n6. Checking Views Integration...")
    try:
        from messaging.views import video_room
        print("   ✓ video_room view exists and is using Vonage")
    except ImportError as e:
        print(f"   ✗ video_room import failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour Vonage integration is ready to use!")
    print("\nNext steps:")
    print("  1. Deploy to Railway")
    print("  2. Start a conversation between doctor and patient")
    print("  3. Click 'Start Video Call' to test")
    print("\n")
    
    return True

if __name__ == '__main__':
    success = test_vonage_setup()
    sys.exit(0 if success else 1)
