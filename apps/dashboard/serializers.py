from rest_framework import serializers
from apps.loans.models import *

class RecentLoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanForm
        fields = ['first_name', 'last_name', 'loan']
