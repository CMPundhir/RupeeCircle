from django.shortcuts import render
from django.db.models import Count
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
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


class TermsAndConditionViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = TermsAndCondition.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return TermsAndConditionSerializer


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
            queryset = LoanApplication.objects.none()
        return queryset
        
        # queryset = Loan.objects.all()
        # return queryset
    
    def get_serializer_class(self):
        if self.action == 'apply':
            return InvestmentRequestSerializer
        elif self.action == 'create':
            return LoanApplicationCreateSerializer
        return LoanApplicationSerializer
        
    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != User.ROLE_CHOICES[2][1]:
            return Response({"message": "Only borrower can create a Marketplace Loan."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['borrower'] = user
        if serializer.validated_data['type'] == InvestmentProduct.TYPE_CHOICES[0][1]:
            serializer.validated_data['minimum_locking'] = '3 Months'
        if serializer.validated_data['type'] == InvestmentProduct.TYPE_CHOICES[1][1]:
            serializer.validated_data['minimum_locking'] = '12 days'
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "LoanApplication created Successfully."}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()
        # new_app = LoanApplication.objects.get(id=serializer.data['id'])
        # new_app.loan_id = f'LOAN{instance.id}'
        # new_app.save()
        # return instance
        
    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
    
    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        user = request.user
        loan_plan = self.get_object()
        data = request.data

        # Checking if user is a investor
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors are allowed to apply for loans."}, status=status.HTTP_401_UNAUTHORIZED)

        # Checking wallet balance
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < loan_plan.loan_amount:
            return Response({"message": "You do not have enough balance in your wallet. Add funds first."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Creating Investment Request
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            InvestmentRequest.objects.create(loan_amount=serializer.validated_data['loan_amount'],
                                             tenure=serializer.validated_data['tenure'],
                                             interest_rate=serializer.validated_data['interest_rate'],
                                             repayment_terms=serializer.validated_data['repayment_terms'],
                                             collateral=serializer.validated_data['collateral'],
                                             late_pay_penalties=serializer.validated_data['late_pay_penalties'],
                                             prepayment_options=serializer.validated_data['prepayment_options'],
                                             default_remedies=serializer.validated_data['default_remedies'],
                                             privacy=serializer.validated_data['privacy'],
                                             governing_law=serializer.validated_data['governing_law'],
                                             remarks=serializer.validated_data['remarks'],
                                             loan=loan_plan,
                                             investor=user,
                                             borrower=loan_plan.borrower,
                                             type=loan_plan.type)
            LogService.log(user=user, is_activity=True, msg=f'You have successfully bid in {loan_plan}.')
            return Response({"message": "Applied Successfully."}, status=status.HTTP_200_OK)

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
            queryset = InvestmentProduct.objects.filter(type=InvestmentProduct.TYPE_CHOICES[0][1], is_record_active=True, is_special_plan=False)
        else:
            queryset = InvestmentProduct.objects.none()
        return queryset
    
    def get_serializer_class(self, *args, **kwargs):    
        if self.action == 'apply':
            return InvestmentApplicationSerializer
        return InvestmentProductSerializer
    
    @action(methods=['GET', 'POST'], detail=True)
    def apply(self, request, pk):
        instance = self.get_object()
        # print(instance.data)
        user = request.user
        
        # Checking if user is Investor or not.
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors can invest in Investment Plans."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking wallet balance is equal or more than the investment amount.
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.amount:
            return Response({"message": "You don't have enough balance to apply for this Investment plan. Kindly add funds to your wallet."})
        
        # Deducting Amount
        wallet.balance -= instance.amount
        wallet.invested_amount += instance.amount
        wallet.save()
        LogService.transaction_log(owner=user, wallet=wallet, amount=instance.amount, debit=True)

        # Creating Loan
        print("creating loan")
        loan_instance = Loan.objects.create(loan_amount=int(instance.amount),
                            interest_rate=instance.interest_rate,
                            tenure=instance.tenure,
                            investor=user,
                            type=instance.type)
        P = int(loan_instance.loan_amount)
        R = int(loan_instance.interest_rate)
        T = int(loan_instance.tenure)
        installment = ((P*R)/100)/T
        print("entering loop")
        period = int(loan_instance.tenure)
        for i in range(period):
                print("enterred loop")
                month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                installment = Installment.objects.create(parent_loan=loan_instance,
                                                        due_date=month,
                                                        principal=loan_instance.loan_amount,
                                                        interest=installment,
                                                        total_amount=installment,
                                                        )
                print("Adding in Loan_loan_instance")
                loan_instance.installments.add(installment)
        return Response({"message": "Invested Successfully."}, status=status.HTTP_200_OK)
        # # Creating request for this plan.
        # # installment = (serializer.validated_data['amount'] + ((serializer.validated_data['amount']*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        # # installment = (instance.amount + ((instance.amount*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        # # InvestmentRequest.objects.create(plan=instance, 
        # #                                  investor=user, 
        # #                                  remarks=serializer.validated_data['remarks'], 
        # #                                  installments=installment,
        # #                                  amount=serializer.validated_data['amount'],
        #                                  interest_rate=serializer.validated_data['interest_rate'],
        #                                  repayment_terms=serializer.validated_data['repayment_terms'],
        #                                  collateral=serializer.validated_data['collateral'],
        #                                  late_pay_penalties=serializer.validated_data['late_pay_penalties'],
        #                                  prepayment_options=serializer.validated_data['prepayment_options'],
        #                                  default_remedies=serializer.validated_data['default_remedies'],
        #                                  privacy=serializer.validated_data['privacy'],
        #                                  governing_law=serializer.validated_data['governing_law'],
        #                                  )
        # InvestmentRequest.objects.create(plan=instance, 
        #                                  investor=user, 
                                        #  remarks=instance.remarks, 
                                        #  installments=installment,
                                        #  amount=instance.amount,
                                        #  interest_rate=instance.interest_rate,
                                        #  tenure=instance.tenure
                                        #  repayment_terms=instance.repayment_terms,
                                        #  collateral=instance.collateral,
                                        #  late_pay_penalties=instance.late_pay_penalties,
                                        #  prepayment_options=instance.prepayment_options,
                                        #  default_remedies=instance.default_remedies,
                                        #  privacy=instance.privacy,
                                        #  governing_law=instance.governing_law,
                                        #  )
        # LogService.log(user=user, is_activity=True, msg=f'You have successfully applied for an investment plan.')
        # return Response({"message": "Application Successful."}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def addPlanId(self, request):
        for i in InvestmentProduct.objects.all():
            print("adding")
            i.plan_id = f'MP{i.id}'
            print("added")
            i.save()
        return Response({"message": "Done."})
    
    # @action(methods=['GET'], detail=False)
    # def bulkcreate(self, request):
    #     for i in range(5):
    #         InvestmentProduct.objects.create(min_amount=400000,
    #                                          amount=500000, 
    #                                          investing_limit=4,
    #                                          principal_type=InvestmentProduct.PRINCIPAL_CHOICES[1][0],
    #                                          interest_rate=15, 
    #                                          tenure=2, 
    #                                          type=InvestmentProduct.TYPE_CHOICES[0][1])
    #                                         #  type=InvestmentProduct.TYPE_CHOICES[1][1])
    #         InvestmentProduct.objects.create(#min_amount=400000,
    #                                          amount=500000, 
    #                                          investing_limit=4,
    #                                          principal_type=InvestmentProduct.PRINCIPAL_CHOICES[0][0],
    #                                          interest_rate=15, 
    #                                          tenure=2, 
    #                                         #  type=InvestmentProduct.TYPE_CHOICES[0][1])
    #                                          type=InvestmentProduct.TYPE_CHOICES[1][1])
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
            queryset = InvestmentProduct.objects.filter(type=InvestmentProduct.TYPE_CHOICES[1][1], is_record_active=True, is_special_plan=False)
        else:
            queryset = InvestmentProduct.objects.none()
        return queryset
    
    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'apply':
            return InvestmentApplicationSerializer
        return InvestmentProductSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['type'] = InvestmentProduct.TYPE_CHOICES[1][1]
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
        
        # Checking wallet balance is equal or more than the investment amount.
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.amount:
            return Response({"message": "You don't have enough balance to apply for this Investment plan. Kindly add funds to your wallet."})
        
        # Deducting Amount
        wallet.balance -= instance.amount
        wallet.invested_amount += instance.amount
        wallet.save()
        LogService.transaction_log(user=user, amount=instance.amount, debit=True)

        # Creating Loan
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
                                                # borrower=instance.borrower,
                                                investor=instance.investor,
                                                type=instance.type)
        installment = (instance.amount + ((instance.amount*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        principal = instance.amount/(instance.tenure*12)
        interest = installment - principal
        for i in range(loan_instance.tenure*12):
                month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                installment = Installment.objects.create(parent_loan=loan_instance,
                                                            due_date=month,
                                                            principal=principal,
                                                            interest=interest,
                                                            total_amount=installment,
                                                            )
                loan_instance.installments.add(installment)
        return Response({"message": "Invested Successfully."}, status=status.HTTP_200_OK)


class MyInvestmentViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        if self.action == 'marketplace':
            queryset = Loan.objects.filter(investor=user)
            return queryset
        if self.action == 'InvestmentProducts':
            queryset = InvestmentProduct.objects.filter(investor=user)
            return queryset
        return []
        
    def get_serializer_class(self):
        if self.action == 'marketplace':
            return InvestmentSerializer
        if self.action == 'InvestmentProducts':
            return InvestmentProductSerializer
        return InvestmentSerializer
        
    @action(methods=['GET'], detail=False)
    def marketplace(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False)
    def InvestmentProducts(self, request):
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
        # if self.action == 'marketplace':
        #     queryset = Loan.objects.filter(investors__in=all_users)
        #     return queryset
        # if self.action == 'fixedRoi':
        #     queryset = InvestmentProduct.objects.filter(type=InvestmentProduct.TYPE_CHOICES[0][1], investors__in=all_users)
        #     return queryset
        # if self.action == 'anytimeWithdraw':
        #     queryset = InvestmentProduct.objects.filter(type=InvestmentProduct.TYPE_CHOICES[1][1], investors__in=all_users)
        #     return queryset
        queryset = Loan.objects.all()
        return queryset#[]
        
    def get_serializer_class(self):
        if self.action == 'marketplace':
            return LoanApplicationSerializer
        if self.action == 'anytimeWithdraw' or self.action == 'fixedRoi':
            return InvestmentProductSerializer
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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id', 'created']
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[2][1]:
            queryset = InvestmentRequest.objects.filter(borrower=user)
        elif user.role == User.ROLE_CHOICES[3][1]:
            queryset = InvestmentRequest.objects.all()#filter(loan=None)
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
        loan_amount = instance.amount
        wallet = Wallet.objects.get(owner=instance.investor)

        # checking balance in the wallet
        if wallet.balance < loan_amount:
            LogService.log(user=instance.investor, msg=f'Your application for investment plan could not be approved due to insufficient balance.')
            return Response({"message": "Investor doesn't have enough balance in their wallet."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Deducting amount from the wallet
        wallet.balance -= loan_amount
        wallet.invested_amount += loan_amount
        wallet.save()

        borrower_wallet = Wallet.objects.get(owner=instance.borrower)
        borrower_wallet.balance += loan_amount
        borrower_wallet.save()
        LogService.transaction_log(owner=instance.investor, wallet=wallet, amount=loan_amount, debit=True)
        LogService.log(user=instance.investor, msg=f'Your wallet is debited with Rs. {loan_amount}. Current Wallet balance is Rs. {wallet.balance}')
        
        # Creating Loan
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
        
        # Creating and adding installments to Loan
        
        # Calculating Installment when repayment is monthly
        if instance.repayment_terms == LoanApplication.REPAYMENT_CHOICES[1][1]:
            P = float(instance.amount)               #Principal
            R = float(instance.interest_rate/12*100) #Rate of interest
            T = int(instance.tenure*12)              #Tenure
            installment = P*((R*((1+R)**T))/(((1+R)**T)-1))
            # principal = instance.amount/(instance.tenure*12)
            # interest = installment - principal
            for i in range(loan_instance.tenure*12):
                    month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                    interest = P*R
                    paid_P = installment - interest
                    installment = Installment.objects.create(parent_loan=loan_instance,
                                                                due_date=month,
                                                                principal=paid_P,
                                                                interest=interest,
                                                                total_amount=installment,
                                                                )
                    loan_instance.installments.add(installment)
                    P = P - paid_P
                
        # Calculating installment when repayment period is daily.
        if instance.repayment_terms == LoanApplication.REPAYMENT_CHOICES[0][1]:
            P = float(instance.amount)                    #Principal
            R = float(instance.interest_rate/(12*100*30)) #Rate of interest
            T = int(instance.tenure*12*30)                #Tenure
            installment = P*((R*((1+R)**T))/(((1+R)**T)-1))
            # principal = instance.amount/(instance.tenure*12)
            # interest = installment - principal
            for i in range(T):
                    day = datetime.date.today() + relativedelta.relativedelta(days=i+1)
                    # day = datetime. datetime. today() + datetime. timedelta(days=i+1)
                    interest = P*R
                    paid_P = installment - interest
                    installment = Installment.objects.create(parent_loan=loan_instance,
                                                                due_date=day,
                                                                principal=paid_P,
                                                                interest=interest,
                                                                total_amount=installment,
                                                                )
                    loan_instance.installments.add(installment)
                    P = P - paid_P

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
            queryset = InvestmentProduct.objects.filter(is_special_plan=True, is_record_active=True)
        elif user.role == User.ROLE_CHOICES[0][1]:
            queryset = InvestmentProduct.objects.filter(is_special_plan=True, allowed_investor=user, is_record_active=True)
        else:
            queryset = []
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investor = serializer.validated_data['allowed_investor']
        all_plans = InvestmentProduct.objects.filter(is_special_plan=True, is_record_active=True, allowed_investor=investor).count()
        if all_plans >= 4:
            return Response({"message": "An investor can be given maximum 4 special offers."}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        updated_investor = User.objects.get(id=investor.id)
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
        return InvestmentProductSerializer

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
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['borrower', 'investor', 'type']

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


class InstallmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['parent_loan']

    def get_queryset(self):
        queryset = Installment.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return InstallmentSerializer
    
    @action(methods=['POST'], detail=True)
    def pay(self, request, pk):
        user = request.user
        instance = self.get_object()
        wallet = Wallet.objects.get(owner=user)
        pass

    
def DataFormViewSet(request):
    return render(request, 'dataform.html')
