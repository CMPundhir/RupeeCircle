# Generated by Django 4.2.1 on 2023-06-29 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0004_alter_customuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='credit_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]