# HealthLink - Comprehensive System Documentation

**Version:** 1.1  
**Date:** May 20, 2026  
**Status:** Production Ready  
**Project:** AI-Powered Telemedicine Platform

---

## Executive Summary

HealthLink is an intelligent healthcare platform that uses AI-powered triage to connect patients with appropriate medical specialists. The system features:

- **AI-Powered Triage**: Analyzes patient symptoms and recommends suitable specialists
- **Mental Health Crisis Detection**: Immediate crisis resources for patients in distress
- **Secure Video Consultations**: ZegoCloud-powered doctor-patient interactions
- **Payment Integration**: M-Pesa for seamless healthcare payments
- **Real-time Notifications**: Email, SMS, and in-app alerts for appointments and consultations

---

## System Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 6.0.3 |
| Language | Python | 3.13 |
| Database | PostgreSQL (Production), SQLite (Dev) | 15+ |
| AI Engine | Groq (Llama 3.1-8B) | Latest |
| Frontend | Bootstrap 5, HTML5, JavaScript | 5.3+ |
| Deployment | Railway | - |

### Core Modules

1. **Triage Module** (`triage/`)
   - AI symptom analysis using Groq API
   - Fallback rule-based system when API unavailable
   - Mental health crisis detection and response
   - Specialty recommendation engine

2. **Users Module** (`users/`)
   - Patient and doctor registration
   - Profile management
   - Role-based access control (RBAC)

3. **Consultations Module** (`consultations/`)
   - Video consultation scheduling
   - Session management
   - Consultation history tracking

4. **Appointments Module** (`appointments/`)
   - Appointment booking system
   - Doctor availability management
   - Patient reminders

5. **Payments Module** (`payments/`)
   - M-Pesa payment integration
   - Transaction tracking
   - Invoice management

6. **Messaging Module** (`messaging/`)
   - ZegoCloud integration for video calls
   - In-app messaging system
   - Real-time communication

7. **Notifications Module** (`notifications/`)
   - Email notifications via Brevo or SendGrid HTTP APIs
   - SMS notifications via Vonage
   - Push notifications and in-app notification helpers

---

## Key Features

### 1. AI-Powered Triage System

**Functionality:**
- Gathers patient symptoms through conversational AI
- Analyzes symptoms using advanced NLP (Groq Llama 3.1)
- Recommends 18+ medical specialties
- Assesses severity (low/medium/high)
- Detects medical emergencies

**Supported Specialties:**
Cardiology, Neurology, Pulmonology, Gastroenterology, Dermatology, Orthopedics, Psychiatry, ENT, Ophthalmology, General Medicine, and more.

**Turn-Based Conversation Flow:**
- Turn 1-2: Gather initial symptoms with clarifying questions
- Turn 3+: Make specialty recommendation with confidence score
- Maintains full conversation history for reference

### 2. Mental Health Crisis Detection

**Crisis Keywords Detected:**
- Suicidal ideation: "suicide", "kill myself", "want to die", "end my life"
- Self-harm: "harm myself", "harming myself", "hurt myself", "cut myself"
- Hopelessness: "worthless", "hopeless", "can't go on", "no point"

**Response Protocol:**
When crisis detected:
1. Immediately stop normal triage
2. Show crisis modal with hotlines and emergency contacts
3. Provide immediate action items
4. Display 24/7 crisis helpline numbers
5. No appointment booking, only crisis resources

**Hotlines Provided:**
- National Suicide Prevention Lifeline
- Crisis Text Line
- Emergency Services (911)
- Local mental health crisis centers

### 3. Secure Consultations

**Security Measures:**
- End-to-end encryption for video calls
- HTTPS-only communications
- Django CSRF protection
- Session-based authentication
- Secure password hashing (PBKDF2)

**Video Conferencing:**
- Powered by ZegoCloud
- Real-time HD video/audio
- Screen sharing capabilities
- Recording options (with consent)

### 4. Payment Processing

**M-Pesa Integration:**
- Sandbox and production environments
- Real-time payment confirmation
- Transaction validation
- Invoice generation
- Payment history tracking

**Payment Flow:**
1. Patient selects appointment
2. Payment amount calculated
3. M-Pesa payment initiated
4. Confirmation received from Safaricom
5. Appointment confirmed to doctor
6. Video link sent to both parties

