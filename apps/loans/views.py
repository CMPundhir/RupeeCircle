from django.shortcuts import render
from django.db.models import Count
from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.wallet.models import Wallet
from apps.notification.services import LogService

# Create your views here.
    

class LoanViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Loan.objects.all()
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'apply' or self.action == 'recentApplications':
            return RecentLoanSerializer
        else:
            return LoanSerializer
    
    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = LoanForm.objects.create(serializer.validated_data)
            instance.loan = pk
            instance.save()
            return Response({"message": "Application submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        print(f'TOKENS => {request.auth}')
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(methods=['GET'], detail=False)
    def recentApplications(self, request):
        queryset = LoanForm.objects.all().order_by('-id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def invest(self, request, pk):
        # return Response({"message": "Work on progress."})
        user = request.user
        instance = self.get_queryset().get(pk=pk)
        if user in instance.investor.all():
            return Response({"message": "You have already invested in this loan."})
        instance.investor.add(user)
        instance.save()
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.loan_amount:
            return Response({"message": "You don't have enough wallet balance. Add amount to your wallet."})
        wallet.balance -= instance.loan_amount
        wallet.invested_amount += instance.loan_amount
        wallet.save()
        LogService.log(user=user, msg=f"Invested in loan{instance.id}.")
        LogService.log(user=user, msg=f"Your wallet balance is debited with amount {instance.loan_amount}. Current wallet balance is {wallet.balance}.")
        LogService.log(user=instance.borrower, msg=f"{user.first_name} {user.last_name} has invested in your loan.")
        return Response({"message": "Invested Successfully."})

    @action(methods=['GET'], detail=True)
    def investors(self, request, pk):
        instance = Loan.objects.get(pk=pk)
        queryset = instance.investor.all()
        print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
        # serializer = UserSerializer(queryset, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False)
    def popularLoans(self, request):
        print(request.auth)
        queryset = Loan.objects.annotate(investor_count=Count('investor')).order_by('-investor_count')[0:4]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # @action(methods=['GET'], detail=False)
    # def addtoall(self, request):
    #     user = request.user
    #     queryset = self.get_queryset()
    #     for i in queryset:
    #         i.borrower = user
    #         i.investor.add(user)
    #         i.save()
    #     return Response({"message": "added all."})
    

class InvestmentPlanViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = InvestmentPlan.objects.all()
        return queryset
    
    def get_serializer_class(self, *args, **kwargs):
        return InvestmentPlanSerializer