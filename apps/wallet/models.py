from django.db import models
import uuid
from datetime import datetime
from apps.mauth.models import BaseModel
from apps.mauth.models import CustomUser as User

# Create your models here.

# def get_transaction_id():


class Wallet(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    invested_amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    earnings = models.DecimalField(max_digits=100, decimal_places=2, default=0)


class Transaction(BaseModel, models.Model):
    STATUS_CHOICES = (('SUCCESS', 'SUCCESS'), ('PENDING', 'PENDING'), ('FAILED', 'FAILED'))
    TYPE_CHOICES = (('ADD FUNDS', 'ADD FUNDS'), ('WITHDREW FUNDS', 'WITHDREW FUNDS'), ('INVESTMENT', 'INVESTMET'), ('INTEREST', 'INTEREST'), ('REPAYMENT', 'REPAYMENT'))
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=1000, unique=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    penny_drop_utr = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, blank=True, null=True)
    bank = models.ForeignKey('BankAccount', on_delete=models.DO_NOTHING, blank=True, null=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, null=True, blank=True)
    # interest = models.DecimalField(max_digits=100, decimal_places=2, null=True)
    # repayment = models.BooleanField(default=False)
    debit = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            s = datetime.now()
            result = str(s).replace('-', '').replace(' ',  '').replace(':', '').replace('.', '')
            self.transaction_id = f'T{self.wallet.id}{result}'
        super(Transaction, self).save(*args, **kwargs)


class BankAccount(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    bank = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True)
    acc_number = models.CharField(max_length=255, unique=True)
    ifsc = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)

