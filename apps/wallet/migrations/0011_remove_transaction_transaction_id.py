# Generated by Django 4.2.1 on 2023-06-08 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0010_alter_transaction_transaction_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_id',
        ),
    ]
