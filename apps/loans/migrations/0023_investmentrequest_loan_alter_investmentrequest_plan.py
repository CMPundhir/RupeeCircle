# Generated by Django 4.2.1 on 2023-06-12 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0022_alter_loan_collateral_alter_loan_installments_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentrequest',
            name='loan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='loans.loan'),
        ),
        migrations.AlterField(
            model_name='investmentrequest',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='loans.investmentplan'),
        ),
    ]
