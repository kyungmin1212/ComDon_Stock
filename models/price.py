from pydantic import BaseModel


class StocksRealtimepriceRequest(BaseModel):
    AccessTokenDict: dict
    IsuNo: str
    KospiKosdaq: str


class ConditionStockRegisterRealtimepriceRequest(BaseModel):
    AccessTokenDict: dict
    KospiKosdaqStockCodeDict: dict
