# Generated by Django 4.2.1 on 2023-06-23 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0052_alter_investmentproduct_plan_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplication',
            name='tenure',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]