from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Emergency / orchestration
    path('sos/', views.sos_trigger, name='sos'),
    path('emergencies/', views.emergencies_list, name='emergencies'),
    path('emergency/<int:pk>/', views.emergency_detail, name='emergency_detail'),
    path('emergency/<int:pk>/resolve/', views.emergency_resolve, name='emergency_resolve'),

    # Patient
    path('patient/', views.patient_detail, name='patient'),
    path('patient/<int:pk>/', views.patient_detail, name='patient_detail'),

    # Providers
    path('providers/', views.providers_list, name='providers'),

    # Travel plans
    path('travel/', views.travel_list, name='travel'),
    path('travel/create/', views.travel_create, name='travel_create'),
    path('travel/<int:pk>/', views.travel_detail, name='travel_detail'),
]
