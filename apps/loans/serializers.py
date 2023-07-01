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
    # installments = InstallmentSerializer(many=True)
    investor = InvestorGetSerializer()

    class Meta:
        model = Loan
        fields = '__all__'


class ApplySerializer(serializers.Serializer):
    amount = models.IntegerField()


class ProductCreationSerializer(serializers.Serializer):
    min_amount = serializers.IntegerField()
    max_amount = serializers.IntegerField()
    min_tenure = serializers.IntegerField()
    max_tenure = serializers.IntegerField()
    interest_rate = serializers.FloatField()
    # type = serializers.CharField()

    # class Meta:
    #     model = Product
    #     fields = ['min_amount', 'max_amount', 'min_tenure', 'max_tenure', 'interest_rate', 'type']


class ProductInputSerializer(serializers.Serializer):
    all_data = ProductCreationSerializer(many=True)
    type = serializers.ChoiceField(choices=Product.TYPE_CHOICES)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class LoanExcelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = '__all__'
