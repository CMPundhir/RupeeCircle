from django.shortcuts import render
from django.contrib.auth import authenticate, logout
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

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
            user = authenticate(username=username, password=password)
            print(user)
            if user is not None:
                instance = User.objects.get(username=user)
                id = instance.id
                token = get_tokens_for_user(user)
                return Response({"user": id, "tokens": token})
            return Response("User not found !")
        return serializer.errors
    

class LogOutView(APIView):
    def get(self, request):
        logout(request)
        return Response("Logout Successfully.")
