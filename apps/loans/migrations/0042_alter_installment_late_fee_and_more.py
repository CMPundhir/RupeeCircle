# Generated by Django 4.2.1 on 2023-06-20 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0041_investmentrequest_tenure_loan_tenure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installment',
            name='late_fee',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='installment',
            name='paid_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='installment',
            name='payment_reference',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
