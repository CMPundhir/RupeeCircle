from django.shortcuts import render
from .models import ActivityTracker
from .serializers import ActivityTrackerSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


# Create your views here.

class ActivityAppViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    http_method_names = ['get', 'head']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['user', 'type', '']
    ordering_fields = ['id']
    filterset_fields = ['user', 'type', 'is_activity']
    
    def get_queryset(self):
        user = self.request.user
        # self.queryset = ActivityTracker.objects.filter(
        #     user=user).order_by("-id")
        self.queryset = ActivityTracker.objects.filter(user=user).order_by('-id')
        return self.queryset

    def get_serializer_class(self):
        print(f'action => {self.action}')
        # or self.action == "retrieve":
        # if self.action == "list":
        #     self.serializer_class = ActivityTrackerResSerializer
        # else:
        self.serializer_class = ActivityTrackerSerializer
        return self.serializer_class

    @action(detail=False, methods=['post', 'get'])
    def notiCount(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        count = ActivityTracker.objects.filter(
            user=user).filter(is_read=False).count()
        return Response(count)

    @action(detail=False, methods=['post', 'get'])
    def markRead(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        ActivityTracker.objects.filter(
            user=user).filter(is_read=False).update(is_read=True)
        return Response("Success")
    
    @action(methods=['GET'], detail=False)
    def recentActivity(self, request):
        queryset = ActivityTracker.objects.filter(user=request.user, is_activity=True).order_by('-id')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecentActivityViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        queryset = ActivityTracker.objects.filter(user=user, is_activity=True).order_by('-id')[:10]
        return queryset
    
    def get_serializer_class(self):
        return ActivityTrackerSerializer
