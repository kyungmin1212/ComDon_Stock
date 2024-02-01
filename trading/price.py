from utils import fetch, calculate_qty, calculate_profit_price, calculate_loss_price
from models import (
    OrderRequest,
    StocksRealtimepriceRequest,
    ConditionStockRegisterRealtimepriceRequest,
)
from trading import (
    buy_market_order_function,
    sell_market_order_function,
)
import websockets
import json
import asyncio
from settings import env_settings


async def register_stocks_realtimeprice(
    stocks_realtimeprice_request: StocksRealtimepriceRequest,
    stock_profit_loss_price_dict,
):
    profit_1_flag = False
    profit_2_flag = False

    # 참고 :1차 매수에서 profit_2_flag까지 True가 되었다면 추가매수는 진행하지 않습니다.
    if env_settings.ADD_BUY_FLAG == "1":
        add_buy_flag = False
        add_profit_1_flag = False
        add_profit_2_flag = False
    loss_flag = False

    remain_qty = stock_profit_loss_price_dict[stocks_realtimeprice_request.IsuNo][
        "buy_1_qty"
    ]  # 1차 매수한 수량

    BASE_URL = "wss://openapi.ebestsec.co.kr:9443"
    PATH = "websocket"
    URL = f"{BASE_URL}/{PATH}"

    header = {
        "token": stocks_realtimeprice_request.AccessTokenDict["ACCESS_TOKEN"],
        "tr_type": "3",
    }

    stock_code = stocks_realtimeprice_request.IsuNo
    if stocks_realtimeprice_request.KospiKosdaq == "kospi":
        body = {"tr_cd": "S3_", "tr_key": stocks_realtimeprice_request.IsuNo}
    elif stocks_realtimeprice_request.KospiKosdaq == "kosdaq":
        body = {"tr_cd": "K3_", "tr_key": stocks_realtimeprice_request.IsuNo}

    virtual = True if env_settings.VIRTUAL_FLAG == "1" else False  # 모의투자 여부

    # 웹 소켓에 접속을 합니다.
    async with websockets.connect(URL) as websocket:
        data_to_send = json.dumps({"header": header, "body": body})  # json -> str로 변경
        await websocket.send(data_to_send)

        # 매수이후에 최고가를 의미
        after_buy_high_price = stock_profit_loss_price_dict[
            stocks_realtimeprice_request.IsuNo
        ]["buy_price"]

        while True:
            data = await websocket.recv()
            data_dict = json.loads(data)

            # loss_flag가 True면 모든 포지션이 종료된 상태
            if loss_flag:
                break

            # ADD_BUY_FLAG 가 1인경우
            if env_settings.ADD_BUY_FLAG == "1":
                # 추가매수가격에 도달하지 않고 익절가1, 2 에 도달한 경우 추가매수하지 않고 포지션 종료
                if (not add_buy_flag) and profit_1_flag and profit_2_flag:
                    break
                # 추가매수를 한 상태인경우에는 익절가1,2 에 도달하고, 추가매수익절가1,2에 도달한 경우 가격수신 종료
                elif (
                    add_buy_flag
                    and profit_1_flag
                    and profit_2_flag
                    and add_profit_1_flag
                    and add_profit_2_flag
                ):
                    break
            else:  # ADD_BUY_FLAG 가 0 인경우
                if (
                    profit_1_flag and profit_2_flag
                ):  # 익절가 1 ,2 에 도달했으면 모든 포지션 종료된 상태이므로 가격 수신 종료
                    break

            if data_dict["body"] != None:
                now_price = float(data_dict["body"]["price"])

                # 현재가가 고점이면 고점 갱신
                if after_buy_high_price < now_price:
                    after_buy_high_price = now_price

                    # 매수이후 고점대비 하락 퍼센트 기준인경우 기존 가격 갱신 필요
                    if env_settings.LOSS_CRITERION == "high":
                        loss_price = calculate_loss_price(
                            after_buy_high_price, env_settings.LOSS_PERCENT
                        )
                        stock_profit_loss_price_dict[
                            stocks_realtimeprice_request.IsuNo
                        ]["loss_price"] = loss_price
                        if env_settings.ADD_BUY_FLAG == "1":
                            if not add_buy_flag:  # 아직 추가매수를 진행하지 않은 경우라면 같이 업데이트 필요
                                add_buy_price = calculate_loss_price(
                                    after_buy_high_price, env_settings.BUY_PERCENT
                                )
                                add_profit_1_price = calculate_profit_price(
                                    add_buy_price, env_settings.ADD_PROFIT_PERCENT_1
                                )
                                add_profit_2_price = calculate_profit_price(
                                    add_buy_price, env_settings.ADD_PROFIT_PERCENT_2
                                )

                                stock_profit_loss_price_dict[
                                    stocks_realtimeprice_request.IsuNo
                                ]["add_buy_price"] = add_buy_price
                                stock_profit_loss_price_dict[
                                    stocks_realtimeprice_request.IsuNo
                                ]["add_profit_1_price"] = add_profit_1_price
                                stock_profit_loss_price_dict[
                                    stocks_realtimeprice_request.IsuNo
                                ]["add_profit_2_price"] = add_profit_2_price

                # 1차 익절가 # 절반 익절 (매수개수의 절반 익절)
                if (
                    stock_profit_loss_price_dict[stocks_realtimeprice_request.IsuNo][
                        "profit_1_price"
                    ]
                    <= now_price
                ) and (not profit_1_flag):
                    # 시장가 매도
                    asyncio.create_task(
                        sell_market_order_function(
                            virtual=virtual,
                            accesstoekn_dict=stocks_realtimeprice_request.AccessTokenDict,
                            stock_code=stocks_realtimeprice_request.IsuNo,
                            qty=stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["sell_1-1_qty"],
                        )
                    )
                    profit_1_flag = True
                    remain_qty -= stock_profit_loss_price_dict[
                        stocks_realtimeprice_request.IsuNo
                    ]["sell_1-1_qty"]

                # 2차 익절가 # 나머지 전체 익절
                if (
                    stock_profit_loss_price_dict[stocks_realtimeprice_request.IsuNo][
                        "profit_2_price"
                    ]
                    <= now_price
                ) and (not profit_2_flag):
                    # 시장가 매도
                    asyncio.create_task(
                        sell_market_order_function(
                            virtual=virtual,
                            accesstoekn_dict=stocks_realtimeprice_request.AccessTokenDict,
                            stock_code=stocks_realtimeprice_request.IsuNo,
                            qty=stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["sell_1-2_qty"],
                        )
                    )
                    profit_2_flag = True
                    remain_qty -= stock_profit_loss_price_dict[
                        stocks_realtimeprice_request.IsuNo
                    ]["sell_1-2_qty"]

                if env_settings.ADD_BUY_FLAG == "1":
                    if not add_buy_flag:  # 아직 매수하지 않은 경우
                        if (
                            stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["add_buy_price"]
                            >= now_price
                        ):
                            asyncio.create_task(
                                buy_market_order_function(
                                    virtual=virtual,
                                    accesstoekn_dict=stocks_realtimeprice_request.AccessTokenDict,
                                    stock_code=stocks_realtimeprice_request.IsuNo,
                                    qty=stock_profit_loss_price_dict[
                                        stocks_realtimeprice_request.IsuNo
                                    ]["buy_2_qty"],
                                )
                            )
                            add_buy_flag = True
                            remain_qty += stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["buy_2_qty"]
                    else:  # 매수한경우
                        # 추가 매수 1차 익절가
                        if (
                            stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["add_profit_1_price"]
                            <= now_price
                        ) and (not add_profit_1_flag):
                            # 시장가 매도
                            asyncio.create_task(
                                sell_market_order_function(
                                    virtual=virtual,
                                    accesstoekn_dict=stocks_realtimeprice_request.AccessTokenDict,
                                    stock_code=stocks_realtimeprice_request.IsuNo,
                                    qty=stock_profit_loss_price_dict[
                                        stocks_realtimeprice_request.IsuNo
                                    ]["sell_2-1_qty"],
                                )
                            )
                            add_profit_1_flag = True
                            remain_qty -= stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["sell_2-1_qty"]
                        # 추가매수 2차 익절가
                        if (
                            stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["add_profit_2_price"]
                            <= now_price
                        ) and (not add_profit_2_flag):
                            # 시장가 매도
                            asyncio.create_task(
                                sell_market_order_function(
                                    virtual=virtual,
                                    accesstoekn_dict=stocks_realtimeprice_request.AccessTokenDict,
                                    stock_code=stocks_realtimeprice_request.IsuNo,
                                    qty=stock_profit_loss_price_dict[
                                        stocks_realtimeprice_request.IsuNo
                                    ]["sell_2-2_qty"],
                                )
                            )
                            add_profit_2_flag = True
                            remain_qty -= stock_profit_loss_price_dict[
                                stocks_realtimeprice_request.IsuNo
                            ]["sell_2-2_qty"]
                # 전체 손절
                if (
                    stock_profit_loss_price_dict[stocks_realtimeprice_request.IsuNo][
                        "loss_price"
                    ]
                    > now_price
                ):
                    # 시장가 매도
                    asyncio.create_task(
                        sell_market_order_function(
                            virtual=virtual,
                            accesstoekn_dict=stocks_realtimeprice_request.AccessTokenDict,
                            stock_code=stocks_realtimeprice_request.IsuNo,
                            qty=remain_qty,
                        )
                    )

                    loss_flag = True

        del stock_profit_loss_price_dict[stocks_realtimeprice_request.IsuNo]


