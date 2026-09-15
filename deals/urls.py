from django.urls import path
from .views import (
    buyer_dashboard, express_interest,
    manager_deals_dashboard, manager_select_buyer, manager_process_handover,
    seller_deal_confirmation
)

urlpatterns = [
    # Buyer URLs
    path('dashboard/', buyer_dashboard, name='buyer_dashboard'),
    path('interest/<str:pk>/', express_interest, name='express_interest'),
    
    # Manager URLs
    path('manager/deals/', manager_deals_dashboard, name='manager_deals_dashboard'),
    path('manager/select-buyer/<str:pk>/', manager_select_buyer, name='manager_select_buyer'),
    path('manager/handover/<str:pk>/', manager_process_handover, name='manager_handover'),
    
    # Seller URLs
    path('seller/confirm/<str:pk>/', seller_deal_confirmation, name='seller_deal_confirmation'),
]
