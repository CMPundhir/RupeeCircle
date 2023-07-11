from rest_framework import serializers

class PhonePeSerializer(serializers.Serializer):
    amount = serializers.IntegerField()