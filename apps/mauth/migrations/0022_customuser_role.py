# Generated by Django 4.2.1 on 2023-05-23 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0021_customuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('INVESTOR', 'INVESTOR'), ('AGGREGATOR', 'AGGREGATOR'), ('ADMIN', 'ADMIN')], default='INVESTOR'),
        ),
    ]