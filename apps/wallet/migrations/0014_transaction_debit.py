# Generated by Django 4.2.1 on 2023-06-09 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0013_alter_transaction_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='debit',
            field=models.BooleanField(default=False),
        ),
    ]
