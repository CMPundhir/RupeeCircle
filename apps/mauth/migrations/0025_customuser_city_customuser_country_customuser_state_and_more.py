# Generated by Django 4.2.1 on 2023-05-26 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0024_customuser_aggregator'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='state',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='zip_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
