"""
Zegocloud Video API Service
Handles token generation for Zegocloud video calls
"""

import base64
import json
import logging
import os
import secrets
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

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
        expiration_seconds = int(expiration_seconds)

        app_id = int(ZEGOCLOUD_APP_ID)
        ctime = int(time.time())
        expire_time = ctime + expiration_seconds
        nonce = secrets.randbelow(2147483647)

        body = {
            "app_id": app_id,
            "user_id": user_id,
            "nonce": nonce,
            "ctime": ctime,
            "expire": expire_time,
        }

        iv = _generate_iv()
        ciphertext = _encrypt_prebuilt_token_body(body, ZEGOCLOUD_SERVER_SECRET, iv)
        access_token = _assemble_prebuilt_token(expire_time, iv, ciphertext)
        
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


def _generate_iv() -> str:
    """Return a 16-character ASCII IV string."""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    return "".join(secrets.choice(alphabet) for _ in range(16))


def _encrypt_prebuilt_token_body(body: dict, server_secret: str, iv: str) -> bytes:
    """Encrypt the token body with AES-CBC and PKCS7 padding."""
    key = server_secret.encode("utf-8")
    if len(key) not in (16, 24, 32):
        raise ValueError("Zegocloud server secret must be 16, 24, or 32 bytes long.")

    payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_payload = padder.update(payload) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv.encode("utf-8")))
    encryptor = cipher.encryptor()
    return encryptor.update(padded_payload) + encryptor.finalize()


def _assemble_prebuilt_token(expire_time: int, iv: str, ciphertext: bytes) -> str:
    """Build the base64-encoded Zego prebuilt token envelope."""
    expire_bytes = expire_time.to_bytes(4, byteorder="little", signed=False)
    iv_bytes = iv.encode("utf-8")
    ciphertext_length = len(ciphertext).to_bytes(2, byteorder="big", signed=False)
    envelope = bytearray(8 + 2 + 16 + 2 + len(ciphertext))
    envelope[0:4] = b"\x00\x00\x00\x00"
    envelope[4:8] = expire_bytes
    envelope[8:10] = len(iv_bytes).to_bytes(2, byteorder="big", signed=False)
    envelope[10:26] = iv_bytes
    envelope[26:28] = ciphertext_length
    envelope[28:28 + len(ciphertext)] = ciphertext
    return "04" + base64.b64encode(bytes(envelope)).decode("ascii")


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
