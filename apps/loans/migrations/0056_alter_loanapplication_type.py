# Generated by Django 4.2.1 on 2023-06-24 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0055_loanapplication_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanapplication',
            name='type',
            field=models.CharField(choices=[('OPEN BID', 'OPEN BID'), ('CLOSE BID', 'CLOSE BID')], default='OPEN BID', max_length=100),
        ),
    ]
