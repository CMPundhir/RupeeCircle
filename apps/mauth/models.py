from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.db import models
from django.utils import timezone
from .middleware import get_current_authenticated_user

def upload_selfie(instance, filename):
    return f'selfie/{filename}'


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where phone is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, username, password, **extra_fields):

        if not username:
            raise ValueError('The username must be set')
        username = username
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (('INVESTOR', 'INVESTOR'), ('PARTNER', 'PARTNER'), ('BORROWER', 'BORROWER'), ('ADMIN', 'ADMIN'))
    STATUS_CHOICES = (('MOBILE_VERIFICATION', 'MOBILE_VERIFICATION'), 
                      ('PAN_VERIFICATION', 'PAN_VERIFICATION'), 
                      ('AADHAAR_VERIFICATION', 'AADHAAR_VERIFICATION'),
                      ('BANK_VERIFICATION', 'BANK_VERIFICATION'),
                      ('ACTIVE', 'ACTIVE'))
    GENDER_CHOICES = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHERS', 'OTHERS'))
    RISK_CHOICES = (('LOW', 'LOW'), ('MODERATE', 'MODERATE'), ('HIGH', 'HIGH'))
    REGISTRATION_TYPE_CHOICES = (('SELF', 'SELF'), ('PARTNER', 'PARTNER'), ('ADMIN', 'ADMIN'))

    name = models.CharField(null=True, blank=True)
    user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    selfie = models.ImageField(upload_to=upload_selfie, blank=True, null=True)
    is_tnc_accepted = models.BooleanField(default=False)
    mobile = models.CharField(unique=True, null=True)
    is_mobile_verified = models.BooleanField(default=False)
    # email = models.EmailField(unique=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    pan = models.CharField(null=True, blank=True, unique=True)
    pan_name = models.CharField(null=True, blank=True)
    is_pan_verified = models.BooleanField(default=False)
    aadhaar = models.CharField(null=True, blank=True, unique=True)
    aadhaar_name = models.CharField(null=True, blank=True)
    is_aadhaar_verified = models.BooleanField(default=False)
    acc_holder_name = models.CharField(null=True, blank=True)
    bank_acc = models.CharField(null=True, blank=True, unique=True)
    bank_ifsc = models.CharField(null=True, blank=True)
    bank_name = models.CharField(null=True, blank=True)
    is_bank_acc_verified = models.BooleanField(default=False)
    is_fixedroi_allowed = models.BooleanField(default=True)
    is_anytime_withdrawal_allowed = models.BooleanField(default=False)
    is_marketplace_allowed = models.BooleanField(default=False)
    special_plan_exist = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    role = models.CharField(choices=ROLE_CHOICES, default=ROLE_CHOICES[0][1])
    registration_type = models.CharField(choices=REGISTRATION_TYPE_CHOICES, default=REGISTRATION_TYPE_CHOICES[0][1])
    pan_api_response = models.CharField(max_length=400, blank=True, null=True   )   
    rc_risk = models.CharField(max_length=255, choices=RISK_CHOICES, default=RISK_CHOICES[0][1])
    partner = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True)
    credit_score = models.IntegerField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} {self.role}'
    

class BaseModel(models.Model):
    """
        BaseModel
            This represents the BaseModel for the project without any creation, modification
            or deletion history.
        Inherits : `models.Model`

    """
    is_record_active = models.BooleanField(default=True)
    
    created = models.DateTimeField(null=True, blank=True,
                                   help_text='Indicates the time when the record was created',
                                   verbose_name="Published On", auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True, blank=True,
                                   help_text='Indicates the user who created this record',
                                   related_name='created_%(class)ss')
    last_modified_at = models.DateTimeField(null=True, blank=True,
                                            help_text='Indicates the time when the record was last modified',
                                            auto_now_add=True)
    last_modified_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True, blank=True,
                                         help_text='Indicates the user who last modified this record',
                                         related_name='updated_%(class)ss',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        print("BaseModel : save invoked")
        if self.id is None:
            if self.created_by is None:
                self.created_by = get_current_authenticated_user()
            self.created = timezone.localtime()
        if get_current_authenticated_user() is not None:

            if get_current_authenticated_user()._meta.model.__name__ != "GatewayConsumer":
                self.last_modified_by = get_current_authenticated_user()
        self.last_modified_at = timezone.localtime()
        # self.is_record_active = True
        super(BaseModel, self).save(*args, **kwargs)
        print("BaseModel : save completed")

    class Meta:
        abstract = True


class RiskLog(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    updated_risk = models.CharField(max_length=255, choices=CustomUser.RISK_CHOICES, default=CustomUser.RISK_CHOICES[0][1])
    comment = models.CharField(max_length=1000)


class Activity(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    body = models.CharField(max_length=255)


class LogHistory(BaseModel, models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    activity = models.ManyToManyField(Activity)
    ip = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    platform = models.CharField(max_length=100, null=True, blank=True)

