from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('homepage.urls')),
    path('inventory/', include('inventory.urls')),
    path('transactions/', include('transactions.urls')),
]