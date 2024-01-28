import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from settings import env_settings
from utils import get_kospi_kosdaq_stockcode
from models import (
    AccessTokenRequest,
    OrderRequest,
    QueryIndexRequest,
    sAlertNumRequest,
    RealtimeConditionRequest,
    KosdoqStocksRealtimepriceRequest,
    KospiStocksRealtimepriceRequest,
)
from trading import (
    get_access_token,
    buy_market_order,
    buy_limit_order,
    sell_market_order,
    sell_limit_order,
    get_query_index,
    query_index_to_sAlertNum,
    realtime_condition_connect,
    register_kosdoq_stocks_realtimeprice,
    register_kospi_stocks_realtimeprice,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("프로그램 실행")

    ACCESS_TOKEN_DICT = {}

    # 실제 계좌 APP_KEY, APP_SECRET
    access_token_request = AccessTokenRequest(
        appkey=env_settings.APP_KEY, appsecretkey=env_settings.APP_SECRET
    )

    # 모의투자 계좌 APP_KEY, APP_SECRET
    A_access_token_request = AccessTokenRequest(
        appkey=env_settings.A_APP_KEY, appsecretkey=env_settings.A_APP_SECRET
    )

    ACCESS_TOKEN_DICT["ACCESS_TOKEN"] = get_access_token(access_token_request)
    ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"] = get_access_token(A_access_token_request)

    # kospi / kosdaq 종목 코드가져오기
    kospi_kosdaq_stockcode = get_kospi_kosdaq_stockcode()
    print(
        f"kospi 종목 수 : {len(kospi_kosdaq_stockcode['kospi'])}, kosdaq 종목 수 : {len(kospi_kosdaq_stockcode['kosdaq'])}"
    )

    print(f"{env_settings.CONDITION_NAME} 조건검색을 이용한 자동매매를 시작합니다.")

    # ###########################실시간 조건검색 처리 부분 #######################################
    # ### 조건검색 query_index 가져오기 ###
    # query_index_request = QueryIndexRequest(
    #     AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
    #     UserId=env_settings.USER_ID,
    #     ConditionName=env_settings.CONDITION_NAME,
    # )

    # query_index = await get_query_index(query_index_request)
    # #######################################

    # ### query_index -> sAlertNum 변경 ###
    # salertnum_request = sAlertNumRequest(
    #     AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
    #     query_index=query_index,
    # )

    # sAlertNum = await query_index_to_sAlertNum(salertnum_request)
    # print(sAlertNum)
    # #####################################

    # ### 실시간 조건검색 내역 받아오기(Websocket) ###
    # condition_list = []
    # realtime_condition_request = RealtimeConditionRequest(
    #     AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
    #     sAlertNum=sAlertNum,
    # )

    # # 장이 열린동안 계속해서 실시간 조건검색 내역을 받아와야합니다.
    # asyncio.create_task(
    #     realtime_condition_connect(realtime_condition_request, condition_list)
    # )
    # await asyncio.sleep(1)
    # print(condition_list)
    # ##############################################
    # ###########################################################################################

    ### 실시간 가격 가져오기 ###
    # 등록
    # kosdoq
    # print("등록")
    # kosdoq_stocks_realtimeprice_request = KosdoqStocksRealtimepriceRequest(
    #     AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"], IsuNo="085670"
    # )
    # task1 = asyncio.create_task(
    #     get_kosdoq_stocks_realtimeprice(kosdoq_stocks_realtimeprice_request)
    # )
    # # kospi
    # kospi_stocks_realtimeprice_request = KospiStocksRealtimepriceRequest(
    #     AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"], IsuNo="005930"
    # )
    # task2 = asyncio.create_task(
    #     get_kospi_stocks_realtimeprice(kospi_stocks_realtimeprice_request)
    # )
    # await asyncio.sleep(1)

    # # 해제
    # print("해제")
    # task1.cancel()
    # task2.cancel()

    ############################

    # ### 주문 ####
    # order_request = OrderRequest(
    #     AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"], # 모의투자인 경우 ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"]
    #     IsuNo="005930", # 모의투자인 경우 "A005930"
    #     OrdQty=1,
    #     OrdPrc=70000,
    # )
    # order_result = await buy_market_order(order_request)
    # print(order_result)
    # ############

    yield
    ACCESS_TOKEN_DICT.clear()
    print("프로그램 종료")


app = FastAPI(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
