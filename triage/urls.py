
from django.urls import path
from . import views

app_name = 'triage'

urlpatterns = [
    path('', views.triage, name='triage'),
    path('chat/', views.triage_chat, name='triage_chat'),
    path('chat/api/', views.triage_chat_api, name='triage_chat_api'),
    path('chat/book-appointment/', views.book_appointment_from_chat, name='book_appointment_from_chat'),
    path('save-assessment/', views.save_assessment, name='save_assessment'),
]