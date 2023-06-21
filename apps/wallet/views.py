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
        # if user.role == User.ROLE_CHOICES[3][1]:
        #     queryset = Wallet.objects.all()
        # else:
        #     queryset = []
        # return queryset
        else:
            queryset = Wallet.objects.filter(owner=self.request.user.id)
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
        instance = self.get_queryset().get(owner=user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(methods=['POST'], detail=False)
    def addFunds(self, request):
        data = request.data
        user = request.user
        instance = self.get_queryset()[0]
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance.balance += serializer.validated_data['value']
            instance.save()
            LogService.log(user=user, msg=f"Rs.{serializer.validated_data['value']} credited to  your wallet. Your wallet balance is Rs.{instance.balance}.",
                           is_activity=True)
            LogService.transaction_log(owner=user, wallet=instance, amount=serializer.validated_data['value'])
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
            LogService.transaction_log(owner=user, wallet=instance, amount=serializer.validated_data['value'], debit=True)
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


class TransactionViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['transaction_id', 'owner', 'amount', 'id', 'wallet']
    ordering_fields = ['id']
    filterset_fields = ['transaction_id', 'wallet', 'owner', 'amount']

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(owner=user).order_by('-id')
        return queryset
        # queryset = Transaction.objects.all().order_by('-id')
        # return queryset
    
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
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        queryset = BankAccount.objects.filter(owner=user)
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
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @action(methods=['GET'], detail=False)
    def createAll(self, request):
        all_users = User.objects.all()
        for user in all_users:
            already_exist = BankAccount.objects.filter(owner=user).exists()
            if not already_exist:
                if user.status == User.STATUS_CHOICES[4][1]:
                    BankAccount.objects.create(bank='SBI',  owner=user, bankAccount=user.bank_acc, ifsc=user.bank_ifsc, is_primary=True)
            else:
                pass
        return Response({"message": "Created for all."})
