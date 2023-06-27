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
