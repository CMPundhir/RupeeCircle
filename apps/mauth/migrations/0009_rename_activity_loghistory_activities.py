# Generated by Django 4.2.1 on 2023-07-04 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mauth', '0008_activity_loghistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loghistory',
            old_name='activity',
            new_name='activities',
        ),
    ]
