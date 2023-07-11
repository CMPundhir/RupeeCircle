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
from apps.wallet.models import Wallet, Transaction
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
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, 
                       filters.OrderingFilter]
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
        user = request.user
        
        # Checking if user is Investor or not.
        if user.role != User.ROLE_CHOICES[0][1]:
            return Response({"message": "Only Investors can invest in Investment Plans."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking wallet balance is equal or more than the investment amount.
        wallet = Wallet.objects.get(owner=user)
        if wallet.balance < instance.amount:
            return Response({"message": "You don't have enough balance to apply for this Investment plan. Kindly add funds to your wallet."})
        
        # Checking principle type of Investment plan
        if instance.principal_type == InvestmentProduct.PRINCIPAL_CHOICES[1][1]:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                final_loan_amount = serializer.validated_data['amount']
                is_tnc_accepted = serializer.validated_data['tnc']
            else:
                final_loan_amount = instance.amount
                is_tnc_accepted = False

        if is_tnc_accepted == False:
            return Response({"message": "Please accept T&C."})

        # Deducting Amount
        wallet.balance -= final_loan_amount
        wallet.invested_amount += final_loan_amount
        wallet.save()
        LogService.transaction_log(user=user, amount=final_loan_amount, debit=True, type=Transaction.TYPE_CHOICES[2][1])

        # Creating Loan
        loan_instance = Loan.objects.create(loan_amount=final_loan_amount,
                                                interest_rate=instance.interest_rate,
                                                tenure=instance.tenure,
                                                repayment_terms=instance.repayment_terms,
                                                collateral=instance.collateral,
                                                late_pay_penalties=instance.late_pay_penalties,
                                                prepayment_options=instance.prepayment_options,
                                                default_remedies=instance.default_remedies,
                                                privacy=instance.privacy,
                                                governing_law=instance.governing_law,
                                                tnc=instance.tnc,
                                                is_tnc_accepted = is_tnc_accepted,
                                                # borrower=instance.borrower,
                                                investor=instance.investor,
                                                type=instance.type)
        installment_amount = (final_loan_amount + ((final_loan_amount*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        principal = final_loan_amount/(instance.tenure*12)
        # interest = installment - principal
        for i in range(loan_instance.tenure*12):
                month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                installment = Installment.objects.create(parent_loan=loan_instance,
                                                            due_date=month,
                                                            principal=principal,
                                                            interest=installment_amount,
                                                            total_amount=installment_amount,
                                                            )
                loan_instance.installments.add(installment)
        instance.investors += 1
        instance.invested_amount += final_loan_amount
        instance.investors_detail.add(user)
        instance.save()
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
    
    @action(methods=['GET'], detail=True)
    def allInvestors(self, request, pk):
        instance = self.get_object()
        all_plans = Loan.objects.filter(product__plan_id=instance.plan_id).values_list('investor')
        print(all_plans)
        all_investors = User.objects.filter(id__in=all_plans)
        print(f"your all investors => {all_investors}")
        # return Response(serializer.data)
        page = self.paginate_queryset(all_investors)
        if page is not None:
            serializer = InvestorGetSerializer(all_investors, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InvestorGetSerializer(all_investors, many=True)
        return Response(serializer.data)
        
        # return Response(all_investors)

        investors = instance.investors_detail
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
        
        # Checking principle type of Investment plan
        if instance.principal_type == InvestmentProduct.PRINCIPAL_CHOICES[1][1]:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                final_loan_amount = serializer.validated_data['amount']
                is_tnc_accepted = serializer.validated_data['tnc']
        else:
            final_loan_amount = instance.amount
            is_tnc_accepted = False

        if is_tnc_accepted == False:
            return Response({"message": "Please accept T&C."})

        # Deducting Amount
        wallet.balance -= final_loan_amount
        wallet.invested_amount += final_loan_amount
        wallet.save()
        LogService.transaction_log(user=user, amount=final_loan_amount, debit=True, type=Transaction.TYPE_CHOICES[2][1])

        # Creating Loan
        loan_instance = Loan.objects.create(loan_amount=final_loan_amount,
                                                interest_rate=instance.interest_rate,
                                                tenure=instance.tenure,
                                                repayment_terms=instance.repayment_terms,
                                                collateral=instance.collateral,
                                                late_pay_penalties=instance.late_pay_penalties,
                                                prepayment_options=instance.prepayment_options,
                                                default_remedies=instance.default_remedies,
                                                privacy=instance.privacy,
                                                governing_law=instance.governing_law,
                                                tnc=instance.tnc,
                                                is_tnc_accepted = is_tnc_accepted,
                                                # borrower=instance.borrower,
                                                investor=instance.investor,
                                                type=instance.type)
        installment_amount = (final_loan_amount + ((final_loan_amount*instance.interest_rate/100)*instance.tenure))/(instance.tenure*12)
        principal = final_loan_amount/(instance.tenure*12)
        # interest = installment - principal
        for i in range(loan_instance.tenure*12):
                month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                installment = Installment.objects.create(parent_loan=loan_instance,
                                                            due_date=month,
                                                            principal=principal,
                                                            interest=installment_amount,
                                                            total_amount=installment_amount,
                                                            )
                loan_instance.installments.add(installment)
        instance.investors += 1
        instance.invested_amount += final_loan_amount
        instance.investors_detail.add(user)
        instance.save()
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
            return InvestmentGetSerializer
        if self.action == 'InvestmentProducts':
            return InvestmentProductSerializer
        return InvestmentGetSerializer
        
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
        LogService.transaction_log(owner=instance.investor, wallet=wallet, amount=loan_amount, debit=True, type=Transaction.TYPE_CHOICES[5][1])
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
            if user.special_plan_exist == False:
                user.special_plan_exist = True
                user.save()
            special_plan = InvestmentProduct.objects.get(id=22)
            special_plan.allowed_investor.add(user)
            special_plan.save()
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
    
    @action(methods=['GET', 'POST'], detail=False)
    def addall(self, request):
        all_users = User.objects.all()


class LoanViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['borrower', 'investor', 'type', 'product']

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
        return InvestmentGetSerializer
    
    @action(methods=['GET'], detail=False)
    def excel(self, request):
        queryset = Loan.objects.all()
        serializer = LoanExcelSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = []

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-id')
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductInputSerializer
        elif self.action == 'get_rate':
            return RateSerializer
        elif self.action == 'get_interest' or self.action == 'apply':
            return InterestSerializer
        return ProductSerializer
    
    def create(self, request, *args, **kwargs):
        paramlimit = Param.objects.all()[0]
        serializer = ProductInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Checking if values are valid or not
        for i in serializer.validated_data['all_data']:
            if i['min_amount'] < 0 or i['max_amount'] < 0 or i['min_tenure'] < 0 or i['max_tenure'] < 0 or i['interest_rate'] < 0:
                return Response({"message": "All values should be positive."}, status=status.HTTP_400_BAD_REQUEST)

            if type(i['min_tenure']) and type(i['max_tenure']) and type(i['min_amount']) and type(i['max_amount']) != int:
                return Response({"message": "All values should be numeric except interest rates."}, status=status.HTTP_400_BAD_REQUEST)

            if type(i['interest_rate']) != float:
                return Response({"message": "Interest Values should be decimal values."}, status.HTTP_400_BAD_REQUEST)

        # Checking tenure range
        if not paramlimit.min_tenure <= serializer.validated_data['all_data'][0]['min_tenure'] <= paramlimit.max_tenure or not paramlimit.min_tenure <= serializer.validated_data['all_data'][0]['max_tenure'] <= paramlimit.max_tenure:
            return Response({"message": f"Tenure should be between {paramlimit.min_tenure} and {paramlimit.max_tenure} months."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking amount range
        if not paramlimit.min_amount <= serializer.validated_data['all_data'][0]['min_amount'] <= paramlimit.max_amount or not paramlimit.min_amount <= serializer.validated_data['all_data'][0]['max_amount'] <= paramlimit.max_amount:
            return Response({"message": f"Amount should be between {paramlimit.min_amount} and {paramlimit.max_amount}."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking interest rate range
        if not paramlimit.min_interest < serializer.validated_data['all_data'][0]['interest_rate'] < paramlimit.max_interest:
            return Response({"message": f"Interest Rate should be between {paramlimit.min_interest} and {paramlimit.max_interest}"}, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.validated_data['all_data'])
        
        # Checking if tenure slab clashes
        range_list = set()
        for i in serializer.validated_data['all_data']:
            if i['min_tenure'] in range_list or i['max_tenure'] in range_list:
                return Response({"message": "The Tenure range you entered clashes."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                for j in range(i['min_tenure'], i['max_tenure'] + 1):
                    range_list.add(j)
                    print(range_list)

        # Checking if slabs are inconsistent
        tenure_range = [i + 1 for i in range(paramlimit.max_tenure)]
        missing_tenure = list()
        for i in tenure_range:
            if i not in range_list:
                missing_tenure.append(i)
        if len(missing_tenure) > 0:
            return Response({"message": f"Inconsistent Slabs. Plan not applicable for following months {missing_tenure}"}, status=status.HTTP_400_BAD_REQUEST)

        # Checking if slab already exists.
        for i in serializer.validated_data['all_data']:
            all_products = Product.objects.all()
            if len(all_products) > 0:
                for j in all_products:
                    if int(j.min_tenure) <= int(i['min_tenure']) <= int(j.max_tenure) and j.type == serializer.validated_data['type']:
                        return Response({"message": "Slab Already Exists."}, status=status.HTTP_400_BAD_REQUEST)
                    if int(j.min_tenure) <= int(i['max_tenure']) <= int(j.max_tenure) and j.type == serializer.validated_data['type']:
                        return Response({"message": "Slab Already Exists."}, status=status.HTTP_400_BAD_REQUEST)
        # return Response({"message": "Everything went well."})
        # Creating slabs
        for i in serializer.validated_data['all_data']:
            print(f'This is your {i}')
            Product.objects.create(min_amount=i['min_amount'],
                                   max_amount=i['max_amount'],
                                   min_tenure=i['min_tenure'],
                                   max_tenure=i['max_tenure'],
                                   type=serializer.validated_data['type'],
                                   interest_rate=i['interest_rate'],
                                   )
        return Response({"message": "Created."}, status=status.HTTP_201_CREATED)#, headers=headers)

    @action(methods=['GET'], detail=False)
    def deleteall(self, request):
        queryset = Product.objects.all()
        queryset.delete()
        return Response({"message": "Deleted All."}, status=status.HTTP_200_OK)
    
    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    @action(methods=['POST'], detail=False)
    def get_rate(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        tenure = serializer.validated_data['tenure']
        for i in Product.objects.all():
            if i.min_tenure <= tenure <= i.max_tenure:
                return Response({"interest": i.interest_rate}, status=status.HTTP_200_OK)
        return Response({"message": "No product applicable on given tenure."}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=False)
    def get_interest(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        monthly_interest = (serializer.validated_data['amount']*serializer.validated_data['interest_rate'])/(100*12)
        total_interest = monthly_interest*serializer.validated_data['tenure']
        total = serializer.validated_data['amount'] + total_interest
        return Response({"monthly_interest": monthly_interest, 
                         "total_interest": total_interest, 
                         "principal": serializer.validated_data['amount'],
                         "total": total},
                         status=status.HTTP_200_OK)
        
    # @action(methods=['GET', 'POST'], detail=False)
    # def apply(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     for i in Product.objects.all():
    #         if i.min_tenure <= serializer.validated_data['tenure'] <= i.max_tenure:
    #             print("Looping")
    #             instance = i
    #             break
    #         else:
    #             instance = None
    #     print("Looped")
    #     if instance:
    #         if instance.interest_rate != serializer.validated_data['interest_rate']:
    #             return Response({"message": "Interest Rate doesn't match the slab interest rate."}, status=status.HTTP_400_BAD_REQUEST)
    #         print(f"This is your instance => {instance}")
    #         wallet = Wallet.objects.get(owner=request.user)
    #         if wallet.balance < serializer.validated_data['amount']:
    #             return Response({"message": "You don't have enough balance in your wallet."}, status=status.HTTP_400_BAD_REQUEST)
    #         wallet.balance -= serializer.validated_data['amount']
    #         wallet.save()
    #         LogService.log(user=request.user, msg=f"Investment successful for {instance.plan_id}.")
    #         LogService.log(user=request.user, msg=f"Rs.{serializer.validated_data['amount']} has been deducted from your Wallet.")
    #         LogService.transaction_log(owner=request.user, wallet=wallet, amount=serializer.validated_data['amount'], debit=True, type=Transaction.TYPE_CHOICES[2][1])
    #         investment = Investment.objects.create(principal=serializer.validated_data['amount'],
    #                                                interest_rate=serializer.validated_data['interest_rate'],
    #                                                tenure=serializer.validated_data['tenure'],
    #                                                product=instance,
    #                                                investor=request.user)
    #         for i in range(serializer.validated_data['tenure']):
    #             month = datetime.date.today() + relativedelta.relativedelta(months=i+1)
    #             payment = Payment.objects.create(investor=request.user,
    #                                             due_date=month,
    #                                             product_id=instance.plan_id,
    #                                             amount=serializer.validated_data['amount'],
    #                                             )
    #             investment.installments.add(payment)
    #             investment.save()
    #         return Response({"message": "Invested Successfully."}, status=status.HTTP_200_OK)
    #     return Response({"message": "No product applicable on this tenure."}, status=status.HTTP_404_NOT_FOUND)


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['product_id', 'investor']
    ordering_fields = ['id']
    filterset_fields = ['product_id', 'investor']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            queryset = Payment.objects.all()
        elif user.role == 'INVESTOR':
            queryset = Payment.objects.filter(investor=user)
        else:
            queryset = Payment.objects.none()
        return queryset
    
    def get_serializer_class(self):
        return PaymentSerializer
    
    @action(methods=['GET'], detail=False)
    def deleteall(self, request):
        queryset = Payment.objects.all()
        queryset.delete()
        return Response({"message": "Deleted All."}, status=status.HTTP_200_OK)


class InvestmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id']
    filterset_fields = ['investor', 'product_id']
    
    def get_queryset(self):
        user=self.request.user
        if user.role == 'INVESTOR':
            queryset = Investment.objects.filter(investor=user)
        elif user.role == 'ADMIN':
            queryset = Investment.objects.all()
        else:
            queryset = Investment.objects.none()
        return queryset
    
    def get_serializer_class(self):
        return InvestmentSerializer

    @action(methods=['GET'], detail=False)
    def deleteall(self, request):
        queryset = Investment.objects.all()
        queryset.delete()
        return Response({"message": "Deleted All."}, status=status.HTTP_200_OK)


class ParamViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Param.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return ParamSerializer

    def create(self, request):
        return Response({"message": "Method Not Allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



class NewProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['id', 'month']
    filterset_fields = ['product_id', 'type', 'month', 'is_record_active'] # added filter of record active in Product

    def get_queryset(self):
        queryset = NewProduct.objects.all().order_by("-id")#filter(is_record_active=True)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductInputSerializer
        elif self.action == 'calculate_interest':
            return ProductApplySerializer
        elif self.action == 'apply':
            return ApplySerializer
        return NewProductSerialzier
    
    def partial_update(self, request, *args, **kwargs):
        print("Product Patch => ",request.data)
        data = request.data
        if 'type' in data and data['type'] == NewProduct.TYPE_CHOICES[1][1] and data['is_record_active']:
            flex_list = NewProduct.objects.filter(type=NewProduct.TYPE_CHOICES[1][1])
            for f in flex_list:
                f.is_record_active = False
                f.save()
        return super().partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # paramlimit = Param.objects.all()[0]
        serializer = ProductInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # return Response({"message": type(serializer.validated_data['all_data'])})
        types_of_all = list()

        # Checking if plan with same param is inactive
        inactive_exist = list()
        all_plans = NewProduct.objects.filter(is_record_active=False)
        for i in serializer.validated_data['all_data']:
            for j in all_plans:
                if i['type'] == j.type and i['month'] == j.month and i['interest_rate'] == j.interest_rate:
                    return Response({"message": "Plan(s) already exist with same specification."})

        for i in serializer.validated_data['all_data']:
            if i['type'] == NewProduct.TYPE_CHOICES[1][1]:
                types_of_all.append(i['type'])
        for i in NewProduct.objects.filter(is_record_active=True):
            if i.type == NewProduct.TYPE_CHOICES[1][1]:
                types_of_all.append(i.type)
        if len(types_of_all) > 1:
            return Response({"message": "Only one plan can be created for FLEXI plan."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking if values are valid or not
        for i in serializer.validated_data['all_data']:
            if i['month'] < 1 or i['interest_rate'] < 0:
                return Response({"message": "All values should be positive."}, status=status.HTTP_400_BAD_REQUEST)
            if type(i['month']) != int:
                return Response({"message": "All values should be numeric except interest rates."}, status=status.HTTP_400_BAD_REQUEST)
            if type(i['interest_rate']) != float:
                return Response({"message": "Interest Values should be decimal values."}, status.HTTP_400_BAD_REQUEST)
        
        # Checking if tenure slab clashes
        range_list = list()
        for i in serializer.validated_data['all_data']:
            current_list = [i['month'], i['type']]
            if current_list in range_list:
                return Response({"message": "The Tenure range you entered clashes."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                range_list.append(current_list)

        # Checking if plan already exists
        for i in serializer.validated_data['all_data']:
            exist = NewProduct.objects.filter(type=i['type'], month=i['month']).exists()
            if exist:
                return Response({"message": f"Plan with type {i['type']} and month {i['month']} already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Creating Plans
        for i in serializer.validated_data['all_data']:
            print(f'This is your {i}')
            NewProduct.objects.create(type=i['type'],
                                    month="1" if i.type == NewProduct.TYPE_CHOICES[1][1] else i['month'],
                                    interest_rate=i['interest_rate'])
            
        return Response({"message": "Created."}, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False)
    def deleteall(self, request):
        queryset = NewProduct.objects.all()
        queryset.delete()
        return Response({"message": "Deleted All."}, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False)
    def calculate_interest(self, request):
        data = request.data
        serializer = ProductApplySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            queryset = NewProduct.objects.filter(is_record_active=True)
            response_list = list()
            for i in queryset:
                if i.type == NewProduct.TYPE_CHOICES[1][1]:
                    if 'flexi_month' in serializer.validated_data and serializer.validated_data['flexi_month']:
                        i.month = serializer.validated_data['flexi_month']
                i.total_interest = ((serializer.validated_data['amount'])*(i.interest_rate/100))*(i.month/12)
                response_list.append(i)
            flexi = [i for i in response_list if i.type == 'FLEXI']
            print(f"This is your Flexi {flexi}")
            flexi_index = response_list.index(flexi[0])
            flexi_plan = response_list.pop(flexi_index)
            response_list[0] = flexi_plan
        response_serializer = ProductResponseSerializer(response_list, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        instance = self.get_object()
        wallet = Wallet.objects.get(owner=request.user)
        serializer = ApplySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if wallet.balance < serializer.validated_data['amount']:
                    return Response({"message": "You don't have enough balance in your wallet."}, status=status.HTTP_400_BAD_REQUEST)
            wallet.balance -= serializer.validated_data['amount']
            wallet.invested_amount += serializer.validated_data['amount']
            # return Response({"message": "All good till wallet."})
            wallet.save()
            LogService.log(user=request.user, msg=f"Investment successful for {instance.plan_id}.")
            LogService.log(user=request.user, msg=f"Rs.{serializer.validated_data['amount']} have been deducted from your Wallet.")
            LogService.transaction_log(owner=request.user, wallet=wallet, amount=serializer.validated_data['amount'], debit=True, type=Transaction.TYPE_CHOICES[2][1])
            investment = Investment.objects.create(principal=instance.amount,
                                                    interest_rate=instance.interest_rate,
                                                    tenure=instance.tenure,
                                                    product=instance,
                                                    investor=request.user)
            for i in range(instance.month):
                if instance.interest_payment == Investment.INTEREST_PAYMENT[0][1]:
                    amount = ((serializer.validated_data['amount'])*(instance.interest_rate/100))*(instance.month/12)/(instance.month*30)
                    due_date = datetime.date.today() + relativedelta.relativedelta(days=i+1)
                if instance.interest_payment == Investment.INTEREST_PAYMENT[1][1]:
                    due_date = datetime.date.today() + relativedelta.relativedelta(months=i+1)
                    amount = ((serializer.validated_data['amount'])*(instance.interest_rate/100))*(instance.month/12)/instance.month
                if instance.interest_payment == Investment.INTEREST_PAYMENT[2][1]:
                    amount = (((serializer.validated_data['amount'])*(instance.interest_rate/100))*(instance.month/12)/(instance.month))*4
                    due_date = datetime.date.today() + relativedelta.relativedelta(months=(i+1)*4) 
                if instance.interest_payment == Investment.INTEREST_PAYMENT[0][1]:
                    amount = ((serializer.validated_data['amount'])*(instance.interest_rate/100))#*(instance.month/12)/instance.month
                    due_date = datetime.date.today() + relativedelta.relativedelta(years=i+1)
                payment = Payment.objects.create(investor=request.user,
                                                due_date=due_date,
                                                product_id=instance.plan_id,
                                                amount=amount,
                                                )
                investment.installments.add(payment)
                investment.save()
            return Response({"message": "Invested Successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    @action(methods=['GET'], detail=False)
    def flexi_month(self, request):
        # print(request.auth)
        flexi = self.get_queryset().get(type='FLEXI')
        data = [i for i in range(1,flexi.month + 1)]
        return Response(data, status=status.HTTP_200_OK)
