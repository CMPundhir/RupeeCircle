# Generated by Django 4.2.1 on 2023-06-30 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0062_investmentproduct_invested_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='is_tnc_accepted',
            field=models.BooleanField(default=True),
        ),
    ]
