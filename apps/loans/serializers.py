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


class InvestmentProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentProduct
        fields = '__all__'


class InvestmentRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentRequest
        fields = '__all__'


class InvestmentApplicationSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    remarks = serializers.CharField()


class InvestmentRequestGetSerializer(serializers.ModelSerializer):
    loan = LoanApplicationSerializer()
    # plan = InvestmentProductSerializer()
    investor = InvestorGetSerializer()

    class Meta:
        model = InvestmentRequest
        fields = '__all__'


class InvestmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = '__all__'


class InstallmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Installment
        fields = '__all__'
