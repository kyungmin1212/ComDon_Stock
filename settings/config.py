from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_KEY: str
    APP_SECRET: str
    VIRTUAL_FLAG: str
    VIRTUAL_APP_KEY: str
    VIRTUAL_APP_SECRET: str
    USER_ID: str
    CONDITION_NAME: str
    TOTAL_BALANCE: float
    MAX_STOCKS: int
    PROFIT_PERCENT_1: float
    PROFIT_PERCENT_2: float
    LOSS_CRITERION: str
    LOSS_PERCENT: float
    ADD_BUY_FLAG: str
    BUY_PERCENT: float
    ADD_PROFIT_PERCENT_1: float
    ADD_PROFIT_PERCENT_2: float

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


env_settings = Settings()
