# Generated by Django 4.2.1 on 2023-05-20 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0015_rename_tnc_customuser_is_tnc_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='account_holder_name',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bank',
            field=models.CharField(blank=True, null=True),
        ),
    ]