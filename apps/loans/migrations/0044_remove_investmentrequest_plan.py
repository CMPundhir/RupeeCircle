# Generated by Django 4.2.1 on 2023-06-22 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0043_rename_investmentplan_investmentproduct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investmentrequest',
            name='plan',
        ),
    ]
