# Generated by Django 4.2.1 on 2023-06-08 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0013_alter_loan_loan_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='loan_amount',
            field=models.IntegerField(),
        ),
    ]
