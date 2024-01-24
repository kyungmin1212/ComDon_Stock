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
