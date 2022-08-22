from django.contrib.auth.models import User
from django.db import models


class Bearer:
    def __init__(self, refreshExpiry, accessToken, tokenType, refreshToken, accessTokenExpiry, idToken=None):
        self.refreshExpiry = refreshExpiry
        self.accessToken = accessToken
        self.tokenType = tokenType
        self.refreshToken = refreshToken
        self.accessTokenExpiry = accessTokenExpiry
        self.idToken = idToken


class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quickbook_access_token = models.TextField(null=True, blank=True)
    quickbook_refresh_token = models.TextField(null=True, blank=True)
    quickbook_realmid = models.CharField(max_length=200, null=True, blank=True)
    procore_access_token = models.TextField(null=True, blank=True)
    procore_company_id = models.IntegerField(null=True, blank=True)
    procore_refresh_token = models.TextField(null=True, blank=True)
    procore_username = models.CharField(max_length=200, null=True, blank=True)
    quickbook_username = models.CharField(max_length=200, null=True, blank=True)
    user_encrypted_password = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class SyncProjects(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sync_date_time = models.DateTimeField(auto_now_add=True, blank=True)
    project_name = models.CharField(max_length=255, null=True, blank=True)
    procore_project_id = models.IntegerField(null=True, blank=True)
    qbo_customer_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.username + "--" + self.project_name


class SyncVendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sync_date_time = models.DateTimeField(auto_now_add=True, blank=True)
    vendor_company = models.CharField(max_length=255, null=True, blank=True)
    procore_vendor_id = models.IntegerField(null=True, blank=True)
    qbo_vendor_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username + "--" + self.vendor_company


class SyncCostCodes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sync_date_time = models.DateTimeField(auto_now_add=True, blank=True)
    parent_id = models.IntegerField(null=True, blank=True)
    costcode_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    full_code = models.CharField(max_length=255, null=True, blank=True)
    qbo_cost_code_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username + "--" + self.name


class SyncExpenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sync_date_time = models.DateTimeField(auto_now_add=True, blank=True)
    procore_created_id = models.IntegerField(null=True, blank=True)
    qbo_created_id = models.IntegerField(null=True, blank=True)
    procore_project_name = models.CharField(max_length=200, null=True, blank=True)
    procore_vendor_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.user.username + '--' + self.description


class SyncOwnerInvoices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sync_date_time = models.DateTimeField(auto_now_add=True, blank=True)
    procore_owner_invoice_id = models.IntegerField(null=True, blank=True)
    procore_prime_contract_id = models.IntegerField(null=True, blank=True)
    procore_owner_invoice_amount = models.FloatField(null=True, blank=True)
    qbo_customer_id = models.IntegerField(null=True, blank=True)
    qbo_amount = models.FloatField(null=True, blank=True)
    is_synced = models.BooleanField(default=True)
    qbo_customer_invoice_id = models.IntegerField(null=True, blank=True)
    procore_project_name = models.CharField(max_length=255, null=True, blank=True)
    procore_project_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.procore_project_name


class SubContractorInvoices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sync_date_time = models.DateTimeField(auto_now_add=True, blank=True)
    procore_project_name = models.CharField(max_length=255, null=True, blank=True)
    procore_sbc_invoice_no = models.CharField(max_length=255, null=True, blank=True)
    procore_invc_amount = models.FloatField(null=True, blank=True)
    qbo_vendor_name = models.CharField(max_length=255, null=True, blank=True)
    qbo_vendor_id = models.IntegerField(null=True, blank=True)
    qbo_amount = models.FloatField(null=True, blank=True)
    is_synced = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.procore_project_name


class TaskChoices(models.Model):
    TASK_CHOICES = (
        ('PROJECTS', 'PROJECTS'),
        ('VENDORS', 'VENDORS'),
        ('COST-CODE', 'COST CODES'),
        ('CUSTOMER-INV', 'CUSTOMER INVOICES'),
        ('SUB-CONTRACTOR-INV', 'SUB-CONTRACTOR INVOICES'),
        ('CUSTOMER-PAYMENTS', 'CUSTOMER PAYMENTS'),
        ('SUB-CONTRACTOR-PAYMENTS', 'SUBCONTRACTOR PAYMENTS'),
        ('EXPENSE', 'EXPENSES'),
    )
    tasks = models.CharField(max_length=25, choices=TASK_CHOICES, null=True)

    def __str__(self):
        return self.tasks


class SyncUserTasks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choices = models.ManyToManyField(TaskChoices)

    def __str__(self):
        return "%s (%s)" % (
            self.user,
            ", ".join(choices.tasks for choices in self.choices.all()),
        )
