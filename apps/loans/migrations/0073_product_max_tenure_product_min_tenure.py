# Generated by Django 4.2.1 on 2023-07-01 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0072_remove_product_tenure'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_tenure',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='min_tenure',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]