"""
Management command to populate initial doctor data for testing/deployment
Usage: python manage.py populate_doctors
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import CustomUser, DoctorProfile
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Populates database with sample doctors for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate doctors...'))
        
        doctors_data = [
            {
                'username': 'dr_john_smith',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@healthlink.com',
                'license_number': 'LN001',
                'specialization': 'General Practice',
                'years_of_experience': 8,
                'bio': 'Experienced GP with focus on preventive medicine',
                'consultation_fee': '50.00',
            },
            {
                'username': 'dr_sarah_johnson',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@healthlink.com',
                'license_number': 'LN002',
                'specialization': 'Cardiology',
                'years_of_experience': 12,
                'bio': 'Specialist in cardiovascular diseases',
                'consultation_fee': '75.00',
            },
            {
                'username': 'dr_michael_chen',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'michael.chen@healthlink.com',
                'license_number': 'LN003',
                'specialization': 'Neurology',
                'years_of_experience': 10,
                'bio': 'Expert in neurological disorders',
                'consultation_fee': '70.00',
            },
            {
                'username': 'dr_emily_williams',
                'first_name': 'Emily',
                'last_name': 'Williams',
                'email': 'emily.williams@healthlink.com',
                'license_number': 'LN004',
                'specialization': 'Pediatrics',
                'years_of_experience': 7,
                'bio': 'Dedicated to child health and development',
                'consultation_fee': '60.00',
            },
            {
                'username': 'dr_james_brown',
                'first_name': 'James',
                'last_name': 'Brown',
                'email': 'james.brown@healthlink.com',
                'license_number': 'LN005',
                'specialization': 'Orthopedics',
                'years_of_experience': 15,
                'bio': 'Specialist in bone and joint conditions',
                'consultation_fee': '80.00',
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for doctor_info in doctors_data:
            username = doctor_info.pop('username')
            
            # Check if user already exists
            if CustomUser.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'  [SKIP] Skipped {username} (already exists)'))
                skipped_count += 1
                continue
            
            try:
                # Create user
                user = CustomUser.objects.create(
                    username=username,
                    first_name=doctor_info.pop('first_name'),
                    last_name=doctor_info.pop('last_name'),
                    email=doctor_info.pop('email'),
                    user_type='doctor',
                    password=make_password('defaultpassword123'),  # Default password
                    is_active=True,
                )
                
                # Create doctor profile
                DoctorProfile.objects.create(
                    user=user,
                    license_number=doctor_info.pop('license_number'),
                    specialization=doctor_info.pop('specialization'),
                    years_of_experience=doctor_info.pop('years_of_experience'),
                    bio=doctor_info.pop('bio'),
                    consultation_fee=doctor_info.pop('consultation_fee'),
                )
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created doctor: {username}'))
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error creating {username}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS(f'Completed! Created: {created_count}, Skipped: {skipped_count}'))
        self.stdout.write(self.style.WARNING('Default password for all doctors: defaultpassword123'))
