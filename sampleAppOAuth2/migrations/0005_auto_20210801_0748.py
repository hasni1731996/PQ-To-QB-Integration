# Generated by Django 3.2.5 on 2021-08-01 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampleAppOAuth2', '0004_syncprojects'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncprojects',
            name='procore_project_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='syncprojects',
            name='qbo_customer_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]