from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser, DoctorProfile, PatientProfile
from appointments.models import Specialty, Appointment

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create specialties
        specialties = [
            'Cardiology', 'Dermatology', 'Neurology', 'Pediatrics', 
            'Orthopedics', 'Gynecology', 'Psychiatry', 'Dentistry'
        ]
        
        for spec in specialties:
            Specialty.objects.get_or_create(name=spec)
            self.stdout.write(f'Created specialty: {spec}')
        
        # Create sample doctors
        doctors_data = [
            {
                'username': 'dr_Hawaa',
                'email': 'dr.hawaa@healthlink.com',
                'first_name': 'hassan',
                'last_name': 'hawaa',
                'specialization': 'Cardiology',
                'license': 'CAR12345',
                'experience': 15,
                'fee': 150.00
            },
            {
                'username': 'dr_johnson',
                'email': 'dr.johnson@healthlink.com', 
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'specialization': 'Pediatrics',
                'license': 'PED67890',
                'experience': 10,
                'fee': 120.00
            },
            {
                'username': 'dr_williams',
                'email': 'dr.williams@healthlink.com',
                'first_name': 'Michael',
                'last_name': 'Williams',
                'specialization': 'Dermatology',
                'license': 'DER54321',
                'experience': 8,
                'fee': 130.00
            }
        ]
        
        for doc_data in doctors_data:
            user, created = CustomUser.objects.get_or_create(
                username=doc_data['username'],
                defaults={
                    'email': doc_data['email'],
                    'first_name': doc_data['first_name'],
                    'last_name': doc_data['last_name'],
                    'user_type': 'doctor'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                
                specialty = Specialty.objects.get(name=doc_data['specialization'])
                DoctorProfile.objects.create(
                    user=user,
                    license_number=doc_data['license'],
                    specialization=doc_data['specialization'],
                    years_of_experience=doc_data['experience'],
                    consultation_fee=doc_data['fee']
                )
                self.stdout.write(f'Created doctor: Dr. {doc_data["first_name"]} {doc_data["last_name"]}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )