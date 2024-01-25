from pydantic import BaseModel


class QueryIndexRequest(BaseModel):
    AccessToken: str
    UserId: str  # 본인 id
    ConditionName: str  # 조건검색식 저장한 이름


class sAlertNumRequest(BaseModel):
    AccessToken: str
    query_index: str  # get_query_index를 통해 얻은 index
