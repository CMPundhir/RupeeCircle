"""
URL configuration for rupeecircle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from rest_framework.urls
from django.urls import path, include
from routes.v1_routes import v1_router
from apps.mauth.views import *
# from apps.wallet.views import dataform
from django.conf.urls.static import static
from rupeecircle import settings


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    # path('dataform/', dataform),
    # path('login/', LogInView.as_view(), name='login'),
    # path('logout/', LogOutView.as_view(), name='logout'),
    # path('get-otp/', GetOTPView.as_view(), name='get-otp'),
    # path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    # path('get-pan/', PanDetailView.as_view(), name='get-pan'),
    # path('verify-pan/', PanVerifyView.as_view(), name='verify-pan'),
    # path('get-aadhar/', AadharDetailView.as_view(), name='get-aadhar'),
    # path('verify-aadhar/', AadharVerifyView.as_view(), name='verify-aadhar'),
    path('', include(v1_router.urls), name="v1"),
    path('v1/', include(v1_router.urls), name="v1")
]

admin.site.site_header = "Rupee Circle Admin"
admin.site.site_title = "Rupee Circle Admin Portal"
admin.site.index_title = "Welcome to Rupee Circle Admin Portal"

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
