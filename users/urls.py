from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='healthlink/users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Registration
    path('register/patient/', views.patient_register, name='patient_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
]
