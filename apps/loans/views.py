from django.shortcuts import render
from django.db.models import Count
from .models import *
from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.wallet.models import Wallet
from apps.mauth.models import CustomUser as User
from apps.notification.services import LogService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import datetime
from dateutil import relativedelta

# Create your views here.


class LoanApplicationViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['loan_amount', 'loan_id', 'interest_rate', 'repayment_terms', 'installments', 'borrower', 'investors', 'status']
    ordering_fields = ['id', 'loan_id']
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[3][1] or user.role == User.ROLE_CHOICES[0][1] and user.is_marketplace_allowed == True:
            queryset = LoanApplication.objects.filter(is_record_active=True)
        elif user.role == User.ROLE_CHOICES[2][1]:
            queryset = LoanApplication.objects.filter(borrower=user)
        else:
            queryset = []
        return queryset
        
        # queryset = Loan.objects.all()
        # return queryset
    
    def get_serializer_class(self):
        return LoanApplicationSerializer
        
    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != User.ROLE_CHOICES[2][1]:
            return Response({"message": "Only borrower can create a Marketplace Loan."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['borrower'] = user
        instance = self.perform_create(serializer.data)
        # data = self.get_serializer(instance)
        # instance.loan_id = f'LOAN{instance.id}'
        headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({"result":instance}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.loan_id = f'LOAN{instance.id}'
        instance.save()
        return instance
        
    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
    
    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        user = request.user
        loan_plan = self.get_object()

        # Checking if user is a investor
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors are allowed to apply for loans."}, status=status.HTTP_401_UNAUTHORIZED)

        # Checking wallet balance
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < loan_plan.loan_amount:
            return Response({"message": "You do not have enough balance in your wallet. Add funds first."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Creating Investment Request
        InvestmentRequest.objects.create(loan=loan_plan, investor=user, borrower=loan_plan.borrower)
        LogService.log(user=user, is_activity=True, msg=f'You have successfully applied for investment in {loan_plan}.')
        return Response({"message": "Applied Successfully."}, status=status.HTTP_200_OK)

    # @action(methods=['GET'], detail=True)
    # def invest(self, request, pk):
    #     # return Response({"message": "Work on progress."})
    #     user = request.user
    #     instance = self.get_queryset().get(pk=pk)
    #     if user in instance.investor.all():
    #         return Response({"message": "You have already invested in this loan."})
    #     instance.investor.add(user)
    #     instance.save()
    #     wallet = Wallet.objects.get(owner=user)
    #     if wallet.balance < instance.loan_amount:
    #         return Response({"message": "You don't have enough wallet balance. Add amount to your wallet."})
    #     wallet.balance -= instance.loan_amount
    #     wallet.invested_amount += instance.loan_amount
    #     wallet.save()
    #     LogService.log(user=user, msg=f"Invested in loan{instance.id}.")
    #     LogService.log(user=user, msg=f"Your wallet balance is debited with amount {instance.loan_amount}. Current wallet balance is {wallet.balance}.")
    #     LogService.log(user=instance.borrower, msg=f"{user.first_name} {user.last_name} has invested in your loan.")
    #     return Response({"message": "Invested Successfully."})

    @action(methods=['GET'], detail=True)
    def investors(self, request, pk):
        instance = LoanApplication.objects.get(pk=pk)
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
        queryset = LoanApplication.objects.annotate(investor_count=Count('investors')).order_by('-investor_count')[0:4]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 

class FixedROIViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['amount', 'tenure', 'type', 'interest_rate']
    ordering_fields = ['id']
    filterset_fields = ['amount', 'tenure', 'type', 'interest_rate']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[3][1] or user.role == User.ROLE_CHOICES[0][1] and user.is_fixedroi_allowed == True:
            queryset = InvestmentPlan.objects.filter(type=InvestmentPlan.TYPE_CHOICES[0][1], is_record_active=True, is_special_plan=False)
        else:
            queryset = []
        return queryset
    
    def get_serializer_class(self, *args, **kwargs):
        # if self.action == 'apply':
        #     return InvestmentApplicationSerializer
        return InvestmentPlanSerializer
    
    @action(methods=['GET', 'POST'], detail=True)
    def apply(self, request, pk):
        instance = self.get_object()
        user = request.user
        
        # Checking if user is Investor or not.
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors can invest in Investment Plans."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking serializer data is valid and within limit.
        # serializer = InvestmentApplicationSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # if instance.principal_type == InvestmentPlan.PRINCIPAL_CHOICES[1][1]:
        #     if not instance.min_amount <= serializer.validated_data['amount'] <= instance.amount or instance.investing_limit <= Loan.objects.filter(investor=user).count():
        #         return Response({"message": "Ensure your amount is within the amount limit or you have exceeded the investment limit."}, status=status.HTTP_403_FORBIDDEN)
        
        # Checking wallet balance is equal or more than the investment amount.
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.amount:
            return Response({"message": "You don't have enough balance to apply for this Investment plan. Kindly add funds to your wallet."})
        
        # Creating request for this plan.
        # installment = (serializer.validated_data['amount'] + ((serializer.validated_data['amount']*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        # installment = (instance.amount + ((instance.amount*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        # InvestmentRequest.objects.create(plan=instance, 
        #                                  investor=user, 
        #                                  remarks=serializer.validated_data['remarks'], 
        #                                  installments=installment,
        #                                  amount=serializer.validated_data['amount'],
        #                                  interest_rate=serializer.validated_data['interest_rate'],
        #                                  repayment_terms=serializer.validated_data['repayment_terms'],
        #                                  collateral=serializer.validated_data['collateral'],
        #                                  late_pay_penalties=serializer.validated_data['late_pay_penalties'],
        #                                  prepayment_options=serializer.validated_data['prepayment_options'],
        #                                  default_remedies=serializer.validated_data['default_remedies'],
        #                                  privacy=serializer.validated_data['privacy'],
        #                                  governing_law=serializer.validated_data['governing_law'],
        #                                  )
        InvestmentRequest.objects.create(plan=instance, 
                                         investor=user, 
                                        #  remarks=instance.remarks, 
                                        #  installments=installment,
                                         amount=instance.amount,
                                         interest_rate=instance.interest_rate,
                                         tenure=instance.tenure
                                        #  repayment_terms=instance.repayment_terms,
                                        #  collateral=instance.collateral,
                                        #  late_pay_penalties=instance.late_pay_penalties,
                                        #  prepayment_options=instance.prepayment_options,
                                        #  default_remedies=instance.default_remedies,
                                        #  privacy=instance.privacy,
                                        #  governing_law=instance.governing_law,
                                         )
        LogService.log(user=user, is_activity=True, msg=f'You have successfully applied for an investment plan.')
        return Response({"message": "Application Successful."}, status=status.HTTP_200_OK)

    # @action(methods=['GET'], detail=False)
    # def bulkcreate(self, request):
    #     for i in range(50):
    #         InvestmentPlan.objects.create(amount=500000, interest_rate=15, tenure=2, type=InvestmentPlan.TYPE_CHOICES[0][1])
    #     return Response({"message": "Done"})


class AnytimeWithdrawalViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['amount', 'tenure', 'type', 'interest_rate']
    ordering_fields = ['id']
    filterset_fields = ['amount', 'tenure', 'type', 'interest_rate']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[3][1] or user.role == User.ROLE_CHOICES[0][1] and user.is_fixedroi_allowed == True:
            queryset = InvestmentPlan.objects.filter(type=InvestmentPlan.TYPE_CHOICES[1][1], is_record_active=True, is_special_plan=False)
        else:
            queryset = []
        return queryset
    
    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'apply':
            return InvestmentApplicationSerializer
        return InvestmentPlanSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['type'] = InvestmentPlan.TYPE_CHOICES[1][1]
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
    
    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        instance = self.get_object()
        user = request.user
        
        # Checking if user is Investor or not.
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors can invest in Investment Plans."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking serializer data is valid and within limit.
        # serializer = InvestmentApplicationSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # if instance.principal_type == InvestmentPlan.PRINCIPAL_CHOICES[1][1]:
        #     if not instance.min_amount <= serializer.validated_data['amount'] <= instance.amount or instance.investing_limit <= Loan.objects.filter(investor=user).count():
        #         return Response({"message": "Ensure your amount is within the amount limit or you have exceeded the investment limit."}, status=status.HTTP_403_FORBIDDEN)
        
        # Checking wallet balance is equal or more than the investment amount.
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.amount:
            return Response({"message": "You don't have enough balance to apply for this Investment plan. Kindly add funds to your wallet."})
        
        # Creating request for this plan.
        # installment = (serializer.validated_data['amount'] + ((serializer.validated_data['amount']*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        # installment = (instance.amount + ((instance.amount*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        # InvestmentRequest.objects.create(plan=instance, 
        #                                  investor=user, 
        #                                  remarks=serializer.validated_data['remarks'], 
        #                                  installments=installment,
        #                                  amount=serializer.validated_data['amount'],
        #                                  interest_rate=serializer.validated_data['interest_rate'],
        #                                  repayment_terms=serializer.validated_data['repayment_terms'],
        #                                  collateral=serializer.validated_data['collateral'],
        #                                  late_pay_penalties=serializer.validated_data['late_pay_penalties'],
        #                                  prepayment_options=serializer.validated_data['prepayment_options'],
        #                                  default_remedies=serializer.validated_data['default_remedies'],
        #                                  privacy=serializer.validated_data['privacy'],
        #                                  governing_law=serializer.validated_data['governing_law'],
        #                                  )
        InvestmentRequest.objects.create(plan=instance, 
                                         investor=user, 
                                        #  remarks=instance.remarks, 
                                        #  installments=installment,
                                         amount=instance.amount,
                                         interest_rate=instance.interest_rate,
                                         tenure=instance.tenure
                                        #  repayment_terms=instance.repayment_terms,
                                        #  collateral=instance.collateral,
                                        #  late_pay_penalties=instance.late_pay_penalties,
                                        #  prepayment_options=instance.prepayment_options,
                                        #  default_remedies=instance.default_remedies,
                                        #  privacy=instance.privacy,
                                        #  governing_law=instance.governing_law,
                                         )
        LogService.log(user=user, is_activity=True, msg=f'You have successfully applied for an investment plan.')
        return Response({"message": "Application Successful."}, status=status.HTTP_200_OK)
        

class MyInvestmentViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        if self.action == 'marketplace':
            queryset = LoanApplication.objects.filter(investors__in=[user])
            return queryset
        if self.action == 'investmentPlans':
            queryset = InvestmentPlan.objects.filter(investors__in=[user])
            return queryset
        return []
        
    def get_serializer_class(self):
        if self.action == 'marketplace':
            return LoanApplicationSerializer
        if self.action == 'investmentPlans':
            return InvestmentPlanSerializer
        return LoanApplicationSerializer
        
    @action(methods=['GET'], detail=False)
    def marketplace(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False)
    def investmentPlans(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllInvestmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        all_users = User.objects.all()
        if self.action == 'marketplace':
            queryset = LoanApplication.objects.filter(investors__in=all_users)
            return queryset
        if self.action == 'fixedRoi':
            queryset = InvestmentPlan.objects.filter(type=InvestmentPlan.TYPE_CHOICES[0][1], investors__in=all_users)
            return queryset
        if self.action == 'anytimeWithdraw':
            queryset = InvestmentPlan.objects.filter(type=InvestmentPlan.TYPE_CHOICES[1][1], investors__in=all_users)
            return queryset
        return []
        
    def get_serializer_class(self):
        if self.action == 'marketplace':
            return LoanApplicationSerializer
        if self.action == 'anytimeWithdraw' or self.action == 'fixedRoi':
            return InvestmentPlanSerializer
        return LoanApplicationSerializer
        
    @action(methods=['GET'], detail=False)
    def marketplace(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False)
    def fixedRoi(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False)
    def anytimeWithdraw(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvestmentRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[2][1]:
            queryset = InvestmentRequest.objects.filter(plan=None, borrower=user)
        elif user.role == User.ROLE_CHOICES[3][1]:
            queryset = InvestmentRequest.objects.filter(loan=None)
        else:
            return Response({"message": "You are not authorized to access Investment Requests."}, status=status.HTTP_401_UNAUTHORIZED)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return InvestmentRequestGetSerializer
        return InvestmentRequestSerializer
    
    @action(methods=['GET'], detail=True)
    def approve(self, request, pk):
        user=request.user
        instance = self.get_object()
        if user.role == User.ROLE_CHOICES[2][1]:
            loan_or_role_amount = instance.loan.loan_amount
        elif user.role == User.ROLE_CHOICES[3][1]:
            loan_or_role_amount = instance.plan.amount
        print(f'Your amount => {loan_or_role_amount}')
        wallet = Wallet.objects.get(owner=instance.investor)

        # checking balance in the wallet
        if wallet.balance < loan_or_role_amount:
            LogService.log(user=instance.investor, msg=f'Your application for investment plan could not be approved due to insufficient balance in your wallet.')
            return Response({"message": "Investor doesn't have enough balance in their wallet."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Deducting amount from the wallet
        wallet.balance -= loan_or_role_amount
        wallet.save()
        LogService.transaction_log(owner=instance.investor, wallet=wallet, amount=loan_or_role_amount, debit=True)
        LogService.log(user=instance.investor, msg=f'Your wallet is debited with Rs. {loan_or_role_amount}. Current Wallet balance is Rs. {wallet.balance}')
        
        # Checking if it's loan or investment plan
        if instance.borrower:
            borrower_wallet = Wallet.objects.get(owner=instance.borrower)
            borrower_wallet += loan_or_role_amount
            borrower_wallet.save()

            # Creating Loan object
            loan_instance = Loan.objects.create(loan_amount=instance.amount,
                                                interest_rate=instance.interest_rate,
                                                tenure=instance.tenure,
                                                repayment_terms=instance.repayment_terms,
                                                collateral=instance.collateral,
                                                late_pay_penalties=instance.late_pay_penalties,
                                                prepayment_options=instance.prepayment_options,
                                                default_remedies=instance.default_remedies,
                                                privacy=instance.privacy,
                                                governing_law=instance.governing_law,
                                                borrower=instance.borrower,
                                                investor=instance.investor,
                                                type=instance.type)
            # if loan_instance.type == InvestmentRequest.TYPE_CHOICES[2][1]:
            for i in range(loan_instance.tenure*12):
                month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                installment = Installment.objects.create(parent_loan=loan_instance,
                                                            due_date=month,
                                                            amount=loan_instance.installments,
                                                            )
                loan_instance.installments.add(installment)
            LogService.transaction_log(owner=instance.borrower, wallet=borrower_wallet, amount=loan_or_role_amount, debit=False)
            LogService.log(user=instance.borrower, msg=f'You accepted investor {instance.investor}\'s application.')
        else:
            Loan.objects.create(loan_amount=instance.amount,
                                interest_rate=instance.interest_rate,
                                tenure=instance.tenure,
                                investor=instance.investor,
                                type=instance.type
                                )
        
        # approving request
        instance.status = InvestmentRequest.STATUS_CHOICES[1][1]
        instance.save()

        # Adding investor in investment plan
        if instance.loan == None:
            plan = InvestmentPlan.objects.get(id=instance.plan.id)
            plan.investors.add(instance.investor)
            plan.save()
        else:
            loan = LoanApplication.objects.get(id=instance.loan.id)
            loan.investors.add(instance.investor)
            loan.save()
        LogService.log(user=request.user, msg=f"You approved Investment Request of investor{instance.investor}", is_activity=True)
        LogService.log(user=instance.investor, msg=f'Your Application for Investment Plan is approved.')
        return Response({"message": "Application Approved."}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def approvedRequests(self, request):
        queryset = InvestmentRequest.objects.filter(status=InvestmentRequest.STATUS_CHOICES[1][1])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SpecialPlanViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['interest_rate', 'allowed_investor', 'tenure']

    def get_queryset(self):
        user=self.request.user
        if user.is_superuser:
            queryset = InvestmentPlan.objects.filter(is_special_plan=True, is_record_active=True)
        elif user.role == User.ROLE_CHOICES[0][1]:
            queryset = InvestmentPlan.objects.filter(is_special_plan=True, allowed_investor=user, is_record_active=True)
        else:
            queryset = []
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investor = serializer.validated_data['allowed_investor']
        all_plans = InvestmentPlan.objects.filter(is_special_plan=True, is_record_active=True, allowed_investor=investor).count()
        if all_plans >= 4:
            return Response({"message": "An investor can be given maximum 4 special offers."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        updated_investor = User.objects.get(id=investor)
        updated_investor.special_plan_exist = True
        updated_investor.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['is_special_plan'] = True
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def get_serializer_class(self):
        return InvestmentPlanSerializer

    def destroy(self, request, pk):
        return Response({"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        instance = self.get_object()
        user = request.user
        
        # Checking if user is Investor or not.
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors can invest in Investment Plans."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking serializer data is valid and within limit.
        serializer = InvestmentApplicationSerializer(data=request.data)
        if instance.min_amount and not instance.min_amount < serializer.validated_data['amount'] < instance.amount or instance.investing_limit <= Loan.objects.filter(investor=user).count():
            return Response({"message": "Ensure your amount is within the amount limit or you have exceeded the investment limit."}, status=status.HTTP_403_FORBIDDEN)
        
        # Checking wallet balance is equal or more than the investment amount.
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.amount:
            return Response({"message": "You don't have enough balance to apply for this Investment plan. Kindly add funds to your wallet."})
        
        # Creating request for this plan.
        installment = (serializer.validated_data['amount'] + ((serializer.validated_data['amount']*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        InvestmentRequest.objects.create(plan=instance, 
                                         investor=user, 
                                         remarks=serializer.validated_data['remarks'], 
                                         installments=installment,
                                         amount=serializer.validated_data['amount'],
                                         interest_rate=serializer.validated_data['interest_rate'],
                                         repayment_terms=serializer.validated_data['repayment_terms'],
                                         collateral=serializer.validated_data['collateral'],
                                         late_pay_penalties=serializer.validated_data['late_pay_penalties'],
                                         prepayment_options=serializer.validated_data['prepayment_options'],
                                         default_remedies=serializer.validated_data['default_remedies'],
                                         privacy=serializer.validated_data['privacy'],
                                         governing_law=serializer.validated_data['governing_law'],
                                         )
        LogService.log(user=user, is_activity=True, msg=f'You have successfully applied for an investment plan.')
        return Response({"message": "Application Successful."}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def getPrimary(self, request):
        instance = self.get_queryset().get(is_primary=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def makePrimary(self, request, pk):
        old_primary = self.get_queryset().get(is_primary=True)
        if old_primary:
            old_primary.is_primary = False
            old_primary.save()
        instance = self.get_object()
        instance.is_primary=True
        instance.save()
        return Response({"message": "Made Primary Successfully."}, status=status.HTTP_200_OK)


class LoanViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[0][1]:
            queryset = Loan.objects.filter(investor=user)
        elif user.role == User.ROLE_CHOICES[2][1]:
            queryset = Loan.objects.filter(borrower=user)
        elif user.role == User.ROLE_CHOICES[3][1]:
            queryset = Loan.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return InvestmentSerializer
