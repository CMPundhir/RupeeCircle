# Generated by Django 4.2.1 on 2023-07-10 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0012_rename_company_name_customuser_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='nature',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]