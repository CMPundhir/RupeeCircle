from rest_framework import serializers
from .models import *


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'


class WalletGetSerializer(serializers.ModelSerializer):
    # owner = UserSerializer()

    class Meta:
        model = Wallet
        fields = ['id', 'uid', 'owner', 'balance', 'invested_amount']


class AddFundsSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField()

    class Meta:
        model = Wallet
        fields = ['value']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'

class BankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankAccount
        fields = '__all__'


class TransactionExcelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class BankSlabSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankSlab
        fields = '__all__'

class CreateOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True, min_value=1, max_value=10000)
    redirect_url = serializers.URLField(required=True)


class CheckStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
