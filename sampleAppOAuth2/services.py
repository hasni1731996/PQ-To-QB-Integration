import string

import requests
import json
import random

from django.conf import settings

from sampleAppOAuth2.constants import QBO_MINOR_VERSION


def get_user_profile(access_token):
    auth_header = 'Bearer ' + access_token
    headers = {'Accept': 'application/json', 'Authorization': auth_header, 'accept': 'application/json'}
    r = requests.get(settings.SANDBOX_PROFILE_URL, headers=headers)
    response = json.loads(r.text)
    return response


def get_all_expenses(access_token, realm_id):
    route = '/v3/company/{0}/query?query=select * from Purchase&minorversion={1}'.format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'accept': 'application/json'}
    r = requests.get(settings.SANDBOX_QBO_BASEURL + route, headers=headers)
    status_code = r.status_code
    if status_code != 200:
        response = ''
        return response, status_code
    response = json.loads(r.text)
    return response["QueryResponse"]["Purchase"], status_code


def read_customer(access_token, realm_id, customer_id):
    route = '/v3/company/{0}/customer/{1}?minorversion={2}'.format(realm_id, customer_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'accept': 'application/json'}
    r = requests.get(settings.SANDBOX_QBO_BASEURL + route, headers=headers)
    status_code = r.status_code
    if status_code != 200:
        response = ''
        return response, status_code
    response = json.loads(r.text)
    return response["Customer"], status_code


def read_vendor(access_token, realm_id, vendor_id):
    route = '/v3/company/{0}/vendor/{1}?minorversion={2}'.format(realm_id, vendor_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'accept': 'application/json'}
    r = requests.get(settings.SANDBOX_QBO_BASEURL + route, headers=headers)
    status_code = r.status_code
    if status_code != 200:
        response = ''
        return response, status_code
    response = json.loads(r.text)
    return response["Vendor"], status_code


def get_received_payments(access_token, realm_id):
    route = '/v3/company/{0}/query?query=select * from Payment&minorversion={1}'.format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'accept': 'application/json'}
    r = requests.get(settings.SANDBOX_QBO_BASEURL + route, headers=headers)
    status_code = r.status_code
    if status_code != 200:
        response = ''
        return response, status_code
    response = json.loads(r.text)
    return response["QueryResponse"]["Payment"], status_code


def get_pay_bills(access_token, realm_id):
    route = '/v3/company/{0}/query?query=select * from billpayment&minorversion={1}'.format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'accept': 'application/json'}
    r = requests.get(settings.SANDBOX_QBO_BASEURL + route, headers=headers)
    status_code = r.status_code
    if status_code != 200:
        response = ''
        return response, status_code
    response = json.loads(r.text)
    return response["QueryResponse"]["BillPayment"], status_code


def post_procore_project(access_token, realm_id, project_name, project_id, company_name):
    route = "/v3/company/{0}/customer?minorversion={1}".format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'Content-type': 'application/json', 'accept': 'application/json'}
    data = {
        "DisplayName": project_name,
        "Suffix": str(project_id),
        "CompanyName": company_name
    }
    r = requests.post(settings.SANDBOX_QBO_BASEURL + route, headers=headers, data=json.dumps(data))
    if r.status_code != 200:
        response = ''
        return response
    response = json.loads(r.text)
    return response["Customer"]["Id"]


def post_procore_vendor(access_token, realm_id, vendor_id, company_name):
    route = "/v3/company/{0}/vendor?minorversion={1}".format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'Content-type': 'application/json', 'accept': 'application/json'}
    data = {
        "DisplayName": company_name,
        "Suffix": str(vendor_id),
        "CompanyName": company_name
    }
    r = requests.post(settings.SANDBOX_QBO_BASEURL + route, headers=headers, data=json.dumps(data))
    if r.status_code != 200:
        response = ''
        return response
    response = json.loads(r.text)
    return response["Vendor"]["Id"]


def post_procore_cost_codes(access_token, realm_id, item_name):
    route = "/v3/company/{0}/item?minorversion={1}".format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'Content-type': 'application/json', 'accept': 'application/json'}
    data = {
        "Name": item_name,
        "IncomeAccountRef": {
            "name": "Sales of Product Income",
            "value": "79"
        },
        "Type": "Service",
        "ExpenseAccountRef": {
            "name": "Cost of Goods Sold",
            "value": "80"
        }
    }
    r = requests.post(settings.SANDBOX_QBO_BASEURL + route, headers=headers, data=json.dumps(data))
    if r.status_code != 200:
        response = ''
        return response
    response = json.loads(r.text)
    return response["Item"]["Id"]


