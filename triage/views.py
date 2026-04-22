
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import TriageForm
from .models import TriageSession, Symptom, SavedAssessment
from .chat_bot import HealthLinkChatBot
from .llm_triage_service import LLMTriageService
from users.decorators import patient_required
import json
import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def ensure_default_symptoms():
    """Ensure comprehensive symptoms exist in database"""
    if Symptom.objects.count() < 50:  # Update if we have fewer symptoms
        print("Creating/updating symptoms database...")
        
        default_symptoms = [
            # Pain symptoms
            ('Headache', 'pain', 'Head pain or pressure', 'Head'),
            ('Migraine', 'pain', 'Severe throbbing headache often with nausea', 'Head'),
            ('Back Pain', 'pain', 'Pain in upper or lower back', 'Back'),
            ('Neck Pain', 'pain', 'Pain or stiffness in neck', 'Neck'),
            ('Joint Pain', 'pain', 'Pain in joints like knees, elbows, wrists', 'Joints'),
            ('Muscle Pain', 'pain', 'Soreness or aching in muscles', 'Muscles'),
            ('Chest Pain', 'cardiac', 'Pain or discomfort in chest area', 'Chest'),
            ('Abdominal Pain', 'digestive', 'Stomach or belly pain', 'Abdomen'),
            ('Pelvic Pain', 'pain', 'Pain in lower abdomen or pelvic area', 'Pelvis'),
            ('Toothache', 'pain', 'Pain in or around a tooth', 'Mouth'),
            ('Ear Pain', 'pain', 'Pain inside or around the ear', 'Ear'),
            ('Eye Pain', 'pain', 'Pain in or around the eyes', 'Eyes'),
            ('Leg Pain', 'pain', 'Pain in thigh, calf, or shin', 'Legs'),
            ('Arm Pain', 'pain', 'Pain in upper arm, forearm, or hand', 'Arms'),
            ('Knee Pain', 'pain', 'Pain in or around the knee', 'Knee'),
            ('Shoulder Pain', 'pain', 'Pain in shoulder joint or muscles', 'Shoulder'),
            ('Hip Pain', 'pain', 'Pain in hip joint or surrounding area', 'Hip'),
            
            # Fever/Infection symptoms
            ('Fever', 'fever', 'Elevated body temperature above 38°C/100.4°F', 'General'),
            ('Chills', 'fever', 'Feeling cold with shivering', 'General'),
            ('Night Sweats', 'fever', 'Excessive sweating during sleep', 'General'),
            ('Swollen Lymph Nodes', 'fever', 'Enlarged lymph nodes in neck, armpit, or groin', 'General'),
            
            # Respiratory symptoms
            ('Cough', 'respiratory', 'Persistent or recurring cough', 'Chest'),
            ('Dry Cough', 'respiratory', 'Cough without mucus production', 'Chest'),
            ('Wet Cough', 'respiratory', 'Cough with mucus or phlegm', 'Chest'),
            ('Shortness of Breath', 'respiratory', 'Difficulty breathing or feeling breathless', 'Chest'),
            ('Wheezing', 'respiratory', 'Whistling sound when breathing', 'Chest'),
            ('Sore Throat', 'respiratory', 'Pain or irritation in throat', 'Throat'),
            ('Runny Nose', 'respiratory', 'Nasal discharge or congestion', 'Nose'),
            ('Stuffy Nose', 'respiratory', 'Blocked or congested nasal passages', 'Nose'),
            ('Sneezing', 'respiratory', 'Frequent sneezing episodes', 'Nose'),
            ('Sinus Pressure', 'respiratory', 'Pressure or pain around sinuses', 'Face'),
            ('Loss of Smell', 'respiratory', 'Reduced or absent sense of smell', 'Nose'),
            ('Loss of Taste', 'respiratory', 'Reduced or absent sense of taste', 'Mouth'),
            
            # Digestive symptoms
            ('Nausea', 'digestive', 'Feeling sick or queasy', 'Stomach'),
            ('Vomiting', 'digestive', 'Throwing up or being sick', 'Stomach'),
            ('Diarrhea', 'digestive', 'Frequent loose or watery stools', 'Abdomen'),
            ('Constipation', 'digestive', 'Difficulty passing stools', 'Abdomen'),
            ('Bloating', 'digestive', 'Feeling of fullness or swelling in abdomen', 'Abdomen'),
            ('Heartburn', 'digestive', 'Burning sensation in chest after eating', 'Chest'),
            ('Acid Reflux', 'digestive', 'Stomach acid flowing back into esophagus', 'Chest'),
            ('Loss of Appetite', 'digestive', 'Reduced desire to eat', 'General'),
            ('Indigestion', 'digestive', 'Discomfort or pain after eating', 'Stomach'),
            ('Blood in Stool', 'digestive', 'Red or dark blood in bowel movements', 'Abdomen'),
            
            # Neurological symptoms
            ('Dizziness', 'neurological', 'Feeling lightheaded or unsteady', 'Head'),
            ('Vertigo', 'neurological', 'Spinning sensation or loss of balance', 'Head'),
            ('Numbness', 'neurological', 'Loss of sensation in body parts', 'General'),
            ('Tingling', 'neurological', 'Pins and needles sensation', 'General'),
            ('Tremor', 'neurological', 'Involuntary shaking or trembling', 'General'),
            ('Seizure', 'neurological', 'Sudden uncontrolled electrical disturbance in brain', 'Head'),
            ('Memory Problems', 'neurological', 'Difficulty remembering things', 'Head'),
            ('Confusion', 'neurological', 'Difficulty thinking clearly', 'Head'),
            ('Fainting', 'neurological', 'Brief loss of consciousness', 'Head'),
            ('Weakness', 'neurological', 'Reduced strength in muscles', 'General'),
            
            # Skin symptoms
            ('Rash', 'skin', 'Red or irritated skin patches', 'Skin'),
            ('Itching', 'skin', 'Urge to scratch the skin', 'Skin'),
            ('Hives', 'skin', 'Raised, itchy welts on skin', 'Skin'),
            ('Acne', 'skin', 'Pimples or skin breakouts', 'Face'),
            ('Dry Skin', 'skin', 'Rough, flaky, or cracked skin', 'Skin'),
            ('Bruising', 'skin', 'Discoloration from bleeding under skin', 'Skin'),
            ('Swelling', 'skin', 'Puffiness or enlargement of body parts', 'General'),
            ('Skin Discoloration', 'skin', 'Changes in skin color', 'Skin'),
            ('Wound', 'skin', 'Cut, scrape, or open sore', 'Skin'),
            ('Burn', 'skin', 'Skin damage from heat or chemicals', 'Skin'),
            
            # Mental health symptoms
            ('Anxiety', 'mental', 'Excessive worry or nervousness', 'Mental'),
            ('Depression', 'mental', 'Persistent sadness or hopelessness', 'Mental'),
            ('Insomnia', 'mental', 'Difficulty falling or staying asleep', 'Mental'),
            ('Stress', 'mental', 'Feeling overwhelmed or pressured', 'Mental'),
            ('Panic Attacks', 'mental', 'Sudden intense fear with physical symptoms', 'Mental'),
            ('Mood Swings', 'mental', 'Rapid changes in emotional state', 'Mental'),
            ('Irritability', 'mental', 'Easily annoyed or agitated', 'Mental'),
            ('Fatigue', 'general', 'Persistent tiredness or exhaustion', 'General'),
            ('Low Energy', 'general', 'Lack of energy or motivation', 'General'),
            
            # Cardiac symptoms
            ('Palpitations', 'cardiac', 'Awareness of heartbeat, racing or pounding', 'Chest'),
            ('Rapid Heartbeat', 'cardiac', 'Heart beating faster than normal', 'Chest'),
            ('Irregular Heartbeat', 'cardiac', 'Heart rhythm feels abnormal', 'Chest'),
            ('High Blood Pressure', 'cardiac', 'Elevated blood pressure readings', 'General'),
            ('Low Blood Pressure', 'cardiac', 'Below normal blood pressure', 'General'),
            ('Swollen Ankles', 'cardiac', 'Fluid retention in ankles and feet', 'Legs'),
            
            # Eye symptoms
            ('Blurred Vision', 'general', 'Difficulty seeing clearly', 'Eyes'),
            ('Double Vision', 'general', 'Seeing two images instead of one', 'Eyes'),
            ('Red Eyes', 'general', 'Bloodshot or irritated eyes', 'Eyes'),
            ('Watery Eyes', 'general', 'Excessive tearing', 'Eyes'),
            ('Sensitivity to Light', 'general', 'Eyes hurt in bright light', 'Eyes'),
            
            # Urinary symptoms
            ('Frequent Urination', 'general', 'Urinating more often than usual', 'Urinary'),
            ('Painful Urination', 'general', 'Burning or pain when urinating', 'Urinary'),
            ('Blood in Urine', 'general', 'Red or pink colored urine', 'Urinary'),
            ('Urinary Incontinence', 'general', 'Unintentional urine leakage', 'Urinary'),
            
            # Other symptoms
            ('Weight Loss', 'general', 'Unintentional loss of body weight', 'General'),
            ('Weight Gain', 'general', 'Unintentional increase in body weight', 'General'),
            ('Hair Loss', 'general', 'Thinning or loss of hair', 'Head'),
            ('Excessive Thirst', 'general', 'Feeling very thirsty frequently', 'General'),
            ('Excessive Hunger', 'general', 'Feeling very hungry frequently', 'General'),
            ('Cold Intolerance', 'general', 'Feeling cold when others are comfortable', 'General'),
            ('Heat Intolerance', 'general', 'Feeling hot when others are comfortable', 'General'),
            ('Difficulty Swallowing', 'general', 'Trouble swallowing food or liquids', 'Throat'),
            ('Hoarse Voice', 'respiratory', 'Raspy or strained voice', 'Throat'),
            ('Snoring', 'respiratory', 'Noisy breathing during sleep', 'Throat'),
            ('Sleep Apnea', 'respiratory', 'Breathing stops during sleep', 'General'),
        ]
        
        created_count = 0
        for item in default_symptoms:
            name, category, description = item[0], item[1], item[2]
            body_part = item[3] if len(item) > 3 else ''
            
            symptom, created = Symptom.objects.update_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': description,
                    'body_part': body_part
                }
            )
            if created:
                created_count += 1
        
        print(f"✅ Symptoms database updated: {created_count} new, {len(default_symptoms)} total")
    else:
        print(f"✅ Database has {Symptom.objects.count()} symptoms")


