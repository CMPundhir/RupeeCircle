from django.shortcuts import render
from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ComplaintSerializer
from rest_framework.response import Response
from apps.mauth.models import CustomUser as User
from .models import Complaint
from rest_framework.decorators import action
from rest_framework.settings import api_settings

# Create your views here.

class ComplaintViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['transaction_id', 'owner', 'amount', 'id', 'wallet']
    ordering_fields = ['id']
    filterset_fields = ['transaction_id', 'wallet', 'owner', 'amount']

    def get_queryset(self):
        queryset = Complaint.objects.filter(status=Complaint.STATUS_CHOICES[0][1])
        return queryset
    
    def get_serializer_class(self):
        return ComplaintSerializer
    
    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['complainant'] = user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
        
    def list(self, request, *args, **kwargs):
        user = request.user
        if user.role == User.ROLE_CHOICES[3][1]:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.get_queryset().filter(complainant=user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(methods=['GET'], detail=True)
    def markResolve(self, request, pk):
        user = request.user
        if user.role != User.ROLE_CHOICES[3][1]:
            return Response({"message": "You are not authorized to perform this action."}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        instance.status = Complaint.STATUS_CHOICES[1][1]
        instance.save()
        return Response({"message": "Complaint Resolved Successfully."}, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False)
    def resolved(self, request):
        queryset = Complaint.objects.filter(status=Complaint.STATUS_CHOICES[1][1])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
