import aiohttp
from utils import fetch
from models import QueryIndexRequest, sAlertNumRequest


async def get_query_index(query_index_request: QueryIndexRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/item-search"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {query_index_request.AccessToken}",
        "tr_cd": "t1866",
        "tr_cont": "N",
        "tr_cont_key": "",
    }

    body = {
        "t1866InBlock": {
            "user_id": query_index_request.UserId,
            "gb": "0",
            "group_name": "",
            "cont": "",
            "cont_key": "",
        }
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, URL, header, body)

    query_index = ""

    for item in response["t1866OutBlock1"]:
        if item["query_name"] == query_index_request.ConditionName:
            query_index = item["query_index"]
            break
    else:
        print("찾지 못했습니다.")

    return query_index


async def query_index_to_sAlertNum(salertnum_request: sAlertNumRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/item-search"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {salertnum_request.AccessToken}",
        "tr_cd": "t1860",
        "tr_cont": "N",
        "tr_cont_key": "",
    }

    body = {
        "t1860InBlock": {
            "sSysUserFlag": "U",
            "sFlag": "E",
            "sAlertNum": "",
            "query_index": salertnum_request.query_index,
        }
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, URL, header, body)

    sAlertNum = response["t1860OutBlock"]["sAlertNum"]
    return sAlertNum
