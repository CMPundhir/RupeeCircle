# Generated by Django 4.2.1 on 2023-06-17 06:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loans', '0027_delete_loanform'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Loan',
            new_name='LoanApplication',
        ),
    ]