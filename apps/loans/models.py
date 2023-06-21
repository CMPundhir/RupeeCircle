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

class LoanApplication(BaseModel, models.Model):
    STATUS_CHOICES = (('APPLIED', 'APPLIED'), ('UNDER BIDDING', 'UNDER BIDDING'), ('CLOSED', 'CLOSED'))
    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False, blank=False)
    # loan_id = models.CharField(max_length=1000, blank=True, unique=True)
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


class InvestmentProduct(BaseModel, models.Model):
    TYPE_CHOICES = (('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL'))
    PRINCIPAL_CHOICES = (('FIXED', 'FIXED'), ('VARIABLE', 'VARIABLE'))
    id = models.AutoField(primary_key=True)
    min_amount = models.IntegerField(null=True, blank=True)
    amount = models.IntegerField(null=False, blank=False)
    investing_limit = models.IntegerField(null=True)
    principal_type = models.CharField(max_length=255, choices=PRINCIPAL_CHOICES, default=PRINCIPAL_CHOICES[0][1])
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    tenure = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    is_special_plan = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    allowed_investor = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='allowed_investor', null=True, blank=True)
    investors = models.ManyToManyField(User, blank=True)


class Installment(BaseModel, models.Model):
    STATUS_CHOICES = (('PENDING', 'PENDING'), ('PAID', 'PAID'))
    id = models.AutoField(primary_key=True)
    parent_loan = models.ForeignKey('Loan', on_delete=models.DO_NOTHING)
    due_date = models.DateField()
    amount = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])
    paid_date = models.DateField(blank=True, null=True)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    late_fee = models.CharField(max_length=255, null=True, blank=True)


class InvestmentRequest(BaseModel, models.Model):
    STATUS_CHOICES = (('PENDING', 'PENDING'), ('APPROVED', 'APPROVED'))
    TYPE_CHOICES = (('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL'), ('LOAN', 'LOAN'))
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField(default=0)
    tenure = models.IntegerField(null=True)
    interest_rate = models.IntegerField(null=True, blank=True)
    repayment_terms = models.CharField(max_length=255, null=True, blank=True)
    installments = models.IntegerField(null=True, blank=True)
    collateral = models.CharField(max_length=255, null=True, blank=True)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    plan = models.ForeignKey(InvestmentProduct, on_delete=models.DO_NOTHING, null=True, blank=True)
    loan = models.ForeignKey(LoanApplication, on_delete=models.DO_NOTHING, null=True, blank=True)
    default_remedies = models.CharField(max_length=255, null=True, blank=True)
    privacy = models.CharField(max_length=255, null=True, blank=True)
    governing_law = models.CharField(max_length=255, null=True, blank=True)
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='loan_borrower', null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        self.created_by = user
        super(InvestmentRequest, self).save(*args, **kwargs)


class Loan(BaseModel, models.Model):
    STATUS_CHOICES = (('APPLIED', 'APPLIED'), ('UNDER BIDDING', 'UNDER BIDDING'), ('CLOSED', 'CLOSED'))
    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False, blank=False)
    loan_id = models.CharField(max_length=1000, blank=True, unique=True)
    tenure = models.IntegerField(null=True)
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    repayment_terms = models.CharField(max_length=1000, null=True, blank=True)
    installments = models.ManyToManyField(Installment)
    collateral = models.CharField(max_length=255, null=True, blank=True)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    default_remedies = models.CharField(max_length=1000, null=True, blank=True)
    privacy = models.CharField(max_length=1000, null=True, blank=True)
    governing_law = models.CharField(max_length=1000, null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='final_loan_borrower')
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, related_name='final_loan_investor',null=True)
    type = models.CharField(max_length=255, choices=InvestmentRequest.TYPE_CHOICES, default=InvestmentRequest.TYPE_CHOICES[0][1])
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        self.loan_id = f'LOAN{self.id}'
        super(Loan, self).save(*args, **kwargs)



