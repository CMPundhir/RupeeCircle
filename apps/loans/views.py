from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets

# Create your views here.

class LoanFormViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        return LoanForm.objects.all()
    
    def get_serializer_class(self):
        return LoanFormSerializer
    

class LoanViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Loan.objects.all()
        return queryset
    
    def get_serializer_class(self):
        return LoanSerializer
