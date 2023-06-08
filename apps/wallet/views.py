from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.notification.services import LogService
from rest_framework import status
from .models import Wallet
from apps.mauth.models import CustomUser as User
from .serializers import *


# Create your views here.


class WalletViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        # user = self.request.user
        # if user.role == User.ROLE_CHOICES[3][1]:
        #     queryset = Wallet.objects.all()
        # else:
        #     queryset = []
        # return queryset
        queryset = Wallet.objects.all()
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return WalletGetSerializer
        elif self.action == 'addFunds':
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
            LogService.log(user=user, msg=f"{serializer.validated_data['value']} Rs. added to  your wallet. Your wallet balance is {instance.balance}.",
                           is_transaction=True)
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

    def get_queryset(self):
        # user = self.request.user
        # queryset = Transaction.objects.filter(owner=user).order_by('-id')
        # return queryset
        queryset = Transaction.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return TransactionSerializer

