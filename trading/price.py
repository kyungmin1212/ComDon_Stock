from utils import fetch, calculate_qty, calculate_profit_price, calculate_loss_price
from models import (
    OrderRequest,
    StocksRealtimepriceRequest,
    ConditionStockRegisterRealtimepriceRequest,
)
from trading import buy_market_order, sell_market_order

import websockets
import json
import asyncio
from settings import env_settings


async def register_stocks_realtimeprice(
    stocks_realtimeprice_request: StocksRealtimepriceRequest,
    stock_buy_price,
):
    BASE_URL = "wss://openapi.ebestsec.co.kr:9443"
    PATH = "websocket"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "token": stocks_realtimeprice_request.AccessTokenDict["ACCESS_TOKEN"],
        "tr_type": "3",
    }

    if stocks_realtimeprice_request.KospiKosdaq == "kospi":
        body = {"tr_cd": "S3_", "tr_key": stocks_realtimeprice_request.IsuNo}
    elif stocks_realtimeprice_request.KospiKosdaq == "kosdaq":
        body = {"tr_cd": "K3_", "tr_key": stocks_realtimeprice_request.IsuNo}

    available_qty = calculate_qty(stock_buy_price)
    remain_qty = available_qty - int(available_qty / 2)

    profit_price_1 = calculate_profit_price(
        stock_buy_price, env_settings.PROFIT_PERCENT_1
    )
    profit_price_2 = calculate_profit_price(
        stock_buy_price, env_settings.PROFIT_PERCENT_2
    )
    profit_1_flag = False
    profit_2_flag = False

    loss_price = calculate_loss_price(stock_buy_price, env_settings.LOSS_PERCENT)
    loss_flag = False  # 이게 True가 되면, profit_1과 profit_2 더이상 진행할 필요 없음. 이미 다 손절 / 또는 profit_1_flag와 profit_2_flat가 모두 True가 되면 loss_flag 또한 의미가 없어짐

    # 웹 소켓에 접속을 합니다.
    async with websockets.connect(URL) as websocket:
        data_to_send = json.dumps({"header": header, "body": body})  # json -> str로 변경
        await websocket.send(data_to_send)

        after_buy_high_price = stock_buy_price  # 매수이후에 최고가를 의미

        while True:
            data = await websocket.recv()
            data_dict = json.loads(data)
            if data_dict["body"] != None:
                now_price = data_dict["body"]["price"]

                # 현재가가 고점이면 고점 갱신
                if after_buy_high_price < now_price:
                    after_buy_high_price = now_price
                    if (
                        env_settings.LOSS_CRITERION == "high"
                    ):  # 매수이후 고점대비 하락 퍼센트 기준인경우 lossprice 갱신필요
                        loss_price = calculate_loss_price(
                            after_buy_high_price, env_settings.LOSS_PERCENT
                        )

                # 1차 익절가 # 절반 익절 (매수개수의 절반 익절)
                if (
                    (profit_price_1 <= now_price)
                    and (not profit_1_flag)
                    and (not loss_flag)
                ):
                    remain_qty = available_qty - int(available_qty / 2)
                    # 모의투자인 경우
                    if "A_ACCESS_TOKEN" in stocks_realtimeprice_request.AccessTokenDict:
                        order_request = OrderRequest(
                            AccessToken=stocks_realtimeprice_request.AccessTokenDict[
                                "A_ACCESS_TOKEN"
                            ],  # 모의투자인 경우 ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"]
                            IsuNo="A"
                            + stocks_realtimeprice_request.IsuNo,  # 모의투자인 경우 "A005930"
                            OrdQty=int(available_qty / 2),
                            OrdPrc=0,
                        )
                    else:  # 실제투자인 경우
                        order_request = OrderRequest(
                            AccessToken=stocks_realtimeprice_request.AccessTokenDict[
                                "ACCESS_TOKEN"
                            ],
                            IsuNo=stocks_realtimeprice_request.IsuNo,
                            OrdQty=int(available_qty / 2),
                            OrdPrc=0,
                        )
                    # 시장가 매도 주문
                    asyncio.create_task(sell_market_order(order_request))
                    profit_1_flag = True

                # 2차 익절가 # 나머지 전체 익절
                if (
                    (profit_price_2 <= now_price)
                    and (not profit_2_flag)
                    and (not loss_flag)
                ):
                    # 모의투자인 경우
                    if "A_ACCESS_TOKEN" in stocks_realtimeprice_request.AccessTokenDict:
                        order_request = OrderRequest(
                            AccessToken=stocks_realtimeprice_request.AccessTokenDict[
                                "A_ACCESS_TOKEN"
                            ],  # 모의투자인 경우 ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"]
                            IsuNo="A"
                            + stocks_realtimeprice_request.IsuNo,  # 모의투자인 경우 "A005930"
                            OrdQty=remain_qty,
                            OrdPrc=0,
                        )
                    else:  # 실제투자인 경우
                        order_request = OrderRequest(
                            AccessToken=stocks_realtimeprice_request.AccessTokenDict[
                                "ACCESS_TOKEN"
                            ],
                            IsuNo=stocks_realtimeprice_request.IsuNo,
                            OrdQty=remain_qty,
                            OrdPrc=0,
                        )
                    # 시장가 매도 주문
                    asyncio.create_task(sell_market_order(order_request))
                    profit_2_flag = True
                    break  # 2차 익절가에 매도하면 전체다 매도한것이기때문에 break 하면 됩니다.

                # 전체 손절
                if (
                    (loss_price > now_price)
                    and (not (profit_1_flag and profit_2_flag))
                    and (not loss_flag)
                ):
                    # 모의투자인 경우
                    if profit_1_flag:
                        qty = remain_qty
                    else:
                        qty = available_qty

                    if "A_ACCESS_TOKEN" in stocks_realtimeprice_request.AccessTokenDict:
                        order_request = OrderRequest(
                            AccessToken=stocks_realtimeprice_request.AccessTokenDict[
                                "A_ACCESS_TOKEN"
                            ],  # 모의투자인 경우 ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"]
                            IsuNo="A"
                            + stocks_realtimeprice_request.IsuNo,  # 모의투자인 경우 "A005930"
                            OrdQty=qty,
                            OrdPrc=0,
                        )
                    else:  # 실제투자인 경우
                        order_request = OrderRequest(
                            AccessToken=stocks_realtimeprice_request.AccessTokenDict[
                                "qty"
                            ],
                            IsuNo=stocks_realtimeprice_request.IsuNo,
                            OrdQty=remain_qty,
                            OrdPrc=0,
                        )
                    # 시장가 매도 주문
                    asyncio.create_task(sell_market_order(order_request))
                    loss_flag = True
                    break  # 전체 손절의 경우도 더이상 데이터를 받아올 필요가 없습니다.

            # 너무 잦은 데이터 수신방지
            await asyncio.sleep(0.1)


