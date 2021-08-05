from django.urls import path, include
from rest_framework import routers
from .views import remove_auth_token, obtain_auth_token, register_view
from .views import AppUserView, MenuItemView
from .views import MenuItemView

manager_router = routers.DefaultRouter()
manager_router.register('user', AppUserView, basename='app-user')
manager_router.register('menu', MenuItemView)

urlpatterns = [
    path('', include(manager_router.urls)),
    path('login/', obtain_auth_token, name='login'),
    path('logout/', remove_auth_token, name='logout'),
    path('register/', register_view, name='register'),
]
