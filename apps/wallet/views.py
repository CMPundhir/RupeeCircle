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
from .serializers import *


# Create your views here.


class WalletViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['owner', 'balance', 'invested_amount']
    ordering_fields = ['id']
    filterset_fields = ['owner', 'balance', 'invested_amount']

    def get_queryset(self):
        # user = self.request.user
        # if user.role == User.ROLE_CHOICES[3][1]:
        #     queryset = Wallet.objects.all()
        # else:
        #     queryset = []
        # return queryset
        queryset = Wallet.objects.filter(owner=self.request.user.id)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return WalletGetSerializer
        elif self.action == 'addFunds' or self.action == 'withdrawFunds':
            return AddFundsSerializer
        else:
            return WalletSerializer
    
    # def list(self, request):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=True)
    def addFunds(self, request, pk):
        data = request.data
        user = request.user
        instance = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance.balance += serializer.validated_data['value']
            instance.save()
            LogService.log(user=user, msg=f"Rs.{serializer.validated_data['value']} credited to  your wallet. Your wallet balance is {instance.balance}.",
                           is_activity=True)
            LogService.transaction_log(owner=user, wallet=instance, amount=serializer.validated_data['value'])
            return Response({"message": "Funds added successfully.", "balance": instance.balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def withdrawFunds(self, request, pk):
        data = request.data
        user = request.user
        instance = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            if instance.balance < serializer.validated_data['value']:
                return Response({"message": "You don't have enough balance in your wallet."}, status=status.HTTP_400_BAD_REQUEST)
            instance.balance -= serializer.validated_data['value']
            instance.save()
            LogService.log(user=user, msg=f"Rs.{serializer.validated_data['value']} debited to your wallet. Your wallet balance is {instance.balance}.",
                           is_activity=True)
            LogService.transaction_log(owner=user, wallet=instance, amount=serializer.validated_data['value'], debit=True)
            return Response({"message": "Funds added successfully.", "balance": instance.balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @action(methods=['GET'], detail=False)
    # def addall(self, request):
    #     users = User.objects.all()
    #     for i in users:
    #         wallet = Wallet.objects.filter(owner=i).exists()
    #         if not wallet:
    #             Wallet.objects.create(owner=i)
    #         pass    
    #     return Response("Added")


class TransactionViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['transaction_id', 'owner', 'amount', 'id', 'wallet']
    ordering_fields = ['id']
    filterset_fields = ['transaction_id', 'wallet', 'owner', 'amount']

    def get_queryset(self):
        # user = self.request.user
        # queryset = Transaction.objects.filter(owner=user).order_by('-id')
        # return queryset
        queryset = Transaction.objects.all()
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

