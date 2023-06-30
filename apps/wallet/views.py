from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.notification.services import LogService
from rest_framework import status
from .models import Wallet
from apps.mauth.models import CustomUser as User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.settings import api_settings
from .serializers import *
from utility.ccavutil import encrypt,decrypt
from django.views.decorators.csrf import csrf_exempt


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
        if user.role == User.ROLE_CHOICES[3][1]:
            queryset = Wallet.objects.all()
        else:
            queryset = Wallet.objects.filter(owner=user.id)
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
    
    @csrf_exempt
    @action(methods=['GET', 'POST'], detail=False)
    def addByCcav(self, request):
        p_merchant_id = '2954' # request.form['merchant_id']
        p_order_id = "466555992256  " # request.form['order_id']
        p_currency = 'INR' # request.form['currency']
        p_amount = '1.00' # request.form['amount']
        p_redirect_url = "http://192.168.2.49:8086/ccavResponseHandler" # request.form['redirect_url']
        p_cancel_url = "http://192.168.2.49:8086/ccavResponseHandler" # request.form['cancel_url']
        p_language = "EN" # request.form['language']
        p_billing_name = "Peter" # request.form['billing_name']
        p_billing_address = "billing_address" # request.form['billing_address']
        p_billing_city = "Mumbai" # request.form['billing_city']
        p_billing_state = "MH" # request.form['billing_state']
        p_billing_zip = "400054" # request.form['billing_zip']
        p_billing_country = "India" # request.form['billing_country']
        p_billing_tel = "0229874789" # request.form['billing_tel']
        p_billing_email = "testing@domain.com"# request.form['billing_email']
        p_delivery_name = "Sam"# request.form['delivery_name']
        p_delivery_address = "Vile Parle"# request.form['delivery_address']
        p_delivery_city = "Mumbai"# request.form['delivery_city']
        p_delivery_state = "Maharashtra"# request.form['delivery_state']
        p_delivery_zip = "400038"# request.form['delivery_zip']
        p_delivery_country = "India"# request.form['delivery_country']
        p_delivery_tel = "0221234321"# request.form['delivery_tel']
        p_merchant_param1 = "additional Info."# request.form['merchant_param1']
        p_merchant_param2 = "additional Info." # request.form['merchant_param2']
        p_merchant_param3 = "additional Info."# request.form['merchant_param3']
        p_merchant_param4 = "additional Info."# request.form['merchant_param4']
        p_merchant_param5 = "additional Info."# request.form['merchant_param5']
        p_promo_code = ""# request.form['promo_code']
        p_customer_identifier = ""# request.form['customer_identifier']
        
        

        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
            
        encryption = encrypt(merchant_data,workingKey)
        return Response({"data": encryption})


class TransactionViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['transaction_id', 'owner', 'amount', 'id', 'wallet']
    ordering_fields = ['id']
    filterset_fields = ['transaction_id', 'wallet', 'owner', 'amount', 'type']

    def get_queryset(self):
        user = self.request.user
        # queryset = Transaction.objects.filter(owner=user).order_by('-id')
        # return queryset
        queryset = Transaction.objects.all().order_by('-id')
        return queryset
    
    def get_serializer_class(self):
        return TransactionSerializer

    @action(methods=['GET'], detail=False)
    def recentTransactions(self, request):
        queryset = Transaction.objects.filter(owner=request.user).order_by('-id')[0:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(methods=['GET'], detail=False)
    # def graphDetail(self, request):


class BankAccountViewSet(viewsets.ModelViewSet):    
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['owner']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[3][1]:
            queryset = BankAccount.objects.all()
        else:
            queryset = BankAccount.objects.filter(owner=user)
        # queryset = BankAccount.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return BankAccountSerializer
    
    def create(self, request, *args, **kwargs):
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


def dataform(request):
    return render(request, 'dataform.html')
