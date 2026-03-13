# HEALTHLINK: AN INTELLIGENT AI-POWERED TELEMEDICINE PLATFORM WITH INTEGRATED MOBILE PAYMENT AND REAL-TIME COMMUNICATION SYSTEMS

## CONCEPT PAPER

---

### Document Information

| Field | Details |
|-------|---------|
| **Project Title** | HealthLink: An Intelligent AI-Powered Telemedicine Platform with Integrated Mobile Payment and Real-Time Communication Systems |
| **Academic Level** | Final Year Project |
| **Institution** | Pwani University |
| **Department** | Computer Science |
| **Student Name** | Adan Hassan Adi |
| **Supervisor** | Dr. Mbogholi |
| **Submission Date** | January 2026 |

---

## 1. EXECUTIVE SUMMARY

HealthLink is a sophisticated, multi-layered telemedicine ecosystem that revolutionizes healthcare delivery through the integration of **Artificial Intelligence (AI)**, **Machine Learning (ML)**, **Real-Time Communication Technologies**, **Mobile Money Payment Processing**, and **SMS Gateway Integration**. Unlike basic telemedicine applications that merely connect patients with doctors, HealthLink implements an intelligent end-to-end healthcare workflow that begins with AI-assisted symptom analysis and concludes with prescription management and follow-up care.

The platform addresses the critical healthcare access gap in Kenya and similar developing nations by implementing:

1. **Dual-Mode AI Triage System**: Combining Machine Learning classification algorithms with Natural Language Processing (NLP) chatbot for intelligent symptom assessment
2. **WebRTC-Based Video Consultation**: Peer-to-peer encrypted video calls with signaling server implementation
3. **Safaricom M-Pesa Daraja API Integration**: STK Push payment initiation with callback handling for real-time payment verification
4. **SMS Gateway Integration**: Real-time SMS notifications for offline users when messages, appointments, or prescriptions are created
5. **Electronic Prescription Management**: Digital prescription generation with medication database and dispensing workflow
6. **Administrative Intelligence Dashboard**: Real-time analytics, revenue tracking, and doctor verification system

**Technical Complexity Highlights:**
- 10+ interconnected Django application modules
- Machine Learning model using TF-IDF Vectorization and Random Forest Classification
- WebRTC signaling implementation with ICE candidate exchange
- OAuth 2.0 authentication with M-Pesa Daraja API
- Real-time notification system with SMS fallback
- Role-based access control (RBAC) for patients, doctors, and administrators

---

## 2. INTRODUCTION

### 2.1 Background and Context

The healthcare sector in Kenya faces significant challenges that impede effective healthcare delivery:

- **Doctor-to-Patient Ratio**: Kenya has approximately 1 doctor per 6,000 patients, far below the WHO recommended ratio of 1:1,000
- **Geographic Disparities**: Over 70% of medical specialists are concentrated in Nairobi and Mombasa, leaving rural populations underserved
- **Infrastructure Limitations**: Many healthcare facilities lack modern appointment management systems, resulting in 2-4 hour average wait times
- **Payment Barriers**: Traditional cash-based payment systems create friction in healthcare transactions

The rapid adoption of mobile technology in Kenya (95% mobile penetration) and mobile money services (over 30 million M-Pesa users) presents a unique opportunity to bridge this healthcare access gap through digital innovation.

### 2.2 Problem Definition

The current healthcare delivery model suffers from:

| Problem | Impact | Proposed Solution |
|---------|--------|-------------------|
| No pre-consultation symptom assessment | Patients often consult wrong specialists | AI-powered triage system |
| Manual appointment scheduling | Long queues and double-bookings | Digital scheduling with availability management |
| Cash-only payments | Payment verification delays | M-Pesa integration with instant confirmation |
| Paper prescriptions | Lost/illegible prescriptions, no tracking | Electronic prescription management |
| No communication channel | Lost follow-up, poor continuity of care | Real-time messaging + SMS notifications |
| Unverified practitioners | Risk of consulting unqualified individuals | Doctor verification workflow |

### 2.3 Research Questions

1. How can Artificial Intelligence be effectively utilized to perform preliminary symptom triage and recommend appropriate medical specialties?
2. What architectural patterns enable seamless integration of mobile money payment systems in healthcare applications?
3. How can real-time communication be maintained with offline users through SMS gateway integration?
4. What security measures are necessary to protect sensitive medical data in a telemedicine platform?

### 2.4 Project Significance

This project contributes to:
- **Sustainable Development Goal 3**: Good Health and Well-being
- **Kenya Vision 2030**: Digital transformation of healthcare services
- **Universal Health Coverage (UHC)**: Reducing barriers to healthcare access

---

## 3. LITERATURE REVIEW

### 3.1 Telemedicine Evolution and Current State

Telemedicine has evolved through distinct generations:

| Generation | Era | Characteristics | Limitations |
|------------|-----|-----------------|-------------|
| First | 1960s-1990s | Video conferencing, store-and-forward | Expensive equipment, limited bandwidth |
| Second | 2000s-2010s | Web-based platforms, EHR integration | No mobile optimization, limited interactivity |
| Third | 2015-present | Mobile-first, AI integration, real-time | Limited adoption in developing countries |
| **Fourth (Proposed)** | Future | AI triage, integrated payments, SMS fallback | **HealthLink addresses this generation** |

