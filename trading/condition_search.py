import aiohttp
import asyncio

from utils import fetch, calculate_qty
from models import (
    QueryIndexRequest,
    sAlertNumRequest,
    RealtimeConditionRequest,
    OrderRequest,
)

from trading import buy_market_order
import websockets
import json


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


async def realtime_condition_connect_buy(
    realtime_condition_request: RealtimeConditionRequest, condition_queue
):
    BASE_URL = "wss://openapi.ebestsec.co.kr:9443"
    PATH = "websocket"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "token": realtime_condition_request.AccessTokenDict["ACCESS_TOKEN"],
        "tr_type": "3",
    }
    body = {"tr_cd": "AFR", "tr_key": realtime_condition_request.sAlertNum}

    condition_set = set()  # 당일 한번 매매한 종목은 더이상 매매하지 않습니다.

    # 웹 소켓에 접속을 합니다.
    async with websockets.connect(URL) as websocket:
        data_to_send = json.dumps({"header": header, "body": body})  # json -> str로 변경
        await websocket.send(data_to_send)

        while True:
            data = await websocket.recv()
            data_dict = json.loads(data)
            if data_dict["body"] != None:
                stock_code = data_dict["body"]["gsCode"]
                if (stock_code not in condition_set) and (
                    data_dict["body"]["gsJobFlag"] == ("N" or "R")
                ):  # 당일 검색되지 않았던 종목만 매수 진행
                    print(data_dict)
                    stock_price = float(data_dict["body"]["gsPrice"])
                    condition_set.add(stock_code)
                    available_qty = calculate_qty(stock_price)
                    # 모의투자인 경우
                    if "A_ACCESS_TOKEN" in realtime_condition_request.AccessTokenDict:
                        order_request = OrderRequest(
                            AccessToken=realtime_condition_request.AccessTokenDict[
                                "A_ACCESS_TOKEN"
                            ],  # 모의투자인 경우 ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"]
                            IsuNo="A" + stock_code,  # 모의투자인 경우 "A005930"
                            OrdQty=available_qty,
                            OrdPrc=0,
                        )
                    else:  # 실제투자인 경우
                        order_request = OrderRequest(
                            AccessToken=realtime_condition_request.AccessTokenDict[
                                "ACCESS_TOKEN"
                            ],
                            IsuNo=stock_code,
                            OrdQty=available_qty,
                            OrdPrc=0,
                        )
                    # 시장가 매수 주문
                    print("시장가 주문")
                    print(condition_set)
                    asyncio.create_task(buy_market_order(order_request))
                    # condition_stock_register_realprㄴice의 condition_queue로 데이터 전송
                    condition_queue.put_nowait((stock_code, stock_price))
            # 너무 잦은 데이터 수신방지
            await asyncio.sleep(0.1)
