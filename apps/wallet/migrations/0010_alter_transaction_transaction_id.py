# Generated by Django 4.2.1 on 2023-06-08 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0009_alter_transaction_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.UUIDField(default='14f26ef03c6b45c6ac6d659cdcb26706', editable=False, unique=True),
        ),
    ]
