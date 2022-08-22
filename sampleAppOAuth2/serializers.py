from django.contrib.auth.models import User
from rest_framework import serializers

from sampleAppOAuth2.models import SyncProjects, SyncVendor, SyncCostCodes, SyncExpenses, SyncOwnerInvoices, \
    SubContractorInvoices


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SyncProjects
        fields = ('project_name', 'sync_date_time', 'procore_project_id', 'qbo_customer_id', 'user')


class VendorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SyncVendor
        fields = ('sync_date_time', 'vendor_company', 'procore_vendor_id', 'qbo_vendor_id', 'user')


class CostCodesSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SyncCostCodes
        fields = ('sync_date_time', 'parent_id', 'costcode_id', 'name', 'full_code', 'qbo_cost_code_id', 'user')


class ExpenseSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SyncExpenses
        fields = (
            'user', 'procore_created_id', 'qbo_created_id', 'procore_project_name', 'procore_vendor_name',
            'description')


class OwnerInvoicesSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SyncOwnerInvoices
        fields = ('user', 'procore_owner_invoice_id', 'procore_prime_contract_id', 'procore_owner_invoice_amount',
                  'qbo_customer_id', 'qbo_amount',
                  'qbo_customer_invoice_id', 'procore_project_name')


class SubContractorInvoicesSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SubContractorInvoices
        fields = ('user', 'procore_project_name', 'procore_sbc_invoice_no', 'procore_invc_amount', 'qbo_vendor_name',
                  'qbo_vendor_id', 'qbo_amount')
