# triage/ml_service.py - CLEAN VERSION
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
        symptoms_to_specialties = {
            'migraine headache dizziness photophobia': 'Neurology',
            'headache nausea vomiting neck stiffness': 'Neurology',
            'chest pain shortness of breath palpitations': 'Cardiology',
            'chest pain radiating to arm jaw sweating': 'Cardiology',
            'cough fever shortness of breath chest pain': 'Pulmonology',
            'wheezing cough chest tightness': 'Pulmonology',
            'abdominal pain nausea vomiting diarrhea': 'Gastroenterology',
            'heartburn chest pain acid reflux': 'Gastroenterology',
            'rash itching skin redness': 'Dermatology',
            'joint pain swelling stiffness': 'Orthopedics',
            'anxiety depression mood swings': 'Psychiatry',
            'fever cough headache': 'General Medicine',
        }
        
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
                saved = joblib.load(model_path)
                self.model = saved['model']
                self.vectorizer = saved['vectorizer']
                self.specialties = saved.get('specialties', [])
                return True
        except:
            pass
        
        return self.train_model()
    
    def train_model(self):
        """Train advanced model"""
        df = self.load_medical_dataset()
        
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=500,
            stop_words='english',
            min_df=1
        )
        
        X = self.vectorizer.fit_transform(df['symptoms'])
        y = df['specialty']
        self.specialties = y.unique().tolist()
        
        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=8,
            random_state=42
        )
        
        self.model.fit(X, y)
        
        model_path = os.path.join(settings.BASE_DIR, 'triage', 'advanced_model.pkl')
        joblib.dump({
            'model': self.model,
            'vectorizer': self.vectorizer,
            'specialties': self.specialties
        }, model_path)
        
        return True
    
    def predict_specialty(self, symptoms_text):
        """Simple prediction"""
        result = self.predict_with_explanation(symptoms_text)
        return result['primary_specialty'], result['confidence']
    
    def predict_with_explanation(self, symptoms_text):
        """Predict with explanation"""
        if self.model is None or self.vectorizer is None:
            self.load_or_train()
        
        cleaned_text = symptoms_text.lower().strip()
        X_input = self.vectorizer.transform([cleaned_text])
        
        prediction = self.model.predict(X_input)[0]
        probabilities = self.model.predict_proba(X_input)[0]
        confidence = np.max(probabilities)
        
        specialties = self.model.classes_
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_specialties = [
            {'specialty': specialties[i], 'confidence': float(probabilities[i])}
            for i in top_indices
        ]
        
        explanation = f"Based on symptoms: {cleaned_text}"
        
        return {
            'primary_specialty': prediction,
            'confidence': float(confidence),
            'alternative_specialties': top_specialties,
            'explanation': explanation
        }