# Generated by Django 4.2.1 on 2023-06-30 09:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loans', '0065_remove_investmentproduct_allowed_investor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentproduct',
            name='investors_detail',
            field=models.ManyToManyField(related_name='investor_detail', to=settings.AUTH_USER_MODEL),
        ),
    ]
