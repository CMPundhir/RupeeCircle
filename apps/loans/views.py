from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

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
        if self.action == 'apply':
            return LoanFormSerializer
        return LoanSerializer
    
    @action(methods=['POST'], detail=True)
    def apply(self, request, pk):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            instance = LoanForm.objects.create(serializer.validated_data)
            instance.loan = pk
            instance.save()
            return Response({"message": "Application submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
