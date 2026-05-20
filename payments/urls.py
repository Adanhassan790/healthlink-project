from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/<int:appointment_id>/', views.payment_page, name='payment_page'),
    path('initiate/<int:appointment_id>/', views.initiate_payment, name='initiate_payment'),
    path('status/<int:transaction_id>/', views.payment_status, name='payment_status'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('history/', views.payment_history, name='payment_history'),
]