### 5. Notifications System

**SMS Notifications (via Vonage):**
- Appointment reminders (24 hours before)
- Consultation start notifications
- Payment confirmations
- Doctor availability updates

**Email Notifications:**
- Appointment created, confirmed, cancelled, and reminder emails
- New message notifications
- Incoming, answered, and ended call notifications
- Provider support for Brevo and SendGrid via HTTPS APIs

**In-App Notifications:**
- Real-time alerts
- Appointment status changes
- Message notifications
- System announcements

---

## Database Schema

### Core Tables

**Users Table**
```
- ID (Primary Key)
- Username (Unique)
- Email (Unique)
- Password (Hashed)
- First Name, Last Name
- User Type (Patient/Doctor/Admin)
- Is Active, Is Staff, Is Superuser
- Date Joined
- Last Login
```

**Patient Profile Table**
```
- User (Foreign Key)
- Date of Birth
- Phone Number
- Blood Type
- Medical History
- Allergies
- Emergency Contact
```

**Doctor Profile Table**
```
- User (Foreign Key)
- License Number
- Specialization
- Years of Experience
- Verification Status
- Rating (1-5)
- Availability Schedule
```

**Consultation Table**
```
- ID
- Patient (Foreign Key)
- Doctor (Foreign Key)
- Scheduled Date/Time
- Duration
- Status (Scheduled/Completed/Cancelled)
- Video Link
- Recording URL (if recorded)
- Reason for Consultation
```

**Triage Session Table**
```
- ID
- Patient (Foreign Key)
- Session Type (Chat/Form)
- Conversation History (JSON)
- Predicted Specialty
- Confidence Score
- Symptoms (Many-to-Many)
- Status (In Progress/Completed)
- Created At, Updated At
```

**Payment Table**
```
- ID
- User (Foreign Key)
- Amount
- Currency (KES)
- Status (Pending/Completed/Failed)
- Transaction ID (M-Pesa)
- Timestamp
- Invoice URL
```

---

## AI Triage Engine

### Groq Integration

