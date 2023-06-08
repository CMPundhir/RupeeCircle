from rest_framework import serializers
from apps.mauth.serializers import UserSerializer
from .models import *

class LoanSerializer(serializers.ModelSerializer):
    borrower = UserSerializer()
    investor = UserSerializer(many=True)

    class Meta:
        model = Loan
        fields = ['id', 'loan_id', 'created', 'loan_amount', 'interest_rate', 'repayment_terms', 'installments', 'collateral', 'late_pay_penalties', 'prepayment_options', 'default_remedies', 'privacy', 'governing_law', 'borrower', 'investor']


class LoanFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanForm
        fields = '__all__'


class RecentLoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanForm
        fields = ['id', 'first_name', 'last_name', 'loan']


class InvestmentPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentPlan
        fields = '__all__'
