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
    
    def create(self, request):
        return Response("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request):
        return Response("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def retrieve(self, request):
        return Response("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self, request):
        return Response("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        '''
        Login API accepts phone number and otp validates and sends response accordingly.
        '''
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
                if user.status != CustomUser.STATUS_CHOICES[4][0]:
                    verification = f'{user.status}'.replace('_', ' ')
                    return Response({"id": user.id, "token": token, "message": f"Kindly complete your registration from {verification}", "step": user.status}, status=status.HTTP_200_OK)
                return Response({"id": user.id, "token": token, 'message':'Login Successful.', "status": user.status}, status=status.HTTP_200_OK)
            return Response({"message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def getOtp(self, request):
        '''
        Takes mobile number and generates OTP and returns User Id and OTP in response.
        '''
        data = request.data
        print(data)
        # global OTP
        serializer = GetOTPSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile=serializer.validated_data['mobile']
            otp = random.randint(100000, 999999)
            OTP_DICT[f'{mobile}'] = otp
            print(OTP_DICT[f'{mobile}'])
            return Response({"message": f"Your OTP is {otp}."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False)
    def registerApi(self, request):
        '''
        Verifies OTP for the given mobile number and return registration status and auth tokens in response if OTP matches
        else returns response accordingly.
        '''
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            mobile = serializer.validated_data['mobile']
            # global OTP
            if f'{mobile}' in OTP_DICT:
                print(OTP_DICT[f'{mobile}'])
                if OTP_DICT[f'{mobile}'] == otp:
                    instance = User.objects.filter(mobile=mobile).exists()
                    print(instance)
                    if instance:
                        user = User.objects.get(mobile=mobile)
                        print(user)
                        verification = f'{user.status}'.replace('_',' ')
                        token = get_tokens_for_user(user)
                        return Response({"id": user.id, "token": token, "message": f"User Already exists. Kindly continue with {verification}", "step": user.status}, status=status.HTTP_200_OK)
                    user = User.objects.create(username=mobile, mobile=mobile, is_mobile_verified=True, status=CustomUser.STATUS_CHOICES[1][0])
                    # user = User.objects.get(pk=pk)
                    # if user.status == CustomUser.STATUS_CHOICES[0][0]:
                    user.is_mobile_verified = True
                    # user.tnc = True
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
                    return Response({"id": id, "message": "OTP Verified", "step": user.status, "token": token}, status=status.HTTP_200_OK)
                return Response({"message": "OTP does not match."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Please generate OTP first."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

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
        elif self.action == 'bankDetail':
            return BankDetailSerializer
        else:
            return UserSerializer

    @action(methods=['POST'], detail=True)
    def panDetail(self, request, pk):
        '''
        Takes PAN number and obtains response from PAN database if matches return owner Name in response
        '''
        # user = request.user
        data = request.data
        serializer = PanSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            pan = serializer.validated_data['pan']
            pan_already_exists = User.objects.filter(pan=pan).exists()
            if pan_already_exists:
                return Response({'message': 'PAN is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            # user = User.objects.get(id=request.user.id)
            # user = User.objects.get(pk=pk)
            # user.pan = serializer.validated_data['pan']
            # user.save()
            return Response({"name": "Your Name", "message": "PAN Details Successfully fetched."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def panVerify(self, request, pk):
        '''
        Takes response and saves PAN verification status of user
        '''
        # user = request.user
        data = request.data
        serializer = PanVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # user = User.objects.get(id=request.user.id)
            user = User.objects.get(pk=pk)
            pan = serializer.validated_data['pan']
            name = serializer.validated_data['name']
            is_verified = serializer.validated_data['is_verified']
            if is_verified == True:
                pan_already_exists = User.objects.filter(pan=pan).exists()
                if pan_already_exists:
                    return Response({'message': 'PAN is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                user.pan = pan
                user.name = name
                user.is_pan_verified = True
                user.status = CustomUser.STATUS_CHOICES[2][0]
                user.save()
                return Response({'message': 'PAN Verification successful', 'step': user.status})
            return Response({"message": "Please verify Name."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def aadharDetail(self, request, pk):
        '''
        Takes Aadhar detail and generates OTP for verification for aadhar Verification
        '''
        data = request.data
        serializer = AadharSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            aadhaar = serializer.validated_data['aadhaar']
            aadhaar_already_exists = User.objects.filter(aadhaar=aadhaar).exists()
            if aadhaar_already_exists:
                return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            otp = random.randint(100000, 999999)
            OTP_DICT[f'{aadhaar}'] = otp
            return Response({"message": "OTP sent successfully.", "otp": otp})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
            user = User.objects.get(pk=pk)
            aadhaar = serializer.validated_data['aadhaar']
            otp = serializer.validated_data['otp']
            # global AADHAR_OTP
            if otp == OTP_DICT[f'{aadhaar}']:
                aadhaar_already_exists = User.objects.filter(aadhaar=aadhaar).exists()
                if aadhaar_already_exists:
                    return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                user.aadhaar = aadhaar
                user.is_aadhar_verified = True
                user.status = CustomUser.STATUS_CHOICES[3][0]
                user.save()
                return Response({'message': 'Aadhar Verification successful', 'step': user.status})
            return Response({"message": "OTP does not match."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def bankDetail(self, request, pk):
        '''
        Takes bank details and verifies Bank with a Penny drop testing.
        '''
        data = request.data
        serializer = BankDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            if 'bank' in serializer.validated_data and 'bank_acc' in serializer.validated_data:
                return Response({"message": "Hello Ankur."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @action(methods=['POST'], detail=True)
    # def bankVerify(self, request, pk):
    #     data = request.data
