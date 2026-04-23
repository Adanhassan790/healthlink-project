from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration URLs - point to users.views for actual form processing
    path('register/patient/', user_views.patient_register, name='patient_register'),
    path('register/doctor/', user_views.doctor_register, name='doctor_register'),
    
    # Profile URL
    path('profile/', views.profile, name='profile'),
    
    # IMPORTANT: 
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('users/', include('users.urls', namespace='users')),
    path('administration/', include('administration.urls', namespace='administration')),

    path('triage/', include('triage.urls', namespace='triage')),
    path('messaging/', include('messaging.urls', namespace='messaging')),  
    path('payments/', include('payments.urls', namespace='payments')),
    path('prescriptions/', include('prescriptions.urls', namespace='prescriptions')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom error handlers
handler500 = 'healthlink.views.error_500'
handler404 = 'healthlink.views.error_404'
handler403 = 'healthlink.views.error_403'