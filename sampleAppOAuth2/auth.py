import urllib

import requests
import base64
import json
import random

from jose import jwk
from datetime import datetime

from django.conf import settings

from sampleAppOAuth2 import getDiscoveryDocument
from sampleAppOAuth2.common import check_prod_sandbox_credentials_status
from sampleAppOAuth2.models import Bearer


# token can either be an accessToken or a refreshToken
def revoke_qbo_token(request):
    active_credentials = check_prod_sandbox_credentials_status(request)
    if active_credentials:
        revoke_endpoint = getDiscoveryDocument.revoke_endpoint
        auth_header = 'Basic ' + string_to_base64(
            active_credentials.get('qbo_app_id') + ':' + active_credentials.get('qbo_app_secret'))
        headers = {'Accept': 'application/json', 'content-type': 'application/json', 'Authorization': auth_header}
        payload = {'token': request.user.authtoken_set.get(user_id=request.user.id).quickbook_refresh_token}
        r = requests.post(revoke_endpoint, json=payload, headers=headers)

        if r.status_code >= 500:
            return 'internal_server_error'
        elif r.status_code >= 400:
            return 'Token is incorrect.'
        else:
            return r.status_code


def revoke_procore_token(request):
    active_credentials = check_prod_sandbox_credentials_status(request)
    if active_credentials:
        post_data = {"client_id": active_credentials.get('procore_app_id'),
                     "client_secret": active_credentials.get('procore_app_secret'),
                     "token": request.user.authtoken_set.get(user_id=request.user.id).procore_access_token
                     }
        response = requests.post(active_credentials.get("BASE_URL") + "/oauth/revoke", data=post_data)
        if response.status_code >= 500:
            return 'internal_server_error'
        elif response.status_code >= 400:
            return 'Token is incorrect.'
        else:
            return response.status_code


def get_bearer_token(auth_code, request):
    active_credentials = check_prod_sandbox_credentials_status(request)
    if active_credentials:
        token_endpoint = getDiscoveryDocument.token_endpoint
        auth_header = 'Basic ' + string_to_base64(
            active_credentials.get('qbo_app_id') + ':' + active_credentials.get('qbo_app_secret'))
        headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',
                   'Authorization': auth_header}
        payload = {
            'code': auth_code,
            'redirect_uri': active_credentials.get('qbo_redirect_url'),
            'grant_type': 'authorization_code'
        }
        r = requests.post(token_endpoint, data=payload, headers=headers)
        if r.status_code != 200:
            return r.text
        bearer_raw = json.loads(r.text)

        if 'id_token' in bearer_raw:
            id_token = bearer_raw['id_token']
        else:
            id_token = None

        return Bearer(bearer_raw['x_refresh_token_expires_in'], bearer_raw['access_token'], bearer_raw['token_type'],
                      bearer_raw['refresh_token'], bearer_raw['expires_in'], idToken=id_token)


def get_bearer_token_from_refresh_token(refresh_token, active_credentials):
    token_endpoint = getDiscoveryDocument.token_endpoint
    auth_header = 'Basic ' + string_to_base64(
        active_credentials.get('qbo_app_id') + ':' + active_credentials.get('qbo_app_secret'))
    headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',
               'Authorization': auth_header}
    payload = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    r = requests.post(token_endpoint, data=payload, headers=headers)
    bearer_raw = json.loads(r.text)

    if 'id_token' in bearer_raw:
        id_token = bearer_raw['id_token']
    else:
        id_token = None
    return Bearer(bearer_raw['x_refresh_token_expires_in'], bearer_raw['access_token'], bearer_raw['token_type'],
                  bearer_raw['refresh_token'], bearer_raw['expires_in'], idToken=id_token)


# The validation steps can be found at ours docs at developer.intuit.com
def validate_jwt_token(token, request):
    active_credentials = check_prod_sandbox_credentials_status(request)
    if active_credentials:
        current_time = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        token_parts = token.split('.')
        id_token_header = json.loads(base64.b64decode(token_parts[0]).decode('ascii'))
        id_token_payload = json.loads(base64.b64decode(incorrect_padding(token_parts[1])).decode('ascii'))

        if id_token_payload['iss'] != settings.ID_TOKEN_ISSUER:
            return False
        elif id_token_payload['aud'][0] != active_credentials.get('qbo_app_id'):
            return False
        elif id_token_payload['exp'] < current_time:
            return False

        token = token.encode()
        token_to_verify = token.decode("ascii").split('.')
        message = token_to_verify[0] + '.' + token_to_verify[1]
        id_token_signature = base64.urlsafe_b64decode(incorrect_padding(token_to_verify[2]))

        keys = get_key_from_jwk_url(id_token_header['kid'])

        public_key = jwk.construct(keys)
        return public_key.verify(message.encode('utf-8'), id_token_signature)


