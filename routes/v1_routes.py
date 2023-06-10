from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import *
from apps.notification.views import ActivityAppViewSet
from apps.wallet.views import *
from apps.dashboard.views import *
from apps.loans.views import *
from routes.auth_router import AuthRouter
from routes.extend_router import ExtendRouter


v1_router = AuthRouter()

v1_router.admin_register(r'users', UserViewSet, basename='users')
v1_router.admin_register(r'auth', AuthViewSet, basename='auth')

v1_router.investor_register(r'investor', InvestorViewSet, basename='investor')

v1_router.admin_register(r'partner', PartnerViewSet, basename='partner')

v1_router.register(r'wallet', WalletViewSet, basename='wallet')

v1_router.common_registry(r'transaction', TransactionViewSet, basename='transaction')
v1_router.common_registry(r'loan', LoanViewSet, basename='loan')
v1_router.common_registry(r'notification', ActivityAppViewSet, basename='notification')


ex_router = ExtendRouter()
ex_router.extend(v1_router)

urlpatterns = [
    path('', include(ex_router))
]
