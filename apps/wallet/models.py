from django.db import models
import uuid
from apps.mauth.models import BaseModel
from apps.mauth.models import CustomUser as User

# Create your models here.

class Wallet(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    balance = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    invested_amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)


class Transaction(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.UUIDField(default=uuid.uuid4().hex, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
