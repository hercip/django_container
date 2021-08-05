"""Face To Face Poker URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/manager/', include('manager.urls')),
]
