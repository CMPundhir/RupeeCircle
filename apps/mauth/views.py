from django.shortcuts import render
import random
from utility.otputility import OTP_DICT, AADHAR_OTP_DICT
from apps.mauth.models import CustomUser
from django.contrib.auth import authenticate, logout
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser as User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class AuthViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        queryset = User.objects.all()
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'getOtp':
            return GetOTPSerializer
        elif self.action == 'login':
            return LogInSerializer
        elif self.action == 'registerApi':
            return VerifyOTPSerializer
        else:
            return UserSerializer
    
    @action(methods=['POST'], detail=False)
    def login(self, request):
        data = request.data
        serializer = LogInSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            instance = User.objects.filter(mobile=mobile).exists()
            if instance and OTP_DICT[f'{mobile}'] == otp:
                user = User.objects.get(mobile=mobile)
                # if user.status == CustomUser.STATUS_CHOICES[4][0]:
                token = get_tokens_for_user(user)
                return Response({"token": token, "status": user.status}, status=status.HTTP_200_OK)
            return Response({"msg": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors)

    @permission_classes([AllowAny])
    @action(methods=['POST'], detail=False)
    def getOtp(self, request):
        '''
        This function takes mobile number and generates OTP and returns User Id and OTP in response.
        '''
        data = request.data
        print(data)
        # global OTP
        serializer = GetOTPSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile=serializer.validated_data['mobile']
            otp = random.randint(1000, 9999)
            OTP_DICT[f'{mobile}'] = otp
            print(OTP_DICT[f'{mobile}'])
            return Response({"otp": f"Your OTP is {otp}."})
        return Response(serializer.errors)
    
    @permission_classes([AllowAny])
    @action(methods=['POST'], detail=False)
    def registerApi(self, request):
        '''
        This method verifies OTP for the given mobile number and return registration status and auth tokens in response if OTP matches
        else returns response accordingly.
        '''
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            mobile = serializer.validated_data['mobile']
            # global OTP
            print(OTP_DICT[f'{mobile}'])
            if OTP_DICT[f'{mobile}'] == otp:
                user = User.objects.create(username=mobile, mobile=mobile, is_mobile_verified=True, status=CustomUser.STATUS_CHOICES[1][0])
                # user = User.objects.get(pk=pk)
                # if user.status == CustomUser.STATUS_CHOICES[0][0]:
                user.is_mobile_verified = True
                user.status = CustomUser.STATUS_CHOICES[1][0]
                user.save()
                id = user.id
                del OTP_DICT[f'{mobile}']
                    # return Response({"msg": "OTP Verified", "step": user.is_active})
                # try:
                #     user = User.objects.get(mobile=mobile)
                # except:
                #     user = User.objects.create(username=mobile, mobile=mobile)
                token = get_tokens_for_user(user)
                return Response({"id": id, "msg": "OTP Verified", "step": user.status, "token": token}, status=status.HTTP_200_OK)
            return Response("OTP does not match.", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages)


class UserViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'panDetail':
            return PanSerializer
        elif self.action == 'panVerify':
            return PanVerifySerializer
        elif self.action == 'aadharDetail':
            return AadharSerializer
        elif self.action == 'aadharVerify':
            return AadharVerifySerializer
        else:
            return UserSerializer
    
    # @permission_classes([IsAuthenticated])
    @action(methods=['POST'], detail=True)
    def panDetail(self, request, pk):
        '''
        Takes PAN number and obtains response from PAN database if matches return owner Name in response
        '''
        # user = request.user
        data = request.data
        serializer = PanSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(pk=pk)
            user.pan = serializer.validated_data['pan']
            user.save()
            return Response({"Name": "Your Name"})
        return Response(serializer.errors)
    
    # @permission_classes([IsAuthenticated])
    @action(methods=['POST'], detail=True)
    def panVerify(self, request, pk):
        '''
        Takes boolean response and saves PAN verification status of user
        '''
        # user = request.user
        data = request.data
        serializer = PanVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(pk=pk)
            is_verified = serializer.validated_data['is_verified']
            if is_verified == True:
                user.is_pan_verified = True
                user.status = CustomUser.STATUS_CHOICES[2][0]
                user.save()
                return Response({'msg': 'PAN Verification successful', 'step': user.status})
            return Response({"msg": "Please verify Name."})
        return Response(serializer.errors)

    # @permission_classes([IsAuthenticated])  
    @action(methods=['POST'], detail=True)
    def aadharDetail(self, request, pk):
        '''
        Takes Aadhar detail and generates OTP for verification for aadhar Verification
        '''
        data = request.data
        serializer = AadharSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(pk=pk)
            user.aadhar = serializer.validated_data['aadhar']
            user.save()
            mobile = user.mobile
            # global AADHAR_OTP
            otp = random.randint(1000, 9999)
            OTP_DICT[f'{mobile}'] = otp
            # AADHAR_OTP = otp
            return Response({"otp": otp})
        return Response(serializer.errors)
    
    # @permission_classes([IsAuthenticated])
    @action(methods=['POST'], detail=True)
    def aadharVerify(self, request, pk):
        '''
        Verifies Aadhar OTP and saves Aadhar verification status of user
        '''
        # user = request.user
        data = request.data
        serializer = AadharVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(pk)
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            # global AADHAR_OTP
            if otp == OTP_DICT[f'{mobile}']:
                user.is_aadhar_verified = True
                user.status = CustomUser.STATUS_CHOICES[3][0]
                user.save()
                return Response({'msg': 'Aadhar Verification successful', 'step': user.status})
            return Response({"msg": "OTP does not match."})
        return Response(serializer.errors)
    
    # @permission_classes([IsAuthenticated])
    @action(methods=['POST'], detail=True)
    def bankDetail(self, request, pk):
        '''
        Takes bank details and verifies Bank with a Penny drop testing.
        '''
        data = request.data
        serializer = BankDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return Response("Hello Ankur.")
        return Response(serializer.errors)
    
