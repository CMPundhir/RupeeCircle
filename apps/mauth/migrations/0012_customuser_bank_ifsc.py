# Generated by Django 4.2.1 on 2023-05-20 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0011_rename_aadhar_customuser_aadhaar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bank_ifsc',
            field=models.CharField(blank=True, null=True),
        ),
    ]