def get_key_from_jwk_url(kid):
    jwk_uri = getDiscoveryDocument.jwks_uri
    r = requests.get(jwk_uri)
    if r.status_code >= 400:
        return ''
    data = json.loads(r.text)

    key = next(ele for ele in data["keys"] if ele['kid'] == kid)
    return key


# for decoding ID Token
def incorrect_padding(s):
    return s + '=' * (4 - len(s) % 4)


def string_to_base64(s):
    return base64.b64encode(bytes(s, 'utf-8')).decode()


# Returns a securely generated random string. Source from the django.utils.crypto module.
def get_random_string(length, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))


# Create a random secret key. Source from the django.utils.crypto module.
def get_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return get_random_string(40, chars)


def make_authorization_url(active_credentials):
    """
    DESCRIPTION:
        Creates the authorization URL to obtain the authorization code from Procore.
    INPUTS:
        N/A
    OUTPUTS:
        url: the url used to obtain the authorization code from the application.
        """
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    params = {
        "client_id": active_credentials.get('procore_app_id'),
        "response_type": "code",
        "redirect_uri": active_credentials.get('procore_redirect_url')
    }
    url = active_credentials.get("OAUTH_URL") + "/oauth/authorize?" + urllib.parse.urlencode(params)
    return url


def get_token(code, request):
    """
    DESCRIPTION:
        Gets the access token by utilizating the authorization code that was
        previously obtained from the authorization_url call.
    INPUTS:
        code = authorization code
    OUTPUTS:
        response_json["access_token"]  = user's current access token
        response_json["refresh_token"] = user's current refresh token
        response_json['created_at']    = the date and time the user's access
        token was generated
    """
    active_credentials = check_prod_sandbox_credentials_status(request)
    if active_credentials:
        client_auth = requests.auth.HTTPBasicAuth(active_credentials.get('procore_app_id'),
                                                  active_credentials.get('procore_app_secret'))
        post_data = {"grant_type": "authorization_code",
                     "code": code,
                     "redirect_uri": active_credentials.get('procore_redirect_url')
                     }
        response = requests.post(active_credentials.get("BASE_URL") + "/oauth/token",
                                 auth=client_auth,
                                 data=post_data)
        response_json = response.json()
        return response_json["access_token"], response_json["refresh_token"], response_json['created_at']


def refresh_procore_access_token(refresh_token, active_credentials):
    client_auth = requests.auth.HTTPBasicAuth(active_credentials.get('procore_app_id'),
                                              active_credentials.get('procore_app_secret'))
    post_data = {"grant_type": "refresh_token",
                 "redirect_uri": active_credentials.get('procore_redirect_url'),
                 "refresh_token": refresh_token
                 }
    response = requests.post(active_credentials.get("BASE_URL") + "/oauth/token",
                             auth=client_auth,
                             data=post_data)
    response_json = response.json()
    return response_json


def get_csrf_token(request):
    token = request.session.get('csrfToken', None)
    if token is None:
        token = get_secret_key()
        request.session['csrfToken'] = token
    return token


def refresh_user_tokens(user_, request):
    """
    Storing newly created access-token & refresh-token aginst specific user for both QBO / procore
    """
    active_credentials = check_prod_sandbox_credentials_status(request)
    if active_credentials:
        quickbok_res = get_bearer_token_from_refresh_token(user_.quickbook_refresh_token, active_credentials)
        user_.quickbook_access_token = quickbok_res.accessToken
        user_.quickbook_refresh_token = quickbok_res.refreshToken
        user_.save()

        procore_res = refresh_procore_access_token(user_.procore_refresh_token, active_credentials)
        user_.procore_access_token = procore_res["access_token"]
        user_.procore_refresh_token = procore_res["refresh_token"]
        user_.save()
        return True if user_ else False
