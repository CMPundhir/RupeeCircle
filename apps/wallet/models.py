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


class Transaction(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=1000, unique=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    debit = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        s = datetime.now()
        result = str(s).replace('-', '').replace(' ',  '').replace(':', '').replace('.', '')
        self.transaction_id = f'T{self.wallet.id}{result}'
        super(Transaction, self).save(*args, **kwargs)


class BankAccount(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    bank = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True)
    acc_number = models.CharField(max_length=255, unique=True)
    ifsc = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)

