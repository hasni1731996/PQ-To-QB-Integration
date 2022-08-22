import urllib

import cryptocode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.views import View

from sampleAppOAuth2 import getDiscoveryDocument
from sampleAppOAuth2.auth import make_authorization_url, get_token, get_csrf_token
from sampleAppOAuth2.common import check_prod_sandbox_credentials_status
from sampleAppOAuth2.constants import PASSWORD_SECRET_KEY
from sampleAppOAuth2.models import AuthToken, SyncProjects, SyncVendor, SyncCostCodes, SubContractorInvoices, \
    SyncOwnerInvoices
from sampleAppOAuth2.services import (get_procore_user_name, get_procore_company_against_user)


class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        if request.method == "POST":
            user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
            if user is not None:
                login(request, user)
                return redirect('app:Setting')
            else:
                return render(request, 'login.html', context={"errors": "Login credentials are wrong"})


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        try:
            if request.method == 'POST':
                user = User()
                user.username = request.POST.get('username')
                user.set_password(request.POST.get('password'))
                user.email = request.POST.get('email')
                user.save()
                if user:
                    auth_user = AuthToken.objects.create(user_id=user.id)
                    auth_user.user_encrypted_password = cryptocode.encrypt(request.POST.get('password'),
                                                                           PASSWORD_SECRET_KEY)
                    auth_user.save()
                    login(request, user)
                    return redirect('app:DashBoard')
                else:
                    return render(request, "register.html", context={"errors": "Error creating user"})
        except Exception as e:
            return render(request, "register.html", context={"errors": str(e)})


class AppSettingView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'appsetting.html')


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        return redirect('app:index')


class DashboardView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'index.html')


class SettingView(LoginRequiredMixin, View):

    def get(self, request):
        if request.method == 'GET':
            try:
                user_ = AuthToken.objects.get(user_id=request.user.id)
                return render(request, 'setting.html', context={"procore_username": user_.procore_username,
                                                                "quickbook_username": user_.quickbook_username})
            except Exception as e:
                return render(request, 'setting.html', context={"error": str(e)})


class SyncSettingView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'sync-setting.html')


class CustomersView(LoginRequiredMixin, View):

    def get(self, request):
        res = SyncProjects.objects.filter(user_id=request.user.id)
        return render(request, 'customers.html', context={"customers": res})


class VendorsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        res = SyncVendor.objects.filter(user_id=request.user.id)
        return render(request, 'vendors.html', context={"vendors": res})


class CustomerInvoicesView(LoginRequiredMixin, View):

    def get(self, request):
        res = SyncOwnerInvoices.objects.filter(user_id=request.user.id)
        return render(request, 'cust_invoices.html', context={"cust_invoices": res})


class SubContractorInvoiceView(LoginRequiredMixin, View):

    def get(self, request):
        res = SubContractorInvoices.objects.filter(user_id=request.user.id)
        return render(request, 'sub_invoices.html', context={"sub_contract_invoices": res})


class CustomerPaymentsView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'cust_payments.html')


class SubContractorPaymentsView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'sub_payments.html')


class ExpensesView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'sync-expenses.html')


class CostCodesView(LoginRequiredMixin, View):

    def get(self, request):
        res = SyncCostCodes.objects.filter(user_id=request.user.id)
        return render(request, 'costcodes.html', context={"costcodes": res})


class SyncLogView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'synclog.html')


class GetQboApp(LoginRequiredMixin, View):
    def get(self, request):
        try:
            active_credentials = check_prod_sandbox_credentials_status(request)
            if active_credentials:
                url = getDiscoveryDocument.auth_endpoint
                scope = ' '.join(settings.GET_APP_SCOPES)  # Scopes are required to be sent delimited by a space
                params = {'scope': scope,
                          'redirect_uri': active_credentials.get('qbo_redirect_url'),
                          'response_type': 'code', 'state': get_csrf_token(request),
                          'client_id': active_credentials.get('qbo_app_id')}
                url += '?' + urllib.parse.urlencode(params)
                return redirect(url)
        except ObjectDoesNotExist:
            return HttpResponse("App credentials are not provided for `QuickBook` or have not being active yet.!!",
                                status=400)


class LoginToProcore(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            active_credentials = check_prod_sandbox_credentials_status(request)
            if active_credentials:
                return redirect(make_authorization_url(active_credentials))
        except ObjectDoesNotExist:
            return HttpResponse("App credentials are not provided for `PROCORE` or have not being active yet.!!",
                                status=400)


class ProcoreAppCallback(LoginRequiredMixin, View):

    def get(self, request):
        if request.method == "GET":
            code = request.GET.get('code')
            access_token, refresh_token, created_at = get_token(code, request)
            active_credentials = check_prod_sandbox_credentials_status(request)
            procore_user = get_procore_user_name(access_token, active_credentials.get("BASE_URL"))
            user_company_id = get_procore_company_against_user(access_token, active_credentials.get("BASE_URL"))
            AuthToken.objects.filter(user_id=request.user.id).update(procore_access_token=access_token,
                                                                     procore_refresh_token=refresh_token,
                                                                     procore_company_id=user_company_id[0]["id"],
                                                                     procore_username=procore_user)
            return redirect('app:Setting')
