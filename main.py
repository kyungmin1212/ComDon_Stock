import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from settings import env_settings
from utils import get_kospi_kosdaq_stockcode
from models import (
    AccessTokenRequest,
    QueryIndexRequest,
    sAlertNumRequest,
    RealtimeConditionRequest,
    ConditionStockRegisterRealtimepriceRequest,
)
from trading import (
    get_access_token,
    get_query_index,
    query_index_to_sAlertNum,
    realtime_condition_connect_buy,
    condition_stock_register_realtimeprice,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("프로그램 실행")

    ACCESS_TOKEN_DICT = {}

    # 실제 계좌 APP_KEY, APP_SECRET
    access_token_request = AccessTokenRequest(
        appkey=env_settings.APP_KEY, appsecretkey=env_settings.APP_SECRET
    )
    ACCESS_TOKEN_DICT["ACCESS_TOKEN"] = get_access_token(access_token_request)

    # 모의투자인 경우 추가
    if env_settings.A_FLAG == "1":
        # 모의투자 계좌 APP_KEY, APP_SECRET
        A_access_token_request = AccessTokenRequest(
            appkey=env_settings.A_APP_KEY, appsecretkey=env_settings.A_APP_SECRET
        )
        ACCESS_TOKEN_DICT["A_ACCESS_TOKEN"] = get_access_token(A_access_token_request)

    # kospi / kosdaq 종목 코드가져오기
    kospi_kosdaq_stockcode = get_kospi_kosdaq_stockcode()
    print(
        f"kospi 종목 수 : {len(kospi_kosdaq_stockcode['kospi'])}, kosdaq 종목 수 : {len(kospi_kosdaq_stockcode['kosdaq'])}"
    )

    print(f"{env_settings.CONDITION_NAME} 조건검색을 이용한 자동매매를 시작합니다.")

    ###########################실시간 조건검색 처리 부분 #######################################
    ### 조건검색 query_index 가져오기 ###
    query_index_request = QueryIndexRequest(
        AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
        UserId=env_settings.USER_ID,
        ConditionName=env_settings.CONDITION_NAME,
    )

    query_index = await get_query_index(query_index_request)
    #######################################

    ### query_index -> sAlertNum 변경 ###
    salertnum_request = sAlertNumRequest(
        AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
        query_index=query_index,
    )

    sAlertNum = await query_index_to_sAlertNum(salertnum_request)
    #####################################

    ### 실시간 조건검색 내역 받아오기(Websocket) ###
    realtime_condition_request = RealtimeConditionRequest(
        AccessTokenDict=ACCESS_TOKEN_DICT,
        sAlertNum=sAlertNum,
    )

    # 조건검색에서 검색된 종목을 실시간으로 데이터를 받아오게 등록하고, 정해진 익절 손절에 따라 매도합니다.
    codition_stock_register_realtimeprice_request = (
        ConditionStockRegisterRealtimepriceRequest(
            AccessTokenDict=ACCESS_TOKEN_DICT,
            KospiKosdaqStockCodeDict=kospi_kosdaq_stockcode,
        )
    )

    condition_queue = asyncio.Queue()
    search_condition_stock_buy_task = asyncio.create_task(
        realtime_condition_connect_buy(realtime_condition_request, condition_queue),
    )
    get_stock_realtimeprice_sell_task = asyncio.create_task(
        condition_stock_register_realtimeprice(
            codition_stock_register_realtimeprice_request, condition_queue
        )
    )

    yield
    ACCESS_TOKEN_DICT.clear()
    print("프로그램 종료")


app = FastAPI(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
