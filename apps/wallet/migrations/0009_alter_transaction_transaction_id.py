# Generated by Django 4.2.1 on 2023-06-08 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0008_alter_transaction_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.UUIDField(default='5984444c5bdc420e95799d78ff682708', editable=False, unique=True),
        ),
    ]