async def condition_stock_register_realtimeprice(
    codition_stock_register_realtimeprice_request: ConditionStockRegisterRealtimepriceRequest,
    condition_queue,
):
    stock_profit_loss_price_dict = {}
    # 10초마다 종목별 익절가 손절가 확인
    asyncio.create_task(check_profit_loss_price(stock_profit_loss_price_dict))

    while True:
        (
            stock_code,
            stock_buy_price,
        ) = await condition_queue.get()  # queue에 데이터가 있을때마다 꺼냅니다.

        # 최대보유종목수 넘어가면 조건검색에 검색되었더라도 무시하기
        if len(stock_profit_loss_price_dict) > env_settings.MAX_STOCKS:
            continue

        # 시장가 매수 주문
        # 매수 수량 설정
        available_qty = calculate_qty(stock_buy_price)

        if env_settings.VIRTUAL_FLAG == "1":
            if available_qty < 4:  # 분할매도 4번이상 해야함
                continue
        else:
            if available_qty < 2:  # 분할매도 2번이상해야함
                continue

        if env_settings.ADD_BUY_FLAG == "1":  # 추가매수 설정되어져 있을 경우, 절반씩 매수
            buy_1_qty = available_qty // 2
            buy_2_qty = available_qty - buy_1_qty
        else:
            buy_1_qty = available_qty

        # 매수 (만약 추가매수 설정이 되어있을경우에는 1차 매수)
        virtual = True if env_settings.VIRTUAL_FLAG == "1" else False  # 모의투자 여부
        asyncio.create_task(
            buy_market_order_function(
                virtual=virtual,
                accesstoekn_dict=codition_stock_register_realtimeprice_request.AccessTokenDict,
                stock_code=stock_code,
                qty=buy_1_qty,
            )
        )

        # 손절가 / 익절가
        profit_1_price = calculate_profit_price(
            stock_buy_price, env_settings.PROFIT_PERCENT_1
        )
        profit_2_price = calculate_profit_price(
            stock_buy_price, env_settings.PROFIT_PERCENT_2
        )
        loss_price = calculate_loss_price(
            stock_buy_price, env_settings.LOSS_PERCENT
        )  # 매수가 기준/ 고점 기준 (고점기준일경우 손절가격이 업데이트 됩니다.)

        #  2차 매수가 설정 (추가매수가 설정된 경우만)
        if env_settings.ADD_BUY_FLAG == "1":
            add_buy_price = calculate_loss_price(
                stock_buy_price, env_settings.BUY_PERCENT
            )  # [LOSS CRITERION 따라감] 매수가 기준 / 고점 기준 (고점기준일경우 추가매수가격이 업데이트 됩니다.)
            add_profit_1_price = calculate_profit_price(
                add_buy_price, env_settings.ADD_PROFIT_PERCENT_1
            )  # 구매가격대비 상승가격 (LOSS CRITERION에 따라 add_buy_price가 업데이트되므로 지속적인 업데이트 필요)
            add_profit_2_price = calculate_profit_price(
                add_buy_price, env_settings.ADD_PROFIT_PERCENT_2
            )  # 구매가격대비 상승가격 (LOSS CRITERION에 따라 add_buy_price가 업데이트되므로 지속적인 업데이트 필요)
            # 추가매수의 경우 loss_price에 같이 손절을 진행합니다.

            stock_profit_loss_price_dict[stock_code] = {
                "buy_price": stock_buy_price,  # 고정
                "profit_1_price": profit_1_price,  # 고정
                "profit_2_price": profit_2_price,  # 고정
                "add_buy_price": add_buy_price,  # 고점 기준이면 add_buy할때까지는 계속해서 업데이트
                "add_profit_1_price": add_profit_1_price,  # 고점 기준이면 add_buy할때까지는 계속해서 업데이트
                "add_profit_2_price": add_profit_2_price,  # 고점 기준이면 add_buy할때까지는 계속해서 업데이트
                "loss_price": loss_price,  # 1차매수, 추가매수 모두 동일한 손절 가격
                "buy_1_qty": buy_1_qty,
                "buy_2_qty": buy_2_qty,
                "sell_1-1_qty": int(buy_1_qty // 2),
                "sell_1-2_qty": buy_1_qty - int(buy_1_qty // 2),
                "sell_2-1_qty": int(buy_2_qty // 2),
                "sell_2-2_qty": buy_2_qty - int(buy_2_qty // 2),
            }
        else:
            stock_profit_loss_price_dict[stock_code] = {
                "buy_price": stock_buy_price,  # 고정
                "profit_1_price": profit_1_price,  # 고정
                "profit_2_price": profit_2_price,  # 고정
                "loss_price": loss_price,  # 손절 가격
                "buy_1_qty": buy_1_qty,
                "sell_1-1_qty": int(buy_1_qty // 2),
                "sell_1-2_qty": buy_1_qty - int(buy_1_qty // 2),
            }

        asyncio.create_task(
            register_stocks_realtimeprice_function(
                stock_code=stock_code,
                kospi_kosdaq_stockcode_dict=codition_stock_register_realtimeprice_request.KospiKosdaqStockCodeDict,
                access_token_dict=codition_stock_register_realtimeprice_request.AccessTokenDict,
                stock_profit_loss_price_dict=stock_profit_loss_price_dict,
            )
        )
        condition_queue.task_done()


async def condition_stock_register_realtimeprice_sell_function(
    access_token_dict: dict, kospi_kosdaq_stockcode_dict: dict, condition_queue
):
    # 조건검색에서 검색된 종목을 실시간으로 데이터를 받아오게 등록하고, 정해진 익절 손절에 따라 매도합니다.
    codition_stock_register_realtimeprice_request = (
        ConditionStockRegisterRealtimepriceRequest(
            AccessTokenDict=access_token_dict,
            KospiKosdaqStockCodeDict=kospi_kosdaq_stockcode_dict,
        )
    )

    get_stock_realtimeprice_sell_task = asyncio.create_task(
        condition_stock_register_realtimeprice(
            codition_stock_register_realtimeprice_request, condition_queue
        )
    )


async def check_profit_loss_price(stock_profit_loss_price_dict):
    while True:
        print(stock_profit_loss_price_dict)
        await asyncio.sleep(10)  # 10초마다 보유종목 매수가 익절가 손절가 파악


async def register_stocks_realtimeprice_function(
    stock_code: str,
    kospi_kosdaq_stockcode_dict: dict,
    access_token_dict: dict,
    stock_profit_loss_price_dict: dict,
):
    if stock_code in kospi_kosdaq_stockcode_dict["kospi"]:  # 코스피종목
        stocks_realtimeprice_request = StocksRealtimepriceRequest(
            AccessTokenDict=access_token_dict,
            IsuNo=stock_code,
            KospiKosdaq="kospi",
        )
    elif stock_code in kospi_kosdaq_stockcode_dict["kosdaq"]:  # 코스닥종목
        stocks_realtimeprice_request = StocksRealtimepriceRequest(
            AccessTokenDict=access_token_dict,
            IsuNo=stock_code,
            KospiKosdaq="kosdaq",
        )

    asyncio.create_task(
        register_stocks_realtimeprice(
            stocks_realtimeprice_request,
            stock_profit_loss_price_dict,
        )
    )
