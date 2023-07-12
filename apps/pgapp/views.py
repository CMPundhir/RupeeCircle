from django.shortcuts import render
from rest_framework import viewsets
from .serializers import PhonePeSerializer
from rest_framework.decorators import action
from apps.notification.services import LogService
from apps.wallet.models import Wallet
import requests

# Create your views here.

class PhonePeViewSet(viewsets.ModelViewSet):

    # def get_queryset(self):
    #     serializer = PhonePeSerializer()
    #     return super().get_queryset()
    
    def get_serializer_class(self):
        return PhonePeSerializer

    @action(methods=['POST'], detail=False)
    def create_order(self, request):
        user = request.user
        wallet = Wallet.objects.get(owner=user)
        serializer = PhonePeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            amount = serializer.validated_data['amount']
            transaction = LogService.transaction_log(user, wallet, amount, debit=True, url="NA", ref="NA", type=None)
            data = {"merchantId": "MERCHANTUAT",
                    "merchantTransactionId": f"{transaction.transaction_id}",
                    "merchantUserId": "MUID123",
                    "amount": amount,
                    "redirectUrl": "https://webhook.site/redirect-url",
                    "redirectMode": "POST",
                    "callbackUrl": "https://webhook.site/callback-url",
                    "mobileNumber": "9999999999",
                    "paymentInstrument": {
                        "type": "PAY_PAGE"
                    }}
            headers = {"Content-Type": "application/json", "X-VERIFY": ""}
        
