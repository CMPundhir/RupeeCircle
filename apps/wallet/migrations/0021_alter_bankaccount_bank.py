# Generated by Django 4.2.1 on 2023-06-28 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0020_transaction_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='bank',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
