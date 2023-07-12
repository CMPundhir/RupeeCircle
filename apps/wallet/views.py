from django.shortcuts import render
import requests
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.notification.services import LogService
from apps.mauth.serializers import BankDetailSerializer
from rest_framework import status
from .models import Wallet
from apps.mauth.models import CustomUser as User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.settings import api_settings
from .serializers import *
from utility.ccavutil import encrypt,decrypt
from django.views.decorators.csrf import csrf_exempt
import os
import base64
import hashlib
import json
from dotenv import load_dotenv


load_dotenv()


accessCode = 'AVSA23KB49BS35ASSB' 	
workingKey = '8AEBE08197C1C01D3F141A122A3A7E51'

# Create your views here.


class WalletViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['owner', 'balance', 'invested_amount']
    ordering_fields = ['id']
    filterset_fields = ['owner', 'balance', 'invested_amount']

    def get_queryset(self):
        user = self.request.user
        # if user.role == User.ROLE_CHOICES[3][1]:
        #     queryset = Wallet.objects.all()
        # else:
        queryset = Wallet.objects.filter(owner=user.id).order_by('-id')
        # queryset = Wallet.objects.all()
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return WalletGetSerializer
        elif self.action == 'addFunds' or self.action == 'withdrawFunds':
            return AddFundsSerializer
        else:
            return WalletSerializer

    def list(self, request):
        user = request.user
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset[0])
        if user.role != User.ROLE_CHOICES[3][1]:
            return Response(serializer.data, status=status.HTTP_200_OK)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(methods=['POST'], detail=False)
    def addFunds(self, request):
        data = request.data
        user = request.user
        instance = self.get_queryset().get(owner=user)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance.balance += serializer.validated_data['value']
            instance.save()
            LogService.log(user=user, msg=f"Rs.{serializer.validated_data['value']} credited to  your wallet. Your wallet balance is Rs.{instance.balance}.",
                           is_activity=True)
            LogService.transaction_log(owner=user, wallet=instance, amount=serializer.validated_data['value'], type=Transaction.TYPE_CHOICES[0][1])
            return Response({"message": "Funds added successfully.", "balance": instance.balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False)
    def withdrawFunds(self, request):
        data = request.data
        user = request.user
        instance = self.get_queryset()[0]
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            if instance.balance < serializer.validated_data['value']:
                return Response({"message": "You don't have enough balance in your wallet."}, status=status.HTTP_400_BAD_REQUEST)
            instance.balance -= serializer.validated_data['value']
            instance.save()
            LogService.log(user=user, msg=f"Rs.{serializer.validated_data['value']} debited to your wallet. Your wallet balance is Rs.{instance.balance}.",
                           is_activity=True)
            LogService.transaction_log(owner=user, wallet=instance, amount=serializer.validated_data['value'], debit=True, type=Transaction.TYPE_CHOICES[1][1])
            return Response({"message": "Funds withdrawn successfully.", "balance": instance.balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['GET'], detail=False)
    def addall(self, request):
        users = User.objects.all()
        for i in users:
            wallet = Wallet.objects.filter(owner=i).exists()
            if not wallet:
                Wallet.objects.create(owner=i)
        return Response("Added")
    
    # @csrf_exempt
    # @action(methods=['GET', 'POST'], detail=False)
    # def addByCcav(self, request):
    #     p_merchant_id = '2954' # request.form['merchant_id']
    #     p_order_id = "466555992256  " # request.form['order_id']
    #     p_currency = 'INR' # request.form['currency']
    #     p_amount = '1.00' # request.form['amount']
    #     p_redirect_url = "http://192.168.2.49:8086/ccavResponseHandler" # request.form['redirect_url']
    #     p_cancel_url = "http://192.168.2.49:8086/ccavResponseHandler" # request.form['cancel_url']
    #     p_language = "EN" # request.form['language']
    #     p_billing_name = "Peter" # request.form['billing_name']
    #     p_billing_address = "billing_address" # request.form['billing_address']
    #     p_billing_city = "Mumbai" # request.form['billing_city']
    #     p_billing_state = "MH" # request.form['billing_state']
    #     p_billing_zip = "400054" # request.form['billing_zip']
    #     p_billing_country = "India" # request.form['billing_country']
    #     p_billing_tel = "0229874789" # request.form['billing_tel']
    #     p_billing_email = "testing@domain.com"# request.form['billing_email']
    #     p_delivery_name = "Sam"# request.form['delivery_name']
    #     p_delivery_address = "Vile Parle"# request.form['delivery_address']
    #     p_delivery_city = "Mumbai"# request.form['delivery_city']
    #     p_delivery_state = "Maharashtra"# request.form['delivery_state']
    #     p_delivery_zip = "400038"# request.form['delivery_zip']
    #     p_delivery_country = "India"# request.form['delivery_country']
    #     p_delivery_tel = "0221234321"# request.form['delivery_tel']
    #     p_merchant_param1 = "additional Info."# request.form['merchant_param1']
    #     p_merchant_param2 = "additional Info." # request.form['merchant_param2']
    #     p_merchant_param3 = "additional Info."# request.form['merchant_param3']
    #     p_merchant_param4 = "additional Info."# request.form['merchant_param4']
    #     p_merchant_param5 = "additional Info."# request.form['merchant_param5']
    #     p_promo_code = ""# request.form['promo_code']
    #     p_customer_identifier = ""# request.form['customer_identifier']
        
        

    #     merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
            
    #     encryption = encrypt(merchant_data,workingKey)
    #     return Response({"data": encryption})


class TransactionViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['transaction_id', 'owner', 'amount', 'id', 'wallet']
    ordering_fields = ['id']
    filterset_fields = ['transaction_id', 'wallet', 'owner', 'amount', 'type']

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(owner=user).order_by('-id')
        # return queryset
        # queryset = Transaction.objects.all().order_by('-id')
        return queryset
    
    def get_serializer_class(self):
        if self.action == "createOrder":
            return CreateOrderSerializer
        return TransactionSerializer

    @action(methods=['GET'], detail=False)
    def recentTransactions(self, request):
        queryset = Transaction.objects.filter(owner=request.user).order_by('-id')[0:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def excel(self, request):
        queryset = Transaction.objects.all()
        serializer = TransactionExcelSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False)
    def createOrder(self, request):
        user = request.user
        wallet = Wallet.objects.get(owner=user)
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            amount = serializer.validated_data['amount']
            transaction = Transaction.objects.create(wallet=wallet, owner=user, amount=amount, debit=False, type=type)
            data = {
                "merchantId": os.getenv("PHONE_PE_MERCHANT_ID"),
                "merchantTransactionId": f"{transaction.transaction_id}",
                "merchantUserId": user.id,
                "amount": amount * 100,
                "redirectUrl": "https://webhook.site/redirect-url",
                "redirectMode": "POST",
                "callbackUrl": serializer.data['redirect_url'],
                "mobileNumber": 9876543210,
                "paymentInstrument": {
                    "type": "PAY_PAGE"
                }
            }
            PHONE_PE_SALT_KEY = os.getenv("PHONE_PE_SALT_KEY")
            PHONE_PE_KEY_INDEX = os.getenv("PHONE_PE_KEY_INDEX")
            url = os.getenv("PHONE_PE_PAY_URL")
            json_object = json.dumps(data, indent = 4) 
            b = base64.b64encode(bytes(json_object, 'utf-8'))
            data64 = b.decode('utf-8')

            print("data64 => ", data64)
            data256 = hashlib.sha256(f"{data64}/pg/v1/pay{PHONE_PE_SALT_KEY}".encode('utf-8')).hexdigest()
            print("data256 => ", data256)
            X_VERIFY = f"{data256}###{PHONE_PE_KEY_INDEX}"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-VERIFY": X_VERIFY
            }
            reqData = {
                "request": data64,
            }
            response = requests.post(url, headers=headers, json=reqData)
            # return Response({"res":json.loads(response.text), "data": data, "X_VERIFY": X_VERIFY, "data64": data64})
            return Response({"res":json.loads(response.text)})
    
    @action(methods=['POST'], detail=False , permission_classes=[AllowAny], authentication_classes=[])
    def ppCallback(self, request):
        # LogService.log(request)
        return Response("Success")


class BankAccountViewSet(viewsets.ModelViewSet):    
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['owner']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[3][1]:
            queryset = BankAccount.objects.all().order_by('-id')
        else:
            queryset = BankAccount.objects.filter(owner=user).order_by('-id')
        # queryset = BankAccount.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return BankAccountSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        serializer = BankDetailSerializer(data=data)
        # print("Validating Serializer")
        if serializer.is_valid(raise_exception=True):
            if serializer.is_valid(raise_exception=True):
                # print("Serializer Validated")
                if 'acc_holder_name' in serializer.validated_data and 'bank_acc' in serializer.validated_data and 'bank_ifsc' in serializer.validated_data:
                    # print("Getting User object.")
                    # acc_holder_name = serializer.validated_data['acc_holder_name']
                    bank_acc = serializer.validated_data['bank_acc']
                    bank_ifsc = serializer.validated_data['bank_ifsc']
                    bank_acc_exists = User.objects.filter(bank_acc=bank_acc).exists()
                    if bank_acc_exists:
                        return Response({"message": "Bank account already exist with another user."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Integrate Penny Drop Api below
                    try:
                        wallet = Wallet.objects.create(owner=user)
                    except:
                        wallet = Wallet.objects.get(owner=user)
                    s = datetime.now()
                    traceId = f"T{wallet.id}{str(s).replace('-', '').replace(' ',  '').replace(':', '').replace('.', '')}"
                    transaction = Transaction.objects.create(owner=user, amount=1, wallet=wallet, debit=False, transaction_id=traceId)
                    bank_detail = {
                        "bankAccount": serializer.validated_data['bank_acc'], 
                        "ifsc": serializer.validated_data['bank_ifsc'],
                        "name": "", 
                        "phone": "", 
                        "traceId": traceId}
                    url = 'https://sandbox.transxt.in/api/1.1/pennydrop'
                    response = requests.post(url, data=bank_detail, headers={"Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg4ODEyODExLCJpYXQiOjE2ODg3MjY0MTEsImp0aSI6IjUwMjUyOWQ0OTJhZTQ5ZGNhZmFmOWNjYmY2ZTU0NDIyIiwidXNlcl9pZCI6N30.J1wRCEku7nTjfZ69E3aVDKksn0nPe9j_fkdJQ9OLHsQ"})
                    # r = json.loads(response)
                    res = response.json()
                    transaction.status = res['status']
                    print(f"This is your res => {res}")
                    if res['status'] == 'SUCCESS':
                        user.bank_acc = serializer.validated_data['bank_acc']
                        user.bank_ifsc = serializer.validated_data['bank_ifsc']
                        user.bank_name = res['data']['nameAtBank']
                        user.is_bank_acc_verified = True
                        user.save()
                        transaction.penny_drop_utr = res['data']['utr']
                        transaction.ref_id = res['data']['ref_id']
                        transaction.save()
                        return Response({"message": response.status, "name": res['data']['nameAtBank']})
                    else:
                        try:
                            transaction.ref_id = res['data']['ref_id']
                        except:
                            transaction.ref_id = ''
                        transaction.save()
                        return Response({"message": res['status']}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        all_banks = BankAccount.objects.filter(owner=user).count()
        if all_banks >= 4:
            return Response({"message": "A user can have maximum 4 bank accounts."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['is_primary'] == True:
            all_banks = BankAccount.objects.filter(owner=user)
            for bank in all_banks:
                bank.is_primary = False
                bank.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.validated_data['is_primary'] = False
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     # first_bank = queryset.get(is_primary=True)
    #     # queryset[0] = first_bank

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
    # @action(methods=['GET'], detail=False)
    # def createAll(self, request):
    #     all_users = User.objects.all()
    #     for user in all_users:
    #         already_exist = BankAccount.objects.filter(owner=user).exists()
    #         if not already_exist:
    #             if user.status == User.STATUS_CHOICES[4][1]:
    #                 BankAccount.objects.create(bank='SBI',  owner=user, acc_number='1542365214524587', ifsc='SBIN00007', is_primary=True)
    #         else:
    #             pass
    #     return Response({"message": "Created for all."})

    @action(methods=['GET'], detail=True)
    def makePrimary(self, request, pk):
        user = request.user
        all_banks = BankAccount.objects.filter(owner=user)
        for bank in all_banks:
            bank.is_primary = False
            bank.save()
        instance = self.get_object()
        instance.is_primary = True
        instance.save()
        return Response({"message": "Made Bank primary successfully."}, status=status.HTTP_200_OK)


class BankSlabViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = BankSlab.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return BankSlabSerializer
    