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
        This function takes mobile number and generates OTP and returns User Id and OTP in response.
        '''
        data = request.data
        print(data)
        # global OTP
        serializer = GetOTPSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile=serializer.validated_data['mobile']
            try:
                instance = User.objects.filter(mobile=mobile)[0]
                print("Try")
            except:
                instance = User.objects.create(username=mobile, mobile=mobile)
                print("Except")
            # instance = User.objects.get(mobile=mobile)
            otp = random.randint(1000, 9999)
            # OTP = otp
            OTP_DICT[f'{mobile}'] = otp
            print(OTP_DICT[f'{mobile}'])
            print(instance)
            id = instance.id
            return Response({"id": id, "otp": f"Your OTP is {otp}."})
            # if user:
            #     instance = User.objects.get(mobile=mobile)
            #     otp = random.randint(1000, 9999)
            #     # OTP = otp
            #     OTP_DICT[f'{mobile}'] = otp
            #     id = instance.id
            #     return Response({"id": id, "otp": f"Your OTP is {otp}."})
            # else:
            #     instance = User.objects.create(username=mobile, mobile=mobile)
            #     otp = random.randint(1000, 9999)
            #     OTP_DICT[f'{mobile}'] = otp
            #     id = instance.id
            #     # OTP = int(otp)
            #     return Response({f"Your OTP is {otp}."})
        return Response(serializer.errors)

    @action(methods=['POST'], detail=True)
    def verifyOtp(self, request, pk):
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
                user = User.objects.get(pk=pk)
                if user.status == CustomUser.STATUS_CHOICES[0][0]:
                    user.is_mobile_verified = True
                    user.status = CustomUser.STATUS_CHOICES[1][0]
                    user.save()
                    del OTP_DICT[f'{mobile}']
                    # return Response({"msg": "OTP Verified", "step": user.is_active})
                # try:
                #     user = User.objects.get(mobile=mobile)
                # except:
                #     user = User.objects.create(username=mobile, mobile=mobile)
                token = get_tokens_for_user(user)
                return Response({"msg": "OTP Verified", "step": user.status, "token": token}, status=status.HTTP_200_OK)
            return Response("OTP does not match.", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages)
    
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
           