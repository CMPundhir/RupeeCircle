from django.shortcuts import render
import random, requests, json
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
        print(data)
        # global OTP
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            mobile=serializer.validated_data['mobile']
            otp = random.randint(100000, 999999)
            message = 'OTP for login into your RupeeCircle account is '+str(otp)+'.. Please do not share this OTP with anyone to ensure account\'s security.'
            r = requests.get(url=f'https://api.msg91.com/api/sendotp.php?authkey=244450ArWieIHo15bd15b6a&message={message}&otp={otp}&sender=RUPCLE&mobile={mobile}&DLT_TE_ID=1207165968024629434')
            r = requests.post(url=f'https://control.msg91.com/api/v5/otp?template_id=624809f07c5efc61b777a266&mobile=91{mobile}&otp={otp}', 
                              headers={"Content-Type": "applicaton/json", "Authkey": "244450ArWieIHo15bd15b6a", "Cookie": "PHPSESSID=b830lnmkkuuo4gdovd4qk50io5"})
            res = r.json()
            OTP_DICT[f'{mobile}'] = otp
            print(OTP_DICT[f'{mobile}'])
            return Response({"message": f'Your OTP is {otp}'})
            # return Response({"message": f"{res['message']}"})
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
            role = serializer.validated_data['role']
            mobile = serializer.validated_data['mobile']
            if f'{mobile}' in OTP_DICT:
                print(OTP_DICT[f'{mobile}'])
                if OTP_DICT[f'{mobile}'] == otp:
                    instance = CustomUser.objects.filter(mobile=mobile).exists()
                    print(instance)
                    if instance:
                        user = CustomUser.objects.get(mobile=mobile)
                        print(user)
                        verification = f'{user.status}'.replace('_',' ')
                        token = get_tokens_for_user(user)
                        return Response({"id": user.id, "token": token, "message": f"User Already exists. Kindly continue with {verification}", "step": user.status}, status=status.HTTP_200_OK)
                    if is_tnc_accepted != True:
                        return Response({"message": "Please accept Terms & Conditions."}, status=status.HTTP_400_BAD_REQUEST)
                    user = CustomUser.objects.create(username=mobile, mobile=mobile, is_mobile_verified=True, is_tnc_accepted=is_tnc_accepted, status=CustomUser.STATUS_CHOICES[1][0])
                    # user = CustomUser.objects.get(pk=pk)
                    # if user.status == CustomUser.STATUS_CHOICES[0][0]:
                    user.is_mobile_verified = True
                    # user.tnc = True
                    user.status = CustomUser.STATUS_CHOICES[1][0]
                    user.role = role

                    # Integrate Credit Score fetch api below
                    if role == User.ROLE_CHOICES[2][1]:
                        user.credit_score = serializer.validated_data['credit_score']

                    # Integrate Credit Score fetch api above
                    
                    user.save()
                    id = user.id
                    del OTP_DICT[f'{mobile}']
                        # return Response({"msg": "OTP Verified", "step": user.is_active})
                    # try:
                    #     user = CustomUser.objects.get(mobile=mobile)
                    # except:
                    #     user = CustomUser.objects.create(username=mobile, mobile=mobile)
                    token = get_tokens_for_user(user)
                    return Response({"id": id, "message": "OTP Verified", "step": user.status, "token": token}, status=status.HTTP_200_OK)
                return Response({"message": "OTP does not match."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Please generate OTP first."}, status=status.HTTP_400_BAD_REQUEST)
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
            queryset = CustomUser.objects.filter(id=user.id)
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
    def panDetail(self, request, pk):
        '''
        Takes PAN number and obtains response from PAN database if matches return owner Name in response
        '''
        # user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pan_exist = User.objects.filter(pan=serializer.validated_data['pan']).exists()
        if pan_exist:
            return Response({"message": "PAN already exists."}, status=status.HTTP_400_BAD_REQUEST)
        data = {"access_token": "9dECoXkSlurJQs8C", "panId": serializer.validated_data['pan']}
        # data = json.load({
        # "access_token":"9dECoXkSlurJQs8C",
        # "panId": "AAIPM3854E"
        # })
        instance = self.get_object()

        # Below is pan integration
        r = requests.post(url="http://34.131.215.77:8080/api/v2/nsdlPanVerification", 
                          json=data,
                          headers={"app_version_code": "17", "device_type": "computer", "Content-Type": "application/json", "Cookie": "RupeeCircle=eyJpdiI6IitzUFFuXC9NckdvWGgreHAxSU1uUFNRPT0iLCJ2YWx1ZSI6ImFpNjhoeTlrK29ZbVplK0tPS2pZNXJSS2hZUURkVHk3ZWhYVHJFZmdwbUlpSkkyZCtwYjZWbytsMVppMjE3OUxlamEzeWFYb0ZzdDMrbWpOa0oyQVR3PT0iLCJtYWMiOiJhZjYxYmFmNTFiMzgyY2IyN2Y1N2I0MTcyOTI0MDAzYWEwMmQ0NDcwYWU4Y2E3MzBkNTRiODU5OWZhOTgxMTI2In0%3D; RupeeCircle=eyJpdiI6IldHYlFLRldNc2lmdnh6OWdSb1RKMlE9PSIsInZhbHVlIjoicEJ2anBianhSZW9Ia3U5TUFiaGpORjVYUDE0QlhVZm9wTDYyS1M1V2tjQjZCNXpMR2dHNVZWWW1vOWxGS1g4Mk9EQ2tjbllVV0dHWWpNSWk2MjNxckE9PSIsIm1hYyI6ImViYmEwOTIwYjExYzY1NGFmNDI5MTQ3YTYxYTU1MjE3NGQ5NWExNmU1MGQ5YzlhNjJkOTBiYTdlNDBmNWRkNGQifQ%3D%3D"})
        res = r.json()
        print(r.content)
        if res['flag'] == True:
            instance.pan = res['data']['pan']
            instance.pan_name = res['data']['name']
            instance.first_name = res['data']['name']
            instance.is_pan_verified = True
            instance.pan_api_response = f"{res}"
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
        data = request.data
        serializer = AadharSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            aadhaar = serializer.validated_data['aadhaar']
            aadhaar_already_exists = CustomUser.objects.filter(aadhaar=aadhaar).exists()
            if aadhaar_already_exists:
                return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            otp = random.randint(100000, 999999)
            OTP_DICT[f'{aadhaar}'] = otp
            print(otp)
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
            # user = CustomUser.objects.get(id=request.user.id)
            user = CustomUser.objects.get(pk=pk)
            aadhaar = serializer.validated_data['aadhaar']
            # name = serializer.validated_data['name']
            otp = serializer.validated_data['otp']
            # global AADHAR_OTP
            if otp == OTP_DICT[f'{aadhaar}']:
                aadhaar_already_exists = CustomUser.objects.filter(aadhaar=aadhaar).exists()
                if aadhaar_already_exists:
                    return Response({'message': 'Aadhaar is already registered with another account.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                # if user.pan_name != name:
                #     return Response({'message': 'Aadhaar name doesn\'t match with PAN name.'}, status=status.HTTP_400_BAD_REQUEST)
                user.aadhaar = aadhaar
                # user.aadhaar_name = name
                user.is_aadhaar_verified = True
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
        user = request.user
        serializer = BankDetailSerializer(data=data)
        # print("Validating Serializer")
        if serializer.is_valid(raise_exception=True):
            if serializer.is_valid(raise_exception=True):
                # print("Serializer Validated")
                if 'acc_holder_name' in serializer.validated_data and 'bank_acc' in serializer.validated_data and 'bank_ifsc' in serializer.validated_data:
                    # print("Getting User object.")
                    acc_holder_name = serializer.validated_data['acc_holder_name']
                    bank_acc = serializer.validated_data['bank_acc']
                    bank_ifsc = serializer.validated_data['bank_ifsc']
                    bank_acc_exists = CustomUser.objects.filter(bank_acc=bank_acc).exists()
                    if bank_acc_exists:
                        return Response({"message": "Bank account already exist with another user."}, status=status.HTTP_400_BAD_REQUEST)
                    
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
                        "traceId": "ABCDEF12345678"}
                    url = 'https://sandbox.transxt.in/api/1.1/pennydrop'
                    headers = {
                        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg4ODEyODExLCJpYXQiOjE2ODg3MjY0MTEsImp0aSI6IjUwMjUyOWQ0OTJhZTQ5ZGNhZmFmOWNjYmY2ZTU0NDIyIiwidXNlcl9pZCI6N30.J1wRCEku7nTjfZ69E3aVDKksn0nPe9j_fkdJQ9OLHsQ",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(url, json=bank_detail, headers=headers)
                    # r = json.loads(response)
                    res = response.json()

                    # Below code is to check the request
                    # req = requests.Request('POST',url,headers={"Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg4ODEyODExLCJpYXQiOjE2ODg3MjY0MTEsImp0aSI6IjUwMjUyOWQ0OTJhZTQ5ZGNhZmFmOWNjYmY2ZTU0NDIyIiwidXNlcl9pZCI6N30.J1wRCEku7nTjfZ69E3aVDKksn0nPe9j_fkdJQ9OLHsQ",  "Content-Type": "application/json"},data=bank_detail)
                    # prepared = req.prepare()
                    # def pretty_print_POST(req):
                    #     print('{}\n{}\r\n{}\r\n\r\n{}'.format(
                    #         '-----------START-----------',
                    #         req.method + ' ' + req.url,
                    #         '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
                    #         req.body,
                    #     ))
                    # pretty_print_POST(response.request)
                    print(f"---------------------------------------- Request starts ----------------------------------------")
                    print('response.request => ',response.request)
                    print('response.request.url => ', response.request.url)
                    print('response.request.body => ', response.request.body)
                    print('response.request.headers => ', response.request.headers)
                    print(f"---------------------------------------- Request ENDS ----------------------------------------")

                    print(f"This is your res => {res}")
                    # Above code is to check the request
                        
                    transaction.status = res['status']
                    if res['status'] == 'SUCCESS':
                        user.bank_acc = serializer.validated_data['bank_acc']
                        user.bank_ifsc = serializer.validated_data['bank_ifsc']
                        user.bank_name = res['data']['nameAtBank']
                        user.is_bank_acc_verified = True
                        user.save()
                        transaction.penny_drop_utr = res['data']['utr']
                        transaction.ref_id = res['data']['ref_id']
                        transaction.save()
                        return Response({"message": response.status, "name": res['data']['nameAtBank']})
                    else:
                        try:
                            transaction.ref_id = res['data']['ref_id']
                        except:
                            transaction.ref_id = ''
                        transaction.save()
                        return Response({"message": res['message'] if 'message' in res else res['status'], "res" : res}, status=status.HTTP_400_BAD_REQUEST)
                    # if r.status == 'FAILURE':
                    #     return Response({"message": "Bank Verification Failed. Please try again."})
                    # # Integrate Penny Drop Api above
                    
                    # Match the name here
                    print('getting user')
                    user = CustomUser.objects.get(pk=pk)
                    user.acc_holder_name = acc_holder_name
                    # user.account_holder_name = 'Name'
                    user.bank_acc = bank_acc
                    user.bank_ifsc = bank_ifsc
                    user.is_bank_acc_verified = True
                    user.status = CustomUser.STATUS_CHOICES[4][0]
                    user.save()
                    special_plan = InvestmentProduct.objects.get(id=22)
                    special_plan.allowed_investor.add(user)
                    special_plan.save()
                    BankAccount.objects.create(bank=user.bank_name, owner=user, acc_number=user.bank_acc, ifsc=user.bank_ifsc, is_primary=True)
                    Wallet.objects.create(owner=user)
                    
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
                user = CustomUser.objects.get(pk=pk)
                user.email = email
                user.is_email_verified = True
                user.save()
                del EMAIL_OTP[f'{email}']
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
