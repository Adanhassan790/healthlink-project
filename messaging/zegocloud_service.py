"""
Zegocloud Video API Service
Handles token generation for Zegocloud video calls
"""

import os
import logging
import time
import hashlib
import base64
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Zegocloud credentials
ZEGOCLOUD_APP_ID = os.getenv('ZEGOCLOUD_APP_ID')
ZEGOCLOUD_SERVER_SECRET = os.getenv('ZEGOCLOUD_SERVER_SECRET')

# Validate credentials
try:
    if ZEGOCLOUD_APP_ID and ZEGOCLOUD_SERVER_SECRET:
        logger.info(f"Zegocloud initialized successfully (AppID: {str(ZEGOCLOUD_APP_ID)[:10]}...)")
    else:
        logger.warning("Zegocloud credentials not configured. Video calls will not work.")
except Exception as e:
    logger.error(f"Error initializing Zegocloud: {e}", exc_info=True)


def generate_access_token(user_id, session_id, expiration_seconds=3600):
    """
    Generate a Zegocloud access token for a participant
    
    Args:
        user_id: Unique identifier for the participant (e.g., user.username or user.id)
        session_id: Room/Session ID for the video call
        expiration_seconds: Token expiration time in seconds (default 3600 = 1 hour)
    
    Returns: 
        dict with token, appId, userId, sessionId, and expiration
    """
    if not ZEGOCLOUD_APP_ID or not ZEGOCLOUD_SERVER_SECRET:
        raise ValueError("Zegocloud API not configured. Set ZEGOCLOUD_APP_ID and ZEGOCLOUD_SERVER_SECRET environment variables.")
    
    try:
        # Convert expiration_seconds to integer if needed
        expiration_seconds = int(expiration_seconds)
        
        # Generate token
        # Token format: base64(appId:userId:ctime:nonce:signature)
        app_id = int(ZEGOCLOUD_APP_ID)
        ctime = int(time.time())
        nonce = int(time.time() * 1000) % 2147483647  # Use timestamp as nonce
        
        # Create signature: sha256(serverSecret + userId + ctime + nonce + expiration_seconds)
        signature_source = f"{ZEGOCLOUD_SERVER_SECRET}{user_id}{ctime}{nonce}{expiration_seconds}"
        signature = hashlib.sha256(signature_source.encode()).digest()
        signature_base64 = base64.b64encode(signature).decode()
        
        # Build token
        token_parts = f"{app_id}:{user_id}:{ctime}:{nonce}:{signature_base64}"
        access_token = base64.b64encode(token_parts.encode()).decode()
        
        logger.info(f"Generated Zegocloud token for user {user_id}, room {session_id}")
        
        return {
            'access_token': access_token,
            'app_id': app_id,
            'user_id': user_id,
            'session_id': session_id,
            'expires_in': expiration_seconds
        }
    except Exception as e:
        logger.error(f"Error generating Zegocloud token: {str(e)}", exc_info=True)
        raise


def generate_room_id(conversation_id, user_id=None):
    """
    Generate a room ID for a Zegocloud session
    
    Args:
        conversation_id: Conversation database ID
        user_id: Optional user identifier for uniqueness
    
    Returns: room_id string
    """
    import uuid
    room_id = f"healthlink-{conversation_id}"
    return room_id


def get_app_id():
    """Get Zegocloud App ID for client-side initialization"""
    if not ZEGOCLOUD_APP_ID:
        raise ValueError("Zegocloud App ID not configured.")
    return int(ZEGOCLOUD_APP_ID)


def verify_zegocloud_setup():
    """
    Verify that Zegocloud is properly configured
    
    Returns:
        dict with configuration status
    """
    status = {
        'configured': bool(ZEGOCLOUD_APP_ID and ZEGOCLOUD_SERVER_SECRET),
        'app_id_set': bool(ZEGOCLOUD_APP_ID),
        'server_secret_set': bool(ZEGOCLOUD_SERVER_SECRET),
        'error_message': None
    }
    
    if not status['configured']:
        status['error_message'] = "Zegocloud credentials not configured. Set ZEGOCLOUD_APP_ID and ZEGOCLOUD_SERVER_SECRET environment variables."
    
    return status
