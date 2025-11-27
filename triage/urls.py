from django.urls import path
from . import views

app_name = 'triage'

urlpatterns = [
    path('', views.triage, name='triage'),
    path('chat/', views.triage_chat, name='triage_chat'),
    path('chat/api/', views.triage_chat_api, name='triage_chat_api'),
]