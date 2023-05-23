from django.db import models
from apps.mauth.models import CustomUser
# Create your models here.

class LoanForm(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=False)
    email = models.EmailField(blank=False, null=False)
    age = models.IntegerField(blank=False, null=False)
    gender = models.CharField(choices=CustomUser.GENDER_CHOICES)
    address = models.CharField(max_length=255)
    monthly_income = models.IntegerField()
    credit_score = models.IntegerField()

    def __str__(self):
        return self.id
