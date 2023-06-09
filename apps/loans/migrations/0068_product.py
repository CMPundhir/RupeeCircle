# Generated by Django 4.2.1 on 2023-07-01 07:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loans', '0067_alter_investmentproduct_allowed_investor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('is_record_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Indicates the time when the record was created', null=True, verbose_name='Published On')),
                ('last_modified_at', models.DateTimeField(auto_now_add=True, help_text='Indicates the time when the record was last modified', null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('plan_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('min_amount', models.IntegerField(blank=True, null=True)),
                ('max_amount', models.IntegerField()),
                ('minimum_locking', models.CharField(blank=True, max_length=255, null=True)),
                ('interest_rate', models.FloatField(editable=False)),
                ('tenure', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL')], default='FIXED ROI', max_length=255)),
                ('is_special_plan', models.BooleanField(default=False)),
                ('is_primary', models.BooleanField(default=False)),
                ('investors', models.IntegerField(default=0)),
                ('invested_amount', models.BigIntegerField(default=0)),
                ('created_by', models.ForeignKey(blank=True, help_text='Indicates the user who created this record', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(blank=True, help_text='Indicates the user who last modified this record', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='updated_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('tnc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='loans.termsandcondition')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
