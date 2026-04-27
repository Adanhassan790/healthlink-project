"""
Django management command to create admin superuser if it doesn't exist
Usage: python manage.py shell < create_admin.py
Or: python manage.py create_admin_user
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthlink.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin already exists
if User.objects.filter(username='admin').exists():
    print("[OK] Admin user already exists")
else:
    # Create admin user
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@healthlink.com',
        password='AdminPass123!'
    )
    print("[OK] Admin user created successfully")
    print("Username: admin")
    print("Password: AdminPass123!")
