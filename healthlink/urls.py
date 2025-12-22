from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration URLs 
    path('register/patient/', views.patient_register, name='patient_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    
    # Profile URL
    path('profile/', views.profile, name='profile'),
    
    # IMPORTANT: 
    path('appointments/', include('appointments.urls')),
    path('users/', include('users.urls')),

    path('triage/', include('triage.urls')),
    path('messaging/', include('messaging.urls', namespace='messaging')),  
    path('payments/', include('payments.urls')),
    path('prescriptions/', include('prescriptions.urls')),
    path('notifications/', include('notifications.urls')),
]