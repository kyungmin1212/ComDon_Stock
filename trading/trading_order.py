import aiohttp
import asyncio
from utils import fetch
from models import OrderRequest


async def buy_limit_order(order_request: OrderRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/order"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {order_request.AccessToken}",
        "tr_cd": "CSPAT00601",
        "tr_cont": "N",
        "tr_cont_key": "",
    }

    body = {
        "CSPAT00601InBlock1": {
            "IsuNo": order_request.IsuNo,
            "OrdQty": order_request.OrdQty,
            "OrdPrc": order_request.OrdPrc,
            "BnsTpCode": "2",  # 1 : 매도 / 2 : 매수
            "OrdprcPtnCode": "00",  # 00 : 지정가 / 03 : 시장가
            "MgntrnCode": "000",
            "LoanDt": "",
            "OrdCndiTpCode": "0",
        }
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, URL, header, body)
        print(response)


async def sell_limit_order(order_request: OrderRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/order"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {order_request.AccessToken}",
        "tr_cd": "CSPAT00601",
        "tr_cont": "N",
        "tr_cont_key": "",
    }

    body = {
        "CSPAT00601InBlock1": {
            "IsuNo": order_request.IsuNo,
            "OrdQty": order_request.OrdQty,
            "OrdPrc": order_request.OrdPrc,
            "BnsTpCode": "1",  # 1 : 매도 / 2 : 매수
            "OrdprcPtnCode": "00",  # 00 : 지정가 / 03 : 시장가
            "MgntrnCode": "000",
            "LoanDt": "",
            "OrdCndiTpCode": "0",
        }
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, URL, header, body)

    return response


async def buy_market_order(order_request: OrderRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/order"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {order_request.AccessToken}",
        "tr_cd": "CSPAT00601",
        "tr_cont": "N",
        "tr_cont_key": "",
    }

    body = {
        "CSPAT00601InBlock1": {
            "IsuNo": order_request.IsuNo,
            "OrdQty": order_request.OrdQty,
            "OrdPrc": 0,
            "BnsTpCode": "2",  # 1 : 매도 / 2 : 매수
            "OrdprcPtnCode": "03",  # 00 : 지정가 / 03 : 시장가
            "MgntrnCode": "000",
            "LoanDt": "",
            "OrdCndiTpCode": "0",
        }
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, URL, header, body)

    return response


async def sell_market_order(order_request: OrderRequest):
    BASE_URL = "https://openapi.ebestsec.co.kr:8080"
    PATH = "stock/order"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {order_request.AccessToken}",
        "tr_cd": "CSPAT00601",
        "tr_cont": "N",
        "tr_cont_key": "",
    }

    body = {
        "CSPAT00601InBlock1": {
            "IsuNo": order_request.IsuNo,
            "OrdQty": order_request.OrdQty,
            "OrdPrc": 0,
            "BnsTpCode": "1",  # 1 : 매도 / 2 : 매수
            "OrdprcPtnCode": "03",  # 00 : 지정가 / 03 : 시장가
            "MgntrnCode": "000",
            "LoanDt": "",
            "OrdCndiTpCode": "0",
        }
    }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, URL, header, body)

    return response


async def sell_market_order_function(
    virtual: bool, accesstoekn_dict: dict, stock_code: str, qty: int
):
    if virtual:
        order_request = OrderRequest(
            AccessToken=accesstoekn_dict["VIRTUAL_ACCESS_TOKEN"],
            IsuNo="A" + stock_code,
            OrdQty=qty,
            OrdPrc=0,
        )
    else:
        order_request = OrderRequest(
            AccessToken=accesstoekn_dict["ACCESS_TOKEN"],
            IsuNo=stock_code,
            OrdQty=qty,
            OrdPrc=0,
        )
    # 시장가 매도 주문
    asyncio.create_task(sell_market_order(order_request))


async def buy_market_order_function(
    virtual: bool, accesstoekn_dict: dict, stock_code: str, qty: int
):
    if virtual:
        order_request = OrderRequest(
            AccessToken=accesstoekn_dict["VIRTUAL_ACCESS_TOKEN"],
            IsuNo="A" + stock_code,
            OrdQty=qty,
            OrdPrc=0,
        )
    else:
        order_request = OrderRequest(
            AccessToken=accesstoekn_dict["ACCESS_TOKEN"],
            IsuNo=stock_code,
            OrdQty=qty,
            OrdPrc=0,
        )
    # 시장가 매도 주문
    asyncio.create_task(buy_market_order(order_request))
