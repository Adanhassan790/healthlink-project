# HealthLink AI Symptom Checker - LLM Setup Guide

## Overview

Your symptoms checker now uses **OpenAI's GPT-3.5-turbo** instead of a limited local database. This means:

✅ **Advantages of GPT-based triage:**
- Access to massive medical knowledge (trained on billions of medical texts)
- Better understanding of symptom combinations
- More accurate specialty recommendations
- Conversational and empathetic responses
- Handles rare/complex symptoms confidently
- Learns new symptoms not in your local database

## Setup Instructions

### Step 1: Create OpenAI Account & Get API Key

1. Go to https://platform.openai.com/signup
2. Sign up or log in
3. Navigate to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)
6. **Important**: Save it somewhere safe - you won't see it again!

### Step 2: Add API Key to .env File

Edit the `.env` file in your project root:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

Replace `sk-your-actual-key-here` with your actual OpenAI API key.

### Step 3: Test the Connection

Run your server and try the chat triage:
```
python manage.py runserver
```

Navigate to: `http://127.0.0.1:8000/triage/chat/`

If it works, you'll see a greeting message from the AI.

### Step 4: Cost Management

**Free tier:** OpenAI gives you $5 in free credits (usually for 3 months)

**Pricing:** 
- GPT-3.5-turbo: ~$0.0005 per 1K tokens
- Average triage conversation: 1,000-2,000 tokens
- Cost per triage: ~$0.001-0.002 (less than 1 cent)

**Monitor usage:**
- https://platform.openai.com/usage
- Set spending limits in your OpenAI account settings

## How It Works

### Architecture

```
Patient Message
      ↓
┌─────────────────────────────────────┐
│   LLMTriageService                  │
│   (llm_triage_service.py)          │
└──────────────┬──────────────────────┘
               ↓
    ┌──────────────────────┐
    │  OpenAI API Call     │
    │  (GPT-3.5-turbo)     │
    │  Full Conversation   │
    │  Medical Knowledge   │
    └──────────┬───────────┘
               ↓
    ┌──────────────────────────┐
    │  AI Response             │
    │  - Asks clarifying Qs    │
    │  - Identifies symptoms   │
    │  - Makes recommendation  │
    │  - Detects emergencies   │
    └──────────┬───────────────┘
               ↓
         Save to Database
         (TriageSession)
```

### Conversation Flow

1. **Greeting** → AI welcomes patient
2. **Symptom Gathering** → Patient describes symptoms
3. **Clarification** → AI asks about severity, duration, location
4. **Analysis** → AI understands symptom patterns
5. **Recommendation** → AI suggests specialty + care advice

### Response Format

The AI returns JSON with:
```json
{
  "thinking": "Analysis of symptoms",
  "extracted_symptoms": ["chest pain", "shortness of breath"],
  "severity_assessment": "high",
  "emergency_alert": false,
  "next_question": "How long have you had chest pain?",
  "ready_for_recommendation": false,
  "recommendation": null
}
```

When ready to recommend:
```json
{
  "ready_for_recommendation": true,
  "recommendation": {
    "primary_specialty": "Cardiology",
    "reason": "Your symptoms suggest cardiac concerns",
    "urgency": "urgent",
    "next_steps": "Schedule appointment with cardiologist today",
    "additional_advice": "Avoid strenuous activity"
  }
}
```

## Files Changed

### New Files
- `triage/llm_triage_service.py` - Main LLM service

### Modified Files
- `triage/views.py` - Uses LLMTriageService instead of HealthLinkChatBot
- `.env` - Added OPENAI_API_KEY configuration
- `healthlink/settings.py` - Now loads .env file

### Old Files (Still Available)
- `triage/chat_bot.py` - Rule-based chatbot (fallback)
- `triage/ml_service.py` - ML model (not used in chat)

## Troubleshooting

### "OPENAI_API_KEY not found"
**Problem:** Error saying API key is not in .env
**Solution:** 
1. Make sure `.env` file exists in project root
2. Add line: `OPENAI_API_KEY=sk-your-key`
3. Restart Django server

### "Invalid API key"
**Problem:** API key is invalid or expired
**Solution:**
1. Generate a new key: https://platform.openai.com/api-keys
2. Update `.env` file with new key
3. Restart server

### "Rate limit exceeded"
**Problem:** Too many requests to OpenAI
**Solution:**
1. You've exceeded free tier or spending limit
2. Add payment method: https://platform.openai.com/account/billing
3. Or wait for next billing cycle

### "Slow responses"
**Problem:** Chat is slow
**Solution:** OpenAI is responding slow (not your code)
- This is normal at peak times
- GPT-3.5-turbo is usually 1-2 seconds

## Advanced Configuration

### Change Model
In `llm_triage_service.py`, change:
```python
self.model = "gpt-3.5-turbo"  # Change this
# To:
self.model = "gpt-4"  # More powerful but costs more
# Or:
self.model = "gpt-4-turbo"  # Faster GPT-4
```

### Adjust Temperature
In `process_patient_message()`:
```python
temperature=0.3  # Lower = more consistent, higher = more creative
# For medical: keep low (0.2-0.3)
```

### Change Max Tokens
```python
max_tokens=800  # Response length limit
# Increase for longer recommendations
```

## Security Notes

🔒 **Never commit `.env` file to Git**
- Already in `.gitignore` ✅
- Protects your API key from being public

🔒 **Keep API key secret**
- Don't share it with others
- Don't paste in forums/chat
- Rotate if exposed: https://platform.openai.com/api-keys

## Next Improvements

- [ ] Add conversation history persistence (database)
- [ ] Track AI accuracy statistics
- [ ] Add feedback mechanism (was this recommendation helpful?)
- [ ] Implement caching for common symptoms
- [ ] Multi-language support
- [ ] Integration with booking system
- [ ] Doctor profile matching

## Support

If you have issues:
1. Check OpenAI status: https://status.openai.com/
2. Check API key: https://platform.openai.com/api-keys
3. Check usage: https://platform.openai.com/usage
4. Verify .env file has the key
5. Restart Django server
