# Generated by Django 4.2.1 on 2023-06-26 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0059_investmentproduct_tnc_loan_tnc'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplication',
            name='credit_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
