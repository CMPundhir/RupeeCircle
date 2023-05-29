from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from apps.mauth.models import CustomUser as User
from apps.mauth.views import get_tokens_for_user
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from apps.mauth.serializers import *
from apps.loans.models import *

# Create your views here.

class InvestorViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[1][1]:
            queryset = User.objects.filter(aggregator=user)
        else:
            queryset = User.objects.filter(role=User.ROLE_CHOICES[0][1])
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        return UserSerializer   
    
    def create(self, request):
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
            instance.role = User.ROLE_CHOICES[0][0]
            instance.aggregator = request.user
            instance.save()
            return Response({"message": "Investor registered successfully.", "investor": instance}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AggregatorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.action == 'linkInvestor':
            queryset =  User.objects.filter(role=User.ROLE_CHOICES[1][0])
        elif self.action == 'listInvestor':
            queryset =  User.objects.filter(role=User.ROLE_CHOICES[0][1])
        else:
            queryset =  User.objects.filter(role=User.ROLE_CHOICES[1][1])
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'linkInvestor':
            return LinkAggregatorSerializer
        elif self.action == 'create':
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
    
    def create(self, request):
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
            instance.first_name = serializer.validated_data['first_name']
            instance.last_name = serializer.validated_data['last_name']
            instance.mobile = serializer.validated_data['mobile']
            instance.email = serializer.validated_data['email']
            instance.gender = serializer.validated_data['gender']
            instance.address = serializer.validated_data['address']
            instance.pan = serializer.validated_data['pan']
            instance.aadhaar = serializer.validated_data['aadhaar']
            instance.bank_acc = serializer.validated_data['bank_acc']
            instance.bank_ifsc = serializer.validated_data['bank_ifsc']
            instance.role = User.ROLE_CHOICES[1][0]
            instance.save()
            return Response({"message": "Aggregator registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

