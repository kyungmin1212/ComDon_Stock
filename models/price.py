from pydantic import BaseModel


class KosdoqStocksRealtimepriceRequest(BaseModel):
    AccessToken: str
    IsuNo: str


class KospiStocksRealtimepriceRequest(BaseModel):
    AccessToken: str
    IsuNo: str
