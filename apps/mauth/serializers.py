from rest_framework import serializers
from .models import CustomUser as User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class LogInSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField()
    otp = serializers.IntegerField()
    class Meta:
        model = User
        fields = ['mobile', 'otp']


class GetOTPSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField()

    class Meta:
        model = User
        fields = ['mobile']


class VerifyOTPSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField()
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['mobile', 'otp']

class PanSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    pan = serializers.RegexField(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')

    class Meta:
        model = User
        fields = ['pan']

class PanVerifySerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    pan = serializers.RegexField(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    name = serializers.CharField()
    is_verified = serializers.BooleanField()

    class Meta:
        model = User
        fields = ['pan', 'name', 'is_verified']

class AadharSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    aadhaar = serializers.RegexField(regex=r'^[0-9]{12}$')

    class Meta:
        model = User
        fields = ['aadhaar']

class AadharVerifySerializer(serializers.ModelSerializer):
    aadhaar = serializers.RegexField(regex=r'^[0-9]{12}$')
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['aadhaar', 'otp']


class BankDetailSerializer(serializers.ModelSerializer):
    bank = serializers.CharField()
    bank_acc = serializers.CharField()

    class Meta:
        model = User
        fields = ['bank', 'bank_acc']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'mobile', 'is_mobile_verified', 'pan', 'is_pan_verified', 'aadhaar', 'is_aadhaar_verified', 'bank_acc', 'is_bank_acc_verified', 'status']
