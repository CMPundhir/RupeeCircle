# Generated by Django 4.2.1 on 2023-06-23 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0046_loan_interest_calculation_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentproduct',
            name='minimum_locking',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='loan',
            name='minimum_locking',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
