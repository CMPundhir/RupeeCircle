from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import UserViewSet, AuthViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(v1_router))
]