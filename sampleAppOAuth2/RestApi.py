from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from sampleAppOAuth2.auth import get_csrf_token, get_bearer_token, validate_jwt_token, refresh_user_tokens, \
    revoke_qbo_token, revoke_procore_token
from sampleAppOAuth2.common import check_prod_sandbox_credentials_status
from sampleAppOAuth2.models import SyncProjects, SyncVendor, SyncCostCodes, SubContractorInvoices, SyncOwnerInvoices, \
    SyncExpenses, AuthToken
from sampleAppOAuth2.serializers import ProjectSerializer, VendorSerializer, CostCodesSerializer, \
    SubContractorInvoicesSerializer, OwnerInvoicesSerializer, ExpenseSerializer
from sampleAppOAuth2.services import get_user_profile, get_vendors, post_procore_vendor, get_projects, \
    post_procore_project, get_costcodes_standard_list_id, get_standard_costcodes_list, get_subcontractor_invoice, \
    post_vendor_bill, get_all_expenses, read_customer, read_vendor, get_specific_vendor, get_specific_project, \
    post_direct_cost, get_owner_invoices, post_qbo_customer_invoice, get_received_payments, post_contract_payment, \
    get_pay_bills, post_procore_cost_codes


class AuthQboHandler(APIView):
    def get(self, request):
        state = request.GET.get('state', None)
        error = request.GET.get('error', None)
        if error == 'access_denied':
            return redirect('app:index')
        if state is None:
            return HttpResponseBadRequest()
        elif state != get_csrf_token(request):  # validate against CSRF attacks
            return HttpResponse('unauthorized', status=401)

        auth_code = request.GET.get('code', None)
        if auth_code is None:
            return HttpResponseBadRequest()

        bearer = get_bearer_token(auth_code, request)
        realm_id = request.GET.get('realmId', None)

        # Validate JWT tokens only for OpenID scope
        if bearer.idToken is not None:
            if not validate_jwt_token(bearer.idToken, request):
                return HttpResponse('JWT Validation failed. Please try signing in again.')
            else:
                user_email = get_user_profile(bearer.accessToken)
                AuthToken.objects.filter(user_id=request.user.id).update(quickbook_access_token=bearer.accessToken,
                                                                         quickbook_refresh_token=bearer.refreshToken,
                                                                         quickbook_realmid=realm_id,
                                                                         quickbook_username=user_email["email"])
                return redirect('app:Setting')
        else:
            return HttpResponse('Your Bearer token has expired, please initiate Sign In With Intuit flow again')


