"""
Vonage Video API Service
Handles session creation and token generation for Vonage video calls
"""

import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize OpenTok (Vonage Video API)
VONAGE_API_KEY = os.getenv('VONAGE_API_KEY')
VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')

ot = None

# Try to import and initialize opentok
try:
    import opentok
    if VONAGE_API_KEY and VONAGE_API_SECRET:
        ot = opentok.OpenTok(VONAGE_API_KEY, VONAGE_API_SECRET)
        logger.info("Vonage OpenTok initialized successfully")
    else:
        logger.warning("Vonage credentials not configured. Video calls will not work.")
except ImportError as e:
    logger.error(f"opentok package not installed: {e}. Install with: pip install opentok==3.13.0")
except Exception as e:
    logger.error(f"Error initializing Vonage OpenTok: {e}", exc_info=True)


def create_session():
    """
    Create a new Vonage session for video calls
    Returns: session_id string
    """
    if not ot:
        raise ValueError("Vonage API not configured. Set VONAGE_API_KEY and VONAGE_API_SECRET environment variables.")
    
    try:
        session = ot.create_session()
        logger.info(f"Created Vonage session: {session.session_id}")
        return session.session_id
    except Exception as e:
        logger.error(f"Error creating Vonage session: {str(e)}", exc_info=True)
        raise


def generate_token(session_id, user_id=None, role='publisher', expiration_hours=24):
    """
    Generate a Vonage token for a participant
    
    Args:
        session_id: The Vonage session ID
        user_id: Unique identifier for the participant (optional)
        role: 'publisher' (can publish) or 'subscriber' (can only view)
        expiration_hours: Token expiration time in hours (default 24)
    
    Returns: token string
    """
    if not ot:
        raise ValueError("Vonage API not configured.")
    
    try:
        # Calculate expiration time
        expire_time = int((datetime.utcnow() + timedelta(hours=expiration_hours)).timestamp())
        
        # Generate token
        token = ot.generate_token(
            session_id,
            user_id=user_id,
            role=role,
            expire_time=expire_time
        )
        
        logger.info(f"Generated token for session {session_id}, user {user_id}, role {role}")
        return token
    except Exception as e:
        logger.error(f"Error generating Vonage token: {str(e)}", exc_info=True)
        raise


def get_api_key():
    """Get Vonage API key for client-side initialization"""
    if not VONAGE_API_KEY:
        raise ValueError("Vonage API key not configured.")
    return VONAGE_API_KEY