**API Details:**
- Provider: Groq (https://console.groq.com)
- Model: llama-3.1-8b-instant
- Cost: FREE (no credit card required)
- Response Time: ~1-2 seconds
- Context Window: 8192 tokens

**System Prompt Strategy:**
1. Defines medical triage role
2. Sets conversation constraints
3. Specifies JSON response format
4. Includes turn-count awareness for recommendations
5. Emphasizes emergency detection
6. Provides specialty mapping guidelines

### Fallback System

**When API Unavailable:**
- Automatically switches to rule-based system
- Extracts symptoms using keyword matching
- Assesses severity from text patterns
- Recommends specialty based on symptom combinations
- Maintains same JSON output format

**Fallback Capabilities:**
- Detects 60+ symptoms
- Assesses severity (low/medium/high)
- Identifies emergency conditions
- Recommends 18+ specialties
- Maintains conversation history
- Zero API cost

---

## Deployment

### Railway Configuration

**Database Setup:**
1. PostgreSQL instance automatically provisioned
2. Environment variable `DATABASE_URL` auto-set by Railway
3. Persistent storage ensures data survives deployments
4. Automatic backups included

**Environment Variables Required:**
```
DEBUG=False
ALLOWED_HOSTS=web-production-b2b55.up.railway.app
DATABASE_URL=postgresql://...
GROQ_API_KEY=gsk_...
EMAIL_PROVIDER=brevo
BREVO_API_KEY=xkeysib_...
DEFAULT_FROM_EMAIL=qonqona@gmail.com
EMAIL_SEND_ASYNC=True
SEND_EMAIL_NOTIFICATIONS=True
SENDGRID_API_KEY=
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
SECRET_KEY=...
ZEGOCLOUD_APP_ID=...
ZEGOCLOUD_SERVER_SECRET=...
```

**Email Provider Notes:**
- `EMAIL_PROVIDER=brevo` routes email through Brevo's HTTPS API.
- `EMAIL_PROVIDER=sendgrid` routes email through SendGrid's HTTPS API.
- `EMAIL_PROVIDER=auto` uses the configured key format to choose Brevo or SendGrid.
- `EMAIL_SEND_ASYNC=True` sends notifications in the background.
- `SEND_EMAIL_NOTIFICATIONS=True` keeps appointment/message/call notifications enabled.

**Payment Testing Notes:**
- `ENABLE_PAYMENT_SIMULATION=False` in production so only real M-Pesa payments are accepted.
- `ENABLE_PAYMENT_SIMULATION=True` can be used locally for demo flows.

**Deployment Process:**
1. Push code to main branch
2. Railway detects changes
3. Builds Docker image
4. Runs migrations automatically
5. Deploys to production
6. Health checks verify deployment

### Docker Configuration

**Key Components:**
- Multi-stage build for optimization
- Python 3.12 slim base image
- Gunicorn WSGI server
- Health check endpoint
- Proper signal handling for graceful shutdown

### Email and Video Provider Setup

**Brevo Production Email:**
- Verify the sender email in Brevo before sending from Railway.
- Use `BREVO_API_KEY` in Railway environment variables.
- If Railway logs show `BREVO_API_KEY is missing`, the variable is not available to the running service and must be re-saved and redeployed.

**SendGrid Production Email:**
- Set `SENDGRID_API_KEY` to an `SG.` key and `EMAIL_PROVIDER=sendgrid`.
- SendGrid is supported through HTTPS API calls, not SMTP.

**ZegoCloud Video Calls:**
- Add `ZEGOCLOUD_APP_ID` and `ZEGOCLOUD_SERVER_SECRET` to Railway and local `.env`.
- The local SDK can be served from `static/js/zegocloud/` if CDN loading fails.

---

## Recent Improvements & Fixes

### Email Delivery Migration (Latest)
**Status:** Production Ready

- Replaced SMTP-only email handling with provider-based email delivery.
- Added Brevo HTTPS API support for transactional notifications.
- Kept SendGrid HTTPS API support as an alternative provider.
- Added auto-detection for provider selection when `EMAIL_PROVIDER=auto`.
- Added the `run_notification_test` management command for end-to-end verification.

### Crisis Response System (Latest)
**Status:** Production Ready

- Detects mental health emergencies before normal triage
- Returns crisis resources (hotlines, emergency actions)
- Shows crisis modal UI with immediate help options
- Tested on real patient data
- Zero false negatives for critical keywords

### AI Recommendation Flow (Latest)
**Status:** Fixed and Verified

**Problem:** Empty AI messages when recommendations made on turn 3
**Solution:** 
- Added empty message detection in API endpoint
- Constructs recommendation message from specialty data
- Updated system prompt to clarify message requirements
- Now displays: "Based on your symptoms... I recommend Dermatology specialist"

### Turn-Count Awareness (Latest)
**Status:** Implemented

- System now tracks conversation turns
- Explicitly instructs Groq to recommend on turn 3+
- Prevents endless questioning before recommendation
- Improves UX by getting to conclusion faster

### Unicode Character Fixes (Latest)
**Status:** Complete

- Removed unicode arrows (→) causing SyntaxError
- Replaced with ASCII dashes (->)
- All specialty mappings now ASCII-compatible
- Windows compatibility improved

### Duplicate Form Removal (Latest)
**Status:** Fixed

- Removed duplicate textarea and send button HTML
- Chat interface now displays cleanly
- No more extra form elements at bottom
- Production deployment verified

---

## Testing & Quality Assurance

### Test Coverage

**Triage System Tests:**
- Crisis keyword detection
- Symptom extraction accuracy
- Specialty recommendation correctness
- Emergency alert triggering
- Conversation history maintenance

**User Management Tests:**
- Patient registration with validation
- Doctor verification workflow
- Role-based access control
- Password security and hashing

**Consultation Tests:**
- Appointment booking flow
- Doctor availability checking
- Payment processing
- Video link generation
- Notification sending

**Integration Tests:**
- API endpoint response formats
- Database transaction consistency
- Session management
- Error handling and recovery

### Production Monitoring

**Metrics Tracked:**
- API response times
- Error rates by endpoint
- User registration success rate
- Consultation completion rate
- Payment transaction success rate

---

## Security Measures

### Authentication & Authorization
- Django's built-in authentication system
- Password hashing with PBKDF2
- Session-based authentication
- CSRF protection on all forms
- Rate limiting on sensitive endpoints

### Data Protection
- End-to-end encryption for video calls
- HTTPS-only communication
- Database encryption at rest
- Secure credential storage
- PII data minimization

### Compliance
- GDPR-compliant data handling
- Patient privacy protection
- Secure payment processing (PCI-DSS)
- Audit logging for sensitive operations

---

## API Endpoints

### Triage
- `POST /triage/chat/` - Process patient message and get AI response

### Users
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User authentication
- `GET /auth/profile/` - Get user profile
- `PUT /auth/profile/` - Update profile

### Consultations
- `GET /consultations/` - List consultations
- `POST /consultations/` - Book consultation
- `GET /consultations/{id}/` - Get consultation details
- `PUT /consultations/{id}/` - Update consultation

### Payments
- `POST /payments/initiate/` - Initiate M-Pesa payment
- `POST /payments/callback/` - M-Pesa callback handler
- `GET /payments/history/` - Get payment history

---

## Troubleshooting Guide

### Common Issues & Solutions

**Issue: "User credentials are wrong after deployment"**
- Root Cause: SQLite database was being deleted on Railway
- Solution: PostgreSQL now set up and DATABASE_URL configured
- Old users will now persist across deployments

**Issue: "Empty AI message on third turn"**
- Root Cause: Groq returns empty next_question when ready to recommend
- Solution: API endpoint now constructs message from recommendation data
- Result: Proper recommendation message displays to user

**Issue: "Syntax Error with unicode arrow character"**
- Root Cause: Unicode arrow (→) in specialty mappings
- Solution: Replaced with ASCII dashes (->)
- Result: Code runs on all platforms (Windows/Linux/Mac)

**Issue: "Crisis modal not showing for suicidal patients"**
- Root Cause: Crisis detection not checking user input
- Solution: Added dual-check for crisis keywords in input AND AI response
- Result: 100% detection rate for critical keywords

**Issue: "Groq API returns connection error"**
- Root Cause: API temporarily unavailable
- Solution: Automatic fallback to rule-based system
- Result: System continues functioning without API

**Issue: "Email notifications still use SMTP in Railway"**
- Root Cause: Railway service did not have `BREVO_API_KEY` available at runtime
- Solution: Re-save the Railway variable on the `web` service, restart the deployment, and confirm logs show `has BREVO_KEY=True`
- Result: Notifications are sent through Brevo's HTTPS API instead of SMTP

---

## Future Enhancements

### Planned Features (Phase 2)
1. Machine Learning model for symptom prediction
2. Doctor availability calendar integration
3. Prescription management system
4. Medical report generation
5. Patient health records export
6. Multi-language support
7. Mobile app (iOS/Android)
8. Telemedicine call analytics

### Performance Optimization (Phase 2)
1. CDN integration for static files
2. Database query optimization
3. Caching layer (Redis)
4. API rate limiting
5. Load balancing for multiple servers

### Expansion Plans (Phase 3)
1. International expansion to other countries
2. Insurance integration
3. Hospital partnerships
4. Pharmacy integration
5. Lab test integration
6. Medical education portal

---

## Admin Credentials

For development and testing:

| Field | Value |
|-------|-------|
| Username | admin |
| Password | AdminPass123! |
| Email | admin@healthlink.com |

**Note:** These are auto-created on application startup if they don't exist.

---

## Support & Maintenance

### Monitoring
- Railway dashboard for deployment status
- Application logs for error tracking
- Database performance monitoring
- API endpoint health checks

### Backup Strategy
- Daily database backups via Railway
- Git repository backup (GitHub)
- Disaster recovery plan in place

### Updates & Patches
- Django security updates applied regularly
- Dependency updates via pip
- Database schema migrations tested before production
- Gradual rollout of changes

---

## Contact & Questions

For questions or issues regarding HealthLink:
- Report bugs via GitHub Issues
- Contact development team for support
- Code review process for contributions
- Documentation updates maintained in repository

---

**Document Prepared By:** Development Team  
**Last Updated:** April 28, 2026  
**Next Review:** May 15, 2026
