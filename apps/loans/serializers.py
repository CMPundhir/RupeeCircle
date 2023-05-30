from rest_framework import serializers
from .models import *

class LoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = '__all__'


class LoanFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanForm
        fields = '__all__'


class RecentLoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanForm
        fields = ['first_name', 'last_name', 'loan']
