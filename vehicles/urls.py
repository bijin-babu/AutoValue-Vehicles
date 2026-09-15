from django.urls import path
from .views import seller_dashboard, submit_vehicle, edit_vehicle, delete_vehicle

urlpatterns = [
    path('dashboard/', seller_dashboard, name='seller_dashboard'),
    path('submit/', submit_vehicle, name='submit_vehicle'),
    path('<str:pk>/edit/', edit_vehicle, name='edit_vehicle'),
    path('<str:pk>/delete/', delete_vehicle, name='delete_vehicle'),
]
