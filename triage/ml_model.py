
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from django.conf import settings

class AdvancedSymptomTriageModel:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.specialties = []
        
    def load_medical_dataset(self):
        """Load comprehensive medical dataset"""
        # Enhanced medical data patterns
        symptoms_to_specialties = {
            # Neurology
            'migraine headache dizziness photophobia': 'Neurology',
            'headache nausea vomiting neck stiffness': 'Neurology',
            'seizures confusion memory loss': 'Neurology',
            'numbness tingling weakness limbs': 'Neurology',
            'head pain vision problems': 'Neurology',
            
            # Cardiology
            'chest pain shortness of breath palpitations': 'Cardiology',
            'chest pain radiating to arm jaw sweating': 'Cardiology',
            'high blood pressure swelling legs fatigue': 'Cardiology',
            'irregular heartbeat dizziness fainting': 'Cardiology',
            'heart pain pressure discomfort': 'Cardiology',
            
            # Respiratory/Pulmonology
            'cough fever shortness of breath chest pain': 'Pulmonology',
            'wheezing cough chest tightness': 'Pulmonology',
            'chronic cough blood in sputum weight loss': 'Pulmonology',
            'asthma breathing difficulty': 'Pulmonology',
            'lung pain breathing problems': 'Pulmonology',
            
            # Gastroenterology
            'abdominal pain nausea vomiting diarrhea': 'Gastroenterology',
            'heartburn chest pain acid reflux': 'Gastroenterology',
            'abdominal pain bloating constipation diarrhea': 'Gastroenterology',
            'stomach pain indigestion': 'Gastroenterology',
            'liver gall bladder issues': 'Gastroenterology',
            
            # Dermatology
            'rash itching skin redness': 'Dermatology',
            'acne pimples oily skin': 'Dermatology',
            'eczema dry skin flaking': 'Dermatology',
            'skin infection swelling': 'Dermatology',
            'hair loss scalp issues': 'Dermatology',
            
            # Orthopedics
            'joint pain swelling stiffness': 'Orthopedics',
            'back pain muscle spasms': 'Orthopedics',
            'fracture broken bone swelling': 'Orthopedics',
            'arthritis joint inflammation': 'Orthopedics',
            'muscle pain injury': 'Orthopedics',
            
            # Psychiatry
            'anxiety depression mood swings': 'Psychiatry',
            'stress insomnia fatigue': 'Psychiatry',
            'panic attacks fear avoidance': 'Psychiatry',
            'mental health counseling': 'Psychiatry',
            'emotional distress trauma': 'Psychiatry',
            
            # ENT (Ear, Nose, Throat)
            'sore throat ear pain sinus': 'ENT',
            'nose bleeding sinus issues': 'ENT',
            'hearing loss ear problems': 'ENT',
            'tonsillitis throat infection': 'ENT',
            
            # Ophthalmology
            'eye pain vision problems': 'Ophthalmology',
            'red eyes itching discharge': 'Ophthalmology',
            'blurred vision eye strain': 'Ophthalmology',
            
            # General Medicine (fallback)
            'fever cough headache': 'General Medicine',
            'cold sneezing runny nose': 'General Medicine',
            'fatigue weakness tiredness': 'General Medicine',
            'general illness checkup': 'General Medicine',
            'vaccination preventive care': 'General Medicine',
        }
        
        # Convert to DataFrame
        data = []
        for symptoms, specialty in symptoms_to_specialties.items():
            data.append({
                'symptoms': symptoms,
                'specialty': specialty
            })
        
        return pd.DataFrame(data)
    
    def load_or_train(self):
        """Load or train the model"""
        model_path = os.path.join(settings.BASE_DIR, 'triage', 'advanced_model.pkl')
        
        try:
            if os.path.exists(model_path):
                # Load saved model
                saved = joblib.load(model_path)
                self.model = saved['model']
                self.vectorizer = saved['vectorizer']
                self.specialties = saved.get('specialties', [])
                print("✅ ML Model loaded from cache")
                return True
        except Exception as e:
            print(f"⚠️ Failed to load cached model: {e}")
        
        # Train new model
        return self.train_model()
    
    def train_model(self):
        """Train advanced model"""
        df = self.load_medical_dataset()
        
        # Use TF-IDF for better text representation
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Capture symptom combinations
            max_features=500,
            stop_words='english',
            min_df=1
        )
        
        X = self.vectorizer.fit_transform(df['symptoms'])
        y = df['specialty']
        
        # Store unique specialties
        self.specialties = y.unique().tolist()
        
        # Use Random Forest for better accuracy
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            min_samples_split=2,
            min_samples_leaf=1
        )
        
        self.model.fit(X, y)
        
        # Save model
        model_path = os.path.join(settings.BASE_DIR, 'triage', 'advanced_model.pkl')
        joblib.dump({
            'model': self.model,
            'vectorizer': self.vectorizer,
            'specialties': self.specialties
        }, model_path)
        
        print("✅ ML Model trained and saved")
        return True
    
    def predict_specialty(self, symptoms_text):
        """Simple prediction method for compatibility"""
        result = self.predict_with_explanation(symptoms_text)
        return result['primary_specialty'], result['confidence']
    
    def predict_with_explanation(self, symptoms_text, symptom_details=None):
        """Predict with confidence and explanation"""
        # Ensure model is loaded
        if self.model is None or self.vectorizer is None:
            self.load_or_train()
        
        # Clean and prepare input
        cleaned_text = symptoms_text.lower().strip()
        
        # Transform input
        X_input = self.vectorizer.transform([cleaned_text])
        
        # Get prediction and probabilities
        prediction = self.model.predict(X_input)[0]
        probabilities = self.model.predict_proba(X_input)[0]
        
        # Get confidence
        confidence = np.max(probabilities)
        
        # Get top 3 specialties
        specialties = self.model.classes_
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_specialties = [
            {'specialty': specialties[i], 'confidence': float(probabilities[i])}
            for i in top_indices
        ]
        
        # Generate explanation
        explanation = self.generate_explanation(cleaned_text, prediction, symptom_details)
        
        return {
            'primary_specialty': prediction,
            'confidence': float(confidence),
            'alternative_specialties': top_specialties,
            'explanation': explanation
        }
    
    def generate_explanation(self, symptoms_text, predicted_specialty, symptom_details=None):
        """Generate human-readable explanation"""
        symptoms = symptoms_text.split()
        
        explanations = {
            'Neurology': f"Your symptoms ({', '.join(symptoms[:3])}) commonly relate to nervous system issues. Neurology specialists handle conditions affecting the brain, nerves, and spinal cord.",
            'Cardiology': f"Cardiac symptoms like {symptoms[0] if symptoms else 'these'} require heart specialist evaluation. Cardiologists diagnose and treat heart conditions, blood pressure, and circulation issues.",
            'Pulmonology': f"Respiratory symptoms ({', '.join(symptoms[:2])}) are evaluated by pulmonologists who specialize in lung diseases, breathing disorders, and respiratory infections.",
            'Gastroenterology': f"Digestive system symptoms fall under gastroenterology. These specialists handle stomach, intestine, liver, and pancreas issues.",
            'Dermatology': f"Skin-related symptoms require dermatology expertise for proper diagnosis of skin conditions, allergies, infections, and cosmetic issues.",
            'Orthopedics': f"Musculoskeletal symptoms like {symptoms[0] if symptoms else 'these'} are evaluated by orthopedic specialists who treat bones, joints, muscles, and connective tissues.",
            'Psychiatry': f"Mental health symptoms benefit from psychiatric evaluation for diagnosis and treatment of emotional, behavioral, and mental disorders.",
            'ENT': f"Ear, nose, and throat symptoms are handled by ENT specialists who treat sinus issues, hearing problems, throat infections, and related conditions.",
            'Ophthalmology': f"Eye and vision problems require ophthalmology expertise for proper diagnosis and treatment of eye diseases and vision correction.",
            'General Medicine': f"For general symptoms, starting with a primary care physician is recommended for comprehensive evaluation, diagnosis, and referral to specialists if needed."
        }
        
        # Custom explanation based on symptom details
        if symptom_details:
            if 'severity' in symptom_details and symptom_details['severity'] > 7:
                return explanations.get(predicted_specialty, "") + " Given the high severity of symptoms, prompt medical attention is advised."
            if 'duration' in symptom_details and symptom_details['duration'] in ['weeks', 'months', 'years']:
                return explanations.get(predicted_specialty, "") + " Since these symptoms have persisted for an extended period, specialist evaluation is recommended."
        
        return explanations.get(predicted_specialty, "Based on symptom patterns, this medical specialty is recommended for proper evaluation and treatment.")