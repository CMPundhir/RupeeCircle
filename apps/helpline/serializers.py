from rest_framework import serializers
from .models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = '__all__'


class ComplaintCreateSerializer(serializers.Serializer):
    nature = serializers.CharField()
    body = serializers.CharField()
    medium = serializers.CharField()


class MailComplaintSerializer(serializers.Serializer):
    email = serializers.EmailField()
    body = serializers.CharField()
    nature = serializers.ChoiceField(Complaint.NATURE_CHOICES)


class MarkResolveSerializer(serializers.Serializer):
    remarks = serializers.CharField()
