from django.contrib import admin
from django.urls import path, include
from accounts.views import HomeView
from django.conf import settings
from django.conf.urls.static import static
from vehicles.views import manager_dashboard, manager_review, manager_list_vehicle

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('seller/', include('vehicles.urls')),
    path('deals/', include('deals.urls')),
    path('manager/dashboard', manager_dashboard, name='manager_dashboard'),
    path('manager/review/<str:pk>/', manager_review, name='manager_review'),
    path('manager/list/<str:pk>/', manager_list_vehicle, name='manager_list_vehicle'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
