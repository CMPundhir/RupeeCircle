from rest_framework import serializers
from .models import CustomUser as User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

# class LogInSerializer(serializers.Serializer):
#     phone = serializers.CharField()
    # class Meta:
    #     model = User
    #     fields = ['username', 'password']


# class RegistrationSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField()
#     email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(required=True, write_only=True)

#     def validate(self, args):
#         if args['password'] != args['password2']:
#             raise serializers.ValidationError({"Password":"Password fields does not match."})
#         return args
    
#     def create(self, validated_data):
#         user = User.objects.create(
#             username = validated_data['username'],
#             first_name = validated_data['first_name'],
#             last_name = validated_data['last_name'],
#             email = validated_data['email']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user


# class UserSerializer(serializers.ModelSerializer):
#     # username = serializers.CharField()
#     # password = serializers.CharField()

#     class Meta:
#         model = User
#         fields = '__all__'

class GetOTPSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField()

    class Meta:
        model = User
        fields = ['mobile']


class VerifyOTPSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['otp']

class PanSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    pan = serializers.RegexField(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')

    class Meta:
        model = User
        fields = ['pan']

class PanVerifySerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    is_verified = serializers.BooleanField()

    class Meta:
        model = User
        fields = ['is_verified']

class AadharSerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    aadhar = serializers.RegexField(regex=r'^[0-9]{12}$')

    class Meta:
        model = User
        fields = ['aadhar']

class AadharVerifySerializer(serializers.ModelSerializer):
    # mobile = serializers.CharField()
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['otp']


class BankDetailSerializer(serializers.ModelSerializer):
    bank_acc = serializers.CharField()

    class Meta:
        model = User
        fields = ['bank_acc']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'mobile', 'is_phone_verified', 'pan', 'is_pan_verified', 'aadhar', 'is_aadhar_verified', 'bank_acc', 'is_bank_acc_verified', 'status']
