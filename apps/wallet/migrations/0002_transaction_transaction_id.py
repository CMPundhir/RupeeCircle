# Generated by Django 4.2.1 on 2023-06-01 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_id',
            field=models.UUIDField(default='dc2399623ab6456483c9c4942819a6f3', editable=False),
        ),
    ]
