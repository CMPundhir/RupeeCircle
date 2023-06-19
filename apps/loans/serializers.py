from rest_framework import serializers
from apps.mauth.serializers import UserSerializer
from apps.dashboard.serializers import InvestorGetSerializer
from .models import *

class LoanApplicationSerializer(serializers.ModelSerializer):
    # borrower = UserSerializer()
    # investors = UserSerializer(many=True)

    class Meta:
        model = LoanApplication
        fields = ['id', 'created', 'loan_amount', 'interest_rate', 'repayment_terms', 'installments', 'collateral', 'late_pay_penalties', 'prepayment_options', 'default_remedies', 'privacy', 'governing_law', 'borrower', 'investors']


# class RecentLoanSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = LoanForm
#         fields = ['id', 'first_name', 'last_name', 'loan']


class InvestmentPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentPlan
        fields = '__all__'


class InvestmentRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentRequest
        fields = '__all__'


class InvestmentRequestGetSerializer(serializers.ModelSerializer):
    loan = LoanApplicationSerializer()
    plan = InvestmentPlanSerializer()
    investor = InvestorGetSerializer()

    class Meta:
        model = InvestmentRequest
        fields = '__all__'
