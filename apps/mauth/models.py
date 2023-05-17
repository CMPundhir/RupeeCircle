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
    STATUS_CHOICES = (('MOBILE VERIFICATION', 'MOBILE VERIFICATION'), 
                      ('PAN VERIFICATION', 'PAN VERIFICATION'), 
                      ('AADHAR VERIFICATION', 'AADHAR VERIFICATION'),
                      ('BANK VERIFICATION', 'BANK VERIFICATION'),
                      ('ACTIVE', 'ACTIVE'))

    name = models.CharField(null=True, blank=True)
    phone = models.CharField(unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    pan = models.CharField(null=True, blank=True)
    is_pan_verified = models.BooleanField(default=False)
    aadhar = models.CharField(null=True, blank=True)
    is_aadhar_verified = models.BooleanField(default=False)
    bank_acc = models.CharField(null=True, blank=True)
    is_bank_acc_verified = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.phone
