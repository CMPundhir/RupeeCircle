# Generated by Django 4.2.1 on 2023-06-19 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0036_investmentplan_investing_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentrequest',
            name='remarks',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
