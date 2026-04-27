from datetime import datetime
import json
import os
from dotenv import load_dotenv
from .models import Symptom, SymptomChoice

# Load environment variables
load_dotenv()

class ThinkingHealthBot:
    def __init__(self, user=None, use_local=False):
        self.user = user
        self.conversation_history = []
        self.symptoms_context = []
        self.state = 'greeting'
        
        # LLM Configuration
        self.llm_client = None
        self.use_local = use_local
        
        if not use_local:
            # For Groq API (FREE - no payment needed - lazy import)
            try:
                from groq import Groq
                self.llm_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                self.model = "mixtral-8x7b-32768"  # Free Groq model
            except ImportError:
                print("Groq module not installed. Chat features disabled.")
                self.use_local = True
                self.model = "fallback"
        else:
            # For local LLM (Ollama, Llama.cpp, etc.)
            self.model = "llama2"  # or "mistral", "phi-2", etc.
        
        # Load medical knowledge base - using predefined specialties list
        self.specialties = [
            'General Physician', 'Cardiologist', 'Neurologist', 'Orthopedist',
            'Gastroenterologist', 'Dermatologist', 'Psychiatrist', 
            'ENT Specialist', 'Pulmonologist', 'Endocrinologist'
        ]
        self.symptom_database = self.load_symptom_database()
    
    def load_symptom_database(self):
        """Load structured symptom database"""
        symptoms = {}
        for symptom in Symptom.objects.all():
            symptoms[symptom.name.lower()] = {
                'id': symptom.id,
                'name': symptom.name,
                'category': symptom.category,
                'body_part': symptom.body_part,
                'description': symptom.description
            }
        return symptoms
    
    def think_about_symptoms(self, user_input):
        """Let the LLM analyze and think about symptoms"""
        
        system_prompt = """You are a medical triage AI assistant. Your job is to:
        1. Identify symptoms from patient descriptions
        2. Ask clarifying questions about severity, duration, location
        3. Gather enough information to recommend a medical specialty
        4. Never diagnose, only triage to appropriate care
        
        Think step by step:
        - Extract all mentioned symptoms
        - Note severity (1-10), duration, location
        - Consider symptom combinations
        - Ask for missing but relevant information
        - When enough info, recommend specialty with reasoning
        
        Available specialties: General Physician, Cardiologist, Neurologist, Orthopedist, Gastroenterologist, Dermatologist, Psychiatrist, ENT Specialist, Pulmonologist, Endocrinologist
        
        Respond in JSON format with:
        {
            "thinking": "your step-by-step reasoning",
            "extracted_symptoms": ["symptom1", "symptom2"],
            "missing_info": ["severity", "duration", "location"],
            "next_question": "What to ask next",
            "ready_for_recommendation": true/false,
            "potential_specialties": ["Specialty1", "Specialty2"]
        }
        """
        
        # Build conversation context
        context = []
        for msg in self.conversation_history[-6:]:  # Last 6 messages for context
            context.append(f"{msg['role'].capitalize()}: {msg['message']}")
        
        user_prompt = f"""
        Conversation so far:
        {' '.join(context)}
        
        Latest patient input: {user_input}
        
        Please analyze this and provide your thinking in JSON format.
        """
        
        try:
            if not self.use_local:
                # Call Groq API (FREE - no payment needed!)
                try:
                    response = self.llm_client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=500
                    )
                    result = json.loads(response.choices[0].message.content)
                except Exception as e:
                    print(f"Groq API error: {e}")
                    result = self.fallback_analysis(user_input)
            else:
                # Call local LLM
                result = self.call_local_llm(system_prompt, user_prompt)
            
            return result
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return self.fallback_analysis(user_input)
    
    def process_message(self, user_message):
        """Main processing with thinking capability"""
        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Let the AI think about the symptoms
        analysis = self.think_about_symptoms(user_message)
        
        # Update symptom context
        if analysis.get('extracted_symptoms'):
            for symptom in analysis['extracted_symptoms']:
                if symptom not in self.symptoms_context:
                    self.symptoms_context.append(symptom)
        
        # Generate response based on AI's thinking
        if analysis.get('ready_for_recommendation'):
            response = self.generate_specialty_recommendation(analysis)
            self.state = 'recommendation'
        else:
            response = analysis.get('next_question', 
                "Could you tell me more about your symptoms?")
            self.state = 'gathering'
        
        # Save AI response
        self.conversation_history.append({
            'role': 'assistant',
            'message': response,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def generate_specialty_recommendation(self, analysis):
        """Generate final recommendation with reasoning"""
        
        reasoning_prompt = f"""
        Based on these symptoms: {', '.join(self.symptoms_context)}
        
        And this analysis: {analysis.get('thinking', '')}
        
        Recommend the most appropriate medical specialty with:
        1. Primary recommendation
        2. Alternative if primary not available
        3. Urgency level (low/medium/high)
        4. Clear reasoning
        5. Specific questions the patient should ask the doctor
        
        Format as a helpful, empathetic medical triage response.
        """
        
        try:
            if not self.use_local:
                # Use Groq API (FREE - no payment needed!)
                try:
                    response = self.llm_client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a medical triage specialist."},
                            {"role": "user", "content": reasoning_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=600
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    print(f"Groq API error: {e}")
                    return self.fallback_recommendation()
            else:
                return self.call_local_llm("You are a medical triage specialist.", reasoning_prompt)
                
        except Exception as e:
            return self.fallback_recommendation()
    
    def fallback_analysis(self, user_input):
        """Fallback when LLM fails"""
        return {
            'thinking': 'Fallback analysis',
            'extracted_symptoms': [],
            'missing_info': ['severity', 'duration'],
            'next_question': 'Could you describe your symptoms in more detail?',
            'ready_for_recommendation': False,
            'potential_specialties': []
        }
    
    def fallback_recommendation(self):
        """Fallback recommendation when LLM fails"""
        return f"""Based on your symptoms ({', '.join(self.symptoms_context)}), I recommend consulting with a General Physician for initial evaluation.

They can provide proper diagnosis and refer you to specialists if needed.

Would you like to browse available doctors?"""

    def call_local_llm(self, system_prompt, user_prompt):
        """Call local LLM (placeholder for Ollama/etc.)"""
        # This would integrate with local LLM
        return self.fallback_analysis(user_prompt)


class HealthLinkChatBot:
    """Advanced rule-based chatbot with intelligent symptom analysis and specialist recommendations"""
    
    # Comprehensive symptom-to-specialty mapping with weights
    SPECIALTY_RULES = {
        'Cardiologist': {
            'primary': ['chest pain', 'palpitations', 'rapid heartbeat', 'irregular heartbeat', 'high blood pressure', 'low blood pressure'],
            'secondary': ['shortness of breath', 'swollen ankles', 'fatigue', 'dizziness', 'fainting'],
            'combinations': [
                (['chest pain', 'shortness of breath'], 0.95),
                (['palpitations', 'dizziness'], 0.85),
                (['chest pain', 'arm pain'], 0.90),
            ]
        },
        'Neurologist': {
            'primary': ['headache', 'migraine', 'seizure', 'tremor', 'numbness', 'tingling', 'memory problems', 'confusion'],
            'secondary': ['dizziness', 'vertigo', 'weakness', 'fainting', 'vision problems', 'blurred vision'],
            'combinations': [
                (['headache', 'vision problems'], 0.85),
                (['numbness', 'weakness'], 0.90),
                (['dizziness', 'vertigo'], 0.80),
                (['headache', 'nausea', 'sensitivity to light'], 0.95),  # Migraine pattern
            ]
        },
        'Orthopedist': {
            'primary': ['joint pain', 'back pain', 'knee pain', 'shoulder pain', 'hip pain', 'neck pain', 'bone', 'fracture', 'sprain'],
            'secondary': ['muscle pain', 'swelling', 'stiffness', 'weakness', 'leg pain', 'arm pain'],
            'combinations': [
                (['back pain', 'leg pain'], 0.85),  # Sciatica pattern
                (['joint pain', 'swelling'], 0.80),
                (['knee pain', 'swelling'], 0.85),
            ]
        },
        'Gastroenterologist': {
            'primary': ['abdominal pain', 'nausea', 'vomiting', 'diarrhea', 'constipation', 'bloating', 'heartburn', 'acid reflux', 'blood in stool'],
            'secondary': ['loss of appetite', 'indigestion', 'weight loss', 'fatigue'],
            'combinations': [
                (['abdominal pain', 'diarrhea'], 0.85),
                (['heartburn', 'acid reflux'], 0.90),
                (['nausea', 'vomiting', 'abdominal pain'], 0.90),
                (['constipation', 'bloating'], 0.75),
            ]
        },
        'Pulmonologist': {
            'primary': ['cough', 'dry cough', 'wet cough', 'shortness of breath', 'wheezing', 'asthma', 'sleep apnea'],
            'secondary': ['chest pain', 'fatigue', 'fever', 'snoring'],
            'combinations': [
                (['cough', 'shortness of breath'], 0.90),
                (['wheezing', 'shortness of breath'], 0.95),
                (['cough', 'fever', 'chest pain'], 0.85),  # Pneumonia pattern
            ]
        },
        'Dermatologist': {
            'primary': ['rash', 'itching', 'hives', 'acne', 'dry skin', 'skin discoloration', 'wound', 'burn'],
            'secondary': ['swelling', 'bruising', 'hair loss'],
            'combinations': [
                (['rash', 'itching'], 0.90),
                (['rash', 'fever'], 0.80),
                (['hives', 'swelling'], 0.85),
            ]
        },
        'ENT Specialist': {
            'primary': ['sore throat', 'ear pain', 'runny nose', 'stuffy nose', 'sinus pressure', 'loss of smell', 'hoarse voice', 'hearing'],
            'secondary': ['cough', 'headache', 'fever', 'sneezing', 'difficulty swallowing'],
            'combinations': [
                (['sore throat', 'fever'], 0.80),
                (['ear pain', 'fever'], 0.85),
                (['sinus pressure', 'headache'], 0.85),
                (['runny nose', 'sneezing', 'sore throat'], 0.80),
            ]
        },
        'Psychiatrist': {
            'primary': ['anxiety', 'depression', 'panic attacks', 'mood swings', 'irritability'],
            'secondary': ['insomnia', 'stress', 'fatigue', 'low energy', 'memory problems'],
            'combinations': [
                (['anxiety', 'insomnia'], 0.85),
                (['depression', 'fatigue'], 0.85),
                (['anxiety', 'panic attacks'], 0.95),
                (['mood swings', 'irritability'], 0.80),
            ]
        },
        'Endocrinologist': {
            'primary': ['excessive thirst', 'excessive hunger', 'weight loss', 'weight gain', 'hair loss', 'cold intolerance', 'heat intolerance'],
            'secondary': ['fatigue', 'frequent urination', 'weakness', 'mood swings'],
            'combinations': [
                (['excessive thirst', 'frequent urination'], 0.95),  # Diabetes pattern
                (['fatigue', 'weight gain', 'cold intolerance'], 0.90),  # Hypothyroid pattern
                (['weight loss', 'rapid heartbeat', 'heat intolerance'], 0.90),  # Hyperthyroid pattern
            ]
        },
        'Urologist': {
            'primary': ['frequent urination', 'painful urination', 'blood in urine', 'urinary incontinence'],
            'secondary': ['abdominal pain', 'back pain', 'fever'],
            'combinations': [
                (['painful urination', 'fever'], 0.90),  # UTI pattern
                (['frequent urination', 'excessive thirst'], 0.85),
            ]
        },
        'Ophthalmologist': {
            'primary': ['blurred vision', 'double vision', 'eye pain', 'red eyes', 'watery eyes', 'sensitivity to light'],
            'secondary': ['headache'],
            'combinations': [
                (['eye pain', 'headache'], 0.80),
                (['blurred vision', 'headache'], 0.75),
                (['red eyes', 'eye pain'], 0.85),
            ]
        },
        'Rheumatologist': {
            'primary': ['joint pain', 'swelling', 'stiffness'],
            'secondary': ['fatigue', 'fever', 'rash', 'muscle pain'],
            'combinations': [
                (['joint pain', 'swelling', 'stiffness'], 0.95),  # Arthritis pattern
                (['joint pain', 'fatigue', 'rash'], 0.85),  # Lupus pattern
            ]
        },
    }
    
    # Urgency keywords for emergency detection
    EMERGENCY_KEYWORDS = [
        'severe chest pain', 'difficulty breathing', 'cannot breathe', 'unconscious', 
        'seizure', 'stroke', 'heart attack', 'severe bleeding', 'suicidal', 
        'overdose', 'poisoning', 'severe allergic reaction', 'anaphylaxis'
    ]
    
    # Synonym mapping for better symptom detection
    SYMPTOM_SYNONYMS = {
        'headache': ['head hurts', 'head pain', 'head ache', 'my head'],
        'fever': ['temperature', 'hot', 'feverish', 'burning up'],
        'cough': ['coughing', 'hacking'],
        'nausea': ['feel sick', 'queasy', 'want to vomit', 'feeling nauseous'],
        'vomiting': ['throwing up', 'being sick', 'vomit', 'puking'],
        'diarrhea': ['loose stools', 'watery stool', 'runny stomach'],
        'fatigue': ['tired', 'exhausted', 'no energy', 'worn out', 'tiredness'],
        'dizziness': ['dizzy', 'lightheaded', 'light headed', 'woozy'],
        'shortness of breath': ['cant breathe', 'hard to breathe', 'breathing difficulty', 'breathless'],
        'chest pain': ['chest hurts', 'pain in chest', 'chest discomfort'],
        'abdominal pain': ['stomach pain', 'tummy ache', 'belly pain', 'stomach hurts'],
        'anxiety': ['anxious', 'worried', 'nervous', 'panicking'],
        'depression': ['depressed', 'sad', 'hopeless', 'down'],
        'insomnia': ['cant sleep', 'trouble sleeping', 'sleepless', 'not sleeping'],
        'rash': ['skin rash', 'breaking out', 'spots on skin'],
        'joint pain': ['joints hurt', 'painful joints', 'arthritis'],
        'back pain': ['back hurts', 'backache', 'pain in back'],
        'sore throat': ['throat hurts', 'painful throat', 'scratchy throat'],
        'palpitations': ['heart racing', 'heart pounding', 'heart beating fast'],
    }
    
    def __init__(self, user=None):
        self.user = user
        self.symptoms = []  # List of Symptom objects
        self.symptom_details = {}  # {symptom_id: {severity: 3, duration: 'days', notes: ''}}
        self.conversation_history = []
        self.state = 'greeting'  # greeting, symptom_gathering, details, recommendation
        self.current_question = None
        self.details_gathered = False
        self.asked_followups = set()  # Track which follow-up questions we've asked
        self.emergency_detected = False
        
    def process_message(self, user_message):
        """Process user message and return AI response"""
        self.conversation_history.append({
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check for emergency situations first
        if self.check_emergency(user_message):
            response = self.handle_emergency()
            self.state = 'recommendation'
        else:
            # Extract symptoms from text
            extracted_symptoms = self.extract_symptoms(user_message)
            
            # Add new symptoms (avoid duplicates)
            for symptom in extracted_symptoms:
                if symptom not in self.symptoms:
                    self.symptoms.append(symptom)
            
            # Update symptom details if provided
            self.update_symptom_details(user_message)
            
            # Update state based on symptoms collected
            self.update_state()
            
            # Determine response based on state
            if self.state == 'greeting':
                response = self.handle_greeting()
            elif self.state == 'symptom_gathering':
                response = self.handle_symptom_gathering()
            elif self.state == 'details':
                response = self.handle_symptom_details()
            else:  # recommendation state
                response = self.generate_recommendation()
        
        # Save conversation
        self.conversation_history.append({
            'role': 'ai',
            'message': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def check_emergency(self, text):
        """Check if user describes an emergency situation"""
        text_lower = text.lower()
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                self.emergency_detected = True
                return True
        return False
    
    def handle_emergency(self):
        """Handle emergency situations"""
        return """🚨 **EMERGENCY DETECTED**

Based on what you've described, this may be a medical emergency.

**Please take immediate action:**
1. **Call emergency services (999/911/112) immediately**
2. If someone is with you, ask them to help
3. Do not drive yourself to the hospital

**While waiting for help:**
- Stay calm and try to remain still
- If experiencing chest pain, sit or lie down
- If having difficulty breathing, sit upright
- Keep your phone nearby

This is not a substitute for emergency medical care. Please seek immediate professional help.
"""
    
    def extract_symptoms(self, text):
        """Extract symptoms from text using Django Symptom model and synonyms"""
        symptoms = []
        text_lower = text.lower()
        
        # First, expand text with synonym matches
        expanded_text = text_lower
        for symptom_name, synonyms in self.SYMPTOM_SYNONYMS.items():
            for synonym in synonyms:
                if synonym in text_lower:
                    expanded_text += f" {symptom_name}"
        
        # Query Symptom model for matches
        for symptom in Symptom.objects.all():
            symptom_name_lower = symptom.name.lower()
            
            # Check exact match first
            if symptom_name_lower in expanded_text:
                if symptom not in self.symptoms and symptom not in symptoms:
                    symptoms.append(symptom)
                continue
            
            # Check partial word matches (for multi-word symptoms)
            symptom_words = symptom_name_lower.split()
            if len(symptom_words) > 1:
                # For multi-word symptoms, require at least the main word
                if symptom_words[0] in expanded_text or symptom_words[-1] in expanded_text:
                    if symptom not in self.symptoms and symptom not in symptoms:
                        symptoms.append(symptom)
        
        return symptoms
    
    def update_symptom_details(self, user_message):
        """Extract severity and duration from user message with improved parsing"""
        message_lower = user_message.lower()
        
        # Extract severity (1-10 scale) with multiple patterns
        severity = None
        
        # Pattern: "7/10", "8 out of 10", "level 6"
        import re
        severity_patterns = [
            r'(\d+)\s*/\s*10',
            r'(\d+)\s+out\s+of\s+10',
            r'severity\s*:?\s*(\d+)',
            r'level\s*:?\s*(\d+)',
            r'rate\s+it\s+(\d+)',
            r'(\d+)\s+on\s+a\s+scale',
        ]
        
        for pattern in severity_patterns:
            match = re.search(pattern, message_lower)
            if match:
                val = int(match.group(1))
                if 1 <= val <= 10:
                    severity = val
                    break
        
        # Word-based severity
        if severity is None:
            if any(word in message_lower for word in ['mild', 'slight', 'minor', 'little', 'bit']):
                severity = 3
            elif any(word in message_lower for word in ['moderate', 'medium', 'somewhat', 'fairly']):
                severity = 5
            elif any(word in message_lower for word in ['severe', 'intense', 'bad', 'terrible', 'worst', 'extreme', 'unbearable', 'very']):
                severity = 8
        
        # Extract duration with more patterns
        duration = None
        duration_patterns = {
            'hours': [r'(\d+)\s*hours?', r'few hours', r'couple hours', r'today', r'just started', r'started today'],
            'days': [r'(\d+)\s*days?', r'few days', r'couple days', r'yesterday', r'since yesterday', r'2-3 days'],
            'weeks': [r'(\d+)\s*weeks?', r'few weeks', r'couple weeks', r'last week', r'past week', r'week ago'],
            'months': [r'(\d+)\s*months?', r'few months', r'couple months', r'last month', r'month ago'],
            'years': [r'(\d+)\s*years?', r'few years', r'couple years', r'long time', r'chronic'],
        }
        
        for duration_type, patterns in duration_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    duration = duration_type
                    break
            if duration:
                break
        
        # Update details for all symptoms
        if self.symptoms and (severity is not None or duration is not None):
            for symptom in self.symptoms:
                prev = self.symptom_details.get(symptom.id, {})
                sev = severity if severity is not None else prev.get('severity')
                dur = duration if duration is not None else prev.get('duration')
                
                self.symptom_details[symptom.id] = {
                    'severity': sev,
                    'duration': dur,
                    'notes': user_message
                }
        
        # Check if we have gathered enough details
        for details in self.symptom_details.values():
            if details.get('severity') is not None and details.get('duration') is not None:
                self.details_gathered = True
                break
    
    def update_state(self):
        """Update conversation state based on collected information"""
        if len(self.symptoms) == 0:
            self.state = 'greeting'
        elif len(self.symptoms) >= 1 and not self.details_gathered:
            if not self.symptom_details:
                self.state = 'symptom_gathering'
            else:
                self.state = 'details'
        elif self.details_gathered:
            self.state = 'recommendation'
    
    def handle_greeting(self):
        """Handle initial greeting state with personalized response"""
        if self.symptoms:
            symptom_name = self.symptoms[0].name
            return f"I understand you're experiencing **{symptom_name}**. I'm sorry to hear that. Can you tell me about any other symptoms you're having? Also, how severe is this symptom on a scale of 1-10?"
        
        greeting = """Hello! I'm your HealthLink AI Health Assistant. 🏥

I'm here to help you understand your symptoms and guide you to the right specialist.

**Please describe what symptoms you're experiencing.** For example:
- "I have a headache and feel dizzy"
- "I've had a cough for 3 days"
- "My stomach hurts and I feel nauseous"

The more details you provide, the better I can help you!"""
        return greeting
    
    def handle_symptom_gathering(self):
        """Handle symptom gathering with intelligent follow-up questions"""
        symptom_names = [s.name for s in self.symptoms]
        
        # Generate contextual follow-up based on symptoms
        followup = self.get_contextual_followup()
        
        if len(self.symptoms) == 1:
            return f"""I've noted that you're experiencing **{symptom_names[0]}**.

{followup}

Also, please tell me:
• How severe is this symptom? (1-10 or mild/moderate/severe)
• How long have you had it? (hours, days, weeks)"""
        else:
            return f"""Thank you. I've noted these symptoms: **{', '.join(symptom_names)}**

{followup}

On a scale of 1-10, how severe are your symptoms? And how long have you been experiencing them?"""
    
    def get_contextual_followup(self):
        """Get context-aware follow-up questions based on current symptoms"""
        symptom_names_lower = [s.name.lower() for s in self.symptoms]
        
        followups = []
        
        if 'headache' in symptom_names_lower and 'headache_location' not in self.asked_followups:
            self.asked_followups.add('headache_location')
            followups.append("Where exactly is the headache located? (front, back, sides, or all over)")
        
        if 'chest pain' in symptom_names_lower and 'chest_pain_type' not in self.asked_followups:
            self.asked_followups.add('chest_pain_type')
            followups.append("⚠️ Does the pain radiate to your arm, jaw, or back? Is it sharp or squeezing?")
        
        if 'cough' in symptom_names_lower and 'cough_type' not in self.asked_followups:
            self.asked_followups.add('cough_type')
            followups.append("Is the cough dry or are you coughing up mucus/phlegm?")
        
        if 'abdominal pain' in symptom_names_lower and 'abdominal_location' not in self.asked_followups:
            self.asked_followups.add('abdominal_location')
            followups.append("Where is the pain located? (upper, lower, left side, right side)")
        
        if any(s in symptom_names_lower for s in ['fever', 'chills']) and 'fever_temp' not in self.asked_followups:
            self.asked_followups.add('fever_temp')
            followups.append("What is your temperature if you've measured it?")
        
        if followups:
            return followups[0]
        
        return "Are there any other symptoms you're experiencing?"
    
    def handle_symptom_details(self):
        """Handle symptom details gathering"""
        has_severity = any(
            details.get('severity') is not None 
            for details in self.symptom_details.values()
        )
        has_duration = any(
            details.get('duration') is not None 
            for details in self.symptom_details.values()
        )
        
        if not has_severity:
            return """On a scale of **1-10**, how would you rate the severity of your symptoms?

You can also describe it as:
• **Mild** (1-3): Noticeable but not affecting daily activities
• **Moderate** (4-6): Affecting some daily activities
• **Severe** (7-10): Significantly impacting daily life"""
        elif not has_duration:
            return """How long have you been experiencing these symptoms?

For example:
• Just started today / a few hours
• A few days / since yesterday
• About a week
• Several weeks or longer"""
        else:
            self.details_gathered = True
            self.state = 'recommendation'
            return self.generate_recommendation()
    
    def generate_recommendation(self):
        """Generate comprehensive recommendation with confidence scoring"""
        symptom_names = [s.name for s in self.symptoms]
        symptom_names_lower = [s.lower() for s in symptom_names]
        all_symptoms_text = ' '.join(symptom_names_lower)
        
        # Calculate specialty scores
        specialty_scores = self.calculate_specialty_scores(symptom_names_lower)
        
        # Get best match
        if specialty_scores:
            sorted_specialties = sorted(specialty_scores.items(), key=lambda x: x[1], reverse=True)
            primary_specialty = sorted_specialties[0][0]
            confidence = min(sorted_specialties[0][1], 0.95)  # Cap at 95%
            
            # Get alternative if available
            alternative = sorted_specialties[1][0] if len(sorted_specialties) > 1 else None
        else:
            primary_specialty = 'General Physician'
            confidence = 0.60
            alternative = None
        
        # Calculate urgency based on severity
        max_severity = max(
            (d.get('severity', 5) for d in self.symptom_details.values() if d.get('severity')),
            default=5
        )
        
        if max_severity >= 8 or self.emergency_detected:
            urgency = "urgent"
            urgency_icon = "🔴"
            urgency_advice = "Please seek medical attention as soon as possible, ideally within 24 hours."
        elif max_severity >= 6:
            urgency = "soon"
            urgency_icon = "🟡"
            urgency_advice = "Please schedule an appointment within the next few days."
        else:
            urgency = "routine"
            urgency_icon = "🟢"
            urgency_advice = "You can schedule a routine appointment at your convenience."
        
        # Build recommendation
        recommendation = f"""
✅ **Triage Assessment Complete**

Based on the symptoms you've described ({', '.join(symptom_names)}), here is my recommendation:

---

🏥 **Recommended Specialist:** **{primary_specialty}**
📊 **Confidence:** {confidence:.0%}
{urgency_icon} **Urgency:** {urgency.capitalize()}

---

**Why {primary_specialty}?**
{self.get_specialty_explanation(primary_specialty, symptom_names_lower)}
"""
        
        if alternative and specialty_scores.get(alternative, 0) > 0.4:
            recommendation += f"""
**Alternative Option:** {alternative}
If a {primary_specialty} is not available, a {alternative} could also evaluate your symptoms.
"""
        
        recommendation += f"""
---

**{urgency_advice}**

**Preparation Tips:**
1. Write down all your symptoms and when they started
2. Note any medications you're currently taking
3. List any allergies or previous medical conditions
4. Prepare questions you want to ask the doctor

---

Would you like to find available **{primary_specialty}** specialists on HealthLink?
"""
        
        return recommendation.strip()
    
    def calculate_specialty_scores(self, symptom_names_lower):
        """Calculate match scores for each specialty"""
        scores = {}
        all_symptoms_text = ' '.join(symptom_names_lower)
        
        for specialty, rules in self.SPECIALTY_RULES.items():
            score = 0.0
            
            # Check primary symptoms (higher weight)
            primary_matches = sum(1 for s in rules['primary'] if s in all_symptoms_text)
            score += primary_matches * 0.25
            
            # Check secondary symptoms (lower weight)
            secondary_matches = sum(1 for s in rules['secondary'] if s in all_symptoms_text)
            score += secondary_matches * 0.10
            
            # Check symptom combinations (bonus)
            for combo, bonus in rules.get('combinations', []):
                if all(symptom in all_symptoms_text for symptom in combo):
                    score = max(score, bonus)  # Use combination score if higher
            
            if score > 0:
                scores[specialty] = min(score, 0.95)
        
        # Default to General Physician if no good match
        if not scores or max(scores.values()) < 0.3:
            scores['General Physician'] = 0.60
        
        return scores
    
    def get_specialty_explanation(self, specialty, symptom_names_lower):
        """Get explanation for why a specialty was recommended"""
        explanations = {
            'Cardiologist': "Cardiologists specialize in heart and cardiovascular conditions. Your symptoms may indicate a condition that should be evaluated by a heart specialist.",
            'Neurologist': "Neurologists specialize in the nervous system, including the brain. Your symptoms suggest a neurological evaluation would be beneficial.",
            'Orthopedist': "Orthopedists specialize in bones, joints, and muscles. Your symptoms point to a musculoskeletal issue that they can diagnose and treat.",
            'Gastroenterologist': "Gastroenterologists specialize in the digestive system. Your symptoms suggest a gastrointestinal condition that needs evaluation.",
            'Pulmonologist': "Pulmonologists specialize in the respiratory system. Your breathing-related symptoms should be evaluated by a lung specialist.",
            'Dermatologist': "Dermatologists specialize in skin conditions. Your skin-related symptoms can be properly diagnosed and treated by a skin specialist.",
            'ENT Specialist': "ENT (Ear, Nose, Throat) specialists handle conditions affecting these areas. Your symptoms fall within their expertise.",
            'Psychiatrist': "Psychiatrists specialize in mental health conditions. They can provide proper evaluation and treatment for your symptoms.",
            'Endocrinologist': "Endocrinologists specialize in hormones and metabolism. Your symptoms may indicate a hormonal or metabolic condition.",
            'Urologist': "Urologists specialize in the urinary system. Your symptoms suggest a urological evaluation would be helpful.",
            'Ophthalmologist': "Ophthalmologists are eye specialists who can properly evaluate and treat your vision-related symptoms.",
            'Rheumatologist': "Rheumatologists specialize in autoimmune and inflammatory conditions affecting joints. Your symptoms pattern suggests this specialty.",
            'General Physician': "A General Physician can perform an initial evaluation of your symptoms and refer you to specialists if needed. This is a good starting point when symptoms don't clearly point to one specialty.",
        }
        
        return explanations.get(specialty, f"A {specialty} can properly evaluate and address your symptoms.")
    
    def get_conversation_summary(self):
        """Get summary of the conversation"""
        return {
            'symptoms': [s.name for s in self.symptoms],
            'symptom_details': self.symptom_details,
            'state': self.state,
            'details_gathered': self.details_gathered,
            'message_count': len(self.conversation_history),
            'emergency_detected': self.emergency_detected
        }
    
    def reset(self):
        """Reset the chatbot state"""
        self.symptoms = []
        self.symptom_details = {}
        self.conversation_history = []
        self.state = 'greeting'
        self.current_question = None
        self.details_gathered = False
        self.asked_followups = set()
        self.emergency_detected = False