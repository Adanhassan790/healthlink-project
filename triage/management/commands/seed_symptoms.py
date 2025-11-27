from django.core.management.base import BaseCommand
from triage.models import Symptom

class Command(BaseCommand):
    help = 'Seed initial symptoms data'

    def handle(self, *args, **options):
        symptoms = [
            'Fever', 'Cough', 'Headache', 'Chest Pain', 'Shortness of Breath',
            'Rash', 'Itching', 'Skin Redness', 'Dizziness', 'Nausea',
            'Abdominal Pain', 'Diarrhea', 'Vomiting', 'Joint Pain', 'Swelling',
            'Stiffness', 'Anxiety', 'Depression', 'Mood Swings', 'Sore Throat',
            'Runny Nose', 'Sneezing', 'Back Pain', 'Muscle Spasms', 'Vision Problems',
            'Eye Pain', 'Fatigue', 'Weight Loss', 'Weight Gain', 'Insomnia'
        ]
        
        for symptom_name in symptoms:
            Symptom.objects.get_or_create(name=symptom_name)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(symptoms)} symptoms')
        )