def post_qbo_customer_invoice(access_token, realm_id, item_ref_value, customer_id, total_amount_paid, description):
    route = "/v3/company/{0}/invoice?minorversion={1}".format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'Content-type': 'application/json', 'accept': 'application/json'}
    data = {
        'Line': [
            {
                'DetailType': 'SalesItemLineDetail',
                'Amount': total_amount_paid,
                'Description': description,
                'SalesItemLineDetail': {
                    'ItemRef': {
                        'value': item_ref_value
                    }
                }
            }
        ],
        'CustomerRef': {
            'value': customer_id
        }
    }
    r = requests.post(settings.SANDBOX_QBO_BASEURL + route, headers=headers, data=json.dumps(data))
    response = json.loads(r.text)
    return response["Invoice"]["DocNumber"]


def post_vendor_bill(access_token, realm_id, vendor_id, customer_id, total_amt):
    route = "/v3/company/{0}/bill?minorversion={1}".format(realm_id, QBO_MINOR_VERSION)
    auth_header = 'Bearer ' + access_token
    headers = {'Authorization': auth_header, 'Content-type': 'application/json', 'accept': 'application/json'}
    data = {
        "Line": [
            {
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": float(total_amt),
                "Id": "1",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                        "value": "7"
                    },
                    "BillableStatus": "HasBeenBilled",
                    "CustomerRef": {
                        "value": customer_id
                    }
                }
            }
        ],
        "VendorRef": {
            "value": vendor_id
        }
    }

    r = requests.post(settings.SANDBOX_QBO_BASEURL + route, headers=headers, data=json.dumps(data))
    response = json.loads(r.text)
    return response["Bill"]["Id"]


def get_procore_user_name(access_token, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/me", headers=headers)
    me_json = response.json()
    return me_json['login']


def get_procore_company_against_user(access_token, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/companies", headers=headers)
    return response.json()


def get_projects(access_token, company_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/projects?company_id={0}".format(company_id),
                            headers=headers)  # comapny_id here needs to be provided from user
    return response.json()


def get_vendors(access_token, company_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/vendors?company_id={0}".format(company_id),
                            headers=headers)  # comapny_id here needs to be provided from user
    return response.json()


def get_costcodes_standard_list_id(access_token, company_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/standard_cost_code_lists?company_id={0}".format(company_id),
                            headers=headers)
    return response.json()


def get_standard_costcodes_list(access_token, company_id, standard_cost_code_list_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(
        base_url + "/rest/v1.0/standard_cost_codes?company_id={0}&standard_cost_code_list_id={1}".format(company_id,
                                                                                                         standard_cost_code_list_id),

        headers=headers)
    return response.json()


def get_specific_project(access_token, company_id, project_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/projects/{0}?company_id={1}".format(project_id, company_id),
                            headers=headers)
    return response.json()


def get_specific_vendor(access_token, company_id, vendor_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(
        base_url + "/rest/v1.0/vendors/{0}?company_id={1}&view=compact".format(vendor_id, company_id),
        headers=headers)
    return response.json()


def get_subcontractor_invoice(access_token, project_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(base_url + "/rest/v1.0/requisitions?project_id={0}".format(project_id),
                            headers=headers)
    return response.json()


def post_direct_cost(access_token, vendor_id, project_id, description, txn_date, base_url):
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    post_data = {
        "item": {
            "description": description,
            "direct_cost_date": txn_date,
            "payment_date": txn_date,
            "received_date": txn_date,
            "invoice_number": "Invoice # " + ''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
            "vendor_id": int(vendor_id),
            "direct_cost_type": "invoice"
        }
    }
    response = requests.post(base_url + "/rest/v1.0/projects/{0}/direct_costs".format(int(project_id)),
                             headers=headers, data=json.dumps(post_data))
    return response.json()


def post_contract_payment(access_token, project_id, txn_date, invoice_no, contract_id, amount, base_url):
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}

    data = {
        "project_id": project_id,
        "contract_id": contract_id,
        "contract_payment": {
            "date": txn_date,
            "invoice_number": invoice_no,
            "invoice_date": txn_date,
            "amount": amount
        }
    }
    response = requests.post(base_url + "/rest/v1.0/contract_payments", headers=headers, data=json.dumps(data))
    return response.json()


def get_owner_invoices(access_token, project_id, base_url):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(
        base_url + "/rest/v1.0/payment_applications?project_id={0}&filters[status]=Approved".format(project_id),
        headers=headers)
    return response.json()
