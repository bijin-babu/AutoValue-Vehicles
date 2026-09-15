from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register_seller_view, register_buyer_view, UserLoginView, HomeView

urlpatterns = [
    path('register/seller/', register_seller_view, name='register_seller'),
    path('register/buyer/', register_buyer_view, name='register_buyer'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
