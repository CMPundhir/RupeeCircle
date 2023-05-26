from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.db import models

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
    ROLE_CHOICES = (('INVESTOR', 'INVESTOR'), ('AGGREGATOR', 'AGGREGATOR'), ('ADMIN', 'ADMIN'))
    STATUS_CHOICES = (('MOBILE_VERIFICATION', 'MOBILE_VERIFICATION'), 
                      ('PAN_VERIFICATION', 'PAN_VERIFICATION'), 
                      ('AADHAAR_VERIFICATION', 'AADHAAR_VERIFICATION'),
                      ('BANK_VERIFICATION', 'BANK_VERIFICATION'),
                      ('ACTIVE', 'ACTIVE'))
    GENDER_CHOICES = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHERS', 'OTHERS'))

    name = models.CharField(null=True, blank=True)
    selfie = models.ImageField(upload_to=upload_selfie, blank=True, null=True)
    is_tnc_accepted = models.BooleanField(default=False)
    mobile = models.CharField(unique=True, null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)
    # email = models.EmailField(unique=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    gender = models.CharField(choices=GENDER_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
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
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    role = models.CharField(choices=ROLE_CHOICES, default=ROLE_CHOICES[0][1])
    aggregator = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} {self.role}'
