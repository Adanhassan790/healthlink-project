from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import TriageForm
from .models import TriageSession, Symptom
from .ml_model import SymptomTriageModel
import json

def triage(request):
    """Main triage page - this matches your URL pattern"""
    if request.method == 'POST':
        form = TriageForm(request.POST)
        if form.is_valid():
            # Get selected symptoms
            symptoms = form.cleaned_data['symptoms']
            additional_notes = form.cleaned_data['additional_notes']
            
            # Convert symptoms to text for ML model
            symptoms_text = ' '.join([symptom.name for symptom in symptoms])
            if additional_notes:
                symptoms_text += ' ' + additional_notes
            
            # Get prediction from ML model (or use fallback)
            try:
                ml_model = SymptomTriageModel()
                predicted_specialty, confidence = ml_model.predict_specialty(symptoms_text)
            except:
                # Fallback if ML model isn't working
                predicted_specialty = "General Practice"
                confidence = 0.7
            
            # Save triage session
            if request.user.is_authenticated:
                triage_session = TriageSession.objects.create(
                    user=request.user,
                    predicted_specialty=predicted_specialty,
                    confidence_score=confidence,
                    additional_notes=additional_notes
                )
                triage_session.symptoms.set(symptoms)
            else:
                triage_session = None
            
            # Show results
            return render(request, 'triage/results.html', {
                'predicted_specialty': predicted_specialty,
                'confidence': round(confidence * 100, 1),
                'symptoms': symptoms,
                'triage_session': triage_session
            })
    else:
        form = TriageForm()
    
    # Use your existing template
    return render(request, 'triage/start.html', {'form': form})

def triage_chat(request):
    """Interactive chat-based triage"""
    return render(request, 'triage/chat.html')

def triage_chat_api(request):
    """API endpoint for chat interactions"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Simple rule-based chatbot for demonstration
            response = generate_chat_response(user_message)
            
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Invalid request'})

def generate_chat_response(message):
    """Generate chatbot response based on user input"""
    message = message.lower()
    
    # Simple rule-based responses
    if any(word in message for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your HealthLink AI assistant. Could you describe what symptoms you're experiencing?"
    elif any(word in message for word in ['fever', 'temperature']):
        return "I see you mentioned fever. How long have you had this fever? Any other symptoms like cough or headache?"
    elif any(word in message for word in ['pain', 'hurt']):
        return "I understand you're experiencing pain. Can you tell me where the pain is located and how severe it is?"
    elif any(word in message for word in ['head', 'headache']):
        return "Headaches can have various causes. Are you experiencing any dizziness, vision changes, or nausea?"
    elif any(word in message for word in ['chest', 'heart']):
        return "Chest symptoms should be taken seriously. Are you experiencing shortness of breath or pain radiating to other areas?"
    elif any(word in message for word in ['thank', 'thanks']):
        return "You're welcome! Is there anything else you'd like to discuss about your symptoms?"
    elif any(word in message for word in ['bye', 'goodbye']):
        return "Thank you for using HealthLink AI assistant. Remember to consult with a healthcare professional for proper medical advice."
    else:
        return "Thank you for describing your symptoms. Based on what you've told me, I recommend consulting with a specialist. Would you like me to help you find an appropriate doctor?"