# Generated by Django 3.2.5 on 2021-08-04 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampleAppOAuth2', '0007_synccostcodes'),
    ]

    operations = [
        migrations.AddField(
            model_name='authtoken',
            name='procore_username',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
