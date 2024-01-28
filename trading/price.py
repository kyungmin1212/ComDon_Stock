from utils import fetch
from models import KosdoqStocksRealtimepriceRequest, KospiStocksRealtimepriceRequest
import websockets
import json


async def register_kosdoq_stocks_realtimeprice(
    kosdoq_stocks_realtimeprice_request: KosdoqStocksRealtimepriceRequest,
):
    BASE_URL = "wss://openapi.ebestsec.co.kr:9443"
    PATH = "websocket"
    URL = f"{BASE_URL}/{PATH}"

    header = {"token": kosdoq_stocks_realtimeprice_request.AccessToken, "tr_type": "3"}
    body = {"tr_cd": "K3_", "tr_key": kosdoq_stocks_realtimeprice_request.IsuNo}

    # 웹 소켓에 접속을 합니다.
    async with websockets.connect(URL) as websocket:
        data_to_send = json.dumps({"header": header, "body": body})  # json -> str로 변경
        await websocket.send(data_to_send)

        while True:
            data = await websocket.recv()
            print(data)


async def register_kospi_stocks_realtimeprice(
    kospi_stocks_realtimeprice_request: KospiStocksRealtimepriceRequest,
):
    BASE_URL = "wss://openapi.ebestsec.co.kr:9443"
    PATH = "websocket"
    URL = f"{BASE_URL}/{PATH}"

    header = {"token": kospi_stocks_realtimeprice_request.AccessToken, "tr_type": "3"}
    body = {"tr_cd": "S3_", "tr_key": kospi_stocks_realtimeprice_request.IsuNo}

    # 웹 소켓에 접속을 합니다.
    async with websockets.connect(URL) as websocket:
        data_to_send = json.dumps({"header": header, "body": body})  # json -> str로 변경
        await websocket.send(data_to_send)

        while True:
            data = await websocket.recv()
            print(data)
