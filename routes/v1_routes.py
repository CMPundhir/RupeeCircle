from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.mauth.views import *
from apps.notification.views import *
from apps.wallet.views import *
from apps.dashboard.views import *
from apps.loans.views import *
from apps.helpline.views import *
from routes.auth_router import AuthRouter
from routes.extend_router import ExtendRouter


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



# v1_router = AuthRouter()

# v1_router.admin_register(r'users', UserViewSet, basename='users')
# v1_router.admin_register(r'auth', AuthViewSet, basename='auth')
# v1_router.admin_register(r'investor', InvestorViewSet, basename='investor')
# v1_router.admin_register(r'partner', PartnerViewSet, basename='partner')

# v1_router.partner_register(r'investor', InvestorViewSet, basename='investor')

# v1_router.common_registry(r'users', UserViewSet, basename='users')
# v1_router.common_registry(r'auth', AuthViewSet, basename='auth')
# v1_router.common_registry(r'wallet', WalletViewSet, basename='wallet')
# v1_router.common_registry(r'transaction', TransactionViewSet, basename='transaction')
# v1_router.common_registry(r'loan', LoanViewSet, basename='loan')
# v1_router.common_registry(r'notification', ActivityAppViewSet, basename='notification')


# ex_router = ExtendRouter()
# ex_router.extend(v1_router)

# urlpatterns = [
#     path('', include(ex_router))
# ]

urlpatterns = [
    path('', include(v1_router))
]
