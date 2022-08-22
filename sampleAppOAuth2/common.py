from sampleAppOAuth2.constants import SANDBOX_PROCORE_OAUTH_URL, SANDBOX_PROCORE_BASE_URL, PROD_PROCORE_OAUTH_URL, \
    PROD_PROCORE_BASE_URL


def check_prod_sandbox_credentials_status(request):
    """
        BASE_URL, OAUTH_URL will be changed according to sandbox or production
    """
    if request.user.userappcredentials_set.get(user_id=request.user.id).is_sandbox_active:
        return {
            "procore_app_id": request.user.userappcredentials_set.get(
                user_id=request.user.id).sandbox_procore_app_id,
            "procore_app_secret": request.user.userappcredentials_set.get(
                user_id=request.user.id).sandbox_procore_app_secret,
            "procore_redirect_url": request.user.userappcredentials_set.get(
                user_id=request.user.id).sandbox_procore_redirect_url,
            "qbo_app_id": request.user.userappcredentials_set.get(user_id=request.user.id).sandbox_qbo_app_id,
            "qbo_app_secret": request.user.userappcredentials_set.get(
                user_id=request.user.id).sandbox_qbo_app_secret,
            "qbo_redirect_url": request.user.userappcredentials_set.get(
                user_id=request.user.id).sandbox_qbo_redirect_url,
            "OAUTH_URL": SANDBOX_PROCORE_OAUTH_URL,
            "BASE_URL": SANDBOX_PROCORE_BASE_URL
        }
    elif request.user.userappcredentials_set.get(user_id=request.user.id).is_prod_active:
        return {
            "procore_app_id": request.user.userappcredentials_set.get(user_id=request.user.id).prod_procore_app_id,
            "procore_app_secret": request.user.userappcredentials_set.get(
                user_id=request.user.id).prod_procore_app_secret,
            "procore_redirect_url": request.user.userappcredentials_set.get(
                user_id=request.user.id).prod_procore_redirect_url,
            "qbo_app_id": request.user.userappcredentials_set.get(user_id=request.user.id).prod_qbo_app_id,
            "qbo_app_secret": request.user.userappcredentials_set.get(user_id=request.user.id).prod_qbo_app_secret,
            "qbo_redirect_url": request.user.userappcredentials_set.get(
                user_id=request.user.id).prod_qbo_redirect_url,
            "OAUTH_URL": PROD_PROCORE_OAUTH_URL,
            "BASE_URL": PROD_PROCORE_BASE_URL
        }
    else:
        return False
