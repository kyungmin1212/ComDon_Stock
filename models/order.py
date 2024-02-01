from pydantic import BaseModel


class OrderRequest(BaseModel):
    AccessToken: str
    IsuNo: str  # 종목코드 / 모의투자일경우 앞에 A 붙여주기 ex. 005930 / A005930
    OrdQty: int  # 수량
    OrdPrc: float  # 가격 / 시장가일경우(OrdprcPtnCode : "03") 가격은 반드시 0으로 입력
