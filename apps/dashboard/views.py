from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from apps.mauth.models import CustomUser as User
from apps.mauth.views import get_tokens_for_user
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.response import Response
from apps.notification.services import LogService
from .serializers import *
from apps.mauth.serializers import *
from apps.loans.models import *
from apps.loans.serializers import InvestmentPlanSerializer

# Create your views here.

class InvestorViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['first_name', 'mobile', 'email', 'pan', 'aadhaar', 'bank_acc', 'partner']
    ordering_fields = ['id']
    filterset_fields = ['partner']

    def get_queryset(self):
        user = self.request.user
        if user.role == User.ROLE_CHOICES[1][1]:
            queryset = User.objects.filter(aggregator=user).order_by('-id')
        else:
            queryset = User.objects.filter(role=User.ROLE_CHOICES[0][1]).order_by('-id')
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvestorSerializer
        elif self.action == 'list':
            return UserSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'investmentOptions':
            return InvestmentOptionsSerializer
        else:
            return InvestorSerializer   
    
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
            instance.is_tnc_accepted = True
            instance.mobile = serializer.validated_data['mobile']
            instance.is_mobile_verified = True
            instance.email = serializer.validated_data['email']
            instance.is_email_verified = True
            instance.gender = serializer.validated_data['gender']
            instance.first_name = serializer.validated_data['first_name']
            instance.pan = serializer.validated_data['pan']
            instance.is_pan_verified = True
            instance.aadhaar = serializer.validated_data['aadhaar']
            instance.is_aadhaar_verified = True
            instance.bank_acc = serializer.validated_data['bank_acc']
            instance.bank_ifsc = serializer.validated_data['bank_ifsc']
            instance.is_bank_acc_verified = True
            instance.role = User.ROLE_CHOICES[0][0]
            instance.status = User.STATUS_CHOICES[4][1]
            if 'country' in serializer.validated_data and serializer.validated_data['country']:
                instance.country = serializer.validated_data['country']
            if 'state' in serializer.validated_data and serializer.validated_data['state']:
                instance.state = serializer.validated_data['state']
            if 'city' in serializer.validated_data and serializer.validated_data['city']:
                instance.city = serializer.validated_data['city']
            if 'address' in serializer.validated_data and serializer.validated_data['address']:
                instance.address = serializer.validated_data['address']
            if 'pincode' in serializer.validated_data and serializer.validated_data['pincode']:
                instance.pincode = serializer.validated_data['pincode']
            if 'company' in serializer.validated_data and serializer.validated_data['company']:
                instance.company = serializer.validated_data['company']
            if 'last_name' in serializer.validated_data and serializer.validated_data['last_name']:
                instance.last_name = serializer.validated_data['last_name']
            if 'aggregator' in serializer.validated_data and serializer.validated_data['aggregator']:
                instance.aggregator = serializer.validated_data['aggregator']
            else:
                instance.aggregator = request.user
            instance.save()
            LogService.log(user=instance, msg="Welcome to RupeeCircle.", is_transaction=False)
            serializer = InvestorGetSerializer(instance)
            return Response({"message": "Investor registered successfully.", "investor": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def investmentOptions(self, request, pk):
        # data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            if 'is_fixedroi_allowed' in data and data['is_fixedroi_allowed']:
                instance.is_fixedroi_allowed = data['is_fixedroi_allowed']
            if 'is_anytime_withdrawal_allowed' in data and data['is_anytime_withdrawal_allowed']:
                instance.is_anytime_withdrawal_allowed = data['is_anytime_withdrawal_allowed']
            if 'is_marketplace_allowed' in data and data['is_marketplace_allowed']:
                instance.is_marketplace_allowed = data['is_marketplace_allowed']
            instance.save()
        return Response({"message": "Investment Options updated Successfully."}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def specialPlans(self, request, pk):
        user = self.get_object()
        queryset = InvestmentPlan.objects.filter(allowed_investor=user)
        # serializer = InvestmentPlanSerializer(queryset, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InvestmentPlanSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InvestmentPlanSerializer(queryset, many=True)
        return Response(serializer.data)
        
        
class PartnerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['first_name', 'mobile', 'email', 'pan', 'aadhaar', 'bank_acc', 'partner']
    ordering_fields = ['id']
    filterset_fields = []

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
            return PartnerRegistrationSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return PartnerGetSerializer
        return UserSerializer
    
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
            instance.is_tnc_accepted = True
            instance.mobile = serializer.validated_data['mobile']
            instance.is_mobile_verified = True
            instance.email = serializer.validated_data['email']
            instance.is_email_verified = True
            instance.gender = serializer.validated_data['gender']
            instance.first_name = serializer.validated_data['first_name']
            instance.pan = serializer.validated_data['pan']
            instance.is_pan_verified = True
            instance.aadhaar = serializer.validated_data['aadhaar']
            instance.is_aadhaar_verified = True
            instance.bank_acc = serializer.validated_data['bank_acc']
            instance.bank_ifsc = serializer.validated_data['bank_ifsc']
            instance.is_bank_acc_verified = True
            instance.role = User.ROLE_CHOICES[1][0]
            instance.status = User.STATUS_CHOICES[4][1]
            if 'country' in serializer.validated_data and serializer.validated_data['country']:
                instance.country = serializer.validated_data['country']
            if 'state' in serializer.validated_data and serializer.validated_data['state']:
                instance.state = serializer.validated_data['state']
            if 'city' in serializer.validated_data and serializer.validated_data['city']:
                instance.city = serializer.validated_data['city']
            if 'address' in serializer.validated_data and serializer.validated_data['address']:
                instance.address = serializer.validated_data['address']
            if 'pincode' in serializer.validated_data and serializer.validated_data['pincode']:
                instance.pincode = serializer.validated_data['pincode']
            if 'company' in serializer.validated_data and serializer.validated_data['company']:
                instance.company = serializer.validated_data['company']
            if 'last_name' in serializer.validated_data and serializer.validated_data['last_name']:
                instance.last_name = serializer.validated_data['last_name']
            instance.save()
            LogService.log(user=instance, msg="Welcome to RupeeCircle.", is_transaction=False)
            serializer = self.get_serializer(instance)
            return Response({"message": "Partner registered successfully.", "partner": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
    
    @action(methods=['GET'], detail=False)
    def allPartners(self, request):
        queryset = User.objects.filter(role=User.ROLE_CHOICES[1][0])
        serializer = PartnerDetailSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
