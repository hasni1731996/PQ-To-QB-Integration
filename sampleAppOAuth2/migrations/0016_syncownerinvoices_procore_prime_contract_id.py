# Generated by Django 3.2.5 on 2021-09-08 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampleAppOAuth2', '0015_alter_subcontractorinvoices_procore_sbc_invoice_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncownerinvoices',
            name='procore_prime_contract_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]