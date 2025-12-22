from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    # Doctor views
    path('', views.prescription_list, name='prescription_list'),
    path('create/', views.create_prescription, name='create_prescription'),
    path('quick/', views.quick_prescription, name='quick_prescription'),
    path('<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('<int:pk>/items/', views.add_prescription_items, name='add_items'),
    path('<int:pk>/items/<int:item_pk>/remove/', views.remove_prescription_item, name='remove_item'),
    path('<int:pk>/sign/', views.sign_prescription, name='sign_prescription'),
    path('<int:pk>/cancel/', views.cancel_prescription, name='cancel_prescription'),
    
    # Patient views
    path('my/', views.my_prescriptions, name='my_prescriptions'),
    path('view/<int:pk>/', views.view_prescription, name='patient_view'),
    path('<int:pk>/download/', views.download_prescription, name='download_prescription'),
    path('verify/', views.verify_prescription, name='verify_prescription'),
    
    # API endpoints
    path('api/medications/', views.medication_search_api, name='medication_search'),
    path('api/stats/', views.prescription_stats, name='prescription_stats'),
]
