# Generated by Django 4.2.1 on 2023-06-27 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0019_transaction_penny_drop_utr'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='wallet.bankaccount'),
        ),
    ]
