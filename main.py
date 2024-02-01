import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from settings import env_settings
from utils import get_kospi_kosdaq_stockcode

from trading import (
    get_access_token_function,
    realtime_condition_connect_buy_function,
    condition_stock_register_realtimeprice_sell_function,
    command_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("프로그램 실행")

    ACCESS_TOKEN_DICT = {}

    # 실제 계좌 APP_KEY, APP_SECRET
    ACCESS_TOKEN_DICT["ACCESS_TOKEN"] = get_access_token_function(virtual=False)

    # 모의투자인 경우 추가
    if env_settings.VIRTUAL_FLAG == "1":
        # 모의투자 계좌 APP_KEY, APP_SECRET
        ACCESS_TOKEN_DICT["VIRTUAL_ACCESS_TOKEN"] = get_access_token_function(
            virtual=True
        )

    # kospi / kosdaq 종목 코드가져오기
    kospi_kosdaq_stockcode = get_kospi_kosdaq_stockcode()
    print(
        f"kospi 종목 수 : {len(kospi_kosdaq_stockcode['kospi'])}, kosdaq 종목 수 : {len(kospi_kosdaq_stockcode['kosdaq'])}"
    )

    print(f"{env_settings.CONDITION_NAME} 조건검색을 이용한 자동매매를 시작합니다.")

    condition_queue = asyncio.Queue()
    command_queue = asyncio.Queue()
    condition_set = set()

    asyncio.create_task(
        realtime_condition_connect_buy_function(
            access_token_dict=ACCESS_TOKEN_DICT,
            condition_queue=condition_queue,
            condition_set=condition_set,
        )
    )
    asyncio.create_task(
        condition_stock_register_realtimeprice_sell_function(
            access_token_dict=ACCESS_TOKEN_DICT,
            kospi_kosdaq_stockcode_dict=kospi_kosdaq_stockcode,
            condition_queue=condition_queue,
            command_queue=command_queue,
        )
    )

    asyncio.create_task(command_handler(command_queue, condition_set))

    yield

    print("프로그램 종료")


app = FastAPI(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
