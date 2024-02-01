from models import AccessTokenRequest
from settings import env_settings

import requests
from models import AccessTokenRequest


def get_access_token(access_token_request: AccessTokenRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "oauth2/token"
    URL = f"{BASE_URL}/{PATH}"

    header = {"content-type": "application/x-www-form-urlencoded"}
    param = {
        "grant_type": "client_credentials",
        "appkey": access_token_request.appkey,
        "appsecretkey": access_token_request.appsecretkey,
        "scope": "oob",
    }

    request = requests.post(URL, headers=header, params=param)
    ACCESS_TOKEN = request.json()["access_token"]
    return ACCESS_TOKEN


def get_access_token_function(virtual: bool = False):
    if virtual:
        access_token_request = AccessTokenRequest(
            appkey=env_settings.VIRTUAL_APP_KEY,
            appsecretkey=env_settings.VIRTUAL_APP_SECRET,
        )

        token = get_access_token(access_token_request)

    else:
        access_token_request = AccessTokenRequest(
            appkey=env_settings.APP_KEY, appsecretkey=env_settings.APP_SECRET
        )

        token = get_access_token(access_token_request)

    return token
