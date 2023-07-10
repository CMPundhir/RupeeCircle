# Generated by Django 4.2.1 on 2023-07-10 07:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wallet', '0024_alter_transaction_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankSlab',
            fields=[
                ('is_record_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Indicates the time when the record was created', null=True, verbose_name='Published On')),
                ('last_modified_at', models.DateTimeField(auto_now_add=True, help_text='Indicates the time when the record was last modified', null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('system', models.CharField(choices=[('IMPS', 'IMPS'), ('NEFT', 'NEFT'), ('RTGS', 'RTGS')], default='IMPS', max_length=50)),
                ('charges', models.IntegerField()),
                ('min_limit', models.IntegerField()),
                ('max_limit', models.IntegerField()),
                ('created_by', models.ForeignKey(blank=True, help_text='Indicates the user who created this record', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(blank=True, help_text='Indicates the user who last modified this record', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='updated_%(class)ss', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]