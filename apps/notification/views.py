from django.shortcuts import render
from .models import ActivityTracker
from .serializers import ActivityTrackerSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated


# Create your views here.

class ActivityAppViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = ActivityTrackerSerializer
    http_method_names = ['get', 'head']
    # filterset_fields = ['is_notification']
    
    def get_queryset(self):
        user = self.request.user
        # self.queryset = ActivityTracker.objects.filter(
        #     user=user).order_by("-id")
        self.queryset = ActivityTracker.objects.all()
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