@patient_required
def triage(request):
    """Main triage page - for patients only"""
    ensure_default_symptoms()
    
    if request.method == 'POST':
        form = TriageForm(request.POST)
        
        print(f"DEBUG: Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")
            return render(request, 'triage/start.html', {
                'form': form,
                'error': 'Please correct the errors below.'
            })
        
        symptoms = form.cleaned_data['symptoms']
        additional_notes = form.cleaned_data['additional_notes']
        
        print(f"DEBUG: Selected {len(symptoms)} symptoms")
        print(f"DEBUG: Symptoms: {[s.name for s in symptoms]}")
        
        symptoms_text = ' '.join([symptom.name for symptom in symptoms])
        if additional_notes:
            symptoms_text += ' ' + additional_notes
        
        print(f"DEBUG: Symptoms text for ML: {symptoms_text}")
        
        try:
            from .ml_service import AdvancedSymptomTriageModel
            ml_model = AdvancedSymptomTriageModel()
            result = ml_model.predict_with_explanation(symptoms_text)
            predicted_specialty = result['primary_specialty']
            confidence = result['confidence']
            explanation = result['explanation']
            alternatives = result['alternative_specialties']
            print(f"DEBUG: ML prediction: {predicted_specialty} ({confidence:.1%})")
        except Exception as e:
            print(f"ML Model Error: {e}")
            predicted_specialty, confidence = fallback_prediction(symptoms)
            explanation = f"Based on symptoms: {', '.join([s.name for s in symptoms])}"
            alternatives = []
            print(f"DEBUG: Fallback prediction: {predicted_specialty} ({confidence:.1%})")
        
        if request.user.is_authenticated:
            triage_session = TriageSession.objects.create(
                user=request.user,
                predicted_specialty=predicted_specialty,
                confidence_score=confidence,
                additional_notes=additional_notes
            )
            triage_session.symptoms.set(symptoms)
        else:
            triage_session = TriageSession.objects.create(
                predicted_specialty=predicted_specialty,
                confidence_score=confidence,
                additional_notes=additional_notes
            )
            triage_session.symptoms.set(symptoms)
        
        print(f"DEBUG: Created triage session ID: {triage_session.id}")
        
        # ✅ FINAL COMBINED CONTEXT WITH session_id ADDED
        return render(request, 'triage/results.html', {
            'predicted_specialty': predicted_specialty,
            'confidence': round(confidence * 100, 1),
            'symptoms': symptoms,
            'triage_session': triage_session,
            'explanation': explanation,
            'alternatives': alternatives,
            'session_id': triage_session.id if hasattr(triage_session, 'id') else None
        })
    
    else:
        form = TriageForm()
        
        print(f"DEBUG: Form symptoms queryset count: {form.fields['symptoms'].queryset.count()}")
        print(f"DEBUG: Database symptom count: {Symptom.objects.count()}")
        
        all_symptoms = Symptom.objects.all()
        print(f"DEBUG: All symptoms in DB: {[s.name for s in all_symptoms[:5]]}...")
        
        return render(request, 'triage/start.html', {
            'form': form,
            'all_symptoms': all_symptoms
        })


