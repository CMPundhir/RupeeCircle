from django.shortcuts import render
from .models import LoanForm
from .serializers import LoanFormSerializer
from rest_framework import viewsets

# Create your views here.

class LoanFormViewSet(viewsets.ModelViewSet):
    
    def get_queryset(self):
        return LoanForm.objects.all()
    
    def get_serializer_class(self):
        return LoanFormSerializer