### 3.2 Artificial Intelligence in Healthcare

**Machine Learning for Medical Triage:**

Studies by Semigran et al. (2015) evaluated symptom checker accuracy, finding that correct diagnosis was achieved in only 34% of cases. However, recent advances in NLP and classification algorithms have improved accuracy significantly.

**Our Approach:**
HealthLink implements a hybrid triage system:
1. **Form-Based Triage**: Structured symptom selection using predefined categories
2. **Chatbot Triage**: Natural language processing for conversational symptom gathering
3. **ML Classification**: TF-IDF Vectorization combined with Random Forest Classifier

```
Technical Implementation:
- Feature Extraction: TF-IDF (Term Frequency-Inverse Document Frequency)
- Classification Algorithm: Random Forest (ensemble of decision trees)
- Training Data: 100+ symptom-specialty mappings across 15 specialties
- Confidence Scoring: Probability-based specialty recommendations
```

### 3.3 Mobile Money Integration in Healthcare

M-Pesa has transformed financial transactions in Kenya. Integration in healthcare settings offers:
- Instant payment verification
- Transaction audit trails
- Reduced cash handling risks
- Accessibility for unbanked populations

**Daraja API Technical Flow:**
```
1. Patient initiates payment → 
2. System calls Daraja OAuth endpoint → 
3. Access token obtained → 
4. STK Push request sent → 
5. M-Pesa prompt appears on patient's phone → 
6. Patient enters PIN → 
7. Transaction processed → 
8. Callback URL receives confirmation → 
9. Appointment status updated automatically
```

### 3.4 Real-Time Communication in Healthcare

WebRTC (Web Real-Time Communication) enables peer-to-peer communication without plugins. Key components:
- **Signaling Server**: Exchange of session descriptions and ICE candidates
- **STUN/TURN Servers**: NAT traversal for establishing connections
- **Media Streams**: Audio/video transmission

### 3.5 SMS as Fallback Communication Channel

In regions with limited internet connectivity, SMS serves as a reliable fallback:
- 98% of mobile users can receive SMS
- No internet connection required
- Immediate delivery notification

**Africa's Talking API** and **Twilio** provide robust SMS gateway services suitable for healthcare notifications.

### 3.6 Gap Analysis

| Existing System | Strengths | Weaknesses | HealthLink Advantage |
|-----------------|-----------|------------|---------------------|
| Teladoc | Global presence, established | Not in Kenya, no M-Pesa | Local payment integration |
| Babylon Health | Strong AI | No local support | Kenyan context adaptation |
| MyDawa | Pharmacy focus | No consultations | Full telemedicine suite |
| Ponea Health | Local presence | Limited features | Comprehensive AI + payments |

---

## 4. PROPOSED SYSTEM ARCHITECTURE

### 4.1 System Overview

HealthLink implements a **Modular Monolith Architecture** using Django's application structure, enabling:
- Independent module development
- Shared database for data consistency
- Easy future migration to microservices

