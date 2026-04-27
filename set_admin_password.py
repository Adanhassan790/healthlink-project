#!/usr/bin/env python
"""Set password for admin superuser"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthlink.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    u = User.objects.get(username='admin')
    u.set_password('AdminPass123!')
    u.save()
    print('[OK] Password set successfully for admin')
    print('Username: admin')
    print('Password: AdminPass123!')
except User.DoesNotExist:
    print('[ERROR] Admin user not found')
