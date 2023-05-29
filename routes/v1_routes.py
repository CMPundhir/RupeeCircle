from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import *
from apps.notification.views import ActivityAppViewSet
from apps.dashboard.views import *
from apps.loans.views import *

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'auth', AuthViewSet, basename='auth')
v1_router.register(r'investor', InvestorViewSet, basename='investor')
v1_router.register(r'aggregator', AggregatorViewSet, basename='aggregator')
v1_router.register(r'loanform', LoanFormViewSet, basename='loanform')
v1_router.register(r'loan', LoanViewSet, basename='loan')
v1_router.register(r'notification', ActivityAppViewSet, basename='notification')

urlpatterns = [
    path('', include(v1_router))
]
