from rest_framework import serializers
from apps.mauth.serializers import UserSerializer
from apps.dashboard.serializers import InvestorGetSerializer
from .models import *


class TermsAndConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsAndCondition
        fields = '__all__'


class BorrowerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'credit_score']


class LoanApplicationSerializer(serializers.ModelSerializer):
    borrower = BorrowerDetailSerializer()
    # investors = UserSerializer(many=True)

    class Meta:
        model = LoanApplication
        fields = ['id', 'plan_id', 'tenure', 'type', 'created', 'loan_amount', 'interest_rate', 'repayment_terms', 'installments', 'collateral', 'late_pay_penalties', 'prepayment_options', 'default_remedies', 'privacy', 'governing_law', 'borrower', 'investors']


class LoanApplicationCreateSerializer(serializers.ModelSerializer):
    # borrower = BorrowerDetailSerializer()
    # investors = UserSerializer(many=True)

    class Meta:
        model = LoanApplication
        fields = ['id', 'plan_id', 'tenure', 'type', 'created', 'loan_amount', 'interest_rate', 'repayment_terms', 'installments', 'collateral', 'late_pay_penalties', 'prepayment_options', 'default_remedies', 'privacy', 'governing_law']


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
        # fields = '__all__'
        fields = ['loan_amount', 'tenure', 'interest_rate', 'repayment_terms', 'collateral', 'late_pay_penalties', 'prepayment_options', 'default_remedies', 'privacy', 'governing_law', 'remarks']


class InvestmentApplicationSerializer(serializers.Serializer):
    amount = serializers.CharField()
    tnc = serializers.BooleanField()


class InvestmentRequestGetSerializer(serializers.ModelSerializer):
    # loan = LoanApplicationSerializer()
    # plan = InvestmentProductSerializer()
    investor = InvestorGetSerializer()

    class Meta:
        model = InvestmentRequest
        fields = '__all__'


class InstallmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Installment
        fields = '__all__'


class InvestmentSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True)

    class Meta:
        model = Loan
        fields = '__all__'


class ApplySerializer(serializers.Serializer):
    amount = models.IntegerField()
