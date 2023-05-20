from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.db import models

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
    STATUS_CHOICES = (('MOBILE_VERIFICATION', 'MOBILE_VERIFICATION'), 
                      ('PAN_VERIFICATION', 'PAN_VERIFICATION'), 
                      ('AADHAAR_VERIFICATION', 'AADHAAR_VERIFICATION'),
                      ('BANK_VERIFICATION', 'BANK_VERIFICATION'),
                      ('ACTIVE', 'ACTIVE'))

    name = models.CharField(null=True, blank=True)
    is_tnc_accepted = models.BooleanField(default=False)
    mobile = models.CharField(unique=True, null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    pan = models.CharField(null=True, blank=True, unique=True)
    pan_name = models.CharField(null=True, blank=True)
    is_pan_verified = models.BooleanField(default=False)
    aadhaar = models.CharField(null=True, blank=True, unique=True)
    aadhaar_name = models.CharField(null=True, blank=True)
    is_aadhaar_verified = models.BooleanField(default=False)
    # bank = models.CharField(blank=True, null=True)
    acc_holder_name = models.CharField(null=True, blank=True)
    bank_acc = models.CharField(null=True, blank=True, unique=True)
    bank_ifsc = models.CharField(null=True, blank=True)
    bank_name = models.CharField(null=True, blank=True)
    is_bank_acc_verified = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
