from rest_framework import serializers
from .models import ActivityTracker


class ActivityTrackerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityTracker
        fields = '__all__'
