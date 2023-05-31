from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

# Create your views here.
    

class LoanViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Loan.objects.all()
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'apply' or self.action == 'recentApplications':
            return RecentLoanSerializer
        else:
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
    
    @action(methods=['GET'], detail=False)
    def recentApplications(self, request):
        queryset = LoanForm.objects.all().order_by('-id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def invest(self, request):
        return Response({"message": "Work on progress."})

    @action(methods=['GET'], detail=True)
    def investors(self, request, pk):
        instance = Loan.objects.get(pk=pk)
        queryset = instance.investor.all()
        print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
        # serializer = UserSerializer(queryset, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    
    # @action(methods=['GET'], detail=False)
    # def addtoall(self, request):
    #     user = request.user
    #     queryset = self.get_queryset()
    #     for i in queryset:
    #         i.borrower = user
    #         i.investor.add(user)
    #         i.save()
    #     return Response({"message": "added all."})
    