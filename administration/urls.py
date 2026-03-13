from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
]
