from pydantic import BaseModel


class AccessTokenRequest(BaseModel):
    appkey: str
    appsecretkey: str