### 4.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Patient    │  │    Doctor    │  │    Admin     │  │   Mobile     │    │
│  │   Portal     │  │   Portal     │  │  Dashboard   │  │   Browser    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  Users  │ │Appoint- │ │ Triage  │ │Messaging│ │Payments │ │Prescrip-│  │
│  │ Module  │ │  ments  │ │  (AI)   │ │ + Video │ │ (M-Pesa)│ │  tions  │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌───────────────────────────────────────────────┐ │
│  │Notifica-│ │ Admin   │ │                                               │ │
│  │  tions  │ │ Module  │ │          Django ORM / Business Logic          │ │
│  └─────────┘ └─────────┘ └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │   M-Pesa       │  │    SMS         │  │    WebRTC      │                │
│  │  Daraja API    │  │   Gateway      │  │  Signaling     │                │
│  │  (Payments)    │  │ (Africa's Talk)│  │   (PeerJS)     │                │
│  └────────────────┘  └────────────────┘  └────────────────┘                │
│  ┌────────────────┐  ┌────────────────┐                                    │
│  │   OpenAI       │  │    ML Model    │                                    │
│  │   GPT API      │  │  (Scikit-learn)│                                    │
│  │  (Chatbot)     │  │   (Triage)     │                                    │
│  └────────────────┘  └────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL / SQLite Database                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │  Users  │ │Appoint- │ │ Triage  │ │Messages │ │ Payment │       │   │
│  │  │ Profiles│ │  ments  │ │Sessions │ │  Calls  │ │  Trans  │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                                │   │
│  │  │Prescrip-│ │Notifica-│ │ Doctor  │                                │   │
│  │  │  tions  │ │  tions  │ │Availabi-│                                │   │
│  │  │         │ │         │ │  lity   │                                │   │
│  │  └─────────┘ └─────────┘ └─────────┘                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Module Descriptions

| Module | Purpose | Key Features |
|--------|---------|--------------|
| **Users** | User management | Patient/Doctor/Admin roles, Profile management, Authentication |
| **Appointments** | Scheduling | Doctor availability, Time slot booking, Status tracking |
| **Triage** | AI symptom assessment | ML model, Chatbot, Specialty recommendation |
| **Messaging** | Communication | Real-time chat, Video calls, SMS notifications |
| **Payments** | Financial transactions | M-Pesa STK Push, Payment verification, Transaction history |
| **Prescriptions** | Medication management | Digital prescriptions, Medication database, Dispensing workflow |
| **Notifications** | Alerts | In-app notifications, Email alerts, SMS fallback |
| **Administration** | System oversight | User management, Analytics, Doctor verification |

---

## 5. DETAILED SYSTEM PROCESSES

### 5.1 Patient Registration and Onboarding Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATIENT REGISTRATION FLOW                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Access Website │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Click "Register │
                    │   as Patient"   │
                    └────────┬────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │      Enter Personal Details      │
            │  - Full Name                     │
            │  - Email Address                 │
            │  - Phone Number (M-Pesa)         │
            │  - Date of Birth                 │
            │  - Password                      │
            └────────────────┬────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │    Complete Medical Profile      │
            │  - Blood Type                    │
            │  - Known Allergies               │
            │  - Medical History               │
            │  - Emergency Contact             │
            └────────────────┬────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Account Created │
                    │   + Welcome     │
                    │   Notification  │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Redirect to    │
                    │   Dashboard     │
                    └─────────────────┘
```

**Technical Implementation:**
- Django Forms with validation
- Password hashing using PBKDF2
- Automatic PatientProfile creation via Django signals
- Session-based authentication

### 5.2 Doctor Registration and Verification Process

```
┌─────────────────────────────────────────────────────────────────┐
│                 DOCTOR REGISTRATION & VERIFICATION               │
└─────────────────────────────────────────────────────────────────┘

STAGE 1: REGISTRATION
─────────────────────
Doctor → Submit Registration Form
          │
          ├── Personal Details (Name, Email, Phone)
          ├── Professional Details:
          │     • Medical License Number
          │     • Specialization
          │     • Years of Experience
          │     • Consultation Fee
          │     • Professional Bio
          │
          └── Account created with status: "PENDING VERIFICATION"

STAGE 2: ADMIN VERIFICATION
───────────────────────────
Admin Dashboard → Doctor Verification Queue
          │
          ├── View Doctor Details
          ├── Verify License Number (Manual/External API)
          ├── Review Credentials
          │
          └── Decision:
                ├── APPROVE → Status: "VERIFIED"
                │              → Doctor can receive appointments
                │              → SMS notification sent
                │
                └── REJECT → Status: "REJECTED"
                             → Reason documented
                             → Email notification sent

STAGE 3: AVAILABILITY SETUP
───────────────────────────
Verified Doctor → Manage Availability
          │
          ├── Set Weekly Schedule
          │     • Monday: 09:00 - 17:00
          │     • Tuesday: 09:00 - 17:00
          │     • ...
          │
          ├── Define Slot Duration (15/30/60 minutes)
          │
          └── System generates bookable time slots
```

### 5.3 AI-Powered Symptom Triage Process

```
┌─────────────────────────────────────────────────────────────────┐
│              AI TRIAGE SYSTEM - DUAL MODE OPERATION              │
└─────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │  Patient Starts │
                         │  Symptom Check  │
                         └────────┬────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
         ┌─────────────────┐         ┌─────────────────┐
         │   FORM-BASED    │         │   AI CHATBOT    │
         │     TRIAGE      │         │     TRIAGE      │
         └────────┬────────┘         └────────┬────────┘
                  │                           │
                  ▼                           ▼
    ┌─────────────────────────┐   ┌─────────────────────────┐
    │ Select Symptom Category │   │ "Describe your symptoms │
    │  • Head & Neurological  │   │  in your own words..."  │
    │  • Chest & Cardiac      │   │                         │
    │  • Abdominal            │   │  Patient: "I have a     │
    │  • Skin                 │   │  severe headache and    │
    │  • Musculoskeletal      │   │  feel nauseous"         │
    │  • General              │   └────────────┬────────────┘
    └────────────┬────────────┘                │
                 │                             ▼
                 ▼                ┌─────────────────────────┐
    ┌─────────────────────────┐   │    NLP PROCESSING       │
    │  Select Specific        │   │  • Tokenization         │
    │  Symptoms               │   │  • Entity Extraction    │
    │  □ Headache             │   │  • Symptom Mapping      │
    │  □ Migraine             │   │                         │
    │  □ Dizziness            │   │  GPT/Local LLM:         │
    │  □ Nausea               │   │  {                      │
    │  ☑ Rate Severity (1-10) │   │    "symptoms": [...],   │
    └────────────┬────────────┘   │    "questions": [...],  │
                 │                │    "specialties": [...]  │
                 │                │  }                       │
                 │                └────────────┬────────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ▼
              ┌─────────────────────────────────────┐
              │        ML CLASSIFICATION ENGINE      │
              │                                     │
              │  Input: Symptom text/selections     │
              │           │                         │
              │           ▼                         │
              │  ┌─────────────────────────┐       │
              │  │  TF-IDF Vectorization   │       │
              │  │  • Term Frequency       │       │
              │  │  • Inverse Document     │       │
              │  │    Frequency            │       │
              │  └───────────┬─────────────┘       │
              │              │                     │
              │              ▼                     │
              │  ┌─────────────────────────┐       │
              │  │  Random Forest          │       │
              │  │  Classifier             │       │
              │  │  • 100+ trees           │       │
              │  │  • Majority voting      │       │
              │  └───────────┬─────────────┘       │
              │              │                     │
              │              ▼                     │
              │  Output: Specialty + Confidence    │
              │  • Neurology (87%)                 │
              │  • General Physician (65%)         │
              └──────────────┬──────────────────────┘
                             │
                             ▼
              ┌─────────────────────────────────────┐
              │      TRIAGE RESULTS DISPLAY         │
              │                                     │
              │  Recommended Specialty: NEUROLOGY   │
              │  Confidence: 87%                    │
              │                                     │
              │  Possible Conditions:               │
              │  • Migraine                         │
              │  • Tension Headache                 │
              │                                     │
              │  Urgency: MODERATE                  │
              │                                     │
              │  [Save Assessment] [Book Doctor]    │
              └─────────────────────────────────────┘
```

**ML Model Technical Details:**
```python
# Training Pipeline
1. Load symptom-specialty dataset (100+ mappings)
2. Preprocess text (lowercase, remove punctuation)
3. TF-IDF Vectorization (max_features=1000)
4. Train RandomForestClassifier (n_estimators=100)
5. Save model using joblib

# Prediction Pipeline
1. Receive user symptoms
2. Preprocess input
3. Vectorize using trained TF-IDF
4. Predict using Random Forest
5. Return top 3 specialties with confidence scores
```

### 5.4 Appointment Booking and Payment Process

```
┌─────────────────────────────────────────────────────────────────┐
│            APPOINTMENT BOOKING WITH M-PESA PAYMENT               │
└─────────────────────────────────────────────────────────────────┘

STEP 1: DOCTOR SELECTION
────────────────────────
Patient → Browse Doctors by Specialty
          │
          ├── Filter by: Specialization, Rating, Fee, Availability
          │
          ├── View Doctor Profile:
          │     • Credentials (Verified ✓)
          │     • Experience
          │     • Consultation Fee
          │     • Patient Reviews & Ratings
          │
          └── Click "Book Appointment"

STEP 2: TIME SLOT SELECTION
───────────────────────────
          │
          ▼
    ┌─────────────────────────────────────┐
    │     Doctor Availability Calendar     │
    │                                      │
    │  Monday 03/02/2026                   │
    │  ┌──────┐ ┌──────┐ ┌──────┐        │
    │  │09:00 │ │09:30 │ │10:00 │ ...    │
    │  │ FREE │ │BOOKED│ │ FREE │        │
    │  └──────┘ └──────┘ └──────┘        │
    │                                      │
    │  Selected: Monday, 09:00 - 09:30    │
    └────────────────┬────────────────────┘
                     │
                     ▼

STEP 3: SYMPTOM DESCRIPTION
───────────────────────────
    ┌─────────────────────────────────────┐
    │  Describe your symptoms:            │
    │  ┌─────────────────────────────┐   │
    │  │ "I have been experiencing    │   │
    │  │  severe headaches for 3 days │   │
    │  │  with nausea and light       │   │
    │  │  sensitivity..."             │   │
    │  └─────────────────────────────┘   │
    │                                      │
    │  Consultation Fee: KES 1,500         │
    │                                      │
    │  [Proceed to Payment]               │
    └────────────────┬────────────────────┘
                     │
                     ▼

STEP 4: M-PESA PAYMENT FLOW
───────────────────────────
    ┌─────────────────────────────────────────────────────────────┐
    │                     M-PESA INTEGRATION                       │
    └─────────────────────────────────────────────────────────────┘
    
    SYSTEM (Backend)                          PATIENT (Phone)
    ────────────────                          ─────────────────
          │
          │  1. Create MpesaTransaction record
          │     status: "pending"
          │
          │  2. Request OAuth Token
          ├──────────────────────────────────►  Safaricom API
          │◄──────────────────────────────────  Access Token
          │
          │  3. Generate Security Password
          │     Base64(Shortcode + Passkey + Timestamp)
          │
          │  4. Send STK Push Request
          ├──────────────────────────────────►  Safaricom API
          │                                          │
          │                                          │  5. Push to Phone
          │                                          ├────────────────►
          │                                          │
          │                                     ┌────────────────┐
          │                                     │  M-PESA PROMPT │
          │                                     │                │
          │                                     │  Pay KES 1,500 │
          │                                     │  to HealthLink │
          │                                     │                │
          │                                     │ Enter M-Pesa   │
          │                                     │ PIN: ****      │
          │                                     │                │
          │                                     │ [Cancel] [OK]  │
          │                                     └────────┬───────┘
          │                                              │
          │                                     6. Patient enters PIN
          │                                              │
          │  7. Callback received                        │
          │◄─────────────────────────────────────────────┘
          │
          │  8. Verify callback signature
          │
          │  9. Update transaction status
          │     ResultCode == 0 → "success"
          │     ResultCode != 0 → "failed"
          │
          │  10. If successful:
          │      • Update appointment status to "confirmed"
          │      • Create notification for patient
          │      • Create notification for doctor
          │      • Send SMS confirmation to both parties
          │
          ▼
    ┌─────────────────────────────────────┐
    │      APPOINTMENT CONFIRMED!          │
    │                                      │
    │  Appointment ID: APT-2026-0130-001  │
    │  Doctor: Dr. Amina Hassan           │
    │  Date: Monday, 03/02/2026           │
    │  Time: 09:00 - 09:30                │
    │  Payment: KES 1,500 ✓               │
    │  M-Pesa Receipt: QHK7XXXXX          │
    │                                      │
    │  SMS sent to: 0797XXXXXX            │
    └─────────────────────────────────────┘
```

### 5.5 Real-Time Communication Process

```
┌─────────────────────────────────────────────────────────────────┐
│           REAL-TIME MESSAGING WITH SMS FALLBACK                  │
└─────────────────────────────────────────────────────────────────┘

SCENARIO: Doctor sends message to Patient

    ┌─────────────┐                         ┌─────────────┐
    │   DOCTOR    │                         │   PATIENT   │
    │  (Online)   │                         │  (Offline)  │
    └──────┬──────┘                         └──────┬──────┘
           │                                       │
           │  1. Type and send message             │
           │  "Your test results are ready.        │
           │   Please schedule a follow-up."       │
           │                                       │
           ▼                                       │
    ┌─────────────────────────────────────────────────────────────┐
    │                    HEALTHLINK SERVER                         │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │  2. Save message to database                                 │
    │     Message {                                                │
    │       conversation: 42,                                      │
    │       sender: "dr_amina",                                    │
    │       content: "Your test results...",                       │
    │       timestamp: "2026-01-30 10:15:00",                     │
    │       is_read: false                                         │
    │     }                                                        │
    │                                                              │
    │  3. Create in-app notification                               │
    │                                                              │
    │  4. Check patient's online status                            │
    │     └── Patient OFFLINE                                      │
    │                                                              │
    │  5. Trigger SMS notification                                 │
    │     ┌─────────────────────────────────────┐                 │
    │     │  SMS GATEWAY (Africa's Talking)     │                 │
    │     │                                     │                 │
    │     │  To: +254797754321                  │                 │
    │     │  From: HealthLink                   │                 │
    │     │  Message: "New message from         │                 │
    │     │  Dr. Amina on HealthLink:           │                 │
    │     │  'Your test results are ready...'   │                 │
    │     │  Login to view: healthlink.co.ke"   │                 │
    │     └─────────────────────────────────────┘                 │
    │                                                              │
    └──────────────────────────────┬───────────────────────────────┘
                                   │
                                   │  6. SMS delivered
                                   ▼
                            ┌─────────────┐
                            │   PATIENT   │
                            │   (Phone)   │
                            ├─────────────┤
                            │  📱 SMS     │
                            │  New message│
                            │  from       │
                            │  HealthLink │
                            └─────────────┘
```

**SMS Notification Triggers:**
| Event | SMS to Patient | SMS to Doctor |
|-------|---------------|---------------|
| Appointment Booked | ✓ | ✓ |
| Appointment Confirmed | ✓ | ✓ |
| Appointment Cancelled | ✓ | ✓ |
| New Message (if offline) | ✓ | ✓ |
| Prescription Created | ✓ | - |
| Payment Received | ✓ | ✓ |
| Video Call Incoming | ✓ | ✓ |
| Appointment Reminder (1hr before) | ✓ | ✓ |

### 5.6 Video Consultation Process

```
┌─────────────────────────────────────────────────────────────────┐
│              WEBRTC VIDEO CONSULTATION FLOW                      │
└─────────────────────────────────────────────────────────────────┘

INITIATOR: Doctor                    RECEIVER: Patient

    ┌─────────────┐                  ┌─────────────┐
    │   DOCTOR    │                  │   PATIENT   │
    │  Browser    │                  │   Browser   │
    └──────┬──────┘                  └──────┬──────┘
           │                                │
           │  1. Click "Start Video Call"   │
           │                                │
           ▼                                │
    ┌─────────────────────────────────────────────────────────────┐
    │                    SIGNALING SERVER                          │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │  2. Create VideoCall record                                  │
    │     {                                                        │
    │       room_id: "hl-call-abc123",                            │
    │       caller: doctor_id,                                     │
    │       receiver: patient_id,                                  │
    │       status: "initiated"                                    │
    │     }                                                        │
    │                                                              │
    │  3. Generate SDP Offer (Session Description Protocol)        │
    │     - Video codec: VP8/VP9                                   │
    │     - Audio codec: Opus                                      │
    │     - ICE candidates                                         │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
           │                                │
           │  4. Store caller_offer         │
           │  5. Notify patient             │
           │────────────────────────────────►
           │                                │
           │                         6. Patient sees
           │                         "Incoming Call from
           │                          Dr. Amina"
           │                                │
           │                         7. Click "Accept"
           │                                │
           │◄────────────────────────────────
           │  8. Generate SDP Answer        │
           │  9. Exchange ICE candidates    │
           │                                │
    ┌─────────────────────────────────────────────────────────────┐
    │                    PEER-TO-PEER CONNECTION                   │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │  10. ICE Candidate Exchange                                  │
    │      STUN Server: stun.l.google.com:19302                   │
    │                                                              │
    │  11. Connection Established                                  │
    │      Status: "ongoing"                                       │
    │                                                              │
    │  12. Media Streams Active                                    │
    │      ┌─────────┐        ┌─────────┐                        │
    │      │ Doctor  │◄──────►│ Patient │                        │
    │      │ Camera  │  P2P   │ Camera  │                        │
    │      │ Audio   │        │ Audio   │                        │
    │      └─────────┘        └─────────┘                        │
    │                                                              │
    │  13. Call ends                                               │
    │      Duration recorded: 25 minutes                           │
    │      Status: "ended"                                         │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
```

### 5.7 Electronic Prescription Process

```
┌─────────────────────────────────────────────────────────────────┐
│              ELECTRONIC PRESCRIPTION WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘

STEP 1: DOCTOR CREATES PRESCRIPTION
────────────────────────────────────
Doctor → Prescriptions → Create New
          │
          ├── Select Patient (from appointments)
          │
          ├── Add Medications:
          │   ┌────────────────────────────────────────┐
          │   │  Medication Database Search            │
          │   │  🔍 "Para..."                          │
          │   │                                        │
          │   │  Results:                              │
          │   │  • Paracetamol 500mg (Tablet)         │
          │   │  • Paracetamol 250mg/5ml (Syrup)      │
          │   │  • Panadol Extra 500mg (Tablet)       │
          │   └────────────────────────────────────────┘
          │
          │   Selected: Paracetamol 500mg
          │   Dosage: 2 tablets
          │   Frequency: 3 times daily
          │   Duration: 5 days
          │   Instructions: "Take after meals"
          │
          ├── Add Diagnosis Notes
          │   "Tension headache, likely stress-related"
          │
          ├── Add Doctor Notes
          │   "Follow up in 1 week if symptoms persist"
          │
          └── Submit → Prescription Status: ACTIVE

STEP 2: SYSTEM PROCESSING
─────────────────────────
          │
          ▼
    ┌─────────────────────────────────────┐
    │  Prescription Generated             │
    │                                     │
    │  RX-2026-0130-001                   │
    │  ─────────────────                  │
    │                                     │
    │  Patient: Hassan Mohammed           │
    │  Date: 30/01/2026                   │
    │                                     │
    │  Medications:                       │
    │  1. Paracetamol 500mg              │
    │     Dosage: 2 tablets              │
    │     Frequency: 3x daily            │
    │     Duration: 5 days               │
    │                                     │
    │  Diagnosis: Tension headache        │
    │                                     │
    │  Doctor: Dr. Amina Hassan           │
    │  License: MED/2020/12345           │
    │                                     │
    │  [DIGITAL SIGNATURE]                │
    └─────────────────────────────────────┘
          │
          ├── Create notification for patient
          ├── Send SMS: "New prescription from Dr. Amina"
          │
          ▼

STEP 3: PATIENT VIEWS PRESCRIPTION
──────────────────────────────────
Patient → Dashboard → My Prescriptions
          │
          ├── View prescription details
          ├── Download/Print prescription
          │
          └── Take to pharmacy for dispensing

STEP 4: DISPENSING WORKFLOW (Future Enhancement)
────────────────────────────────────────────────
Pharmacy → Scan QR Code → Verify Prescription
          │
          ├── Mark as "Dispensed"
          ├── Record dispensing details
          │
          └── Status updated in system
```

---

## 6. TECHNICAL IMPLEMENTATION DETAILS

### 6.1 Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Backend Framework** | Django 4.x (Python) | Robust ORM, built-in security, rapid development |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript | Responsive design, cross-browser compatibility |
| **Database** | PostgreSQL / SQLite | Reliable, ACID compliant, scalable |
| **Machine Learning** | Scikit-learn, TF-IDF, Random Forest | Proven classification algorithms |
| **NLP/Chatbot** | OpenAI GPT-3.5 / Local LLM | Natural language understanding |
| **Video Calls** | WebRTC, PeerJS | Peer-to-peer, low latency |
| **Payments** | M-Pesa Daraja API | Local mobile money integration |
| **SMS Gateway** | Africa's Talking API | Reliable Kenya SMS delivery |
| **Web Server** | Gunicorn + Nginx | Production-grade serving |

### 6.2 Database Schema (Key Tables)

```sql
-- Core User Tables
CustomUser (
    id, username, email, phone_number, user_type, 
    date_of_birth, is_active, date_joined
)

DoctorProfile (
    user_id, license_number, specialization, 
    years_of_experience, consultation_fee, 
    is_verified, verification_status, verified_by
)

PatientProfile (
    user_id, blood_type, allergies, 
    medical_history, emergency_contact
)

-- Appointment Management
DoctorAvailability (
    doctor_id, day_of_week, start_time, 
    end_time, slot_duration, is_available
)

Appointment (
    id, patient_id, doctor_id, specialty_id,
    appointment_date, symptoms, status,
    created_at, updated_at
)

-- Triage System
TriageSession (
    id, user_id, symptoms, severity,
    predicted_specialty, confidence_score,
    triage_type, created_at
)

-- Communication
Conversation (
    id, patient_id, doctor_id, 
    appointment_id, created_at
)

Message (
    id, conversation_id, sender_id, 
    content, timestamp, is_read
)

VideoCall (
    id, room_id, caller_id, receiver_id,
    status, started_at, ended_at, duration
)

-- Payments
MpesaTransaction (
    id, user_id, appointment_id, amount,
    phone_number, mpesa_receipt_number,
    status, checkout_request_id, created_at
)

-- Prescriptions
Prescription (
    id, prescription_number, doctor_id, patient_id,
    diagnosis, notes, status, created_at
)

PrescriptionItem (
    id, prescription_id, medication_id,
    dosage, frequency, duration, instructions
)

-- Notifications
Notification (
    id, user_id, notification_type, title,
    message, link, is_read, created_at
)

SMSLog (
    id, recipient_phone, message, status,
    gateway_response, sent_at
)
```

### 6.3 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/login/` | POST | User authentication |
| `/api/auth/register/` | POST | User registration |
| `/api/triage/analyze/` | POST | ML symptom analysis |
| `/api/triage/chat/` | POST | Chatbot interaction |
| `/api/doctors/` | GET | List verified doctors |
| `/api/doctors/{id}/availability/` | GET | Doctor's available slots |
| `/api/appointments/` | GET, POST | Manage appointments |
| `/api/payments/mpesa/stk-push/` | POST | Initiate M-Pesa payment |
| `/api/payments/mpesa/callback/` | POST | M-Pesa callback handler |
| `/api/messages/{conversation_id}/` | GET, POST | Conversation messages |
| `/api/video/initiate/` | POST | Start video call |
| `/api/prescriptions/` | GET, POST | Manage prescriptions |
| `/api/notifications/` | GET | User notifications |

### 6.4 Security Implementation

| Security Measure | Implementation |
|------------------|----------------|
| Password Hashing | Django PBKDF2 with SHA256 |
| Session Management | Secure, HttpOnly cookies |
| CSRF Protection | Django middleware, token validation |
| XSS Prevention | Template auto-escaping |
| SQL Injection | Django ORM parameterized queries |
| HTTPS | TLS 1.3 encryption |
| Input Validation | Django Forms, serializers |
| Rate Limiting | Django Ratelimit |
| API Authentication | Token-based (DRF) |

---

## 7. SMS NOTIFICATION SYSTEM (NEW FEATURE)

### 7.1 Overview

The SMS notification system ensures patients and doctors receive critical updates even when they are not actively using the HealthLink platform. This addresses the reality that users may not always have the website open or may be in areas with limited internet connectivity.

### 7.2 SMS Gateway Integration

**Provider: Africa's Talking**
- Reliable delivery across Kenyan networks
- Competitive pricing
- Delivery reports
- Two-way messaging capability

### 7.3 Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMS NOTIFICATION SERVICE                      │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  TRIGGER EVENT  │
    │  (New Message,  │
    │  Appointment,   │
    │  Prescription)  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐      ┌─────────────────┐
    │  Check User's   │──No──►  Send In-App    │
    │  Online Status  │      │  Notification   │
    └────────┬────────┘      │  Only           │
             │               └─────────────────┘
             │ Offline
             ▼
    ┌─────────────────┐
    │  Format SMS     │
    │  Message        │
    │  (160 chars)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │      AFRICA'S TALKING API           │
    │                                     │
    │  POST /version1/messaging           │
    │  {                                  │
    │    "username": "healthlink",        │
    │    "to": ["+254797754321"],         │
    │    "message": "...",                │
    │    "from": "HealthLink"             │
    │  }                                  │
    └────────────────┬────────────────────┘
                     │
                     ▼
    ┌─────────────────┐
    │  Log SMS in     │
    │  Database       │
    │  (Audit Trail)  │
    └─────────────────┘
```

### 7.4 SMS Templates

| Event | SMS Template |
|-------|--------------|
| Appointment Confirmed | "HealthLink: Your appointment with Dr. {name} on {date} at {time} is confirmed. Fee: KES {amount} paid. Ref: {appointment_id}" |
| New Message | "HealthLink: New message from {sender}. Login to view: healthlink.co.ke/messages" |
| Prescription Ready | "HealthLink: Dr. {name} has issued you a prescription. View at: healthlink.co.ke/prescriptions/{id}" |
| Appointment Reminder | "HealthLink Reminder: Your appointment with Dr. {name} is in 1 hour ({time}). Don't forget!" |
| Video Call | "HealthLink: Incoming video call from {caller}. Open HealthLink to join." |

---

## 8. TESTING STRATEGY

### 8.1 Testing Levels

| Level | Description | Tools |
|-------|-------------|-------|
| Unit Testing | Individual function testing | pytest, Django TestCase |
| Integration Testing | Module interaction testing | Django TestClient |
| System Testing | End-to-end workflows | Selenium |
| UAT | User acceptance testing | Real users, feedback forms |
| Security Testing | Vulnerability assessment | OWASP ZAP |
| Performance Testing | Load and stress testing | Locust |

### 8.2 Sample Test Cases

| ID | Module | Test Case | Expected Result |
|----|--------|-----------|-----------------|
| TC001 | Users | Patient registration with valid data | Account created, profile created |
| TC002 | Users | Login with invalid credentials | Error message displayed |
| TC003 | Triage | ML prediction for headache symptoms | Returns Neurology specialty |
| TC004 | Appointments | Book available slot | Appointment created as pending |
| TC005 | Payments | M-Pesa STK Push initiation | STK prompt on user phone |
| TC006 | Payments | Payment callback processing | Appointment status updated |
| TC007 | Messaging | Send message when receiver offline | SMS notification triggered |
| TC008 | Video | WebRTC connection establishment | Peer-to-peer call connected |
| TC009 | Prescriptions | Create prescription with medications | Prescription saved, patient notified |
| TC010 | Admin | Verify doctor credentials | Doctor status updated to verified |

---

## 9. PROJECT TIMELINE

| Phase | Duration | Activities |
|-------|----------|------------|
| **Phase 1: Research & Design** | Week 1-2 | Literature review, requirements gathering, system design |
| **Phase 2: Core Development** | Week 3-6 | User management, authentication, basic UI |
| **Phase 3: AI Module** | Week 7-8 | ML model training, chatbot integration |
| **Phase 4: Payment Integration** | Week 9-10 | M-Pesa API, payment workflow |
| **Phase 5: Communication** | Week 11-12 | Messaging, video calls, SMS gateway |
| **Phase 6: Advanced Features** | Week 13-14 | Prescriptions, admin dashboard |
| **Phase 7: Testing** | Week 15-16 | Unit, integration, UAT testing |
| **Phase 8: Documentation** | Week 17 | User manuals, technical docs |
| **Phase 9: Deployment** | Week 18 | Production deployment, final presentation |

---

## 10. EXPECTED OUTCOMES

### 10.1 Technical Deliverables

1. Fully functional web application with 10+ integrated modules
2. Trained ML model for symptom triage
3. Integrated M-Pesa payment system
4. WebRTC video consultation capability
5. SMS notification gateway integration
6. Comprehensive documentation

### 10.2 Key Performance Indicators

| Metric | Target |
|--------|--------|
| System Uptime | > 99% |
| Page Load Time | < 3 seconds |
| ML Triage Accuracy | > 80% |
| Payment Success Rate | > 95% |
| SMS Delivery Rate | > 98% |
| User Satisfaction | > 4/5 rating |

### 10.3 Impact Assessment

- **Healthcare Access**: Reduced hospital visits, access to specialists regardless of location
- **Efficiency**: Streamlined scheduling, digital prescriptions, automated payments
- **Quality**: Verified providers, structured feedback, consistent documentation
- **Innovation**: Demonstration of AI application in healthcare for Kenyan context

---

## 11. CONCLUSION

HealthLink represents a comprehensive, technically sophisticated solution to healthcare delivery challenges in Kenya. By integrating Artificial Intelligence for symptom triage, mobile money payments for accessibility, WebRTC for real-time communication, and SMS gateways for reliable notifications, the platform creates a complete digital healthcare ecosystem.

The project demonstrates practical application of:
- Machine Learning classification algorithms
- Third-party API integration (M-Pesa, SMS gateways)
- Real-time communication technologies (WebRTC)
- Modern web development frameworks (Django)
- Security best practices for healthcare data

The addition of SMS notification capabilities ensures that the platform remains accessible and functional even in scenarios where internet connectivity is limited, addressing a real-world constraint in the Kenyan context.

---

## 12. REFERENCES

1. World Health Organization. (2022). *Telemedicine: Opportunities and Developments in Member States*.
2. Safaricom. (2024). *M-Pesa Daraja API Documentation*. developer.safaricom.co.ke
3. Africa's Talking. (2024). *SMS API Documentation*. africastalking.com/docs
4. Django Software Foundation. (2024). *Django Documentation*. docs.djangoproject.com
5. Scikit-learn Developers. (2024). *Scikit-learn: Machine Learning in Python*. scikit-learn.org
6. WebRTC Project. (2024). *WebRTC API Documentation*. webrtc.org
7. Semigran, H.L., et al. (2015). "Evaluation of symptom checkers for self-diagnosis and triage". *BMJ*.
8. Kenya Medical Practitioners and Dentists Council. (2023). *Guidelines for Telemedicine Practice*.

---

**Prepared by:** Adan Hassan Adi  
**Supervised by:** Dr. Mbogholi  
**Department of Computer Science, Pwani University**  
**January 2026**
