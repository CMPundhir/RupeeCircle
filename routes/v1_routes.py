from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import *
from apps.notification.views import ActivityAppViewSet
from apps.wallet.views import *
from apps.dashboard.views import *
from apps.loans.views import *

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'auth', AuthViewSet, basename='auth')
v1_router.register(r'investor', InvestorViewSet, basename='investor')
v1_router.register(r'partner', PartnerViewSet, basename='partner')
v1_router.register(r'wallet', WalletViewSet, basename='wallet')
v1_router.register(r'transaction', TransactionViewSet, basename='transaction')
v1_router.register(r'loan', LoanViewSet, basename='loan')
v1_router.register(r'notification', ActivityAppViewSet, basename='notification')

urlpatterns = [
    path('', include(v1_router))
]