@login_required
@patient_required
def triage_chat(request):
    """Interactive chat-based triage - for patients only"""
    if 'chatbot' not in request.session:
        chatbot = HealthLinkChatBot(user=request.user)
        request.session['chatbot'] = {
            'symptoms': [],
            'symptom_details': {},
            'state': 'greeting',
            'conversation': []
        }
    
    return render(request, 'triage/chat.html')


@csrf_exempt
@login_required
def triage_chat_api(request):
    """
    API endpoint for LLM-based chat interactions.
    Uses OpenAI GPT when available, falls back to rule-based system.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)

            # Handle reset command
            if user_message == '__reset__':
                if 'llm_triage_service' in request.session:
                    del request.session['llm_triage_service']
                request.session.modified = True
                return JsonResponse({
                    'response': '✨ Session reset. Starting fresh!',
                    'ready_for_results': False,
                    'symptoms': [],
                    'state': 'greeting',
                    'mode': 'fallback'
                })

            # Initialize or retrieve LLM service
            api_available = False
            if 'llm_triage_service' in request.session:
                service_data = request.session['llm_triage_service']
                llm_service = LLMTriageService(use_openai=False)  # Initialize without API first
                llm_service.conversation_history = service_data.get('conversation_history', [])
                llm_service.symptoms_identified = service_data.get('symptoms_identified', [])
                llm_service.state = service_data.get('state', 'greeting')
                api_available = service_data.get('api_available', False)
            else:
                llm_service = LLMTriageService(use_openai=True)  # Try with API
                api_available = llm_service.api_available
                
                # Get initial greeting
                greeting = llm_service.get_greeting()
                
                request.session['llm_triage_service'] = {
                    'conversation_history': [],
                    'symptoms_identified': [],
                    'state': 'greeting',
                    'api_available': api_available
                }

            # Process user message
            analysis = llm_service.process_patient_message(user_message)

            # Save session state
            request.session['llm_triage_service'] = {
                'conversation_history': llm_service.conversation_history,
                'symptoms_identified': llm_service.symptoms_identified,
                'state': llm_service.state,
                'api_available': llm_service.api_available
            }
            request.session.modified = True

            # Prepare response
            response_text = analysis.get('next_question', 'Please continue describing your symptoms.')
            mode = 'openai' if llm_service.api_available else 'fallback'

            # Handle recommendation state
            if analysis.get('ready_for_recommendation') and analysis.get('recommendation'):
                recommendation = analysis['recommendation']
                
                # Create triage session
                triage_session = TriageSession.objects.create(
                    user=request.user,
                    session_type='chat',
                    predicted_specialty=recommendation.get('primary_specialty', 'General Medicine'),
                    confidence_score=0.85,
                    conversation_history=llm_service.conversation_history,
                    additional_notes=json.dumps(analysis, indent=2)
                )

                # Add identified symptoms to session
                for symptom_name in llm_service.symptoms_identified:
                    symptom, _ = Symptom.objects.get_or_create(
                        name=symptom_name,
                        defaults={'category': 'general', 'body_part': 'General'}
                    )
                    triage_session.symptoms.add(symptom)

                return JsonResponse({
                    'response': response_text,
                    'session_id': triage_session.id,
                    'ready_for_results': True,
                    'symptoms': llm_service.symptoms_identified,
                    'state': 'recommendation',
                    'recommendation': recommendation,
                    'mode': mode,
                    'api_available': llm_service.api_available
                })

            return JsonResponse({
                'response': response_text,
                'ready_for_results': False,
                'symptoms': llm_service.symptoms_identified,
                'state': llm_service.state,
                'severity': analysis.get('severity_assessment', 'medium'),
                'emergency_alert': analysis.get('emergency_alert', False),
                'mode': mode,
                'api_available': llm_service.api_available
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request'}, status=400)
        except Exception as e:
            logger.error(f"Chat API Error: {e}", exc_info=True)
            return JsonResponse({
                'error': str(e),
                'message': 'An error occurred. Please try again.',
                'response': 'I apologize for the technical difficulty. Please try describing your symptoms again.'
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def fallback_prediction(symptoms):
    """Rule-based fallback when ML fails"""
    symptom_names = [s.name.lower() for s in symptoms]
    
    print(f"DEBUG: Fallback prediction for: {symptom_names}")
    
    if any(s in ['chest pain', 'heart', 'palpitations', 'chest'] for s in symptom_names):
        return "Cardiology", 0.8
    elif any(s in ['headache', 'migraine', 'dizziness', 'seizure'] for s in symptom_names):
        return "Neurology", 0.7
    elif any(s in ['cough', 'breathing', 'asthma', 'lung', 'shortness of breath'] for s in symptom_names):
        return "Pulmonology", 0.7
    elif any(s in ['stomach', 'abdominal', 'diarrhea', 'vomiting', 'nausea'] for s in symptom_names):
        return "Gastroenterology", 0.7
    elif any(s in ['rash', 'itching', 'skin', 'acne'] for s in symptom_names):
        return "Dermatology", 0.8
    elif any(s in ['joint', 'arthritis', 'back pain', 'bone'] for s in symptom_names):
        return "Orthopedics", 0.7
    elif any(s in ['anxiety', 'depression', 'stress', 'mental'] for s in symptom_names):
        return "Psychiatry", 0.75
    else:
        return "General Medicine", 0.6


@login_required
@patient_required
@csrf_exempt
def save_assessment(request):
    """Save assessment - for patients only"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            saved_assessment = SavedAssessment.objects.create(
                user=request.user,
                predicted_specialty=data.get('specialty'),
                confidence=data.get('confidence'),
                symptoms_text=', '.join(data.get('symptoms', [])),
                explanation=data.get('explanation', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Assessment saved to your dashboard!',
                'assessment_id': saved_assessment.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
