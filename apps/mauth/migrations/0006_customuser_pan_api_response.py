# Generated by Django 4.2.1 on 2023-06-30 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0005_customuser_credit_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='pan_api_response',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
