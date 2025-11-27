import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
from django.conf import settings

class SymptomTriageModel:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.specialties = []
        
    def create_sample_data(self):
        """Create sample training data for demonstration"""
        data = {
            'symptoms': [
                'fever cough headache',
                'chest_pain shortness_of_breath',
                'rash itching skin_redness',
                'headache dizziness nausea',
                'abdominal_pain diarrhea vomiting',
                'joint_pain swelling stiffness',
                'anxiety depression mood_swings',
                'sore_throat runny_nose sneezing',
                'back_pain muscle_spasms',
                'vision_problems eye_pain'
            ],
            'specialty': [
                'General Medicine',
                'Cardiology',
                'Dermatology',
                'Neurology',
                'Gastroenterology',
                'Orthopedics',
                'Psychiatry',
                'ENT',
                'Orthopedics',
                'Ophthalmology'
            ]
        }
        return pd.DataFrame(data)
    
    def train_model(self):
        """Train the ML model"""
        # Create sample data
        df = self.create_sample_data()
        
        # Create pipeline
        self.model = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('classifier', MultinomialNB())
        ])
        
        # Train the model
        self.model.fit(df['symptoms'], df['specialty'])
        self.specialties = df['specialty'].unique().tolist()
        
        # Save the model
        model_path = os.path.join(settings.BASE_DIR, 'triage', 'symptom_model.pkl')
        joblib.dump(self.model, model_path)
        
        return True
    
    def predict_specialty(self, symptoms_text):
        """Predict specialty based on symptoms"""
        if self.model is None:
            # Load or train model
            model_path = os.path.join(settings.BASE_DIR, 'triage', 'symptom_model.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
            else:
                self.train_model()
        
        # Make prediction
        prediction = self.model.predict([symptoms_text])
        probabilities = self.model.predict_proba([symptoms_text])
        
        confidence = np.max(probabilities)
        predicted_specialty = prediction[0]
        
        return predicted_specialty, confidence