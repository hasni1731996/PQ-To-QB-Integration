from django.contrib import admin
from .models import AuthToken, SyncProjects, SyncVendor, SyncCostCodes, SyncExpenses, SyncOwnerInvoices, \
    SubContractorInvoices, TaskChoices, SyncUserTasks

admin.site.register(AuthToken)
admin.site.register(SyncProjects)
admin.site.register(SyncVendor)
admin.site.register(SyncCostCodes)
admin.site.register(SyncExpenses)
admin.site.register(SyncOwnerInvoices)
admin.site.register(SubContractorInvoices)
admin.site.register(TaskChoices)
admin.site.register(SyncUserTasks)
