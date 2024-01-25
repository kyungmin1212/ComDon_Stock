import uvicorn
from fastapi import FastAPI

from contextlib import asynccontextmanager

from settings import env_settings
from models import AccessTokenRequest, OrderRequest, QueryIndexRequest, sAlertNumRequest

from trading import (
    get_access_token,
    buy_market_order,
    buy_limit_order,
    sell_market_order,
    sell_limit_order,
    get_query_index,
    query_index_to_sAlertNum,
)

ACCESS_TOKEN_DICT = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("프로그램 실행")
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

    ### 조건검색 query_index 가져오기 ###
    query_index_request = QueryIndexRequest(
        AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
        UserId=env_settings.USER_ID,
        ConditionName=env_settings.CONDITION_NAME,
    )

    query_index = await get_query_index(query_index_request)
    print(query_index)
    #######################################

    ### query_index -> sAlertNum 변경 ###
    salertnum_request = sAlertNumRequest(
        AccessToken=ACCESS_TOKEN_DICT["ACCESS_TOKEN"],
        query_index=query_index,
    )

    sAlertNum = await query_index_to_sAlertNum(salertnum_request)
    print(sAlertNum)
    #####################################

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
