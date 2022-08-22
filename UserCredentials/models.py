from django.contrib.auth.models import User
from django.db import models


class UserAppCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # SANDBOX Credentials stored here for PROCORE
    sandbox_procore_app_id = models.CharField(max_length=255, null=True, blank=True)
    sandbox_procore_app_secret = models.CharField(max_length=255, null=True, blank=True)
    sandbox_procore_redirect_url = models.CharField(max_length=255, null=True, blank=True)
    # PRODUCTION Credentials string here for PROCORE
    prod_procore_app_id = models.CharField(max_length=255, null=True, blank=True)
    prod_procore_app_secret = models.CharField(max_length=255, null=True, blank=True)
    prod_procore_redirect_url = models.CharField(max_length=255, null=True, blank=True)
    # SANDBOX Credentials stored here for QBO
    sandbox_qbo_app_id = models.CharField(max_length=255, null=True, blank=True)
    sandbox_qbo_app_secret = models.CharField(max_length=255, null=True, blank=True)
    sandbox_qbo_redirect_url = models.CharField(max_length=255, null=True, blank=True)
    # PRODUCTION Credentials stored here for QBO
    prod_qbo_app_id = models.CharField(max_length=255, null=True, blank=True)
    prod_qbo_app_secret = models.CharField(max_length=255, null=True, blank=True)
    prod_qbo_redirect_url = models.CharField(max_length=255, null=True, blank=True)
    is_sandbox_active = models.BooleanField(default=False)
    is_prod_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
