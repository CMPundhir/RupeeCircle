from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import UserViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router))
]