# Generated by Django 3.2.5 on 2021-10-08 16:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sampleAppOAuth2', '0019_auto_20210921_2210'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchedulingSynchronizing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_sync_frequency_choices', models.CharField(blank=True, choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('MONTHLY', 'Monthly')], max_length=12, null=True)),
                ('user_choices', models.CharField(blank=True, choices=[('PROJECTS', 'Projects'), ('VENDORS', 'Vendors'), ('EXPENSES', 'Expenses'), ('COST-CODES', 'Cost-codes'), ('CUSTOMER-INVOICES', 'Customer-invoices'), ('SUBCONTRACTOR-INVOICES', 'Subcontractor-invoices'), ('CUSTOMER-PAYMENTS', 'Customer-payments'), ('SUBCONTRACTOR-PAYMENTS', 'Subcontractor-payments')], max_length=30, null=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
                ('repeat_after', models.CharField(blank=True, max_length=15, null=True)),
                ('next_schedule', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
