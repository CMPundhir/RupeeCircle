from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import *
from apps.notification.views import ActivityAppViewSet
from apps.loans.views import LoanFormViewSet

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'auth', AuthViewSet, basename='auth')
v1_router.register(r'aggregator', AggregatorViewSet, basename='aggregator')
v1_router.register(r'loan', LoanFormViewSet, basename='loan')
v1_router.register(r'notification', ActivityAppViewSet, basename='notification')
v1_router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('', include(v1_router))
]