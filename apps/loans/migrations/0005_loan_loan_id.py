# Generated by Django 4.2.1 on 2023-06-01 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0004_loan_borrower_loan_investor'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='loan_id',
            field=models.UUIDField(default='b01f08aac1dd43969039bf8b24e6f535', editable=False),
        ),
    ]
