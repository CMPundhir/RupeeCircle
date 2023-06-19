# Generated by Django 4.2.1 on 2023-06-19 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0033_installment_loan_installment_parent_loan'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentrequest',
            name='amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='collateral',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='default_remedies',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='governing_law',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='installments',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='interest_rate',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='late_pay_penalties',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='prepayment_options',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='privacy',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='investmentrequest',
            name='repayment_terms',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='Bid',
        ),
    ]
