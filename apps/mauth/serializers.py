from rest_framework import serializers
from django.contrib.auth.models import User

class LogInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    # class Meta:
    #     model = User
    #     fields = ['username', 'password']

class UserSerializer(serializers.ModelSerializer):
    # username = serializers.CharField()
    # password = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'