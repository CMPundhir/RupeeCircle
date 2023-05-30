from rest_framework import serializers
from apps.loans.models import *
from .models import Wallet, Transaction
from apps.mauth.serializers import UserSerializer


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'


class WalletGetSerializer(serializers.ModelSerializer):
    # owner = UserSerializer()

    class Meta:
        model = Wallet
        fields = ['id', 'owner', 'balance', 'invested_amount']


class AddFundsSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField()

    class Meta:
        model = Wallet
        fields = ['value']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'
