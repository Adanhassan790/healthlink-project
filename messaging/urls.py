from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('start/<int:appointment_id>/', views.start_conversation, name='start_conversation'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    
    # Video call URLs
    path('call/start/<int:conversation_id>/', views.start_video_call, name='start_video_call'),
    path('call/join/<int:call_id>/', views.join_video_call, name='join_video_call'),
    path('call/end/<int:call_id>/', views.end_video_call, name='end_video_call'),
    path('call/decline/<int:call_id>/', views.decline_video_call, name='decline_video_call'),
    path('call/status/<int:call_id>/', views.get_call_status, name='get_call_status'),
    path('call/check/<int:conversation_id>/', views.check_incoming_call, name='check_incoming_call'),
    path('call/room/<str:room_id>/', views.video_room, name='video_room'),
    path('call/register-peer/<int:call_id>/', views.register_peer, name='register_peer'),
    path('call/get-peer/<int:call_id>/', views.get_peer, name='get_peer'),
    
    # WebRTC Signaling URLs
    path('call/signal/offer/<int:call_id>/', views.send_offer, name='send_offer'),
    path('call/signal/get-offer/<int:call_id>/', views.get_offer, name='get_offer'),
    path('call/signal/answer/<int:call_id>/', views.send_answer, name='send_answer'),
    path('call/signal/get-answer/<int:call_id>/', views.get_answer, name='get_answer'),
    path('call/signal/ice/<int:call_id>/', views.send_ice_candidate, name='send_ice_candidate'),
    path('call/signal/get-ice/<int:call_id>/', views.get_ice_candidates, name='get_ice_candidates'),
    path('call/signal/state/<int:call_id>/', views.get_signaling_state, name='get_signaling_state'),
    
    # Call history and statistics URLs
    path('call/history/<int:conversation_id>/', views.call_history, name='call_history'),
    path('call/stats/dashboard/', views.call_statistics_dashboard, name='call_stats_dashboard'),
    path('call/stats/<int:conversation_id>/', views.call_statistics, name='call_stats_conversation'),
    path('call/stats/', views.call_statistics, name='call_stats_user'),
    path('call/recording/<int:call_id>/', views.toggle_call_recording, name='toggle_recording'),
    
    # Diagnostics
    path('call/diagnostics/<int:conversation_id>/', views.video_call_diagnostics, name='call_diagnostics'),
]