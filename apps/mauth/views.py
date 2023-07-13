from django.shortcuts import render
import random, requests, json
import smtplib
from utility.name_verification import match_name
from smtplib import SMTPException
from utility.otputility import *
from apps.mauth.models import CustomUser
from apps.loans.models import InvestmentProduct
from apps.wallet.models import Wallet
# from apps.dashboard.models import Wallet
from django.contrib.auth import authenticate, logout
from apps.wallet.models import BankAccount, Transaction
from apps.notification.services import LogService
from .serializers import *
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
# from .models import CustomUser as User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from utility.sms_email_utils import *
import os
from dotenv import load_dotenv


load_dotenv()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = CustomUser.objects.all()
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
            instance = CustomUser.objects.filter(mobile=mobile).exists()
            if instance:
                if mobile in OTP_DICT and OTP_DICT[f'{mobile}'] == otp:
                    user = CustomUser.objects.get(mobile=mobile)
                    # if user.status == CustomUser.STATUS_CHOICES[4][0]:
                    token = get_tokens_for_user(user)
                    if user.status == CustomUser.STATUS_CHOICES[4][0]:
                        return Response({"id": user.id, "token": token, 'message':'Login Successful.', 'message': 'Login Successful.', "step": user.status}, status=status.HTTP_200_OK)
                    verification = f'{user.status}'.replace('_', ' ')
                    return Response({"id": user.id, "token": token, "message": f"Kindly complete your registration from {verification}", "step": user.status}, status=status.HTTP_200_OK)
                return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "User does not exist. Please Register First.", "step": CustomUser.STATUS_CHOICES[0][0]}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def getOtp(self, request):
        '''
        Takes mobile number and generates OTP and returns User Id and OTP in response.
        '''
        data = request.data
        # global OTP
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data['type'] == "LOGIN":
                if "mobile" in serializer.validated_data and serializer.validated_data['mobile']:
                    mobile = serializer.validated_data['mobile']
                    user_exist = User.objects.filter(mobile=mobile).exists()
                    if not user_exist:
                        return Response({"message": "User not Registered"}, status=status.HTTP_400_BAD_REQUEST)
                    data = sendMobileOtp(mobile)
                    return Response({"message": "Otp Send Successfully", "POT": f"{int(data['otp']%100)}{int(data['otp']/100)}" })
                else:
                    return Response({"message": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)
            elif serializer.validated_data['type'] == "REGISTER":    
                mobile = None
                email = None
                
                if "mobile" in serializer.validated_data and serializer.validated_data['mobile']:
                    mobile=serializer.validated_data['mobile']
                if "email" in serializer.validated_data and serializer.validated_data['email']:
                    email = serializer.validated_data['email']
                if not mobile and not email:
                    return Response({"message": "Phone number or email required"}, status=status.HTTP_400_BAD_REQUEST)
                mob_data = None
                if mobile:
                    mob_data = sendMobileOtp(mobile)
                email_data = None
                if email:
                    email_data = sendEmailOtp(email)
                return Response({"message": "Success", "mob": mob_data, "email": email_data}, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False)
    def registerApi(self, request):
        '''
        Verifies OTP for the given mobile number and return registration status and auth tokens in response if OTP matches
        else returns response accordingly.
        '''
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            otp = serializer.validated_data['otp']
            is_tnc_accepted = serializer.validated_data['is_tnc_accepted']
            role = serializer.validated_data['role']
            mobile = serializer.validated_data['mobile']
            email = None
            email_otp = None
            if "email" in serializer.validated_data and serializer.validated_data['email']:
                email = serializer.validated_data['email']
                if "email_otp" in serializer.validated_data and serializer.validated_data['email_otp']:
                    email_otp = serializer.validated_data['email_otp']
                else:
                    return Response({"message": "Please Enter EMail OTP as well"}, status=status.HTTP_400_BAD_REQUEST)
            if f'{mobile}' in OTP_DICT and OTP_DICT[f'{mobile}'] == otp and (not email or f'{email}' in EMAIL_DICT and EMAIL_DICT[f'{email}'] == email_otp):
                mobile_exist = CustomUser.objects.filter(mobile=mobile).exists()
                if mobile_exist:
                    user = CustomUser.objects.get(mobile=mobile)
                    print(user)
                    verification = f'{user.status}'.replace('_',' ')
                    token = get_tokens_for_user(user)
                    user.email = email
                    user.is_email_verified = True
                    user.save()
                    return Response({"id": user.id, "token": token, "message": f"User Already exists. Kindly continue with {verification}", "step": user.status}, status=status.HTTP_200_OK)
                    # return Response({"message": "User exist with this mobile number."}, status=status.HTTP_400_BAD_REQUEST)
                if email:
                    email_exist = CustomUser.objects.filter(email=email).exists()
                    if email_exist:
                        return Response({"message": "Email ID already registered with other user"}, status=status.HTTP_400_BAD_REQUEST)
                if is_tnc_accepted != True:
                    return Response({"message": "Please accept Terms & Conditions."}, status=status.HTTP_400_BAD_REQUEST)
                if email: 
                    user = CustomUser.objects.create(username=mobile, 
                                                    mobile=mobile,
                                                    email=email,
                                                    is_email_verified=True, 
                                                    is_mobile_verified=True, 
                                                    is_tnc_accepted=is_tnc_accepted, 
                                                    status=CustomUser.STATUS_CHOICES[1][0],
                                                    role=role)
                else:
                    user = CustomUser.objects.create(username=mobile, 
                                                    mobile=mobile,
                                                    is_mobile_verified=True, 
                                                    is_tnc_accepted=is_tnc_accepted, 
                                                    status=CustomUser.STATUS_CHOICES[1][0],
                                                    role=role)
                try:
                    DocumentVerificationResponse.objects.create(owner=user)
                except Exception as e:
                    print("DocumentVerificationResponse.objects.create(owner=user) error => ",e.message)
                token = get_tokens_for_user(user)
                return Response({"id": user.id, "message": "OTP Verified", "step": user.status, "token": token}, status=status.HTTP_200_OK)
            return Response({"message": "Email or Mobile OTP doesn't match"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['POST'], detail=False)
    def dedup(self, request):
        '''
        API verifies whether user detail already exists.
        '''
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile_exist = CustomUser.objects.filter(mobile=serializer.validated_data['mobile']).exists()
            email_exist = CustomUser.objects.filter(email=serializer.validated_data['email']).exists()
            pan_exist = CustomUser.objects.filter(pan=serializer.validated_data['pan']).exists()
            aadhaar_exist = CustomUser.objects.filter(aadhaar=serializer.validated_data['aadhaar']).exists()
            bank_acc_exist = CustomUser.objects.filter(bank_acc=serializer.validated_data['bank_acc']).exists()

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
    
    @action(methods=['GET'], detail=False)
    def getRoles(self, request):
        result = [i[1] for i in CustomUser.ROLE_CHOICES[0:3]]
        print(result)
        return Response(result)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['first_name', 'mobile', 'email', 'pan', 'aadhaar', 'bank_acc', 'role', 'partner']
    ordering_fields = ['id']
    filterset_fields = ['role', 'partner', 'mobile']

    def get_queryset(self):
        user = self.request.user
        # queryset = User.objects.filter(pk=self.request.user.id)
        if user.role == CustomUser.ROLE_CHOICES[3][1]:
            queryset = CustomUser.objects.all().order_by('-id')
        else:
            queryset = CustomUser.objects.filter(id=user.id).order_by('-id')
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'panDetail' or self.action == 'myIpTest':
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
        elif self.action == 'updateRisk':
            return RiskLogSerializer
        else:
            return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        balance = Wallet.objects.filter(owner=instance)
        serializer.data['balance'] = balance
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def myIpTest(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)       
        data = {"access_token": "FuGUrmePylKM3jDp",
                "firstname": "",
                "middlename": "",
                "lastname": "", 
                "panId": serializer.validated_data['pan']}
        r = requests.post(url="https://www.rupeecircle.com/api/v4/vendor/ip", 
                          json=data,
                          headers={"app_version_code": "17", "device_type": "computer", "Content-Type": "application/json", "Cookie": "RupeeCircle=eyJpdiI6InhmOWhWOHdLeUJ1UVNSVHNpY2hDK3c9PSIsInZhbHVlIjoidldmYW9ScTVvVXVqT0JDNFlnbldlRmlBNVgyK2lscEhXZmlEbDJtYzhjWnlrRkJHYXVlRFZBZXRkampNeUxlMUdmSTJ0ZFIxcFJTRFQ2ektpbVpyTXc9PSIsIm1hYyI6ImY2ZWUwMzdlMGM4NmExN2ZkMjU2Yzk1ODVhMmQ1Mzg1OGI1NGZjN2I3NjMwNTM1MTY1ZDIyMDlkZmMxMDgzMWIifQ%3D%3D; AWSALB=WBdG3GfUaTWPbNMTywpA66A6v/wrLvBkiCQcUQcEcS3N2pQTxQI5v/GTjq4TnO2WVZOoNedB4Tm5eGjvFvoqE1UhK5xscji/0y5iGChV0Lyo5V6BWXPHR1Lb8BvZ; AWSALBCORS=WBdG3GfUaTWPbNMTywpA66A6v/wrLvBkiCQcUQcEcS3N2pQTxQI5v/GTjq4TnO2WVZOoNedB4Tm5eGjvFvoqE1UhK5xscji/0y5iGChV0Lyo5V6BWXPHR1Lb8BvZ"})
        # res = r.json()
        print(r.content)
        return Response({"message": "Success", "res": r})

    @action(methods=['POST'], detail=True)
    def panDetail(self, request, pk):
        '''
        Takes PAN number and obtains response from PAN database if matches return owner Name in response
        '''
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user and user.pan and user.pan == request.data['pan']:
            print("pan already saved => ", user.pan)
        else:   
            pan_exist = User.objects.filter(pan=serializer.validated_data['pan']).exclude(id=user.id).exists()
            print("pan_exist => ", pan_exist)
            if pan_exist:
                return Response({"message": "PAN already exists."}, status=status.HTTP_400_BAD_REQUEST)
        data = {"access_token": "FuGUrmePylKM3jDp",
                "firstname": "",
                "middlename": "",
                "lastname": "", 
                "panId": serializer.validated_data['pan']}
        # data = json.load({
        # "access_token":"9dECoXkSlurJQs8C",
        # "panId": "AAIPM3854E"
        # })
        instance = self.get_object()
        r = requests.post(url="https://www.rupeecircle.com/api/v4/nsdl-pan-verification", 
                          json=data,
                          headers={"app_version_code": "17", "device_type": "computer", "Content-Type": "application/json", "Cookie": "RupeeCircle=eyJpdiI6InhmOWhWOHdLeUJ1UVNSVHNpY2hDK3c9PSIsInZhbHVlIjoidldmYW9ScTVvVXVqT0JDNFlnbldlRmlBNVgyK2lscEhXZmlEbDJtYzhjWnlrRkJHYXVlRFZBZXRkampNeUxlMUdmSTJ0ZFIxcFJTRFQ2ektpbVpyTXc9PSIsIm1hYyI6ImY2ZWUwMzdlMGM4NmExN2ZkMjU2Yzk1ODVhMmQ1Mzg1OGI1NGZjN2I3NjMwNTM1MTY1ZDIyMDlkZmMxMDgzMWIifQ%3D%3D; AWSALB=WBdG3GfUaTWPbNMTywpA66A6v/wrLvBkiCQcUQcEcS3N2pQTxQI5v/GTjq4TnO2WVZOoNedB4Tm5eGjvFvoqE1UhK5xscji/0y5iGChV0Lyo5V6BWXPHR1Lb8BvZ; AWSALBCORS=WBdG3GfUaTWPbNMTywpA66A6v/wrLvBkiCQcUQcEcS3N2pQTxQI5v/GTjq4TnO2WVZOoNedB4Tm5eGjvFvoqE1UhK5xscji/0y5iGChV0Lyo5V6BWXPHR1Lb8BvZ"})
        res = r.json()
        print(r.content)
        if res['flag'] == True:
            instance.pan = res['data']['pan']
            instance.pan_name = res['data']['name']
            instance.first_name = res['data']['name']
            instance.is_pan_verified = True
            api_response = DocumentVerificationResponse.objects.get(owner=user)
            api_response.pan_response = f"{res}"
            api_response.save()
            instance.pan_api_response = f"{res}"
            user.status = CustomUser.STATUS_CHOICES[2][0]
            instance.save()
            return Response({"message": "Success", "name": res['data']['name']})
        else:
            print(request.data)
            print(res)
            return Response({"message": "Failed", "response": res}, status=status.HTTP_403_FORBIDDEN)
        # Above is PAN integration
        serializer = PanSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            pan = serializer.validated_data['pan']
            pan_already_exists = CustomUser.objects.filter(pan=pan).exists()
            if pan_already_exists:
                return Response({'message': 'PAN is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            # user = CustomUser.objects.get(id=request.user.id)
            # user = CustomUser.objects.get(pk=pk)
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
            # user = CustomUser.objects.get(id=request.user.id)
            user = CustomUser.objects.get(pk=pk)
            # pan = serializer.validated_data['pan']
            # name = serializer.validated_data['name']
            is_verified = serializer.validated_data['is_verified']
            if is_verified == True:
                # pan_already_exists = CustomUser.objects.filter(pan=pan).exists()
                # if pan_already_exists:
                #     return Response({'message': 'PAN is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                # user.pan = pan
                # user.pan_name = name
                # user.first_name = name
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
        user = request.user
        data = request.data
        serializer = AadharSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            aadhaar = serializer.validated_data['aadhaar']
            aadhaar_already_exists = CustomUser.objects.filter(aadhaar=aadhaar).exclude(id=user.id).exists()
            if aadhaar_already_exists:
                return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            headers = {"Content-Type": "application/json", "Authorization": "OXX3dFnFsQRwsOb6gU9jDLNpHACUhX5B"}
            res = requests.post(url='https://api.signzy.app/api/v3/getOkycOtp', json={"aadhaarNumber": aadhaar}, headers=headers)
            r = res.json()
            api_response = DocumentVerificationResponse.objects.get(owner=user)
            api_response.aadhaar_response = f"{r}"
            api_response.save()
            print("aadharDetail => ", r)
            # otp = random.randint(100000, 999999)
            # OTP_DICT[f'{aadhaar}'] = otp
            # print(otp)
            return Response({"message": "OTP sent to AADHAAR registered mobile number.", "requestId": r['data']['requestId']})
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
            # user = CustomUser.objects.get(id=request.user.id)
            user = CustomUser.objects.get(pk=pk)
            aadhaar = serializer.validated_data['aadhaar']
            request_id = serializer.validated_data['request_id']
            otp = serializer.validated_data['otp']
            # global AADHAR_OTP
            # Checking aadhar already exist.

            # if otp == OTP_DICT[f'{aadhaar}']:
            aadhaar_already_exists = CustomUser.objects.filter(aadhaar=aadhaar).exclude(id=user.id).exists()
            if aadhaar_already_exists:
                return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            headers = {"Authorization": "OXX3dFnFsQRwsOb6gU9jDLNpHACUhX5B", "Content-Type": "application/json"}
            data = {"requestId": request_id, "otp": otp}
            response = requests.post(url='https://api.signzy.app/api/v3/fetchOkycData', json=data, headers=headers)
            
            print(f"---------------------------------------- Request starts ----------------------------------------")
            print('response.request => ',response.request)
            print('response.request.url => ', response.request.url)
            print('response.request.body => ', response.request.body)
            print('response.request.headers => ', response.request.headers)
            print(f"---------------------------------------- Request ENDS ----------------------------------------")

            res = response.json()
            if res and 'statusCode' in res and res['statusCode']==200:

                # Matching Aadhaar name with PAN name

                # pan_name = user.first_name
                # if 'data' in res:
                #     aadhar_data = res['data']
                #     if 'full_name' in aadhar_data and aadhar_data['full_name']:
                #         is_name_matching = match_name(pan_name, aadhar_data['full_name'])
                #         if not is_name_matching:
                #             return Response({"message": f"Aadhaar name {aadhar_data['full_name']} doesn't match PAN name {pan_name}"}, status=status.HTTP_400_BAD_REQUEST)
                # else:
                #     return Response({"message": "Could not fetch name from Aadhar details."}, status=status.HTTP_204_NO_CONTENT)

                user.is_aadhaar_verified = True
                user.status = CustomUser.STATUS_CHOICES[3][0]
            else:
                user.is_aadhaar_verified = False
            user.aadhaar = aadhaar
            api_response = DocumentVerificationResponse.objects.get(owner=user)
            api_response.aadhaar_response += f"{res}"
            api_response.save()
            user.aadhaar_verify_data = f'{res}'
            user.save()
            #JUST
            if user.is_aadhaar_verified:
                return Response({'message': res['message'], 'step': user.status})
            else:
                return Response({'message': res['message'], 'step': user.status, "res": res}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': res['data']['status'], 'step': user.status})
            # return Response({"message": "OTP does not match."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def bankDetail(self, request, pk):
        '''
        Takes bank details and verifies Bank with a Penny drop testing.
        '''
        data = request.data
        user = request.user
        if not user: return Response({'message':"User not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_superuser and not user.is_bank_acc_verified: return Response({'message':"Bank Account already verified"}, status=status.HTTP_400_BAD_REQUEST)
        PENNY_DROP_PROD_TOKEN = os.getenv("PENNY_DROP_PROD_TOKEN")
        serializer = BankDetailSerializer(data=data)
        # print("PENNY_DROP_PROD_TOKEN => ", PENNY_DROP_PROD_TOKEN)
        # print("Validating Serializer")
        if serializer.is_valid(raise_exception=True):
            if serializer.is_valid(raise_exception=True):
                # print("Serializer Validated")
                if 'acc_holder_name' in serializer.validated_data and 'bank_acc' in serializer.validated_data and 'bank_ifsc' in serializer.validated_data:
                    # print("Getting User object.")
                    acc_holder_name = serializer.validated_data['acc_holder_name']
                    bank_acc = serializer.validated_data['bank_acc']
                    bank_ifsc = serializer.validated_data['bank_ifsc']
                    is_bank_acc_exists = BankAccount.objects.filter(acc_number=bank_acc).exclude(owner=user).exists()
                    if is_bank_acc_exists:
                        return Response({"message": "Bank account already exist with another user."}, status=status.HTTP_400_BAD_REQUEST)
                    if user.penny_trial_left <=-1 : return Response({'message':"Bank Verification limit exceeded ", "penny_trial_left":user.penny_trial_left}, status=status.HTTP_400_BAD_REQUEST)
                    user.penny_trial_left = user.penny_trial_left - 1
                    user.save()
                    # Integrate Penny Drop Api below
                    try:
                        wallet = Wallet.objects.create(owner=user)
                    except:
                        wallet = Wallet.objects.get(owner=user)
                    s = datetime.now()
                    traceId = f"T{wallet.id}{str(s).replace('-', '').replace(' ',  '').replace(':', '').replace('.', '')}"
                    transaction = Transaction.objects.create(owner=user, amount=1, wallet=wallet, debit=False, transaction_id=traceId)
                    bank_detail = {
                        "bankAccount": serializer.validated_data['bank_acc'], 
                        "ifsc": serializer.validated_data['bank_ifsc'],
                        "name": "", 
                        "phone": "",
                        # "traceId": "X738393937202"}
                        "traceId": traceId}
                    # url = 'https://sandbox.transxt.in/api/1.1/pennydrop'
                    url = 'https://auroapi.transxt.in/api/1.1/pennydrop'
                    headers = {
                        # "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiI0NjYiLCJzdWIiOiJ0cmFucyIsImlzcyI6IlRSQU5TWFQiLCJTRVNTSU9OSUQiOiIwIiwiU0VDUkVUIjoiIiwiUFJPRExJU1QiOltdLCJVU0VSSUQiOiIwIiwiUE9SVEFMIjoiIiwiRU5WIjoidWF0In0.uVpDCnsllwcYCyL44dTX5sHXtGYljRqXV06etoRfSerEa94f6oakN0e_rK0pE6HEOhvjHgA8xR89bamSxqGGzQ",
                        "Authorization": f"Bearer {PENNY_DROP_PROD_TOKEN}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(url, json=bank_detail, headers=headers)
                    print(f"---------------------------------------- Request starts ----------------------------------------")
                    print('response.request => ',response.request)
                    print('response.request.url => ', response.request.url)
                    print('response.request.body => ', response.request.body)
                    print('response.request.headers => ', response.request.headers)
                    print('response.text => ', response.text)
                    print(f"---------------------------------------- Request ENDS ----------------------------------------")
                    print(f"---------------------------------------- Reponse starts ----------------------------------------")
                    print('response.request => ',response.request)
                    print('response.request.url => ', response.request.url)
                    print('response.request.body => ', response.request.body)
                    print('response.request.headers => ', response.request.headers)
                    print('response.text => ', response.text)
                    print(f"---------------------------------------- Reponse ENDS ----------------------------------------")
                    try:
                        res = response.json()
                    except Exception as e:
                        return Response({"res": response.text}, status=status.HTTP_406_NOT_ACCEPTABLE)

                    print(f"This is your res => {res}")
                    # Above code is to check the request
                        
                    transaction.status = res['status']
                    if 'status' in res and res['status'] == 'SUCCESS':
                        # user.bank_acc = serializer.validated_data['bank_acc']
                        # user.bank_ifsc = serializer.validated_data['bank_ifsc']
                        # user.bank_name = res['data']['nameAtBank']
                        if 'data' in res:
                            data = res['data']
                            transaction.penny_drop_utr = data['utr'] if 'utr' in data and data['utr'] else ''
                            transaction.ref_id = data['refId'] if 'refId' in data and data['refId'] else ''
                            transaction.save()
                            if 'nameAtBank' in data and data['nameAtBank']:
                                nameAtBank = data['nameAtBank']
                                BankAccount.objects.create(owner=user, acc_number=serializer.validated_data['bank_acc'], 
                                                    ifsc=serializer.validated_data['bank_ifsc'],
                                                    is_primary=True)
                                user.status = CustomUser.STATUS_CHOICES[4][1]
                                user.is_bank_acc_verified = True
                                user.save()
                                return Response({"message": res['status'], "name": nameAtBank})
                            else:
                                return Response({"message": res['status'], "name": "Name Not found", "res": res}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            transaction.save()
                            return Response({"message": res['status'], "name": "Data Not found", "res": res}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if 'data' in res and res['data']:
                            data = res['data']
                            if 'ref_id' in data and data['ref_id']:
                                transaction.ref_id = res['data']['ref_id']
                            else:
                                transaction.ref_id = ''
                        transaction.save()
                        return Response({"message": res['message'] if 'message' in res else res['status'], "res" : res}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def getEmailOtp(self, request, pk):
        data = request.data
        serializer = EmailDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            otp = random.randint(100000, 999999)
            EMAIL_DICT[f'{email}'] = otp
            return Response({"message": f"OTP for email verification is {otp}"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True)
    def verifyEmail(self, request, pk):
        data = request.data
        serializer = EmailVerifySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            if f'{email}' in EMAIL_DICT and EMAIL_DICT[f'{email}'] == otp:
                user = CustomUser.objects.get(pk=pk)
                user.email = email
                user.is_email_verified = True
                user.save()
                del EMAIL_DICT[f'{email}']
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid OTP. Please enter valid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False)
    def count(self, request):
        investors = CustomUser.objects.filter(role=CustomUser.ROLE_CHOICES[0][1]).count()
        borrowers = CustomUser.objects.filter(role=CustomUser.ROLE_CHOICES[2][1]).count()
        partners = CustomUser.objects.filter(role=CustomUser.ROLE_CHOICES[1][1]).count()
        return Response({"investors": investors, "borrowers": borrowers, "partners": partners}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def addcs(self, request):
        borrowers = User.objects.filter(role=User.ROLE_CHOICES[2][1])
        for i in borrowers:
            i.credit_score = 600
            i.save()
        return Response({"message": "Done"})
    # @action(methods=['GET'], detail=False)
    # def updateSpecialPlan(self, request):
    #     queryset = self.get_queryset()
    #     for i in queryset:
    #         plan_exist = InvestmentProduct.objects.filter(allowed_investor=i).exists()
    #         if plan_exist:
    #             i.special_plan_exist = True
    #             i.save()
    #     return Response({"message": "Updated"})
    
    # @action(methods=['GET'], detail=False)
    # def addId(self, request):
    #     for i in CustomUser.objects.all():
    #         i.user_id = f'{i.role[0]}{i.id}'
    #         i.save()
    #     return Response({"message": "Added to all."})
    
    # @action(methods=['GET'], detail=False)
    # def updateBorrower(self, request):
    #     all_b = CustomUser.objects.filter(role=CustomUser.ROLE_CHOICES[2][1])
    #     for i in all_b:
    #         i.is_fixedroi_allowed = False
    #         i.is_anytime_withdrawal_allowed = False
    #         i.is_marketplace_allowed = True
    #         i.save()
    #     return Response({"message": "Done"})


class DocumentVerificationResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = DocumentVerificationResponse.objects.all()
        return queryset

    def get_serializer_class(self):
        return DocumentVerificationResponseSerializer
    
    @action(methods=['GET'], detail=False)
    def createall(self, request):
        user=request.user
        all_users = User.objects.all()
        for i in all_users:
            try:
                DocumentVerificationResponse.objects.get(owner=user)
            except:
                DocumentVerificationResponse.objects.create(owner=user)
        return Response({"message": "Created all."}, status=status.HTTP_200_OK)
    