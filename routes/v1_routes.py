from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import *
from apps.notification.views import *
from apps.wallet.views import *
from apps.dashboard.views import *
from apps.loans.views import *
from apps.helpline.views import *

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='users')
v1_router.register(r'auth', AuthViewSet, basename='auth')
v1_router.register(r'investor', InvestorViewSet, basename='investor')
v1_router.register(r'partner', PartnerViewSet, basename='partner')
v1_router.register(r'wallet', WalletViewSet, basename='wallet')
v1_router.register(r'transaction', TransactionViewSet, basename='transaction')
v1_router.register(r'loan', LoanViewSet, basename='loan')
v1_router.register(r'fixed-roi', FixedROIViewSet, basename='fixed-roi')
v1_router.register(r'anytime-withdrawal', AnytimeWithdrawalViewSet, basename='anytime-withdrawal')
v1_router.register(r'my-investments', MyInvestmentViewSet, basename='my-investments')
v1_router.register(r'investment-request', InvestmentRequestViewSet, basename='investment-request')
v1_router.register(r'notification', ActivityAppViewSet, basename='notification')
v1_router.register(r'recent-activity', RecentActivityViewSet, basename='recent-activity')
v1_router.register(r'helpline', ComplaintViewSet, basename='helpline')


urlpatterns = [
    path('', include(v1_router))
]
