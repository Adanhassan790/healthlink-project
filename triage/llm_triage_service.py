# triage/llm_triage_service.py - HYBRID TRIAGE SERVICE
# Uses Groq API (FREE - no credit card needed) with fallback to advanced rule-based system
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)


class LLMTriageService:
    """
    Hybrid triage service using Groq's LLM (free API) with smart fallback.
    Gracefully degrades to rule-based triage when API is unavailable.
    """

    def __init__(self, use_groq=True):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.use_groq = use_groq and self.api_key is not None
        self.client = None
        # Use a stable, widely-available Groq model - llama-3.1-8b-instant is always available on free tier
        self.model = "llama-3.1-8b-instant"
        self.conversation_history = []
        self.symptoms_identified = []
        self.symptom_duration = None  # Store actual duration from user input
        self.state = 'greeting'  # greeting -> symptom_gathering -> details -> recommendation
        self.api_available = False
        
        # Try to initialize Groq client
        if self.use_groq:
            try:
                # Initialize Groq client with minimal config - no proxy arguments
                self.client = Groq(api_key=self.api_key, timeout=20)
                self.api_available = True
                logger.info("✅ Groq API client initialized successfully (FREE - no payment needed!)")
            except TypeError as e:
                if 'proxies' in str(e):
                    logger.warning(f"⚠️ Groq initialization failed due to proxy config: {e}")
                    # Try without proxy settings
                    try:
                        self.client = Groq(api_key=self.api_key)
                        self.api_available = True
                        logger.info("✅ Groq API client initialized (without proxies)")
                    except Exception as e2:
                        logger.error(f"❌ Groq client failed even without proxies: {e2}")
                        self.api_available = False
                else:
                    logger.warning(f"⚠️ Groq initialization failed: {e}. Using fallback mode.")
                    self.api_available = False
            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {e}. Using fallback mode.")
                self.api_available = False

    def system_prompt(self):
        """Medical triage system prompt with detailed instructions"""
        # Count turns to help Groq know when to make recommendation
        turn_count = len([m for m in self.conversation_history if m['role'] == 'user'])
        
        turn_instruction = ""
        if turn_count >= 3:
            turn_instruction = "\n\n*** IMPORTANT: This is turn #%d of the conversation. You should NOW make a recommendation. Set ready_for_recommendation to TRUE and provide a recommendation with primary_specialty. ***" % (turn_count + 1)
        
        return """You are a professional medical triage AI assistant.

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:
1. You ALWAYS respond with ONLY valid JSON (no markdown, no code blocks, no extra text)
2. You NEVER include ```json or ``` markers
3. Your response is PURE JSON that can be parsed directly

REQUIRED JSON STRUCTURE (exact field names):
{
  "thinking": "Your brief analysis",
  "extracted_symptoms": ["symptom1", "symptom2"],
  "severity_assessment": "low|medium|high",
  "emergency_alert": true/false,
  "next_question": "Your response to patient",
  "ready_for_recommendation": false/true,
  "recommendation": null or {"primary_specialty": "Specialty Name", "urgency": "routine|urgent|emergency", "reasoning": "Why this specialty"}
}

YOUR TRIAGE PROCESS:
1. LISTEN to patient symptoms
2. GATHER details: severity, duration, location, frequency
3. IDENTIFY patterns in symptoms
4. RECOMMEND appropriate specialty (only when ready)
5. ALERT if emergency

CRITICAL RULES:
- NEVER diagnose - only triage to specialty
- ALWAYS ask 1-2 clarifying questions (unless making recommendation)
- Detect EMERGENCIES: chest pain, difficulty breathing, loss of consciousness, severe bleeding, severe trauma
- Be empathetic and professional
- After gathering 3-4 key symptoms + severity info, provide recommendation
- Turn 1-2: Ask clarifying questions, gather symptoms
- Turn 3+: MAKE RECOMMENDATION with primary_specialty and reasoning

SPECIALTY MAPPINGS:
- Chest pain, heart issues -> Cardiology
- Headache, dizziness, neurological -> Neurology  
- Cough, breathing issues -> Pulmonology
- Stomach, digestive issues -> Gastroenterology
- Rash, skin issues -> Dermatology
- Joint, bone pain -> Orthopedics
- Mental health, stress, depression -> Psychiatry
- ENT issues -> ENT
- Eye issues -> Ophthalmology
- Default -> General Medicine""" + turn_instruction

    def process_patient_message(self, user_message: str) -> dict:
        """
        Process a patient message intelligently.
        Tries Groq API first, falls back to rule-based system if API unavailable.
        ALWAYS checks for mental health crises and provides crisis resources.
        """
        try:
            # CRITICAL: Check for mental health crisis FIRST
            if self._detect_mental_health_crisis(user_message):
                logger.critical(f"🚨 MENTAL HEALTH CRISIS DETECTED: {user_message[:50]}...")
                return self._create_crisis_response(user_message)
            
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Try Groq first if available
            if self.api_available and self.client:
                logger.info(f"✅ USING GROQ AI for: '{user_message[:50]}...'")
                response = self._process_with_groq(user_message)
            else:
                # Fallback to rule-based system
                logger.info(f"⚠️ USING FALLBACK RULES for: '{user_message[:50]}...' (api_available={self.api_available}, client={self.client is not None})")
                response = self._process_with_fallback(user_message)
            
            # Check if crisis was detected in the AI response
            if response.get('emergency_alert') and self._detect_mental_health_crisis(response.get('next_question', '')):
                response['is_mental_health_crisis'] = True
                response['crisis_resources'] = self._get_crisis_resources()
            
            return response

        except Exception as e:
            logger.error(f"Error in process_patient_message: {e}")
            return self._create_error_response(f"Processing error: {str(e)}")
    
    def _create_crisis_response(self, user_message: str) -> dict:
        """Create immediate crisis response with resources"""
        logger.critical("Creating crisis response with emergency resources...")
        return {
            "thinking": "Mental health crisis detected - providing immediate crisis resources",
            "extracted_symptoms": ["Suicidal ideation", "Mental health crisis"],
            "severity_assessment": "high",
            "emergency_alert": True,
            "is_mental_health_crisis": True,
            "next_question": "I'm concerned about your safety. Please reach out for help immediately. Crisis counselors are available 24/7.",
            "ready_for_recommendation": False,
            "recommendation": None,
            "crisis_resources": self._get_crisis_resources()
        }
    
    def _get_crisis_resources(self) -> dict:
        """Get mental health crisis resources and hotlines"""
        return {
            "title": "🚨 Mental Health Crisis Support",
            "message": "You are not alone. Help is available right now.",
            "hotlines": [
                {
                    "name": "National Suicide Prevention Lifeline (US)",
                    "number": "988",
                    "available": "24/7 - Call or text"
                },
                {
                    "name": "Crisis Text Line",
                    "number": "Text HOME to 741741",
                    "available": "24/7"
                },
                {
                    "name": "International Association for Suicide Prevention",
                    "url": "https://www.iasp.info/resources/Crisis_Centres/",
                    "available": "Find local resources"
                }
            ],
            "immediate_actions": [
                "Tell someone you trust how you're feeling",
                "Call emergency services (911 in US) if in immediate danger",
                "Go to the nearest emergency room",
                "Remove access to means of self-harm",
                "Stay with someone until you feel safe"
            ]
        }

    def _process_with_groq(self, user_message: str) -> dict:
        """Process using Groq API (FREE - no payment needed)"""
        try:
            logger.info(f"🤖 Groq API call started with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt()},
                ] + self.conversation_history,
                temperature=0.3,  # Low for consistency
                max_tokens=500,
                timeout=20  # 20 second timeout
            )

            ai_message = response.choices[0].message.content
            logger.info(f"✅ Groq response received: {ai_message[:80]}...")

            # Parse JSON response
            analysis = self._parse_json_response(ai_message)

            # Check if this is a mental health crisis (CRITICAL CHECK)
            # Check both the user message AND the AI analysis for crisis indicators
            if self._detect_mental_health_crisis(user_message) or self._detect_mental_health_crisis_in_analysis(analysis):
                logger.critical(f"🚨 MENTAL HEALTH CRISIS DETECTED IN GROQ RESPONSE")
                analysis['is_mental_health_crisis'] = True
                analysis['crisis_resources'] = self._get_crisis_resources()

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })

            # Update state
            self._update_state(analysis)
            return analysis

        except Exception as e:
            logger.error(f"❌ Groq API ERROR: {type(e).__name__}: {str(e)}")
            logger.error(f"Falling back to rule-based system due to: {e}")
            self.api_available = False
            return self._process_with_fallback(user_message)

    def _parse_json_response(self, response_text: str) -> dict:
        """
        Robustly parse JSON from response, handling various formats.
        """
        try:
            # Try direct parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try removing markdown code blocks
        for marker in ["```json", "```"]:
            if marker in response_text:
                try:
                    start_idx = response_text.find(marker) + len(marker)
                    end_idx = response_text.find("```", start_idx)
                    if end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx].strip()
                        return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        # Last resort: extract JSON object
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        # If all parsing fails, create structured response from text
        logger.warning(f"Could not parse JSON, falling back to text analysis")
        return self._create_response_from_text(response_text)

    def _create_response_from_text(self, text: str) -> dict:
        """Create structured response when JSON parsing fails"""
        symptoms = self._extract_symptoms_from_text(text)
        return {
            "thinking": "Processing natural language response",
            "extracted_symptoms": symptoms,
            "severity_assessment": self._assess_severity_from_text(text),
            "emergency_alert": self._detect_emergency_from_text(text),
            "next_question": text[:500],  # Use text as response
            "ready_for_recommendation": len(symptoms) >= 3,
            "recommendation": None
        }

    def _process_with_fallback(self, user_message: str) -> dict:
        """
        Process using rule-based system when API is unavailable.
        More reliable for board demo than broken API calls.
        Intelligently tracks conversation turns and adapts questions.
        """
        # Count conversation turns (how many times user has responded)
        turn_count = len([m for m in self.conversation_history if m['role'] == 'user'])
        
        # Extract symptoms from user message
        symptoms = self._extract_symptoms_from_text(user_message)
        self.symptoms_identified.extend([s for s in symptoms if s not in self.symptoms_identified])

        # Extract duration from user message (e.g., "6 days", "2 weeks")
        duration = self._extract_duration_from_text(user_message)
        if duration:
            self.symptom_duration = duration

        # Assess severity and emergency
        severity = self._assess_severity_from_text(user_message)
        emergency = self._detect_emergency_from_text(user_message)

        # Generate appropriate response based on conversation state
        if emergency:
            self.state = 'emergency'
            response_text = "🚨 EMERGENCY DETECTED. Please seek immediate medical attention or call emergency services. You should visit the Emergency Room right now."
        
        # Decision logic based on symptoms AND conversation turns
        elif len(self.symptoms_identified) == 0:
            # No symptoms detected yet
            response_text = "I didn't quite catch that. Could you please describe your main symptom or health concern? For example: 'I have a cough' or 'I have chest pain'."
        
        elif len(self.symptoms_identified) >= 1 and turn_count == 1:
            # First user response - ask for details about the symptom
            symptom = self.symptoms_identified[0]
            response_text = f"I see you have {symptom}. To help better:\n- How long have you had this? (days, weeks)\n- How severe is it? (mild, moderate, severe)\n- Any other symptoms?"
        
        elif len(self.symptoms_identified) >= 1 and turn_count == 2:
            # Second response - ask about additional symptoms and impact
            response_text = f"Thank you for that information. You mentioned: {', '.join(self.symptoms_identified)}.\n- Do you have any fever, chills, or night sweats?\n- Any pain, swelling, or difficulty with specific activities?\n- How is this affecting your daily life?"
        
        # IMPORTANT: After turn 3+, make recommendation even if more symptoms could be gathered
        # User has had 3+ exchanges, we likely have enough info
        elif turn_count >= 3 and len(self.symptoms_identified) >= 1:
            # Sufficient conversation and symptoms - ready to recommend
            specialty, urgency_level = self._recommend_specialty_from_symptoms()
            
            self.state = 'recommendation'
            self.conversation_history.append({
                "role": "assistant",
                "content": f"Recommending {specialty}"
            })
            
            # Use actual duration if extracted, otherwise use generic message
            duration_text = self.symptom_duration if self.symptom_duration else "recently"
            
            return {
                "thinking": f"After {turn_count} exchanges with {len(self.symptoms_identified)} symptom(s), ready to recommend",
                "extracted_symptoms": self.symptoms_identified,
                "severity_assessment": severity,
                "emergency_alert": emergency,
                "next_question": f"Based on your symptoms of {', '.join(self.symptoms_identified)} lasting {duration_text}, I recommend seeing a {specialty} specialist for proper evaluation and care.",
                "ready_for_recommendation": True,
                "recommendation": {
                    "primary_specialty": specialty,
                    "urgency": urgency_level,
                    "reasoning": f"Your combination of symptoms warrant evaluation by a {specialty} specialist who can provide appropriate care."
                }
            }
        
        elif len(self.symptoms_identified) >= 2 and turn_count >= 2 and severity in ['medium', 'high']:
            # Multiple symptoms with reported severity - recommend now
            specialty, urgency_level = self._recommend_specialty_from_symptoms()
            
            self.state = 'recommendation'
            self.conversation_history.append({
                "role": "assistant",
                "content": f"Recommending {specialty}"
            })
            
            # Use actual duration if extracted
            duration_text = self.symptom_duration if self.symptom_duration else "for some time"
            
            return {
                "thinking": f"Based on {len(self.symptoms_identified)} symptom(s) with {severity} severity lasting {duration_text}",
                "extracted_symptoms": self.symptoms_identified,
                "severity_assessment": severity,
                "emergency_alert": emergency,
                "next_question": f"Based on your {severity.lower()} symptoms of {', '.join(self.symptoms_identified)} lasting {duration_text}, I recommend seeing a {specialty} specialist.",
                "ready_for_recommendation": True,
                "recommendation": {
                    "primary_specialty": specialty,
                    "urgency": urgency_level,
                    "reasoning": f"Your symptoms match {specialty} scope of practice."
                }
            }
        
        else:
            # Keep gathering more details (only for turns 2 to before turn 3)
            response_text = f"Thank you for that information. You mentioned: {', '.join(self.symptoms_identified)}.\n- Do you have any fever, chills, or night sweats?\n- Any pain, swelling, or difficulty with specific activities?\n- How is this affecting your daily life?"
        
        # Update state
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })

        return {
            "thinking": f"Turn {turn_count}, Found {len(self.symptoms_identified)} symptoms, gathering details",
            "extracted_symptoms": self.symptoms_identified,
            "severity_assessment": severity,
            "emergency_alert": emergency,
            "next_question": response_text,
            "ready_for_recommendation": False,
            "recommendation": None
        }

    def _recommend_specialty_from_symptoms(self) -> tuple:
        """
        Recommend specialty based on identified symptoms.
        Uses intelligent pattern matching and symptom combinations.
        Returns (specialty, urgency)
        """
        symptoms_lower = [s.lower() for s in self.symptoms_identified]
        
        # Specialty mapping with keyword patterns
        specialty_patterns = {
            'Cardiology': {
                'keywords': ['chest pain', 'palpitations', 'heart', 'rapid heartbeat', 'irregular heartbeat', 'cardiac'],
                'min_score': 1
            },
            'Neurology': {
                'keywords': ['headache', 'migraine', 'dizziness', 'seizure', 'numbness', 'tingling', 'vertigo', 'sensitivity to light', 'numb'],
                'min_score': 2
            },
            'Pulmonology': {
                'keywords': ['cough', 'breathing', 'asthma', 'lung', 'shortness of breath', 'wheezing', 'respiratory', 'throat'],
                'min_score': 1
            },
            'Gastroenterology': {
                'keywords': ['stomach', 'abdominal', 'diarrhea', 'vomiting', 'nausea', 'bloating', 'indigestion', 'heartburn', 'reflux', 'constipation'],
                'min_score': 2
            },
            'Dermatology': {
                'keywords': ['rash', 'itching', 'skin', 'acne', 'hives', 'burn', 'bruising', 'eczema'],
                'min_score': 1
            },
            'Orthopedics': {
                'keywords': ['joint pain', 'joint', 'arthritis', 'back pain', 'bone', 'knee pain', 'fracture', 'sprain', 'muscle pain'],
                'min_score': 2
            },
            'Psychiatry': {
                'keywords': ['anxiety', 'depression', 'stress', 'mental', 'panic', 'insomnia', 'mood', 'psycho'],
                'min_score': 1
            },
            'ENT': {
                'keywords': ['sore throat', 'ear pain', 'runny nose', 'stuffy nose', 'sinus', 'tonsil', 'throat', 'nasal'],
                'min_score': 1
            },
            'Ophthalmology': {
                'keywords': ['eye pain', 'blurred vision', 'red eyes', 'vision', 'opthal', 'ocular'],
                'min_score': 1
            },
        }

        # Score each specialty
        scores = {}
        for specialty, pattern in specialty_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                for symptom in symptoms_lower:
                    if keyword in symptom or symptom in keyword:
                        score += 1
            scores[specialty] = score

        # Get best match with minimum score consideration
        best_specialty = 'General Medicine'
        best_score = 0
        for specialty, pattern in specialty_patterns.items():
            if scores[specialty] >= pattern['min_score'] and scores[specialty] > best_score:
                best_specialty = specialty
                best_score = scores[specialty]

        # Determine urgency
        urgent_symptoms = ['chest pain', 'difficulty breathing', 'severe pain', 'severe', 'severe bleeding']
        is_urgent = any(any(u in symptom_lower for u in urgent_symptoms) for symptom_lower in symptoms_lower)
        
        if self._detect_emergency_from_text(' '.join(self.symptoms_identified)):
            urgency = 'emergency'
        elif is_urgent and best_specialty in ['Cardiology', 'Pulmonology']:
            urgency = 'urgent'
        else:
            urgency = 'routine'

        return best_specialty, urgency

    def _update_state(self, analysis: dict):
        """Update internal state based on analysis"""
        if analysis.get('extracted_symptoms'):
            new_symptoms = [s for s in analysis['extracted_symptoms'] if s not in self.symptoms_identified]
            self.symptoms_identified.extend(new_symptoms)

        if analysis.get('emergency_alert'):
            self.state = 'emergency'
        elif analysis.get('ready_for_recommendation'):
            self.state = 'recommendation'
        else:
            self.state = 'gathering'

    def _create_error_response(self, error_msg: str) -> dict:
        """Create error response"""
        return {
            "thinking": "Error occurred",
            "extracted_symptoms": [],
            "severity_assessment": "unknown",
            "emergency_alert": False,
            "next_question": "I apologize for the technical difficulty. Could you try describing your main symptom again?",
            "ready_for_recommendation": False,
            "error": error_msg
        }

    def _assess_severity_from_text(self, text: str) -> str:
        """Assess severity from text"""
        text_lower = text.lower()
        if any(w in text_lower for w in ['severe', 'critical', 'extreme', 'unbearable', 'excruciating']):
            return 'high'
        elif any(w in text_lower for w in ['moderate', 'quite', 'fairly', 'bad']):
            return 'medium'
        else:
            return 'low'

    def _detect_emergency_from_text(self, text: str) -> bool:
        """Detect emergency keywords - includes mental health crises"""
        emergency_keywords = [
            # Physical emergencies
            'chest pain', 'difficulty breathing', 'loss of consciousness', 'severe bleeding',
            'poisoning', 'choking', 'severe trauma', 'unconscious', 'can\'t breathe',
            'severe chest', 'heart attack', 'stroke', 'severe injury',
            # Mental health crises
            'suicidal', 'suicide', 'kill myself', 'harm myself', 'self harm',
            'want to die', 'end my life', 'end it all', 'hurt myself'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)

    def _detect_mental_health_crisis(self, text: str) -> bool:
        """Specifically detect mental health crisis situations"""
        crisis_keywords = [
            'suicidal', 'suicide', 'kill myself', 'kill me', 'harming myself', 'harm myself', 'self harm',
            'want to die', 'end my life', 'end it all', 'hurting myself', 'hurt myself', 'give up',
            'no point', 'worthless', 'hopeless', 'can\'t go on', 'end it',
            'cutting myself', 'cut myself', 'cut my',
            'hang myself', 'overdose', 'take my life', 'life is not worth',
            'nothing to live for', 'better off dead', 'don\'t want to live',
            'end my suffering', 'take my own life', 'take a lethal',
            'feel like dying', 'i am going to', 'going to end it',
            'harming me', 'hurting me', 'think of harm', 'think of hurt'
        ]
        
        text_lower = text.lower()
        
        # Check for crisis keywords
        for keyword in crisis_keywords:
            if keyword in text_lower:
                return True
                
        return False
    
    def _detect_mental_health_crisis_in_analysis(self, analysis: dict) -> bool:
        """
        Check if the AI analysis indicates a mental health crisis.
        Looks at extracted_symptoms and the next_question for crisis indicators.
        """
        # Check extracted symptoms for mental health crisis indicators
        symptoms = analysis.get('extracted_symptoms', [])
        for symptom in symptoms:
            if any(keyword in symptom.lower() for keyword in ['suicidal', 'ideation', 'self harm', 'self-harm']):
                return True
        
        # Check the next question for crisis language patterns
        next_q = analysis.get('next_question', '').lower()
        crisis_patterns = [
            'suicidal', 'harming yourself', 'harm yourself', 'crisis', 'emergency',
            'plan to harm', 'think about harm'
        ]
        
        for pattern in crisis_patterns:
            if pattern in next_q:
                return True
        
        return False


    def _extract_duration_from_text(self, text: str) -> str:
        """
        Extract duration from text (e.g., "6 days", "2 weeks", "a month")
        Returns: duration string like "6 days" or None if not found
        """
        import re
        
        text_lower = text.lower()
        
        # Pattern 1: Number + day/week/month/year (e.g., "6 days", "2 weeks")
        match = re.search(r'(\d+)\s*(day|week|month|year)s?', text_lower)
        if match:
            number = match.group(1)
            unit = match.group(2)
            # Pluralize if number != 1
            if number != '1':
                unit = unit + 's'
            return f"{number} {unit}"
        
        # Pattern 2: Written out numbers (e.g., "six days", "two weeks")
        text_words = text_lower.split()
        number_words = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'a': '1', 'couple': '2'
        }
        
        time_units = ['day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years']
        
        for i, word in enumerate(text_words):
            if word in number_words:
                # Check if next word is a time unit
                if i + 1 < len(text_words) and text_words[i + 1] in time_units:
                    num = number_words[word]
                    unit = text_words[i + 1]
                    return f"{num} {unit}"
        
        return None

    def _assess_urgency(self, symptoms: list, specialty: str) -> str:
        """
        Assess urgency level based on symptoms and specialty.
        Returns: 'routine', 'urgent', or 'emergency'
        """
        symptoms_lower = [s.lower() for s in symptoms]
        
        # Check for severe/urgent indicators
        severe_keywords = ['severe', 'unbearable', 'excruciating', 'critical', 'can\'t', 'bleeding']
        has_severe = any(keyword in ' '.join(symptoms_lower) for keyword in severe_keywords)
        
        # Specialty-based urgency
        urgent_specialties = {
            'Cardiology': True,  # Always urgent for heart
            'Pulmonology': True,  # Always urgent for breathing
            'Neurology': True,     # Always urgent for neurological
        }
        
        if has_severe or specialty in urgent_specialties:
            return 'urgent'
        else:
            return 'routine'

    def get_greeting(self) -> str:
        """Get initial greeting message"""
        if self.api_available and self.client:
            try:
                greeting_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a friendly medical triage AI. Greet the patient warmly and ask them to describe their main symptom or concern. Keep it brief and welcoming."}
                    ],
                    temperature=0.5,
                    max_tokens=150,
                    timeout=10
                )
                return greeting_response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Greeting API call failed: {e}")
                self.api_available = False

        # Fallback greeting
        return "👋 Hello! I'm your medical triage assistant. I'm here to help guide you to the right doctor. Could you please describe what brings you in today? What's your main symptom or health concern?"

    def reset_conversation(self):
        """Reset conversation for new patient"""
        self.conversation_history = []
        self.symptoms_identified = []
        self.symptom_duration = None
        self.state = 'greeting'

    def get_specialty_options(self) -> list:
        """Get list of available medical specialties"""
        return [
            "General Medicine",
            "Cardiology",
            "Neurology",
            "Psychiatry",
            "Dermatology",
            "Orthopedics",
            "Gastroenterology",
            "Pulmonology",
            "ENT (Otolaryngology)",
            "Ophthalmology",
            "Urology",
            "Gynecology",
            "Rheumatology",
            "Endocrinology",
            "Nephrology",
            "Infectious Disease",
            "Hematology",
            "Oncology"
        ]

    def _extract_symptoms_from_text(self, text: str) -> list:
        """Extract symptoms from text using comprehensive symptom database"""
        # Comprehensive symptom mappings with variations
        symptom_keywords = {
            'Fever': ['fever', 'temperature', 'temp', 'hot', 'warm'],
            'Cough': ['cough', 'coughing', 'hard cough'],
            'Headache': ['headache', 'head ache', 'head pain', 'head hurt'],
            'Migraine': ['migraine', 'severe headache'],
            'Nausea': ['nausea', 'nauseous', 'feeling sick', 'queasy'],
            'Vomiting': ['vomit', 'vomiting', 'threw up', 'sick'],
            'Diarrhea': ['diarrhea', 'diarrhoea', 'diarhoea', 'diahoea', 'loose stool', 'loose stools', 'loose motion'],
            'Chest Pain': ['chest pain', 'chest ache', 'chest hurt', 'cardiac pain'],
            'Shortness of Breath': ['shortness of breath', 'breathing problem', 'can\'t breathe', 'difficulty breathing'],
            'Dizziness': ['dizziness', 'dizzy', 'lightheaded', 'vertigo', 'spinning'],
            'Fatigue': ['fatigue', 'tired', 'exhausted', 'exhaustion', 'weak', 'weakness'],
            'Excessive Sweating': ['excess sweat', 'excessive sweating', 'sweating a lot', 'heavy sweating', 'heavy sweat'],
            'Sore Throat': ['sore throat', 'throat pain', 'throat hurt', 'pharyngitis'],
            'Runny Nose': ['runny nose', 'nasal discharge', 'nose running'],
            'Rash': ['rash', 'rashes', 'skin rash', 'itchy rash', 'body itching', 'itching all over', 'skin itching'],
            'Joint Pain': ['joint pain', 'joint ache', 'joint hurt', 'arthritis'],
            'Back Pain': ['back pain', 'back ache', 'spinal pain', 'lumbar pain'],
            'Abdominal Pain': ['abdominal pain', 'stomach pain', 'stomach ache', 'stomach issue', 'stomach problem', 'belly pain', 'tummy pain', 'pain in stomach', 'pain in belly', 'stomach ache', 'abdominal'],
            'Anxiety': ['anxiety', 'anxious', 'worried', 'nervousness', 'nervous'],
            'Depression': ['depression', 'depressed', 'sad', 'hopeless'],
            'Insomnia': ['insomnia', 'can\'t sleep', 'sleep problem', 'sleeping problem', 'hard time sleep', 'difficulty sleep', 'trouble sleep'],
            'Palpitations': ['palpitations', 'heart racing', 'heart pounding', 'rapid heartbeat'],
            'Rapid Heartbeat': ['rapid heartbeat', 'fast heartbeat', 'fast heart', 'tachycardia'],
            'Muscle Pain': ['muscle pain', 'muscle ache', 'myalgia', 'muscle hurt'],
            'Numbness': ['numbness', 'numb', 'paresthesia'],
            'Tingling': ['tingling', 'pins and needles', 'prickling'],
            'Dry Cough': ['dry cough', 'non productive cough'],
            'Wet Cough': ['wet cough', 'productive cough', 'phlegm', 'mucus'],
            'Wheezing': ['wheezing', 'wheeze', 'whistling breath'],
            'Stuffy Nose': ['stuffy nose', 'congestion', 'nasal congestion', 'blocked nose'],
            'Sneezing': ['sneezing', 'sneeze', 'sneezes'],
            'Sinus Pressure': ['sinus pressure', 'sinus pain', 'sinus ache'],
            'Loss of Smell': ['loss of smell', 'no smell', 'can\'t smell'],
            'Loss of Taste': ['loss of taste', 'no taste', 'can\'t taste'],
            'Indigestion': ['indigestion', 'upset stomach', 'stomach upset'],
            'Heartburn': ['heartburn', 'acid reflux', 'reflux', 'burning chest'],
            'Bloating': ['bloating', 'bloated', 'abdominal bloating'],
            'Constipation': ['constipation', 'constipated', 'hard stool'],
            'Loss of Appetite': ['loss of appetite', 'no appetite', 'not hungry'],
            'Sensitivity to Light': ['sensitivity to light', 'light sensitivity', 'photophobia', 'light hurt'],
            'Blurred Vision': ['blurred vision', 'blurry vision', 'vision blurred', 'fuzzy vision'],
            'Double Vision': ['double vision', 'diplopia', 'seeing double'],
            'Red Eyes': ['red eyes', 'bloodshot', 'eye redness'],
            'Itching': ['itching', 'itchy', 'itches', 'pruritus'],
            'Hives': ['hives', 'urticaria', 'welts'],
            'Acne': ['acne', 'pimples', 'breakouts', 'pimple'],
            'Swelling': ['swelling', 'swollen', 'edema', 'puffiness'],
            'Bruising': ['bruising', 'bruise', 'bruised', 'hematoma'],
            'Chills': ['chills', 'chilling', 'shivering', 'shiver'],
            'Night Sweats': ['night sweats', 'night sweat', 'sweating at night'],
            'Swollen Lymph Nodes': ['swollen lymph', 'lymph node', 'lymphadenopathy'],
            'Ear Pain': ['ear pain', 'ear ache', 'otitis'],
            'Eye Pain': ['eye pain', 'eye ache', 'eye hurt'],
            'Leg Pain': ['leg pain', 'leg ache', 'leg hurt'],
            'Arm Pain': ['arm pain', 'arm ache', 'arm hurt'],
            'Knee Pain': ['knee pain', 'knee ache', 'knee hurt'],
            'Shoulder Pain': ['shoulder pain', 'shoulder ache', 'shoulder hurt'],
            'Hip Pain': ['hip pain', 'hip ache', 'hip hurt'],
        }
        
        text_lower = text.lower()
        found_symptoms = []
        
        # Check for negations (common patterns showing they DON'T have symptom)
        negation_patterns = [
            'no ', 'not ', 'don\'t have', 'don\'t have ', 'didn\'t have', 'never had',
            'no fever', 'no cough', 'no pain', 'without ', 'none of'
        ]
        
        for symptom_name, keywords in symptom_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Check if this symptom is negated
                    # Look for negation words near the keyword
                    keyword_idx = text_lower.find(keyword)
                    
                    # Get 20 chars before keyword
                    context_start = max(0, keyword_idx - 20)
                    context = text_lower[context_start:keyword_idx + len(keyword) + 10]
                    
                    # Check if negation is nearby
                    is_negated = any(neg in context for neg in negation_patterns)
                    
                    if not is_negated:  # Only add if NOT negated
                        if symptom_name not in found_symptoms:
                            found_symptoms.append(symptom_name)
                        break  # Found this symptom, move to next
        
        return found_symptoms
