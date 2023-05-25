from django.shortcuts import render
import random
from utility.otputility import *
from apps.mauth.models import CustomUser
from django.contrib.auth import authenticate, logout
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser as User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    
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
        elif self.action == 'dedup':
            return DedupSerializer
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
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            instance = User.objects.filter(mobile=mobile).exists()
            if instance:
                if mobile in OTP_DICT and OTP_DICT[f'{mobile}'] == otp:
                    user = User.objects.get(mobile=mobile)
                    # if user.status == CustomUser.STATUS_CHOICES[4][0]:
                    token = get_tokens_for_user(user)
                    if user.status == CustomUser.STATUS_CHOICES[4][0]:
                        return Response({"id": user.id, "token": token, 'message':'Login Successful.', 'message': 'Login Successful.', "step": user.status}, status=status.HTTP_200_OK)
                    verification = f'{user.status}'.replace('_', ' ')
                    return Response({"id": user.id, "token": token, "message": f"Kindly complete your registration from {verification}", "step": user.status}, status=status.HTTP_200_OK)
                return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "User does not exist.", "step": CustomUser.STATUS_CHOICES[0][0]}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def getOtp(self, request):
        '''
        Takes mobile number and generates OTP and returns User Id and OTP in response.
        '''
        data = request.data
        print(data)
        # global OTP
        serializer = self.get_serializer(data=data)
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
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            is_tnc_accepted = serializer.validated_data['is_tnc_accepted']
            mobile = serializer.validated_data['mobile']
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
                    if is_tnc_accepted != True:
                        return Response({"message": "Please accept Terms & Conditions."}, status=status.HTTP_400_BAD_REQUEST)
                    user = User.objects.create(username=mobile, mobile=mobile, is_mobile_verified=True, is_tnc_accepted=is_tnc_accepted, status=CustomUser.STATUS_CHOICES[1][0])
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

    @action(methods=['POST'], detail=False)
    def dedup(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile_exist = User.objects.filter(mobile=serializer.validated_data['mobile']).exists()
            email_exist = User.objects.filter(email=serializer.validated_data['email']).exists()
            pan_exist = User.objects.filter(pan=serializer.validated_data['pan']).exists()
            aadhaar_exist = User.objects.filter(aadhaar=serializer.validated_data['aadhaar']).exists()
            bank_acc_exist = User.objects.filter(bank_acc=serializer.validated_data['bank_acc']).exists()

            response = dict()

            if mobile_exist:
                response['mobile'] = "Mobile Number already exist."
            if email_exist:
                response['email'] = "Email already exist."
            if pan_exist:
                response['pan'] = "PAN Number already exist."
            if aadhaar_exist:
                response['aadhaar'] = "AADHAAR Number already exist."
            if bank_acc_exist:
                response['bank_acc'] = "Bank account already exist."

            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.filter(role=CustomUser.ROLE_CHOICES[0][0])
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
        elif self.action == 'getEmailOtp':
            return EmailDetailSerializer
        elif self.action == 'verifyEmail':
            return EmailVerifySerializer
        elif self.action == 'uploadSelfie':
            return SelfieUploadSerializer
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
                user.pan_name = name
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
            return Response({"message": "OTP sent to AADHAAR registered mobile number.", "otp": otp})
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
            # name = serializer.validated_data['name']
            otp = serializer.validated_data['otp']
            # global AADHAR_OTP
            if otp == OTP_DICT[f'{aadhaar}']:
                aadhaar_already_exists = User.objects.filter(aadhaar=aadhaar).exists()
                if aadhaar_already_exists:
                    return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                # if user.pan_name != name:
                #     return Response({'message': 'Aadhaar name doesn\'t match with PAN name.'}, status=status.HTTP_400_BAD_REQUEST)
                user.aadhaar = aadhaar
                # user.aadhaar_name = name
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
        # print("Validating Serializer")
        if serializer.is_valid(raise_exception=True):
            # print("Serializer Validated")
            if 'acc_holder_name' in serializer.validated_data and 'bank_acc' in serializer.validated_data and 'bank_ifsc' in serializer.validated_data:
                # print("Getting User object.")
                acc_holder_name = serializer.validated_data['acc_holder_name']
                bank_acc = serializer.validated_data['bank_acc']
                bank_ifsc = serializer.validated_data['bank_ifsc']
                # Match the name here
                user = User.objects.get(pk=pk)
                user.acc_holder_name = acc_holder_name
                # user.account_holder_name = 'Name'
                user.bank_acc = bank_acc
                user.bank_ifsc = bank_ifsc
                user.status = CustomUser.STATUS_CHOICES[4][0]
                user.save()
                return Response({"message": "Account Verified", "step": user.status}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def getEmailOtp(self, request, pk):
        data = request.data
        serializer = EmailDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            otp = random.randint(100000, 999999)
            EMAIL_OTP[f'{email}'] = otp
            return Response({"message": f"OTP for email verification is {otp}"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def verifyEmail(self, request, pk):
        data = request.data
        serializer = EmailVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            if f'{email}' in EMAIL_OTP and EMAIL_OTP[f'{email}'] == otp:
                user = User.objects.get(pk=pk)
                user.email = email
                user.is_email_verified = True
                user.save()
                del EMAIL_OTP[f'{email}']
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid OTP. Please enter valid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def uploadSelfie(self, request, pk):
        '''
        API for uploading selfie.
        '''
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = User.objects.get(pk=pk)
            instance.selfie = serializer.validated_data['selfie']
            instance.save()
            return Response({"message": "Image uploaded successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AggregatorViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        # queryset = User.objects.filter(role=CustomUser.ROLE_CHOICES[1][0])
        user = self.request.user
        queryset = User.objects.filter(aggregator=user)
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        return UserSerializer   
    
    @action(methods=['POST'], detail=False)
    def login(self, request):
        '''
        API for Aggregator Login.
        '''
        data = request.data
        serializer = LogInSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = User.objects.filter(mobile=serializer.validated_data['mobile']).exists()
            if instance:
                user = User.objects.get(username=serializer.validated_data['mobile'])
                if user.role == CustomUser.ROLE_CHOICES[1][0]:
                    token = get_tokens_for_user(user)
                    return Response({"message": "Login successful.", "id": user.id, "token": token}, status=status.HTTP_200_OK)
                return Response({"message": "User is not an Aggregator."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Invalid credentials."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors)

    @action(methods=['POST'], detail=False)
    def investors(self, request):
        user = request.user
        queryset = User.objects.filter(aggregator=user)
        serializer = UserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False)
    def registerInvestor(self, request):
        '''
        API for registering Investor.
        '''
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile_exist = User.objects.filter(mobile=serializer.validated_data['mobile']).exists()
            email_exist = User.objects.filter(email=serializer.validated_data['email']).exists()
            pan_exist = User.objects.filter(pan=serializer.validated_data['pan']).exists()
            aadhaar_exist = User.objects.filter(aadhaar=serializer.validated_data['aadhaar']).exists()
            bank_acc_exist = User.objects.filter(bank_acc=serializer.validated_data['bank_acc']).exists()

            if mobile_exist:
                return Response({"message": "Mobile Number already exist."})
            if email_exist:
                return Response({"message": "Email already exist."})
            if pan_exist:
                return Response({"message": "PAN Number already exist."})
            if aadhaar_exist:
                return Response({"message": "AADHAAR Number already exist."})
            if bank_acc_exist:
                return Response({"message": "Bank account already exist."})
            
            instance = User.objects.create(username=serializer.validated_data['mobile'])
            instance.name = serializer.validated_data['name']
            instance.mobile = serializer.validated_data['mobile']
            instance.email = serializer.validated_data['email']
            instance.gender = serializer.validated_data['gender']
            instance.address = serializer.validated_data['address']
            instance.pan = serializer.validated_data['pan']
            instance.aadhaar = serializer.validated_data['aadhaar']
            instance.bank_acc = serializer.validated_data['bank_acc']
            instance.bank_ifsc = serializer.validated_data['bank_ifsc']
            instance.role = CustomUser.ROLE_CHOICES[0][0]
            instance.aggregator = request.user
            instance.save()
            return Response({"message": "Investor registered successfully.", "investor": instance}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.action == 'linkInvestor':
            return User.objects.filter(role=CustomUser.ROLE_CHOICES[1][0])
        elif self.action == 'listInvestor':
            return User.objects.filter(role=CustomUser.ROLE_CHOICES[0][1])
        else:
            return User.objects.filter(is_superuser=True)
    
    def get_serializer_class(self):
        if self.action == 'linkInvestor':
            return LinkInvestorSerializer
        if self.action == 'registerAggregator':
            return AggregatorRegistrationSerializer
        return UserSerializer
    
    @action(methods=['POST'], detail=True)
    def linkAggregator(self, request, pk):
        '''
        Links Investigator to an Aggregator.
        '''
        data = request.data
        serializer = LinkAggregatorSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = User.objects.get(pk=pk)
            instance.aggregator = serializer.validated_data['aggregator']
            instance.save()
            return Response({"message": "Investor linked successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=False)
    def registerAggregator(self, request):
        '''
        API for registering Aggregator.
        '''
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile_exist = User.objects.filter(mobile=serializer.validated_data['mobile']).exists()
            email_exist = User.objects.filter(email=serializer.validated_data['email']).exists()
            pan_exist = User.objects.filter(pan=serializer.validated_data['pan']).exists()
            aadhaar_exist = User.objects.filter(aadhaar=serializer.validated_data['aadhaar']).exists()
            bank_acc_exist = User.objects.filter(bank_acc=serializer.validated_data['bank_acc']).exists()

            if mobile_exist:
                return Response({"message": "Mobile Number already exist."})
            if email_exist:
                return Response({"message": "Email already exist."})
            if pan_exist:
                return Response({"message": "PAN Number already exist."})
            if aadhaar_exist:
                return Response({"message": "AADHAAR Number already exist."})
            if bank_acc_exist:
                return Response({"message": "Bank account already exist."})
            
            instance = User.objects.create(username=serializer.validated_data['mobile'])
            instance.name = serializer.validated_data['name']
            instance.mobile = serializer.validated_data['mobile']
            instance.email = serializer.validated_data['email']
            instance.gender = serializer.validated_data['gender']
            instance.address = serializer.validated_data['address']
            instance.pan = serializer.validated_data['pan']
            instance.aadhaar = serializer.validated_data['aadhaar']
            instance.bank_acc = serializer.validated_data['bank_acc']
            instance.bank_ifsc = serializer.validated_data['bank_ifsc']
            instance.role = CustomUser.ROLE_CHOICES[1][0]
            instance.save()
            return Response({"message": "Aggregator registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

