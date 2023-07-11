from rest_framework import serializers
from .models import CustomUser as User
from .models import *
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


class DedupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['mobile', 'pan', 'aadhaar', 'bank_acc']


class SelfieUploadSerializer(serializers.ModelSerializer):
    selfie = serializers.ImageField()

    class Meta:
        model = User
        fields = ['selfie']


class VerifyOTPSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField()
    is_tnc_accepted = serializers.BooleanField()
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['mobile', 'role', 'is_tnc_accepted', 'otp']


class PanSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    pan = serializers.RegexField(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')

    class Meta:
        model = User
        fields = ['pan']


class PanVerifySerializer(serializers.Serializer):
    # mobile = serializers.CharField()
    # pan = serializers.RegexField(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    # name = serializers.CharField()
    is_verified = serializers.BooleanField()

    # class Meta:
    #     model = User
    #     fields = ['is_verified']


class AadharSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    aadhaar = serializers.RegexField(regex=r'^[0-9]{12}$')

    class Meta:
        model = User
        fields = ['aadhaar']


class AadharVerifySerializer(serializers.ModelSerializer):
    aadhaar = serializers.RegexField(regex=r'^[0-9]{12}$')
    request_id = serializers.CharField()
    otp = serializers.CharField()

    class Meta:
        model = User
        fields = ['request_id', 'otp', 'aadhaar']


class BankDetailSerializer(serializers.ModelSerializer):
    # acc_holder_name = serializers.CharField()
    bank_ifsc = serializers.CharField()
    bank_acc = serializers.CharField()

    class Meta:
        model = User
        fields = ['bank_ifsc', 'bank_acc', 'acc_holder_name']

# include
# class AddInvestorSerializer(serializers.Serializer):
    # pass
    # investor = serializers.ChoiceField(choices=User.objects.filter(role=User.ROLE_CHOICES[0][1], partner=None))

    # class Meta:
    #     model = User
    #     fields = ['partner']


class EmailDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email']


class EmailVerifySerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['email', 'otp']

# include
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        fields = ['id', 'user_id', 'credit_score', 'selfie', 'username', 'partner', 'first_name', 'last_name', 'email', 'is_email_verified', 'gender', 'mobile', 'is_mobile_verified', 'country', 'state', 'city', 'pincode', 'company', 'address', 'status', 'special_plan_exist', 'is_fixedroi_allowed', 'is_anytime_withdrawal_allowed', 'is_marketplace_allowed', 'rc_risk', 'role']


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'selfie', 'rc_risk', 'credit_score', 'username', 'partner', 'first_name', 'last_name', 'email', 'is_email_verified', 'gender', 'mobile', 'is_mobile_verified', 'country', 'state', 'city', 'pincode', 'company', 'address', 'pan', 'is_pan_verified', 'aadhaar', 'is_aadhaar_verified', 'bank_acc', 'bank_ifsc', 'is_bank_acc_verified', 'status', 'role', 'is_fixedroi_allowed', 'is_anytime_withdrawal_allowed', 'is_marketplace_allowed', 'special_plan_exist']


class RiskLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = RiskLog
        fields = '__all__'


class LogHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = LogHistory
        fields = '__all__'
