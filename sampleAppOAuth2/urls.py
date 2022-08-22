from django.conf.urls import url

from . import views
from . import RestApi
urlpatterns = [
    url(r'^$', views.LoginView.as_view(), name='index'),
    url(r'^getAppNow/$', views.GetQboApp.as_view(), name='getAppNow'),
    url(r'^authCodeHandler/$', RestApi.AuthQboHandler.as_view(), name='authCodeHandler'),

    # main app urls
    url(r'^signup/', views.RegisterView.as_view(), name='RegisterPage'),
    url(r'^logout/$', views.LogoutView.as_view(), name='LogoutView'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name='DashBoard'),
    url(r'^setting/$', views.SettingView.as_view(), name='Setting'),
    url(r'^appsetting/$', views.AppSettingView.as_view(), name='AppSetting'),
    url(r'^sync-setting/$', views.SyncSettingView.as_view(), name='SyncSetting'),
    url(r'^check-auth/$', RestApi.AreTokensExists.as_view()),
    url(r'^sync-projects/$', RestApi.SyncProcoreProjects.as_view()),
    url(r'^sync-vendors/$', RestApi.SyncProcoreVendors.as_view()),
    url(r'^customers/$', views.CustomersView.as_view(), name='Customers'),
    url(r'^api/search/$', RestApi.SearchBySyncDate.as_view()),
    url(r'^vendors/$', views.VendorsView.as_view(), name='Vendors'),
    url(r'^custInv/$', views.CustomerInvoicesView.as_view(), name='CustInvoices'),
    url(r'^subInv/$', views.SubContractorInvoiceView.as_view(), name='SubInvoices'),
    url(r'^custPay/$', views.CustomerPaymentsView.as_view(), name='CustPayments'),
    url(r'^subPay/$', views.SubContractorPaymentsView.as_view(), name='SubPayment'),
    url(r'^expenses/$', views.ExpensesView.as_view(), name='Expenses'),
    url(r'^costcodes/$', views.CostCodesView.as_view(), name='CostCodes'),
    url(r'^synclog/$', views.SyncLogView.as_view(), name='SyncLog'),
    url(r'^sync-cost-codes/$', RestApi.SyncProcoreCostCodes.as_view()),
    url(r'^get-listings/$', RestApi.GetListings.as_view()),
    url(r'^sync-subcontractor-invoice/$', RestApi.SyncProcoreSubcontractorInvoice.as_view()),
    url(r'^sync-expenses/$', RestApi.SyncQboExpenses.as_view()),
    url(r'^sync-owner-invoices/$', RestApi.SyncProcoreOwnerInvoices.as_view()),
    url(r'^sync-payment/$', RestApi.SyncQboReceivedPayments.as_view()),
    url(r'^sync-pay-bills/$', RestApi.SyncQboPayBills.as_view()),
    url(r'^revoke-qbo-user/$', RestApi.RevokeQboUserToken.as_view()),

    # Procore urls
    url(r'^getprocoreapp/$', views.LoginToProcore.as_view(), name='login_procore'),
    url(r'^users/home$', views.ProcoreAppCallback.as_view(), name='procore_home'),
    url(r'^revoke-procore-user/$', RestApi.RevokeProcoreUserToken.as_view()),
]
