from rest_framework import serializers
from .models import LoanForm

class LoanFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanForm
        fields = '__all__'
