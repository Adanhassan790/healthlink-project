from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('start/<int:appointment_id>/', views.start_conversation, name='start_conversation'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
]