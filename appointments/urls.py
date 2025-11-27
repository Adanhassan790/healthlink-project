from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('book/', views.book_appointment_redirect, name='book_appointment_redirect'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    
]