# Generated by Django 4.2.1 on 2023-06-19 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0029_remove_loanapplication_loan_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanapplication',
            name='borrower',
        ),
        migrations.RemoveField(
            model_name='loanapplication',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='loanapplication',
            name='investors',
        ),
        migrations.RemoveField(
            model_name='loanapplication',
            name='last_modified_by',
        ),
        migrations.DeleteModel(
            name='InvestmentRequest',
        ),
        migrations.DeleteModel(
            name='LoanApplication',
        ),
    ]
