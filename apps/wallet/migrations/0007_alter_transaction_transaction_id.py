# Generated by Django 4.2.1 on 2023-06-08 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0006_alter_transaction_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.UUIDField(default='e2cf564571b8426b862166c645417cbe', editable=False, unique=True),
        ),
    ]
