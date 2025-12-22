from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:doctor_id>/reviews/', views.doctor_reviews, name='doctor_reviews'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('book/', views.book_appointment_redirect, name='book_appointment_redirect'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('review/<int:appointment_id>/', views.submit_review, name='submit_review'),
    
    # Doctor availability management
    path('availability/', views.manage_availability, name='manage_availability'),
    path('availability/add/', views.add_availability, name='add_availability'),
    path('availability/delete/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('availability/toggle/<int:slot_id>/', views.toggle_availability, name='toggle_availability'),
    path('api/slots/<int:doctor_id>/', views.get_doctor_available_slots, name='get_doctor_slots'),
]