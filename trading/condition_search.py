import aiohttp
import asyncio
from settings import env_settings

from utils import fetch, calculate_qty
from models import (
    QueryIndexRequest,
    sAlertNumRequest,
    RealtimeConditionRequest,
)

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
    realtime_condition_request: RealtimeConditionRequest, condition_queue, condition_set
):
    BASE_URL = "wss://openapi.ebestsec.co.kr:9443"
    PATH = "websocket"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "token": realtime_condition_request.AccessTokenDict["ACCESS_TOKEN"],
        "tr_type": "3",
    }
    body = {"tr_cd": "AFR", "tr_key": realtime_condition_request.sAlertNum}

    # 웹 소켓에 접속을 합니다.
    async with websockets.connect(URL) as websocket:
        data_to_send = json.dumps(
            {"header": header, "body": body}
        )  # json -> str로 변경
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
                    condition_set.add(stock_code)
                    print(condition_set)

                    stock_price = float(data_dict["body"]["gsPrice"])

                    # condition_stock_register_realtimeprice의 condition_queue로 데이터 전송
                    condition_queue.put_nowait((stock_code, stock_price))


async def realtime_condition_connect_buy_function(
    access_token_dict: dict, condition_queue, condition_set
):
    ### 조건검색 query_index 가져오기 ###
    query_index_request = QueryIndexRequest(
        AccessToken=access_token_dict["ACCESS_TOKEN"],
        UserId=env_settings.USER_ID,
        ConditionName=env_settings.CONDITION_NAME,
    )

    query_index = await get_query_index(query_index_request)
    #######################################

    ### query_index -> sAlertNum 변경 ###
    salertnum_request = sAlertNumRequest(
        AccessToken=access_token_dict["ACCESS_TOKEN"],
        query_index=query_index,
    )

    sAlertNum = await query_index_to_sAlertNum(salertnum_request)
    #####################################

    ### 실시간 조건검색 내역 받아오기(Websocket) ###
    realtime_condition_request = RealtimeConditionRequest(
        AccessTokenDict=access_token_dict,
        sAlertNum=sAlertNum,
    )

    search_condition_stock_buy_task = asyncio.create_task(
        realtime_condition_connect_buy(
            realtime_condition_request, condition_queue, condition_set
        ),
    )


async def command_handler(command_queue, condition_set):
    while True:
        command, stock_code = await command_queue.get()
        if command == "delete":
            condition_set.discard(stock_code)
