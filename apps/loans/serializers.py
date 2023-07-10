from rest_framework import serializers
from apps.mauth.serializers import UserSerializer
from apps.dashboard.serializers import InvestorGetSerializer
from .models import *


# def validate_tenure_range(value):
#     if value < 1 or value > 84:
#         raise serializers.ValidationError('Tenure should be between 1 and 84')
    # elif value > 10:
    #     raise serializers.ValidationError('Value cannot be higher than 10')


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


class InvestmentGetSerializer(serializers.ModelSerializer):
    # installments = InstallmentSerializer(many=True)
    investor = InvestorGetSerializer()

    class Meta:
        model = Loan
        fields = '__all__'


class ApplySerializer(serializers.Serializer):
    amount = serializers.IntegerField()


class NewProductCreationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=NewProduct.TYPE_CHOICES)
    month = serializers.IntegerField()
    # amount = serializers.IntegerField()
    interest_rate = serializers.FloatField()


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
    all_data = NewProductCreationSerializer(many=True)
    # type = serializers.ChoiceField(choices=Product.TYPE_CHOICES)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class LoanExcelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = '__all__'


class RateSerializer(serializers.Serializer):
    tenure = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'


class InterestSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class InvestmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Investment
        fields = '__all__'


class InvestmentGetSerializer(serializers.ModelSerializer):
    installments = PaymentSerializer(many=True)

    class Meta:
        model = Investment
        fields = '__all__'


class ParamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Param
        fields = '__all__'


class NewProductSerialzier(serializers.ModelSerializer):

    class Meta:
        model = NewProduct
        fields = '__all__'


class ProductApplySerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    flexi_month = serializers.IntegerField(required=False)


class ProductResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    total_interest = serializers.IntegerField()
    product_id = serializers.CharField()
    type = serializers.ChoiceField(choices=NewProduct.TYPE_CHOICES)
    month = serializers.IntegerField()
    interest_rate = serializers.FloatField()

    # class Meta:
    #     model = NewProduct
    #     fields = '__all__'
