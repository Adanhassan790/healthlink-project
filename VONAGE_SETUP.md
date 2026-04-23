# VONAGE VIDEO CALL TEMPLATE
# File: templates/messaging/video_room.html
# This template replaces Jitsi with Vonage Video API

# Step 1: Replace entire video_room.html content with the vonage template below:
# Link to complete template: See vonage_template_code.txt

# USE THIS VONAGE SDK SCRIPT:
# <script src="https://static.opentok.com/v2.20/js/opentok.min.js"></script>

# KEY VARIABLES TO PASS FROM Django VIEW:
# - vonage_api_key: The Vonage API key (from environment)
# - vonage_session_id: Session created for this call
# - vonage_token: Token generated for authenticated user
# - user_display_name: Full name or username of current user

# CONFIGURATION IN .env:
# VONAGE_API_KEY=your_api_key_here
# VONAGE_API_SECRET=your_api_secret_here

# INSTALLATION:
# pip install opentok==3.14.0

# The template handles:
# - Session connection
# - Publisher initialization (camera/mic)
# - Subscriber connection (remote participant video)
# - Audio/video toggles
# - Call duration timer
# - Error handling with user-friendly messages
# - Graceful disconnect
