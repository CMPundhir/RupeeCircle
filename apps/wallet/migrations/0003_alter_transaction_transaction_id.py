# Generated by Django 4.2.1 on 2023-06-07 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_transaction_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.UUIDField(default='7167eeb4267f4a54b68a8888947689b4', editable=False),
        ),
    ]
