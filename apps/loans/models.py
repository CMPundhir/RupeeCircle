from django.db import models
from apps.mauth.models import BaseModel
from apps.mauth.models import CustomUser as User
from apps.mauth.middleware import get_current_authenticated_user
import datetime
import uuid
# Create your models here.

# def get_loan_id():
#     date = datetime.datetime.now()
#     date = str(date)
#     user = get_current_authenticated_user()
#     result = date.replace("-", "").replace(" ", f"{user.id}").replace(":", "").replace(".", "")
#     print(result)
#     return f"LOAN{result}"



class Loan(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False, blank=False)
    loan_id = models.UUIDField(default=uuid.uuid4().hex, editable=False)
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    repayment_terms = models.CharField(max_length=1000, null=True, blank=True)
    installments = models.CharField(max_length=1000, null=False, blank=True)
    collateral = models.CharField(max_length=255, null=False, blank=False)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    default_remedies = models.CharField(max_length=1000, null=True, blank=True)
    privacy = models.CharField(max_length=1000, null=True, blank=True)
    governing_law = models.CharField(max_length=1000, null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='borrower')
    investor = models.ManyToManyField(User, related_name='investor')

    def __str__(self):
        return f'{self.id}'


class LoanForm(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=False)
    email = models.EmailField(blank=False, null=False)
    age = models.IntegerField(blank=False, null=False)
    gender = models.CharField(choices=User.GENDER_CHOICES)
    address = models.CharField(max_length=255)
    monthly_income = models.IntegerField()
    credit_score = models.IntegerField()
    loan = models.ForeignKey(Loan, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return f'{self.id}'
