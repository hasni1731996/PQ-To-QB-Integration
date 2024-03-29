# Generated by Django 3.2.5 on 2021-08-24 09:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SandboxCredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('procore_app_id', models.CharField(blank=True, max_length=255, null=True)),
                ('procore_app_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('procore_redirect_url', models.CharField(blank=True, max_length=255, null=True)),
                ('procore_company_id', models.IntegerField(blank=True, null=True)),
                ('qbo_app_id', models.CharField(blank=True, max_length=255, null=True)),
                ('qbo_app_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('qbo_redirect_url', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionCredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('procore_app_id', models.CharField(blank=True, max_length=255, null=True)),
                ('procore_app_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('procore_redirect_url', models.CharField(blank=True, max_length=255, null=True)),
                ('procore_company_id', models.IntegerField(blank=True, null=True)),
                ('qbo_app_id', models.CharField(blank=True, max_length=255, null=True)),
                ('qbo_app_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('qbo_redirect_url', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
