from rest_framework import serializers
from apps.loans.models import *
from apps.mauth.models import CustomUser as User
from apps.mauth.serializers import UserSerializer, UserDetailSerializer


class InvestorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile', 'email', 'gender', 'pan', 'aadhaar', 'bank_acc', 'bank_ifsc', 'company', 'address', 'country', 'state', 'city', 'pincode']


class InvestorGetSerializer(serializers.ModelSerializer):
    partner = UserDetailSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'mobile', 'email', 'gender', 'pan', 'aadhaar', 'bank_acc', 'bank_ifsc', 'company', 'address', 'country', 'state', 'city', 'pincode', 'partner']
        # fields = '__all__'


class BorrowerGetSerializer(serializers.ModelSerializer):
    # partner = UserDetailSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'credit_score', 'first_name', 'last_name', 'mobile', 'email', 'gender', 'pan', 'aadhaar', 'bank_acc', 'bank_ifsc', 'company', 'address', 'country', 'state', 'city', 'pincode', 'partner']
        


class PartnerRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 
                  'last_name', 
                  'mobile', 
                  'email', 
                  'gender', 
                  'pan', 
                  'aadhaar', 
                  'bank_acc', 
                  'bank_ifsc', 
                  'company',
                  'company_gst',
                  'company_pan',
                  'nature', 
                  'address', 
                  'country', 
                  'state', 
                  'city', 
                  'pincode']
        # fields = ['first_name', 'last_name', 'mobile', 'email', 'gender', 'country', 'state', 'city', 'pincode', 'company', 'address', 'pan', 'aadhaar', 'bank_acc', 'bank_ifsc']
        # extra_kwargs = {'first_name': {'required': True},
        #                 'mobile': {'required': True}, 
        #                 'email': {'required': True},
        #                 'pan': {'required': True},
        #                 'aadhaar': {'required': True},
        #                 'bank_acc': {'required': True},
        #                 'bank_ifsc': {'required': True}}


class PartnerGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'mobile', 'email', 'gender', 'pan', 'aadhaar', 'bank_acc', 'bank_ifsc', 'company', 'address', 'country', 'state', 'city', 'pincode']


class PartnerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'mobile']


class InvestmentOptionsSerializer(serializers.Serializer):
    is_fixedroi_allowed = serializers.BooleanField()
    is_anytime_withdrawal_allowed = serializers.BooleanField()
    is_marketplace_allowed = serializers.BooleanField()


class InvestorExcelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

