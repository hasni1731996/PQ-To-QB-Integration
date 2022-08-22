import requests

from django.conf import settings

from .oauth2config import OAuth2Config


def getDiscoveryDocument():
    """
    if we're getting requests.exceptions.ConnectionError: HTTPSConnectionPool(host='developer.api.intuit.com', port=443): Max retries exceeded with url: /.well-known/openid_sandbox_configuration/ (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7ff3f325efa0>: Failed to establish a new connection: [Errno -2] Name or service not known'))
    Then follow this link
    https://stackoverflow.com/questions/63690544/https-connection-error-with-python-requests
    """
    r = requests.get(settings.DISCOVERY_DOCUMENT)
    if r.status_code >= 400:
        return ''
    discovery_doc_json = r.json()
    discovery_doc = OAuth2Config(
        issuer=discovery_doc_json['issuer'],
        auth_endpoint=discovery_doc_json['authorization_endpoint'],
        userinfo_endpoint=discovery_doc_json['userinfo_endpoint'],
        revoke_endpoint=discovery_doc_json['revocation_endpoint'],
        token_endpoint=discovery_doc_json['token_endpoint'],
        jwks_uri=discovery_doc_json['jwks_uri'])

    return discovery_doc


getDiscoveryDocument = getDiscoveryDocument()
