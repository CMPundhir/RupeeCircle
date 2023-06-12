from django.db import models
from apps.mauth.models import BaseModel
from apps.mauth.models import CustomUser as User
from apps.mauth.middleware import get_current_authenticated_user
import datetime
import uuid

# Create your models here.

def get_loan_id(id):
    loan_id = f'LOAN{id}'
    return loan_id

class Loan(BaseModel, models.Model):
    STATUS_CHOICES = (('APPLIED', 'APPLIED'), ('UNDER BIDDING', 'UNDER BIDDING'), ('CLOSED', 'CLOSED'))
    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False, blank=False)
    loan_id = models.CharField(max_length=1000, blank=True, unique=True)
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    repayment_terms = models.CharField(max_length=1000, null=True, blank=True)
    installments = models.CharField(max_length=1000, null=True, blank=True)
    collateral = models.CharField(max_length=255, null=True, blank=True)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    default_remedies = models.CharField(max_length=1000, null=True, blank=True)
    privacy = models.CharField(max_length=1000, null=True, blank=True)
    governing_law = models.CharField(max_length=1000, null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='borrower')
    investors = models.ManyToManyField(User, blank=True)#, related_name='investor')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def __str__(self):
        return f'{self.id}'
    
    # def save(self, *args, **kwargs):
    #     self.loan_id = f'LOAN{self.id}'
    #     super(Loan, self).save(*args, **kwargs)


class InvestmentPlan(BaseModel, models.Model):
    TYPE_CHOICES = (('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL'))
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField(null=False, blank=False)
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    tenure = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    investors = models.ManyToManyField(User, blank=True)


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
    

class InvestmentRequest(BaseModel, models.Model):
    STATUS_CHOICES = (('PENDING', 'PENDING'), ('APPROVED', 'APPROVED'))
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.DO_NOTHING, null=True, blank=True)
    loan = models.ForeignKey(Loan, on_delete=models.DO_NOTHING, null=True, blank=True)
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='loan_borrower', null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        self.created_by = user
        super(InvestmentRequest, self).save(*args, **kwargs)

