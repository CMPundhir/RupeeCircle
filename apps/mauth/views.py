from django.shortcuts import render
import random
from django.contrib.auth import authenticate, logout
from .serializers import LogInSerializer, UserSerializer, RegistrationSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser as User
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

OTP = int()
# Create your views here.
class LogInView(APIView):
    def get(self, request):
        return Response("No Users !")

    def post(self, request):
        data = request.data
        serializer = LogInSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            try:
                user = authenticate(username=username, password=password)
            except:
                user = authenticate(email=username, password=password)
            if user is not None:
                instance = User.objects.get(username=user)
                id = instance.id
                token = get_tokens_for_user(user)
                return Response({"user": id, "tokens": token})
            return Response("User not found !")
        return serializer.errors
    

# class RegistrationViewSet(APIView):
#     def post(self, request):
#         data = request.data
#         serializer = RegistrationSerializer(data=data)
#         if serializer.is_valid(raise_exception=True):
#             user = serializer.save()
#             # user = serializer.data
#             token = get_tokens_for_user(user)
#             return Response({"msg": "Registration Successful", "token": token})
#         return Response(serializer.error_messages)

class GetOTPVIew(APIView):
    def post(self, request):
        phone = request.data.phone
        user = User.objects.get(phone=phone)
        # if user is None:
        otp = random.randint(1000, 9999)
        global OTP 
        OTP = otp
        return Response({f"Your OTP is {otp}."})
        # return Response("Phone number already exists")


class VerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.otp
        phone = request.data.phone
        global OTP
        if OTP == otp:
            try:
                user = User.objects.get(phone=phone)
            except:
                user = User.objects.create(phone=phone)
            token = get_tokens_for_user(user)
            return Response({"msg": "Success", "token": token})
        return Response("OTP does not match.")



class LogOutView(APIView):
    def get(self, request):
        logout(request)
        return Response("Logout Successfully.")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
