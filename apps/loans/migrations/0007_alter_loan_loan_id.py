# Generated by Django 4.2.1 on 2023-06-07 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0006_alter_loan_loan_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='loan_id',
            field=models.UUIDField(default='0e3ff80b1fbd4235891267dceed389a6', editable=False),
        ),
    ]