async def condition_stock_register_realtimeprice(
    codition_stock_register_realtimeprice_request: ConditionStockRegisterRealtimepriceRequest,
    condition_queue,
):
    while True:
        (
            stock_code,
            stock_buy_price,
        ) = await condition_queue.get()  # queue에 데이터가 있을때마다 꺼냅니다.

        if (
            stock_code
            in codition_stock_register_realtimeprice_request.KospiKosdaqStockCodeDict[
                "kospi"
            ]
        ):  # 코스피종목
            stocks_realtimeprice_request = StocksRealtimepriceRequest(
                AccessToken=codition_stock_register_realtimeprice_request.AccessTokenDict[
                    "ACCESS_TOKEN"
                ],
                IsuNo=stock_code,
                KospiKosdaq="kospi",
            )
            asyncio.create_task(
                register_stocks_realtimeprice(
                    stocks_realtimeprice_request,
                    stock_buy_price,
                )
            )
        elif (
            stock_code
            in codition_stock_register_realtimeprice_request.KospiKosdaqStockCodeDict[
                "kosdaq"
            ]
        ):  # 코스닥종목
            stocks_realtimeprice_request = StocksRealtimepriceRequest(
                AccessToken=codition_stock_register_realtimeprice_request.AccessTokenDict[
                    "ACCESS_TOKEN"
                ],
                IsuNo=stock_code,
                KospiKosdaq="kosdaq",
            )
            asyncio.create_task(
                register_stocks_realtimeprice(
                    stocks_realtimeprice_request,
                    stock_buy_price,
                )
            )

        condition_queue.task_done()