class RevokeQboUserToken(APIView):

    def get(self, request):
        delete_token = revoke_qbo_token(request)
        if delete_token == 200:
            request.user.authtoken_set.filter(user_id=request.user.id).update(quickbook_access_token="",
                                                                              quickbook_refresh_token="",
                                                                              quickbook_realmid="",
                                                                              quickbook_username="")
            return Response({"message": "Token has been deleted successfully for QBO..!!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "error deleting token for QBO..!!"}, status=status.HTTP_400_BAD_REQUEST)


class RevokeProcoreUserToken(APIView):

    def get(self, request):
        delete_pc_token = revoke_procore_token(request)
        if delete_pc_token == 200:
            request.user.authtoken_set.filter(user_id=request.user.id).update(procore_access_token="",
                                                                              procore_company_id=None,
                                                                              procore_refresh_token="",
                                                                              procore_username="")
            return Response({"message": "Token has been deleted successfully for PROCORE..!!"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"error": "error deleting token for PROCORE..!!"}, status=status.HTTP_400_BAD_REQUEST)


class SearchBySyncDate(APIView, PageNumberPagination):
    """
    for searching Projects, Vendors, CostCodes against specific date range, date format must be in yy/mm/dd i.e (2016-08-01)
    """

    def get(self, request):
        if self.request.query_params.get('q') == "search_projects":
            if self.request.query_params.get('date_to') and self.request.query_params.get('date_from'):
                from_date = datetime.strptime(self.request.query_params.get('date_from'), '%Y-%m-%d').date()
                to_date = datetime.strptime(self.request.query_params.get('date_to'), '%Y-%m-%d').date()
                qs = SyncProjects.objects.filter(user_id=request.user.id, sync_date_time__range=[from_date, to_date])
                results = self.paginate_queryset(qs, request, view=self)
                serializer = ProjectSerializer(results, many=True)
                return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "search_vendors":
            if self.request.query_params.get('date_to') and self.request.query_params.get('date_from'):
                from_date = datetime.strptime(self.request.query_params.get('date_from'), '%Y-%m-%d').date()
                to_date = datetime.strptime(self.request.query_params.get('date_to'), '%Y-%m-%d').date()
                qs = SyncVendor.objects.filter(user_id=request.user.id, sync_date_time__range=[from_date, to_date])
                results = self.paginate_queryset(qs, request, view=self)
                serializer = VendorSerializer(results, many=True)
                return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "search_costcodes":
            if self.request.query_params.get('date_to') and self.request.query_params.get('date_from'):
                from_date = datetime.strptime(self.request.query_params.get('date_from'), '%Y-%m-%d').date()
                to_date = datetime.strptime(self.request.query_params.get('date_to'), '%Y-%m-%d').date()
                qs = SyncCostCodes.objects.filter(user_id=request.user.id, sync_date_time__range=[from_date, to_date])
                results = self.paginate_queryset(qs, request, view=self)
                serializer = CostCodesSerializer(results, many=True)
                return self.get_paginated_response(serializer.data)

        return Response({"message": "QueryParams are missing"}, status=400)


class GetListings(APIView, PageNumberPagination):
    """
    for getting all Projects, Vendors, CostCodes, Expenses, OwnerInvoices, SubContractorInvoices against specific user
    """

    def get(self, request):
        if self.request.query_params.get('q') == "get_projects":
            qs = SyncProjects.objects.filter(user_id=request.user.id)
            results = self.paginate_queryset(qs, request, view=self)
            serializer = ProjectSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "get_vendors":
            qs = SyncVendor.objects.filter(user_id=request.user.id)
            results = self.paginate_queryset(qs, request, view=self)
            serializer = VendorSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "get_costcodes":
            qs = SyncCostCodes.objects.filter(user_id=request.user.id)
            results = self.paginate_queryset(qs, request, view=self)
            serializer = CostCodesSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "get_expenses":
            qs = SyncExpenses.objects.filter(user_id=request.user.id)
            results = self.paginate_queryset(qs, request, view=self)
            serializer = ExpenseSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "get_owner_invoices":
            qs = SyncOwnerInvoices.objects.filter(user_id=request.user.id)
            results = self.paginate_queryset(qs, request, view=self)
            serializer = OwnerInvoicesSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        elif self.request.query_params.get('q') == "get_sbc_invoices":
            qs = SubContractorInvoices.objects.filter(user_id=request.user.id)
            results = self.paginate_queryset(qs, request, view=self)
            serializer = SubContractorInvoicesSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        return Response({"message": "QueryParams are missing"}, status=400)


class AreTokensExists(APIView):

    def get(self, request):
        try:
            user_ = AuthToken.objects.get(user_id=self.request.user.id)
            if user_.procore_access_token is None and user_.quickbook_access_token is None:
                return Response({"is_procore_token": False, "is_quickbook_token": False})
            if user_.quickbook_access_token is None:
                return Response({"is_quickbook_token": False})
            if user_.procore_access_token is None:
                return Response({"is_procore_token": False})
            return Response({"response": True})
        except ObjectDoesNotExist:
            return Response({"error": "ObjectDoesNotExist"}, status=status.HTTP_400_BAD_REQUEST)


class SyncProcoreVendors(APIView):

    def get(self, request):
        try:
            user_ = AuthToken.objects.get(user_id=self.request.user.id)
            tokens_res = refresh_user_tokens(user_, request)
            if tokens_res:
                active_credentials = check_prod_sandbox_credentials_status(request)
                vendors_response = get_vendors(user_.procore_access_token, user_.procore_company_id,
                                               active_credentials.get("BASE_URL"))
                for vendor in vendors_response:
                    if SyncVendor.objects.filter(user_id=self.request.user.id, procore_vendor_id=vendor['id']).exists():
                        pass
                    else:
                        res = post_procore_vendor(access_token=user_.quickbook_access_token,
                                                  realm_id=user_.quickbook_realmid,
                                                  vendor_id=vendor['id'],
                                                  company_name=vendor['company'])
                        if res:
                            SyncVendor.objects.create(user_id=self.request.user.id,
                                                      vendor_company=str(vendor['id']) + vendor['name'],
                                                      procore_vendor_id=vendor['id'], qbo_vendor_id=res)
                return Response({"response": True})
        except Exception as e:
            return Response({"error": str(e)})


class SyncProcoreProjects(APIView):

    def get(self, request):
        try:
            user_ = AuthToken.objects.get(user_id=self.request.user.id)
            tokens_res = refresh_user_tokens(user_, self.request)
            if tokens_res:
                active_credentials = check_prod_sandbox_credentials_status(self.request)
                projects_response = get_projects(user_.procore_access_token, user_.procore_company_id,
                                                 active_credentials.get("BASE_URL"))
                for project in projects_response:
                    if SyncProjects.objects.filter(user_id=self.request.user.id,
                                                   procore_project_id=project['id']).exists():
                        pass
                    else:
                        res = post_procore_project(access_token=user_.quickbook_access_token,
                                                   realm_id=user_.quickbook_realmid,
                                                   project_name=project['name'], project_id=project['id'],
                                                   company_name=project['company']['name'])
                        if res:
                            SyncProjects.objects.create(user_id=self.request.user.id,
                                                        project_name=str(project['id']) + project['name'],
                                                        procore_project_id=project['id'], qbo_customer_id=res)
                return Response({"response": True})
        except Exception as e:
            print("exception here....", str(e))
            return Response({"error": str(e)})


class SyncProcoreCostCodes(APIView):
    def get(self, request):
        user_ = AuthToken.objects.get(user_id=request.user.id)
        tokens_res = refresh_user_tokens(user_, request)
        if tokens_res:
            active_credentials = check_prod_sandbox_credentials_status(request)
            res_codes = get_costcodes_standard_list_id(user_.procore_access_token, user_.procore_company_id,
                                                       active_credentials.get("BASE_URL"))
            for costcode_id in res_codes:
                standard_cost_codes = get_standard_costcodes_list(user_.procore_access_token,
                                                                  user_.procore_company_id,
                                                                  costcode_id["id"],
                                                                  active_credentials.get("BASE_URL"))
                for codes in standard_cost_codes:
                    if SyncCostCodes.objects.filter(user_id=request.user.id, costcode_id=codes["id"]).exists():
                        pass
                    else:
                        # This condition will sync cost-codes along with divisions
                        if self.request.query_params.get('q') == "sync_with_divisions":
                            res = post_procore_cost_codes(access_token=user_.quickbook_access_token,
                                                          realm_id=user_.quickbook_realmid,
                                                          item_name=str(codes["id"]) + codes["name"])
                            if res:
                                SyncCostCodes.objects.create(user_id=request.user.id, parent_id=codes["parent_id"],
                                                             costcode_id=codes["id"],
                                                             name=str(codes["id"]) + codes["name"],
                                                             full_code=codes["full_code"], qbo_cost_code_id=res)
                        else:
                            # it only sync parental cost codes
                            if codes["parent_id"] is None:
                                res = post_procore_cost_codes(access_token=user_.quickbook_access_token,
                                                              realm_id=user_.quickbook_realmid,
                                                              item_name=str(codes["id"]) + codes["name"])
                                if res:
                                    SyncCostCodes.objects.create(user_id=request.user.id, costcode_id=codes["id"],
                                                                 name=str(codes["id"]) + codes["name"],
                                                                 full_code=codes["full_code"], qbo_cost_code_id=res)

            return Response({"response": True}, status=status.HTTP_200_OK)


class SyncProcoreSubcontractorInvoice(APIView):
    def get(self, request):
        try:
            user_ = AuthToken.objects.get(user_id=self.request.user.id)
            tokens_res = refresh_user_tokens(user_, request)
            if tokens_res:
                projects_response = SyncProjects.objects.filter(user=self.request.user.id)
                active_credentials = check_prod_sandbox_credentials_status(request)
                for project in projects_response:
                    res = get_subcontractor_invoice(user_.procore_access_token, project.procore_project_id,
                                                    active_credentials.get("BASE_URL"))

                    for payment_response in res:
                        bill_id = post_vendor_bill(access_token=user_.quickbook_access_token,
                                                   realm_id=user_.quickbook_realmid,
                                                   vendor_id=266,
                                                   customer_id=284,
                                                   total_amt=payment_response["summary"][
                                                       "total_completed_and_stored_to_date"])
                        if bill_id:
                            SubContractorInvoices.objects.create(
                                user_id=self.request.user.id,
                                procore_project_name=project.project_name,
                                procore_sbc_invoice_no=payment_response["invoice_number"],
                                procore_invc_amount=payment_response["summary"][
                                    "total_completed_and_stored_to_date"],
                                qbo_vendor_name="227569Dobnazbul Gobbradyr - 504ee56f-5ae1-44a2-95dd-049b1c47adc8",
                                qbo_vendor_id=266, qbo_amount=payment_response["summary"][
                                    "total_completed_and_stored_to_date"])
                    # TODO once getting vendor_name from response uncomment these lines
                    # for response in res:
                    # if "vendor_name" in response:
                    #     vendor_ids = SyncVendor.objects.filter(vendor_company=response["vendor_name"]).values(
                    #         "qbo_vendor_id")
                    #     for vendor in vendor_ids:
                    #         print("res......", vendor.qbo_vendor_id)
                return Response({"response": True})
        except Exception as e:
            return Response({"error": str(e)})


class SyncQboExpenses(APIView):

    def get(self, request):
        try:
            user_ = AuthToken.objects.get(user_id=self.request.user.id)
            tokens_res = refresh_user_tokens(user_, request)
            if tokens_res:
                query_response, status = get_all_expenses(user_.quickbook_access_token, user_.quickbook_realmid)
                active_credentials = check_prod_sandbox_credentials_status(request)
                for vendor in query_response:
                    # check if specific expense ID already exists against requested user
                    if SyncExpenses.objects.filter(user_id=request.user.id, qbo_created_id=vendor["Id"]).exists():
                        pass
                    else:
                        # only get those objects which both having Customer ID Vendor ID
                        if "EntityRef" in vendor:
                            for customer in vendor["Line"]:
                                if "AccountBasedExpenseLineDetail" in customer:
                                    if "CustomerRef" in customer["AccountBasedExpenseLineDetail"]:
                                        customer_id, status = read_customer(user_.quickbook_access_token,
                                                                            user_.quickbook_realmid,
                                                                            customer["AccountBasedExpenseLineDetail"][
                                                                                "CustomerRef"]["value"])
                                        vendor_id, status = read_vendor(user_.quickbook_access_token,
                                                                        user_.quickbook_realmid,
                                                                        vendor["EntityRef"]["value"])
                                        if "Suffix" in customer_id and "Suffix" in vendor_id:
                                            get_vendor = get_specific_vendor(access_token=user_.procore_access_token,
                                                                             company_id=user_.procore_company_id,
                                                                             vendor_id=vendor_id["Suffix"],
                                                                             base_url=active_credentials.get(
                                                                                 "BASE_URL"))
                                            get_project = get_specific_project(access_token=user_.procore_access_token,
                                                                               company_id=user_.procore_company_id,
                                                                               project_id=customer_id["Suffix"],
                                                                               base_url=active_credentials.get(
                                                                                   "BASE_URL"))

                                            if "PrivateNote" in vendor:
                                                res = post_direct_cost(access_token=user_.procore_access_token,
                                                                       vendor_id=vendor_id["Suffix"],
                                                                       project_id=customer_id["Suffix"],
                                                                       description=vendor["PrivateNote"],
                                                                       txn_date=vendor["TxnDate"],
                                                                       base_url=active_credentials.get("BASE_URL"))
                                                SyncExpenses.objects.create(user_id=request.user.id,
                                                                            procore_created_id=res["id"],
                                                                            qbo_created_id=vendor["Id"],
                                                                            procore_project_name=get_project[
                                                                                "display_name"],
                                                                            procore_vendor_name=get_vendor["name"],
                                                                            description=vendor["PrivateNote"])
                                            else:
                                                res = post_direct_cost(access_token=user_.procore_access_token,
                                                                       vendor_id=vendor_id["Suffix"],
                                                                       project_id=customer_id["Suffix"],
                                                                       description="Not Provided",
                                                                       txn_date=vendor["TxnDate"],
                                                                       base_url=active_credentials.get("BASE_URL"))
                                                SyncExpenses.objects.create(user_id=request.user.id,
                                                                            procore_created_id=res["id"],
                                                                            qbo_created_id=vendor["Id"],
                                                                            procore_project_name=get_project[
                                                                                "display_name"],
                                                                            procore_vendor_name=get_vendor["name"],
                                                                            description="Not Provided")

                return Response({"response": True})
        except Exception as e:
            return Response({"error": str(e)})


class SyncProcoreOwnerInvoices(APIView):

    def get(self, request):
        try:
            user_ = AuthToken.objects.get(user_id=request.user.id)
            tokens_res = refresh_user_tokens(user_, request)
            if tokens_res:
                projects_response = SyncProjects.objects.filter(user=request.user.id)
                active_credentials = check_prod_sandbox_credentials_status(request)
                for project in projects_response:
                    res = get_owner_invoices(user_.procore_access_token, project.procore_project_id,
                                             active_credentials.get("BASE_URL"))
                    if res:
                        for response in res:
                            if SyncOwnerInvoices.objects.filter(user=request.user.id,
                                                                procore_owner_invoice_id=response["id"]).exists():
                                pass
                            else:
                                invoice_id = post_qbo_customer_invoice(
                                    access_token=user_.quickbook_access_token,
                                    realm_id=user_.quickbook_realmid,
                                    item_ref_value=self.request.query_params.get(
                                        'costcode_id') if self.request.query_params.get('costcode_id') else "1",
                                    customer_id=project.qbo_customer_id,
                                    total_amount_paid=response["g702"]["current_payment_due"],
                                    description=self.request.query_params.get(
                                        'inv_desc') if self.request.query_params.get(
                                        'inv_desc') else "Procore Invoice #" + response["invoice_number"])
                                if invoice_id:
                                    SyncOwnerInvoices.objects.create(user_id=request.user.id,
                                                                     procore_owner_invoice_id=response["id"],
                                                                     procore_prime_contract_id=response["contract"][
                                                                         "id"],
                                                                     procore_owner_invoice_amount=response["g702"][
                                                                         "current_payment_due"],
                                                                     qbo_customer_id=project.qbo_customer_id,
                                                                     qbo_customer_invoice_id=invoice_id,
                                                                     qbo_amount=response["g702"][
                                                                         "current_payment_due"],
                                                                     procore_project_name=project.project_name,
                                                                     procore_project_id=project.procore_project_id)
                return Response({"response": True})
        except Exception as e:
            return Response({"error": str(e)})


class SyncQboReceivedPayments(APIView):

    def get(self, request):
        """
        This method is used to sync the payment into Procore against the owner invoices which are placed in QBO
        """
        try:
            user_ = AuthToken.objects.get(user_id=request.user.id)
            tokens_res = refresh_user_tokens(user_, request)
            active_credentials = check_prod_sandbox_credentials_status(request)
            if tokens_res:
                payments_, status = get_received_payments(access_token=user_.quickbook_access_token,
                                                          realm_id=user_.quickbook_realmid)
                for payment in payments_:
                    if "CustomerRef" in payment:
                        owner_invoices_res = SyncOwnerInvoices.objects.filter(
                            qbo_customer_id=payment["CustomerRef"]["value"])
                        if owner_invoices_res:
                            for data in owner_invoices_res:
                                post_contract_payment(access_token=user_.procore_access_token,
                                                      project_id=data.procore_project_id,
                                                      txn_date=payment["TxnDate"],
                                                      invoice_no=data.procore_owner_invoice_id,
                                                      contract_id=data.procore_prime_contract_id,
                                                      amount=payment["TotalAmt"],
                                                      base_url=active_credentials.get("BASE_URL"))
                return Response({"response": True})
        except Exception as e:
            return Response({"error": str(e)})


class SyncQboPayBills(APIView):

    def get(self, request):
        user_ = AuthToken.objects.get(user_id=request.user.id)
        tokens_res = refresh_user_tokens(user_, request)
        if tokens_res:
            bills_, status = get_pay_bills(access_token=user_.quickbook_access_token, realm_id=user_.quickbook_realmid)
            for bill_data in bills_:
                if "VendorRef" in bill_data:
                    sbc_invoices_res = SubContractorInvoices.objects.filter(
                        qbo_vendor_id=bill_data["VendorRef"]["value"])
                    if sbc_invoices_res:
                        for data in sbc_invoices_res:
                            print("data her5e...", data)

            return Response({"response": True})
