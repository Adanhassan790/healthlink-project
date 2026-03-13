from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication - these are duplicates of healthlink/urls.py, kept for backwards compatibility
    # path('login/', auth_views.LoginView.as_view(template_name='healthlink/users/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Registration
    path('register/patient/', views.patient_register, name='users_patient_register'),
    path('register/doctor/', views.doctor_register, name='users_doctor_register'),
    
    # Redirect old dashboard URL to main dashboard
    path('dashboard/', RedirectView.as_view(pattern_name='dashboard', permanent=True), name='users_dashboard'),
    path('profile/', views.profile, name='users_profile'),

    path('profile/update-patient/', views.update_patient_profile, name='update_patient_profile'),
    path('profile/update-doctor/', views.update_doctor_profile, name='update_doctor_profile'),
]
