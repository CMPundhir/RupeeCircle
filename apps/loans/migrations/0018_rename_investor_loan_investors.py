# Generated by Django 4.2.1 on 2023-06-09 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0017_alter_investmentplan_investors'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loan',
            old_name='investor',
            new_name='investors',
        ),
    ]