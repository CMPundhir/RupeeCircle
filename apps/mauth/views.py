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
from rest_framework.decorators import action

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # serializer_class = UserSerializer

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'getOtp':
            return GetOTPSerializer
        elif self.action == 'verifyOtp':
            return VerifyOTPSerializer
        elif self.action == 'panDetail':
            return PanSerializer
        elif self.action == 'panVerify':
            return PanVerifySerializer
        elif self.action == 'aadharDetail':
            return AadharSerializer
        elif self.action == 'aadharVerify':
            return AadharVerifySerializer
        else:
            return UserSerializer

    @action(methods=['POST'], detail=False)
    def getOtp(self, request):
        '''
        This function takes phone number and generates OTP and returns User Id and OTP in response.
        '''
        data = request.data
        # global OTP
        serializer = GetOTPSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            phone=serializer.validated_data['phone']
            user = User.objects.filter(phone=phone).exists()
            if user:
                otp = random.randint(1000, 9999)
                # OTP = otp
                OTP_DICT[f'{phone}'] = otp
                id = user.id
                return Response({"id": id, "otp": f"Your OTP is {otp}."})
            else:
                User.objects.create(username=phone, phone=phone)
                otp = random.randint(1000, 9999)
                OTP_DICT[f'{phone}'] = otp
                # OTP = int(otp)
                return Response({f"Your OTP is {otp}."})
        return Response(serializer.errors)

    @action(methods=['POST'], detail=True)
    def verifyOtp(self, request):
        '''
        This method verifies OTP for the given mobile number and return registration status and auth tokens in response if OTP matches
        else returns response accordingly.
        '''
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            phone = serializer.validated_data['phone']
            # global OTP
            if OTP_DICT[f'phone'] == otp:
                user = User.objects.get(phone=phone)
                if user.is_active == CustomUser.STATUS_CHOICES[0]:
                    user.is_phone_verified = True
                    user.status = CustomUser.STATUS_CHOICES[1][0]
                    user.save()
                    del OTP_DICT[f'phone']
                    # return Response({"msg": "OTP Verified", "step": user.is_active})
                # try:
                #     user = User.objects.get(phone=phone)
                # except:
                #     user = User.objects.create(username=phone, phone=phone)
                token = get_tokens_for_user(user)
                return Response({"msg": "OTP Verified", "step": user.status, "token": token}, status=status.HTTP_200_OK)
            return Response("OTP does not match.", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages)
    
    @action(methods=['POST'], detail=True)
    def panDetail(self, request):
        '''
        Takes PAN number and obtains response from PAN database if matches return owner Name in response
        '''
        # user = request.user
        data = request.data
        serializer = PanSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(phone=request.data['phone'])
            user.pan = serializer.validated_data['pan']
            user.save()
            return Response({"Name": "Your Name"})
        return Response(serializer.errors)
    
    @action(methods=['POST'], detail=True)
    def panVerify(self, request):
        '''
        Takes boolean response and saves PAN verification status of user
        '''
        # user = request.user
        data = request.data
        serializer = PanVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(phone=request.data['phone'])
            is_verified = serializer.validated_data['is_verified']
            if is_verified == True:
                user.is_pan_verified = True
                user.status = CustomUser.STATUS_CHOICES[2][0]
                user.save()
                return Response({'msg': 'PAN Verification successful', 'step': user.status})
            return Response({"msg": "Please verify Name."})
        return Response(serializer.errors)
            
    @action(methods=['POST'], detail=True)
    def aadharDetail(self, request):
        '''
        Takes Aadhar detail and generates OTP for verification for aadhar Verification
        '''
        data = request.data
        serializer = AadharSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(phone=request.data['phone'])
            user.aadhar = serializer.validated_data['aadhar']
            user.save()
            phone = user.phone
            # global AADHAR_OTP
            otp = random.randint(1000, 9999)
            OTP_DICT[f'{phone}'] = otp
            # AADHAR_OTP = otp
            return Response({"otp": otp})
        return Response(serializer.errors)
    
    @action(methods=['POST'], detail=True)
    def aadharVerify(self, request):
        '''
        Verifies Aadhar OTP and saves Aadhar verification status of user
        '''
        # user = request.user
        data = request.data
        serializer = AadharVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(phone=request.data['phone'])
            otp = serializer.validated_data['otp']
            global AADHAR_OTP
            if otp == AADHAR_OTP:
                user.is_aadhar_verified = True
                user.status = CustomUser.STATUS_CHOICES[3][0]
                user.save()
                return Response({'msg': 'Aadhar Verification successful', 'step': user.status})
            return Response({"msg": "OTP does not match."})
        return Response(serializer.errors)
           